#!/usr/bin/env python3
"""lees — subtract env/machine sediment from a test oracle.

An oracle (snapshot, golden, expected, assertion dump) is a mixture of
specification and the machine that recorded it. lees builds a dictionary
from the live process environment plus host facts, stains the oracle,
and classifies what remains.

Unary:  lees FILE          # sediment vs spec
Binary: lees --par A B     # unify two transcripts under substitution
Fail:   cmd | lees --from-fail
Probe:  lees --probe -- CMD
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import platform
import re
import socket
import stat
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

VERSION = "0.2"

SKIP_ENV = {
    "PATH",
    "INFOPATH",
    "MANPATH",
    "CDPATH",
    "LS_COLORS",
    "LSCOLORS",
    "TERM",
    "TERM_PROGRAM",
    "TERM_PROGRAM_VERSION",
    "TERM_SESSION_ID",
    "ITERM_SESSION_ID",
    "ITERM_PROFILE",
    "COLORTERM",
    "SSH_AUTH_SOCK",
    "SSH_SOCK",
    "DISPLAY",
    "OLDPWD",
    "SHLVL",
    "_",
    "COMMAND_MODE",
    "LC_ALL",
    "LC_CTYPE",
    "LC_COLLATE",
    "SECURITYSESSIONID",
    "XPC_FLAGS",
    "XPC_SERVICE_NAME",
    "TMPDIR",  # macOS TMPDIR is a long unique path; added back as machine fact
}

SKIP_ENV_PREFIX = (
    "TERM_",
    "ITERM_",
    "VSCODE_",
    "CURSOR_",
    "GHOSTTY_",
    "__CF_",
    "LAUNCH_INSTANCE_ID",
)

STOP_VALUES = {
    "true",
    "false",
    "yes",
    "no",
    "on",
    "off",
    "none",
    "null",
    "nil",
    "test",
    "user",
    "home",
    "path",
    "root",
    "admin",
    "local",
    "utf-8",
    "utf8",
    "ascii",
    "c",
    "en_us",
    "c.utf-8",
    "1",
    "0",
    "2",
    "3",
    "ok",
    "debug",
    "info",
    "error",
    "warn",
}

NAMED_ENV = (
    "HOME",
    "USER",
    "LOGNAME",
    "USERNAME",
    "HOSTNAME",
    "PWD",
    "SHELL",
    "USERPROFILE",
    "HOMEDRIVE",
    "HOMEPATH",
    "XDG_CACHE_HOME",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "GITHUB_WORKSPACE",
    "GITHUB_WORKFLOW",
    "RUNNER_TEMP",
    "RUNNER_OS",
    "RUNNER_ARCH",
    "RUNNER_TRACKING_ID",
    "CI",
    "LANG",
    "TZ",
)

SKIP_DIRS = {
    ".git",
    "node_modules",
    "target",
    ".build",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    "venv",
    "vendor",
    ".pnpm",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "DerivedData",
}

ORACLE_NAME_RE = re.compile(
    r"(test_|_test\.|_tests\.|Tests|/tests/|golden|expected|oracle|snapshot|\.snap$|fixture)",
    re.I,
)
ORACLE_SUFFIXES = {
    ".py",
    ".rs",
    ".swift",
    ".ts",
    ".js",
    ".json",
    ".txt",
    ".snap",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
}

PATH_RE = re.compile(
    r"(?:"
    r"/Users/[^/\s'\"\\]+(?:/[^/\s'\"\\]+)*"
    r"|/home/[^/\s'\"\\]+(?:/[^/\s'\"\\]+)*"
    r"|/tmp/[^/\s'\"\\]+"
    r"|[A-Za-z]:\\(?:[^\\\s'\"`]+\\)+[^\\\s'\"`]+"
    r")"
)
# Unix home roots used as identity, not as a file oracle.
HOME_ROOT_RE = re.compile(r"^/(?:Users|home)/[^/]+$")
CLOCK_RE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?\b"
)
PLATFORM_RE = re.compile(
    r"\b(Darwin|Linux|Windows|macOS|Mac OS X|win32|darwin|linux|aarch64|x86_64|amd64|arm64)\b"
)
PLATFORM_WORDS = {
    "darwin",
    "linux",
    "windows",
    "macos",
    "mac os x",
    "win32",
    "aarch64",
    "x86_64",
    "amd64",
    "arm64",
}

IDENT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?$")

PYTEST_PM_RE = re.compile(
    r"^E\s+(?:AssertionError:\s*)?(?:assert\s+)?(?P<a>.*) (?:==|!=) (?P<b>.*)$"
)
PYTEST_DIFF_MINUS = re.compile(r"^E\s+-\s+(?P<v>.*)$")
PYTEST_DIFF_PLUS = re.compile(r"^E\s+\+\s+(?P<v>.*)$")
UNITTEST_RE = re.compile(
    r"AssertionError:\s*(?P<a>.+?) (?:!=|==) (?P<b>.+)$"
)
CARGO_LEFT_RE = re.compile(r"^\s*left:\s*(?P<v>.+)$")
CARGO_RIGHT_RE = re.compile(r"^\s*right:\s*(?P<v>.+)$")
SWIFT_RE = re.compile(
    r"XCTAssert(Equal|NotEqual).* - (?P<a>.+?) is not equal to (?P<b>.+)$"
)


@dataclass(frozen=True)
class Fact:
    name: str
    value: str
    kind: str  # env | machine | runtime
    source: str = ""


@dataclass(frozen=True)
class Hit:
    name: str
    value: str
    kind: str
    start: int
    end: int
    line: int
    col: int
    path: str = ""


@dataclass
class Sub:
    cls: str
    a: str
    b: str


@dataclass
class ParResult:
    verdict: str  # MACHINE | ENV | SPEC | MIXED | CLEAN
    substitutions: list[Sub] = field(default_factory=list)
    residue: list[str] = field(default_factory=list)
    holed_a: str = ""
    holed_b: str = ""


def usable(value: str, min_len: int = 3) -> bool:
    if not value or not isinstance(value, str):
        return False
    v = value.strip()
    if len(v) < min_len:
        return False
    if v.lower() in STOP_VALUES:
        return False
    if v.startswith("-") and " " not in v and len(v) < 8:
        return False
    return True


def collect_facts(
    env: dict[str, str] | None = None,
    cwd: str | None = None,
    extra: Iterable[Fact] = (),
) -> list[Fact]:
    env = dict(os.environ if env is None else env)
    cwd = os.getcwd() if cwd is None else cwd
    facts: list[Fact] = []
    seen_values: set[str] = set()

    def add(name: str, value: str, kind: str, source: str) -> None:
        if not usable(value):
            return
        if value in seen_values:
            return
        # Very short all-digit values are clocks or counts, not identity.
        if value.isdigit() and len(value) < 6:
            return
        seen_values.add(value)
        facts.append(Fact(name=name, value=value, kind=kind, source=source))

    for key in NAMED_ENV:
        if key in env:
            kind = "env"
            add(key, env[key], kind, f"env:{key}")

    for key, val in env.items():
        if key in NAMED_ENV or key in SKIP_ENV:
            continue
        if any(key.startswith(p) for p in SKIP_ENV_PREFIX):
            continue
        if not usable(val, min_len=8):
            continue
        if "/" not in val and "\\" not in val and len(val) < 12:
            continue
        add(key, val, "env", f"env:{key}")

    try:
        add("USER", _username(), "machine", "getpass")
    except Exception:
        pass
    try:
        add("HOST", socket.gethostname(), "machine", "hostname")
        add("HOST_SHORT", socket.gethostname().split(".")[0], "machine", "hostname")
    except Exception:
        pass
    add("HOME", str(Path.home()), "machine", "home")
    add("CWD", cwd, "machine", "cwd")
    add("PLATFORM", platform.system(), "machine", "platform")
    add("MAC_VER", platform.mac_ver()[0], "machine", "mac_ver")
    add("MACHINE", platform.machine(), "machine", "arch")
    add("NODE", platform.node(), "machine", "node")
    add("PY", sys.executable, "runtime", "sys.executable")
    add("PY_PREFIX", sys.prefix, "runtime", "sys.prefix")
    add("PY_VER", platform.python_version(), "runtime", "python")

    tmp = env.get("TMPDIR") or env.get("TMP") or env.get("TEMP")
    if tmp:
        add("TMPDIR", tmp.rstrip("/"), "machine", "tmpdir")

    git_root = _git_root(cwd)
    if git_root:
        add("GIT_ROOT", git_root, "machine", "git")

    for fact in extra:
        add(fact.name, fact.value, fact.kind, fact.source or "extra")

    facts.sort(key=lambda f: (-len(f.value), f.name))
    return facts


def _username() -> str:
    try:
        import getpass

        return getpass.getuser()
    except Exception:
        return os.environ.get("USER") or os.environ.get("LOGNAME") or ""


def _git_root(cwd: str) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip() or None
    except Exception:
        return None


def facts_from_json(blob: str) -> list[Fact]:
    data = json.loads(blob)
    facts = []
    for row in data:
        facts.append(
            Fact(
                name=row["name"],
                value=row["value"],
                kind=row.get("kind", "env"),
                source=row.get("source", "json"),
            )
        )
    facts.sort(key=lambda f: (-len(f.value), f.name))
    return facts


def _ok_boundary(text: str, start: int, end: int, value: str) -> bool:
    """Reject short alphanumeric values that sit inside a larger token."""
    if any(ch in value for ch in "/\\"):
        return True
    if len(value) >= 12:
        return True
    left = text[start - 1] if start > 0 else ""
    right = text[end] if end < len(text) else ""
    # "" in "_-" is True in Python; compare single characters only.
    if left.isalnum() or left in ("_", "-"):
        return False
    if right.isalnum() or right in ("_", "-"):
        return False
    return True


def line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_nl = text.rfind("\n", 0, index)
    col = index - last_nl
    return line, col


def find_dict_hits(text: str, facts: list[Fact], path: str = "") -> tuple[list[Hit], bytearray]:
    occupied = bytearray(len(text))
    hits: list[Hit] = []
    ordered = sorted(facts, key=lambda f: -len(f.value))
    for fact in ordered:
        val = fact.value
        if not val:
            continue
        start = 0
        while True:
            i = text.find(val, start)
            if i < 0:
                break
            j = i + len(val)
            if not any(occupied[i:j]) and _ok_boundary(text, i, j, val):
                occupied[i:j] = b"\x01" * (j - i)
                ln, col = line_col(text, i)
                hits.append(
                    Hit(
                        name=fact.name,
                        value=val,
                        kind=fact.kind,
                        start=i,
                        end=j,
                        line=ln,
                        col=col,
                        path=path,
                    )
                )
            start = i + 1
    hits.sort(key=lambda h: h.start)
    return hits, occupied


def _regex_hits(
    text: str,
    occupied: bytearray,
    regex: re.Pattern[str],
    kind: str,
    name: str,
    path: str,
    min_len: int = 1,
) -> list[Hit]:
    hits: list[Hit] = []
    for m in regex.finditer(text):
        i, j = m.start(), m.end()
        if j - i < min_len:
            continue
        if any(occupied[i:j]):
            continue
        occupied[i:j] = b"\x01" * (j - i)
        ln, col = line_col(text, i)
        hits.append(
            Hit(
                name=name,
                value=m.group(0),
                kind=kind,
                start=i,
                end=j,
                line=ln,
                col=col,
                path=path,
            )
        )
    return hits


def _surrounding_token(text: str, start: int, end: int) -> str:
    lo, hi = start, end
    while lo > 0 and text[lo - 1] not in " \t\n'\"<>(),;|":
        lo -= 1
    while hi < len(text) and text[hi] not in " \t\n'\"<>(),;|":
        hi += 1
    return text[lo:hi]


def _is_identity_fixture(text: str, hit: Hit) -> bool:
    """USER in a URL or owner/repo is test data, not a recording-host leak."""
    if hit.name not in {"USER", "LOGNAME", "USERNAME"}:
        return False
    tok = _surrounding_token(text, hit.start, hit.end)
    if re.search(r"https?://|github\.com|gist\.github", tok, re.I):
        return True
    if "/" in tok and not tok.startswith(("/", "~")):
        return True
    if "@" in tok and "." in tok:
        return True
    return False


def _plausible_foreign_path(value: str) -> bool:
    if "`" in value or "\\n" in value or "\\t" in value:
        return False
    return True


def stain(
    text: str,
    facts: list[Fact],
    path: str = "",
    *,
    foreign: bool = False,
    clocks: bool = False,
    platforms: bool = False,
) -> list[Hit]:
    hits, occupied = find_dict_hits(text, facts, path)
    extra: list[Hit] = []
    if foreign:
        extra.extend(
            h
            for h in _regex_hits(text, occupied, PATH_RE, "path", "PATH", path, min_len=6)
            if _plausible_foreign_path(h.value)
        )
    if clocks:
        extra.extend(_regex_hits(text, occupied, CLOCK_RE, "clock", "CLOCK", path, min_len=10))
    if platforms:
        extra.extend(_regex_hits(text, occupied, PLATFORM_RE, "platform", "PLATFORM", path, min_len=3))
    all_hits = hits + extra
    out: list[Hit] = []
    for h in all_hits:
        if _is_identity_fixture(text, h):
            out.append(
                Hit(
                    name=h.name,
                    value=h.value,
                    kind="fixture",
                    start=h.start,
                    end=h.end,
                    line=h.line,
                    col=h.col,
                    path=h.path,
                )
            )
        else:
            out.append(h)
    out.sort(key=lambda h: h.start)
    return out


def hole_text(text: str, hits: list[Hit]) -> str:
    if not hits:
        return text
    parts: list[str] = []
    last = 0
    for h in hits:
        parts.append(text[last : h.start])
        parts.append("{" + h.name + "}")
        last = h.end
    parts.append(text[last:])
    return "".join(parts)


def _split_keep_filename(p: str) -> tuple[list[str], str]:
    p = p.replace("\\", "/").rstrip("/")
    bits = p.split("/")
    if not bits:
        return [], p
    return bits[:-1], bits[-1]


def _is_filename(last: str) -> bool:
    return "." in last and not last.startswith(".")


def hole_path_pair(p1: str, p2: str) -> tuple[str, str]:
    """Hole differing directory prefixes; keep a shared filename.

    Last components that are *not* filenames (no extension) are machine
    identity — `/tmp/lees-home-a` vs `/tmp/lees-home-b`, `/Users/alice`
    vs `/home/runner` — and hole as a whole. `expected.txt` vs `actual.txt`
    stays as residue.
    """
    n1, n2 = p1.replace("\\", "/").rstrip("/"), p2.replace("\\", "/").rstrip("/")
    if HOME_ROOT_RE.match(n1) and HOME_ROOT_RE.match(n2):
        return "{HOME}", "{HOME}"
    pre1, last1 = _split_keep_filename(p1)
    pre2, last2 = _split_keep_filename(p2)
    if last1 != last2 and not (_is_filename(last1) and _is_filename(last2)):
        return "{PATH}", "{PATH}"
    i = 0
    while i < min(len(pre1), len(pre2)) and pre1[-(i + 1)] == pre2[-(i + 1)]:
        i += 1
    kept1 = [x for x in pre1[len(pre1) - i :] + [last1] if x != ""]
    kept2 = [x for x in pre2[len(pre2) - i :] + [last2] if x != ""]
    return "{PATH}/" + "/".join(kept1), "{PATH}/" + "/".join(kept2)


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return s[1:-1]
    return s


def _looks_path(s: str) -> bool:
    s = _strip_quotes(s)
    return bool(PATH_RE.match(s) or HOME_ROOT_RE.match(s) or re.match(r"^~[^/]*(/|$)", s))


def _looks_clock(s: str) -> bool:
    return bool(CLOCK_RE.fullmatch(_strip_quotes(s).strip()))


def _looks_platform(s: str) -> bool:
    return _strip_quotes(s).lower() in PLATFORM_WORDS


_HOLE_TOKEN_RE = re.compile(r"^\{[A-Z][A-Z0-9_]+\}$")


def _replace_span_pairs(
    a: str, b: str, spans_a: list[re.Match[str]], spans_b: list[re.Match[str]], hole_fn
) -> tuple[str, str]:
    """Replace paired regex spans from the right so indices stay valid."""
    n = min(len(spans_a), len(spans_b))
    if n == 0:
        return a, b
    na, nb = a, b
    for ma, mb in zip(reversed(spans_a[:n]), reversed(spans_b[:n])):
        ha, hb = hole_fn(ma.group(0), mb.group(0))
        na = na[: ma.start()] + ha + na[ma.end() :]
        nb = nb[: mb.start()] + hb + nb[mb.end() :]
    return na, nb


def unify_line(a: str, b: str, facts: list[Fact]) -> tuple[str, str, list[Sub]]:
    """Return holed (a, b) and substitutions discovered on this line pair.

    Path/clock/platform spans are paired on the *original* lines so a foreign
    machine (CI HOME, runner hostname) unifies even when it is not in the
    live dictionary. Dict staining fills named holes afterwards.
    """
    subs: list[Sub] = []
    a1, b1 = a, b

    pa, pb = list(PATH_RE.finditer(a1)), list(PATH_RE.finditer(b1))
    if pa and pb:
        n = min(len(pa), len(pb))
        for ma, mb in zip(pa[:n], pb[:n]):
            if ma.group(0) != mb.group(0):
                subs.append(Sub("PATH", ma.group(0), mb.group(0)))
        a1, b1 = _replace_span_pairs(a1, b1, pa, pb, hole_path_pair)
        if a1 == b1:
            return a1, b1, subs

    ca, cb = list(CLOCK_RE.finditer(a1)), list(CLOCK_RE.finditer(b1))
    if ca and cb:
        for ma, mb in zip(ca, cb):
            if ma.group(0) != mb.group(0):
                subs.append(Sub("CLOCK", ma.group(0), mb.group(0)))
        a1, b1 = CLOCK_RE.sub("{CLOCK}", a1), CLOCK_RE.sub("{CLOCK}", b1)
        if a1 == b1:
            return a1, b1, subs

    sa, sb = list(PLATFORM_RE.finditer(a1)), list(PLATFORM_RE.finditer(b1))
    if sa and sb:
        for ma, mb in zip(sa, sb):
            if ma.group(0) != mb.group(0):
                subs.append(Sub("PLATFORM", ma.group(0), mb.group(0)))
        a1, b1 = PLATFORM_RE.sub("{PLATFORM}", a1), PLATFORM_RE.sub("{PLATFORM}", b1)
        if a1 == b1:
            return a1, b1, subs

    hits_a = stain(a1, facts)
    hits_b = stain(b1, facts)
    a1, b1 = hole_text(a1, hits_a), hole_text(b1, hits_b)
    for ha, hb in zip(hits_a, hits_b):
        if ha.value != hb.value:
            subs.append(Sub(ha.kind.upper(), ha.value, hb.value))
    if a1 == b1:
        return a1, b1, subs

    tok_a = re.findall(r"\{[A-Z][A-Z0-9_]+\}|[^\s:]+|:", a1)
    tok_b = re.findall(r"\{[A-Z][A-Z0-9_]+\}|[^\s:]+|:", b1)
    if len(tok_a) == len(tok_b) and tok_a:
        out_a: list[str] = []
        out_b: list[str] = []
        changed = False
        for ta, tb in zip(tok_a, tok_b):
            if ta == tb:
                out_a.append(ta)
                out_b.append(tb)
                continue
            qa, qb = _strip_quotes(ta), _strip_quotes(tb)
            if _looks_path(qa) and _looks_path(qb):
                ha, hb = hole_path_pair(qa, qb)
                out_a.append(ha)
                out_b.append(hb)
                subs.append(Sub("PATH", qa, qb))
                changed = True
            elif _looks_clock(qa) and _looks_clock(qb):
                out_a.append("{CLOCK}")
                out_b.append("{CLOCK}")
                subs.append(Sub("CLOCK", qa, qb))
                changed = True
            elif _looks_platform(qa) and _looks_platform(qb):
                out_a.append("{PLATFORM}")
                out_b.append("{PLATFORM}")
                subs.append(Sub("PLATFORM", qa, qb))
                changed = True
            elif _HOLE_TOKEN_RE.match(ta) and (
                IDENT_RE.match(qb) or _looks_path(qb) or _looks_clock(qb)
            ):
                out_a.append(ta)
                out_b.append(ta)
                subs.append(Sub("MACHINE", qb, ta))
                changed = True
            elif _HOLE_TOKEN_RE.match(tb) and (
                IDENT_RE.match(qa) or _looks_path(qa) or _looks_clock(qa)
            ):
                out_a.append(tb)
                out_b.append(tb)
                subs.append(Sub("MACHINE", qa, tb))
                changed = True
            elif NUM_RE.match(qa) and NUM_RE.match(qb):
                out_a.append(ta)
                out_b.append(tb)
            elif (
                IDENT_RE.match(qa)
                and IDENT_RE.match(qb)
                and qa.lower() not in STOP_VALUES
                and qb.lower() not in STOP_VALUES
            ):
                out_a.append("{ID}")
                out_b.append("{ID}")
                subs.append(Sub("MACHINE", qa, qb))
                changed = True
            else:
                out_a.append(ta)
                out_b.append(tb)
        if changed:
            def _join(toks: list[str]) -> str:
                out: list[str] = []
                for i, t in enumerate(toks):
                    if i == 0 or t == ":" or toks[i - 1] == ":":
                        out.append(t)
                    else:
                        out.append(" " + t)
                return "".join(out)

            a1, b1 = _join(out_a), _join(out_b)
    return a1, b1, subs


def par(a: str, b: str, facts: list[Fact]) -> ParResult:
    if a == b:
        return ParResult(verdict="CLEAN", holed_a=a, holed_b=b)

    lines_a = a.splitlines()
    lines_b = b.splitlines()
    sm = difflib.SequenceMatcher(a=lines_a, b=lines_b, autojunk=False)
    holed_a_lines = list(lines_a)
    holed_b_lines = list(lines_b)
    subs: list[Sub] = []
    residue: list[str] = []
    env_only = True
    machiney = False

    def note_sub(s: Sub) -> None:
        nonlocal env_only, machiney
        if s.cls not in {"ENV"} and s.cls != "env":
            env_only = False
        if s.cls in {"PATH", "MACHINE", "PLATFORM", "CLOCK", "machine", "runtime"}:
            machiney = True
        if s not in subs:
            subs.append(s)

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace" and (i2 - i1) == (j2 - j1):
            for off, (la, lb) in enumerate(zip(lines_a[i1:i2], lines_b[j1:j2])):
                ha, hb, line_subs = unify_line(la, lb, facts)
                holed_a_lines[i1 + off] = ha
                holed_b_lines[j1 + off] = hb
                for s in line_subs:
                    note_sub(s)
                if ha != hb:
                    residue.append(f"- {ha}")
                    residue.append(f"+ {hb}")
            continue
        for la in lines_a[i1:i2]:
            residue.append(f"- {la}")
        for lb in lines_b[j1:j2]:
            residue.append(f"+ {lb}")

    holed_a = "\n".join(holed_a_lines)
    holed_b = "\n".join(holed_b_lines)
    if not residue:
        if not subs:
            verdict = "CLEAN"
        elif env_only and not machiney:
            verdict = "ENV"
        else:
            verdict = "MACHINE"
    elif not subs:
        verdict = "SPEC"
    else:
        verdict = "MIXED"
    return ParResult(
        verdict=verdict,
        substitutions=subs,
        residue=residue,
        holed_a=holed_a,
        holed_b=holed_b,
    )


def parse_fail(text: str) -> list[tuple[str, str, str]]:
    """Return (kind, expected, actual) pairs from a test runner transcript."""
    pairs: list[tuple[str, str, str]] = []
    lines = text.splitlines()
    minus: str | None = None
    left: str | None = None

    def add(kind: str, a: str, b: str) -> None:
        if pairs and pairs[-1][1] == a and pairs[-1][2] == b:
            return
        pairs.append((kind, a, b))

    for line in lines:
        m = PYTEST_DIFF_MINUS.match(line)
        if m:
            minus = _strip_quotes(m.group("v"))
            continue
        m = PYTEST_DIFF_PLUS.match(line)
        if m and minus is not None:
            add("pytest", minus, _strip_quotes(m.group("v")))
            minus = None
            continue
        m = PYTEST_PM_RE.match(line)
        if m:
            add("pytest", _strip_quotes(m.group("a")), _strip_quotes(m.group("b")))
            continue
        m = UNITTEST_RE.search(line)
        if m:
            add("unittest", _strip_quotes(m.group("a")), _strip_quotes(m.group("b")))
            continue
        m = CARGO_LEFT_RE.match(line)
        if m:
            left = _strip_quotes(m.group("v"))
            continue
        m = CARGO_RIGHT_RE.match(line)
        if m and left is not None:
            add("cargo", left, _strip_quotes(m.group("v")))
            left = None
            continue
        m = SWIFT_RE.search(line)
        if m:
            add("swift", _strip_quotes(m.group("a")), _strip_quotes(m.group("b")))
    return pairs


def is_oracle_path(path: Path) -> bool:
    s = str(path).replace("\\", "/")
    if path.suffix.lower() not in ORACLE_SUFFIXES and path.suffix != "":
        return False
    return bool(ORACLE_NAME_RE.search(s))


def iter_oracle_files(root: Path, *, all_files: bool = False) -> Iterator[Path]:
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                st = p.stat()
            except OSError:
                continue
            if not stat.S_ISREG(st.st_mode):
                continue
            if st.st_size > 2_000_000:
                continue
            if all_files or is_oracle_path(p):
                yield p


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def current_machine_hits(hits: list[Hit]) -> list[Hit]:
    return [h for h in hits if h.kind in {"env", "machine", "runtime"}]


PROBE_AXES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("env:HOME", {"HOME": "/tmp/lees-home-a"}, {"HOME": "/tmp/lees-home-b"}),
    ("env:TZ", {"TZ": "UTC"}, {"TZ": "Asia/Tokyo"}),
    ("env:LANG", {"LANG": "C"}, {"LANG": "ja_JP.UTF-8"}),
    ("env:USER", {"USER": "lees-alice"}, {"USER": "lees-bob"}),
]


def run_cmd(
    argv: list[str], env: dict[str, str], cwd: str | None, timeout: float
) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            argv,
            env=env,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        return 124, out, err + "\nlees: timeout\n"
    except FileNotFoundError:
        return 127, "", f"lees: not found: {argv[0]}\n"


def probe(argv: list[str], timeout: float, cwd: str | None) -> dict:
    base_env = dict(os.environ)
    rows = []
    spec_flip = False
    raw_flip = False
    for name, left, right in PROBE_AXES:
        e1 = dict(base_env)
        e1.update(left)
        e2 = dict(base_env)
        e2.update(right)
        c1, o1, r1 = run_cmd(argv, e1, cwd, timeout)
        c2, o2, r2 = run_cmd(argv, e2, cwd, timeout)
        raw1 = f"{o1}{r1}exit={c1}\n"
        raw2 = f"{o2}{r2}exit={c2}\n"
        raw_same = raw1 == raw2
        extra = [
            Fact("HOME", e1.get("HOME", ""), "env", "probe"),
            Fact("HOME", e2.get("HOME", ""), "env", "probe"),
            Fact("USER", e1.get("USER", ""), "env", "probe"),
            Fact("USER", e2.get("USER", ""), "env", "probe"),
            Fact("TZ", e1.get("TZ", ""), "env", "probe"),
            Fact("LANG", e1.get("LANG", ""), "env", "probe"),
        ]
        facts = collect_facts(env=e1, cwd=cwd or os.getcwd(), extra=extra)
        # Include right-hand overlay values so holing can see both.
        facts = collect_facts(env=e2, cwd=cwd or os.getcwd(), extra=list(facts) + extra)
        result = par(raw1, raw2, facts)
        spec_same = result.verdict in {"CLEAN", "MACHINE", "ENV"} and not result.residue
        if not raw_same:
            raw_flip = True
        if not spec_same:
            spec_flip = True
        rows.append(
            {
                "axis": name,
                "raw": "SAME" if raw_same else "FLIP",
                "spec": "STABLE" if spec_same else "FLIP",
                "verdict": result.verdict,
                "residue": result.residue[:8],
            }
        )
    if spec_flip:
        verdict = "SPEC-TIED"
    elif raw_flip:
        verdict = "ENV-TIED"
    else:
        verdict = "STABLE"
    return {"verdict": verdict, "cmd": argv, "axes": rows}


def format_hits_human(path: str, hits: list[Hit], status: str) -> str:
    lines = [f"lees  {path}  {status}"]
    if not hits:
        lines.append("  (clean — no env/machine sediment)")
        return "\n".join(lines)
    for h in hits:
        shown = h.value if len(h.value) <= 80 else h.value[:77] + "..."
        lines.append(f"  {h.kind.upper():8} {h.name}={shown}  L{h.line}:{h.col}")
    return "\n".join(lines)


def format_par_human(result: ParResult, a: str, b: str) -> str:
    lines = [f"lees  --par  {a}  {b}  verdict={result.verdict}"]
    if result.substitutions:
        lines.append("substitutions:")
        for s in result.substitutions:
            av = s.a if len(s.a) <= 60 else s.a[:57] + "..."
            bv = s.b if len(s.b) <= 60 else s.b[:57] + "..."
            lines.append(f"  {s.cls:8} {av}  →  {bv}")
    if result.residue:
        lines.append("residue:")
        for r in result.residue[:40]:
            lines.append(f"  {r}")
        if len(result.residue) > 40:
            lines.append(f"  ... {len(result.residue) - 40} more")
    if result.verdict in {"MACHINE", "ENV"}:
        lines.append("empty residue — the oracles agree modulo env/machine")
    elif result.verdict == "CLEAN":
        lines.append("byte-identical")
    elif result.verdict == "SPEC":
        lines.append("no sediment explains the diff — specification delta")
    else:
        lines.append("mixed: some env/machine, some spec")
    return "\n".join(lines)


def porcelain_hits(path: str, hits: list[Hit], status: str) -> str:
    rows = [f"status\t{status}\t{path}\t{len(hits)}"]
    for h in hits:
        rows.append(f"{h.kind}\t{h.name}\t{h.value}\t{path}\t{h.line}\t{h.col}")
    return "\n".join(rows)


def load_facts(args: argparse.Namespace) -> list[Fact]:
    extra: list[Fact] = []
    if args.dict_json:
        extra.extend(facts_from_json(Path(args.dict_json).read_text(encoding="utf-8")))
    if args.dict:
        extra.extend(facts_from_json(args.dict))
    env = dict(os.environ)
    if args.clean_dict:
        return sorted(extra, key=lambda f: (-len(f.value), f.name)) if extra else extra
    return collect_facts(env=env, cwd=args.C or os.getcwd(), extra=extra)


def cmd_dump_dict(facts: list[Fact], json_out: bool) -> int:
    rows = [asdict(f) for f in facts]
    if json_out:
        json.dump(rows, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        for f in facts:
            sys.stdout.write(f"{f.kind}\t{f.name}\t{f.value}\n")
    return 0


def cmd_stain(args: argparse.Namespace, facts: list[Fact], files: list[Path]) -> int:
    tainted = False
    reports = []
    for path in files:
        text = read_text(path)
        if text is None:
            print(f"lees: skip binary/unreadable {path}", file=sys.stderr)
            continue
        hits = stain(
            text,
            facts,
            str(path),
            foreign=args.foreign,
            clocks=args.clocks,
            platforms=args.platforms,
        )
        gate = current_machine_hits(hits)
        status = "TAINTED" if gate else "CLEAN"
        if status == "TAINTED":
            tainted = True
        reports.append({"path": str(path), "status": status, "hits": [asdict(h) for h in hits]})
        if args.json:
            continue
        if args.porcelain:
            print(porcelain_hits(str(path), hits, status))
        else:
            print(format_hits_human(str(path), hits, status))
        if args.holes:
            sys.stdout.write(hole_text(text, hits))
            if not text.endswith("\n"):
                sys.stdout.write("\n")
    if args.json:
        json.dump({"mode": "stain", "files": reports}, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    if args.check:
        return 1 if tainted else 0
    return 0


def cmd_par(args: argparse.Namespace, facts: list[Fact]) -> int:
    pa, pb = Path(args.par[0]), Path(args.par[1])
    ta, tb = read_text(pa), read_text(pb)
    if ta is None or tb is None:
        print("lees: --par requires two readable text files", file=sys.stderr)
        return 2
    result = par(ta, tb, facts)
    if args.json:
        json.dump(
            {
                "mode": "par",
                "a": str(pa),
                "b": str(pb),
                "verdict": result.verdict,
                "substitutions": [asdict(s) for s in result.substitutions],
                "residue": result.residue,
            },
            sys.stdout,
            indent=2,
            ensure_ascii=False,
        )
        sys.stdout.write("\n")
    elif args.porcelain:
        print(f"verdict\t{result.verdict}\t{len(result.substitutions)}\t{len(result.residue)}")
        for s in result.substitutions:
            print(f"sub\t{s.cls}\t{s.a}\t{s.b}")
        for r in result.residue:
            print(f"res\t{r}")
    else:
        print(format_par_human(result, str(pa), str(pb)))
    if args.check:
        return 0 if result.verdict in {"CLEAN", "MACHINE", "ENV"} else 1
    return 0


def cmd_from_fail(args: argparse.Namespace, facts: list[Fact], text: str) -> int:
    pairs = parse_fail(text)
    if not pairs:
        # Fall back: whole stdin vs nothing is not a pair. Try stain.
        hits = stain(text, facts, "-", foreign=True, clocks=True, platforms=True)
        status = "TAINTED" if current_machine_hits(hits) else "CLEAN"
        if args.json:
            json.dump(
                {"mode": "from-fail", "pairs": [], "fallback": status, "hits": [asdict(h) for h in hits]},
                sys.stdout,
                indent=2,
                ensure_ascii=False,
            )
            sys.stdout.write("\n")
        else:
            print(format_hits_human("-", hits, status))
            print("lees: no expected/actual pairs parsed")
        return 1 if args.check and status == "TAINTED" else 0

    rows = []
    blocking = False
    for kind, exp, act in pairs:
        result = par(exp + "\n", act + "\n", facts)
        rows.append(
            {
                "parser": kind,
                "expected": exp,
                "actual": act,
                "verdict": result.verdict,
                "substitutions": [asdict(s) for s in result.substitutions],
                "residue": result.residue,
            }
        )
        if result.verdict not in {"CLEAN", "MACHINE", "ENV"}:
            blocking = True
        if not args.json and not args.porcelain:
            print(f"pair  {kind}  verdict={result.verdict}")
            print(f"  expected {exp}")
            print(f"  actual   {act}")
            for s in result.substitutions:
                print(f"  {s.cls:8} {s.a}  →  {s.b}")
            for r in result.residue:
                print(f"  residue {r}")
    if args.json:
        json.dump({"mode": "from-fail", "pairs": rows}, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    elif args.porcelain:
        for row in rows:
            print(f"pair\t{row['parser']}\t{row['verdict']}\t{row['expected']}\t{row['actual']}")
    if args.check:
        return 1 if blocking else 0
    return 0


def cmd_probe(args: argparse.Namespace) -> int:
    if not args.cmd:
        print("lees: --probe requires a command after --", file=sys.stderr)
        return 2
    result = probe(args.cmd, timeout=args.timeout, cwd=args.C)
    if args.json:
        json.dump({"mode": "probe", **result}, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        print(f"lees  --probe  verdict={result['verdict']}")
        print("cmd   " + " ".join(result["cmd"]))
        for row in result["axes"]:
            print(f"  {row['axis']:10}  raw={row['raw']:4}  spec={row['spec']:6}  ({row['verdict']})")
            for r in row["residue"]:
                print(f"             {r}")
    if args.check:
        return 0 if result["verdict"] in {"STABLE", "ENV-TIED"} else 1
    return 0


def cmd_holes(args: argparse.Namespace, facts: list[Fact], path: Path) -> int:
    text = read_text(path)
    if text is None:
        print(f"lees: cannot read {path}", file=sys.stderr)
        return 2
    hits = stain(
        text,
        facts,
        str(path),
        foreign=args.foreign,
        clocks=args.clocks,
        platforms=args.platforms,
    )
    sys.stdout.write(hole_text(text, hits))
    if not text.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lees",
        description="Subtract env/machine sediment from a test oracle. "
        "What remains is the specification.",
    )
    p.add_argument("paths", nargs="*", help="oracle files (or a directory with --scan)")
    p.add_argument("-C", metavar="DIR", default=None, help="working directory / scan root")
    p.add_argument("--scan", action="store_true", help="walk a tree for test/golden/snapshot files")
    p.add_argument("--all", action="store_true", help="with --scan, consider every text file")
    p.add_argument("--par", nargs=2, metavar=("A", "B"), help="unify two transcripts")
    p.add_argument("--from-fail", action="store_true", help="parse expected/actual pairs from stdin")
    p.add_argument("--probe", action="store_true", help="rerun command under env axis tilts")
    p.add_argument("--cmd", nargs=argparse.REMAINDER, help="command for --probe (use -- to separate)")
    p.add_argument("--holes", action="store_true", help="rewrite stained files to stdout")
    p.add_argument("--dump-dict", action="store_true", help="print the live env/machine dictionary")
    p.add_argument("--dict-json", metavar="FILE", help="load extra facts from JSON")
    p.add_argument("--dict", metavar="JSON", help="inline extra facts JSON")
    p.add_argument("--clean-dict", action="store_true", help="use only --dict / --dict-json (no live host)")
    p.add_argument(
        "--foreign",
        action="store_true",
        help="also stain foreign absolute paths (/Users, /home, /tmp)",
    )
    p.add_argument("--clocks", action="store_true", help="also stain ISO timestamps")
    p.add_argument("--platforms", action="store_true", help="also stain Darwin/Linux/arch tokens")
    p.add_argument("--check", action="store_true", help="exit 1 if current-machine sediment (or spec residue)")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--porcelain", action="store_true", help="stable TSV")
    p.add_argument("--timeout", type=float, default=15.0, help="--probe timeout seconds")
    p.add_argument("--self-test", action="store_true", help="run built-in tests")
    p.add_argument("--version", action="version", version=f"lees {VERSION}")
    return p


def self_test() -> int:
    """Hermetic tests; no dependence on this host's HOME."""
    failed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal failed
        if cond:
            print(f"ok  {name}")
        else:
            failed += 1
            print(f"FAIL  {name}  {detail}", file=sys.stderr)

    facts = facts_from_json(
        json.dumps(
            [
                {"name": "HOME", "value": "/Users/alice", "kind": "env"},
                {"name": "USER", "value": "alice", "kind": "env"},
                {"name": "HOST", "value": "alice-mbp", "kind": "machine"},
            ]
        )
    )
    snap = (
        "build: ok\n"
        "user: alice\n"
        "home: /Users/alice\n"
        "host: alice-mbp\n"
        "when: 2026-08-20T01:14:03Z\n"
        "timeout: 30\n"
    )
    hits = stain(snap, facts)
    names = {h.name for h in hits}
    check("stain HOME", "HOME" in names)
    check("stain USER", "USER" in names)
    check("stain HOST", "HOST" in names)
    check("stain skips spec", all(h.value != "30" for h in hits))

    holed = hole_text(snap, hits)
    check("holes hide home", "/Users/alice" not in holed)
    check("holes keep spec", "timeout: 30" in holed)

    ci = (
        "build: ok\n"
        "user: runner\n"
        "home: /home/runner\n"
        "host: fv-az123\n"
        "when: 2026-08-20T09:00:11Z\n"
        "timeout: 30\n"
    )
    r = par(snap, ci, facts)
    check("par machine-only → MACHINE", r.verdict in {"MACHINE", "ENV"}, r.verdict)
    check("par empty residue", r.residue == [], str(r.residue))

    mixed = ci.replace("timeout: 30", "timeout: 60")
    r2 = par(snap, mixed, facts)
    check("par timeout 30 vs 60 → MIXED or SPEC", r2.verdict in {"MIXED", "SPEC"}, r2.verdict)
    check("par keeps 30/60 residue", any("30" in x or "60" in x for x in r2.residue), str(r2.residue))

    spec_a = "build: ok\ntimeout: 30\n"
    spec_b = "build: ok\ntimeout: 60\n"
    r3 = par(spec_a, spec_b, facts)
    check("par numeric-only → SPEC", r3.verdict == "SPEC", r3.verdict)

    r4 = par(spec_a, spec_a, facts)
    check("par identical → CLEAN", r4.verdict == "CLEAN")

    pytest_log = (
        "    def test_cwd():\n"
        "E       AssertionError: '/Users/alice/proj' != '/home/runner/work/proj'\n"
    )
    pairs = parse_fail(pytest_log)
    check("parse unittest/pytest !=", len(pairs) == 1, str(pairs))
    if pairs:
        pr = par(pairs[0][1] + "\n", pairs[0][2] + "\n", facts)
        check("from-fail path pair → MACHINE", pr.verdict in {"MACHINE", "ENV"}, pr.verdict + str(pr.residue))

    cargo_log = '  left: "/Users/alice/x"\n right: "/home/runner/x"\n'
    cp = parse_fail(cargo_log)
    check("parse cargo left/right", len(cp) == 1, str(cp))

    pytest_pm = "E       assert '/Users/alice' == '/home/runner'\n"
    pp = parse_fail(pytest_pm)
    check("parse pytest assert ==", len(pp) == 1, str(pp))

    ugly = "home: /Users/alice/日本語/dir with space/snap.txt\n"
    uh = stain(ugly, facts)
    check("unicode path still hits HOME prefix", any(h.name == "HOME" for h in uh), str(uh))

    # Occupied: USER must not match inside HOME.
    only_home = "/Users/alice/secret\n"
    hh = stain(only_home, facts)
    check("USER not inside HOME", all(h.name != "USER" for h in hh), str(hh))

    # Boundary: short user should not match inside 'malice'.
    bound = "malice\n"
    bh = stain(bound, facts)
    check("boundary blocks malice", bh == [], str(bh))

    tz_facts = facts_from_json(
        json.dumps(
            [
                {"name": "TZ", "value": "UTC", "kind": "env"},
                {"name": "TZ", "value": "Asia/Tokyo", "kind": "env"},
                {"name": "USER", "value": "lees-alice", "kind": "env"},
                {"name": "USER", "value": "lees-bob", "kind": "env"},
            ]
        )
    )
    utc_hits = stain("tz:UTC\n", tz_facts)
    check("UTC at EOL stains", any(h.value == "UTC" for h in utc_hits), str(utc_hits))
    pr_tz = par("tz:UTC\nuser:lees-alice\n", "tz:Asia/Tokyo\nuser:lees-bob\n", tz_facts)
    check("probe-like TZ/USER → MACHINE/ENV", pr_tz.verdict in {"MACHINE", "ENV"} and not pr_tz.residue, pr_tz.verdict + str(pr_tz.residue))
    pr_home = par("home:/tmp/lees-home-a\n", "home:/tmp/lees-home-b\n", facts)
    check("tmp overlay homes unify", pr_home.verdict in {"MACHINE", "ENV"} and not pr_home.residue, pr_home.verdict + str(pr_home.residue))

    ident = facts_from_json(json.dumps([{"name": "USER", "value": "annenpolka", "kind": "env"}]))
    url_hits = stain('url = "https://github.com/annenpolka/sitbone"\n', ident)
    check(
        "USER in github URL is fixture",
        url_hits and all(h.kind == "fixture" for h in url_hits),
        str(url_hits),
    )
    owner_hits = stain('title = "GitHub - annenpolka/sitbone - Chrome"\n', ident)
    check(
        "USER in owner/repo is fixture",
        owner_hits and all(h.kind == "fixture" for h in owner_hits),
        str(owner_hits),
    )
    lone_hits = stain("user: annenpolka\n", ident)
    check(
        "standalone USER stays env",
        lone_hits and all(h.kind == "env" for h in lone_hits),
        str(lone_hits),
    )
    check(
        "fixture does not taint --check",
        current_machine_hits(url_hits) == [],
        str(current_machine_hits(url_hits)),
    )

    live = collect_facts()
    check("live dict nonempty", len(live) >= 3, str(len(live)))
    check("live has HOME", any(f.name == "HOME" for f in live), ",".join(f.name for f in live[:12]))

    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # Allow `lees --probe -- cmd args` and `lees --probe cmd args`
    if "--" in argv:
        i = argv.index("--")
        pre, post = argv[:i], argv[i + 1 :]
        args = build_parser().parse_args(pre)
        if post:
            args.cmd = post
    else:
        args = build_parser().parse_args(argv)

    if args.self_test:
        return self_test()

    if args.C:
        os.chdir(args.C)

    facts = load_facts(args)

    if args.dump_dict:
        return cmd_dump_dict(facts, args.json)

    if args.probe:
        return cmd_probe(args)

    if args.par:
        return cmd_par(args, facts)

    if args.from_fail:
        text = sys.stdin.read()
        return cmd_from_fail(args, facts, text)

    files: list[Path] = []
    if args.scan:
        root = Path(args.paths[0]) if args.paths else Path(".")
        files = list(iter_oracle_files(root, all_files=args.all))
        if not files:
            print("lees: no oracle-like files", file=sys.stderr)
            return 1
    else:
        files = [Path(p) for p in args.paths]

    if not files and not args.holes:
        build_parser().print_help()
        return 2

    if args.holes and len(files) == 1 and not args.scan:
        return cmd_holes(args, facts, files[0])

    return cmd_stain(args, facts, files)


if __name__ == "__main__":
    sys.exit(main())
