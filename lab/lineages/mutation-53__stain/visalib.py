#!/usr/bin/env python3
"""visa — emit the machine condition an oracle implies.

lees subtracts a live env/host dictionary from an oracle so two
transcripts can be compared modulo substitution. visa is the unary
flip: one oracle in, the skip/apply predicate that machine must
satisfy. Empty require means the oracle is portable (OPEN). A
consistent HOME/platform/CI shape is BOUND. Contradictory recording
homes are UNSAT.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import platform
import re
import shlex
import stat
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator

VERSION = "0.2"

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

# Unquoted unix/windows paths. A single space inside a home component is
# allowed so `/Users/John Doe/kizu` is one path, not HOME=/Users/John.
PATH_RE = re.compile(
    r"(?:"
    r"/Users/[^/\s'\"\\`]+(?: [^/\s'\"\\`]+)*(?:/[^/\s'\"\\`]+)*"
    r"|/home/[^/\s'\"\\`]+(?: [^/\s'\"\\`]+)*(?:/[^/\s'\"\\`]+)*"
    r"|/tmp/[^/\s'\"\\`]+"
    r"|/private/var/folders/[^/\s'\"\\]+(?:/[^/\s'\"\\]+)*"
    r"|/var/folders/[^/\s'\"\\]+(?:/[^/\s'\"\\]+)*"
    r"|[A-Za-z]:\\(?:[^\\\s'\"`]+\\)+[^\\\s'\"`]+"
    r")"
)
# Quote-aware so `/home/ev'an` inside double quotes and backtick-wrapped
# markdown paths survive. Groups: pd double, ps single, pb backtick.
QUOTED_PATH_RE = re.compile(
    r'"(?P<pd>/(?:Users|home|tmp|private/var/folders|var/folders)/[^"]+|[A-Za-z]:\\[^"]+)"'
    r"|'(?P<ps>/(?:Users|home|tmp|private/var/folders|var/folders)/[^']+|[A-Za-z]:\\[^']+)'"
    r"|`(?P<pb>/(?:Users|home|tmp|private/var/folders|var/folders)/[^`]+|[A-Za-z]:\\[^`]+)`"
)

LABEL_RE = re.compile(
    r"(?im)^(?:export\s+)?(?P<k>home|user|username|logname|host|hostname|cwd|pwd|"
    r"platform|os|tmp(?:dir)?)\s*[:=]\s*(?P<v>.+?)\s*$"
)
ASSIGN_RE = re.compile(
    r"\b(?P<k>HOME|USER|USERNAME|LOGNAME|HOSTNAME|PWD|TMPDIR|RUNNER_OS|GITHUB_ACTIONS)"
    r"\s*=\s*(?P<q>['\"]?)(?P<v>[^'\"\s]+)(?P=q)"
)
PLATFORM_RE = re.compile(
    r"\b(Darwin|Linux|Windows|macOS|Mac OS X|win32|darwin|linux|aarch64|x86_64|amd64|arm64)\b"
)
PLATFORM_CANON = {
    "darwin": "Darwin",
    "macos": "Darwin",
    "mac os x": "Darwin",
    "linux": "Linux",
    "windows": "Windows",
    "win32": "Windows",
}

# Hostnames / users that are grammar, not identity.
STOP_ID = {
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
    "localhost",
    "hostname",
    "host",
    "ok",
    "debug",
    "info",
    "error",
    "warn",
    "green",
    "red",
    "unknown",
}

HARD_AXES = ("platform", "layout", "HOME", "USER", "CI")
SOFT_AXES = ("HOST", "CWD", "TMPDIR")
SOURCE_SUFFIX = {
    ".rs",
    ".swift",
    ".py",
    ".ts",
    ".js",
    ".tsx",
    ".jsx",
    ".go",
    ".c",
    ".h",
    ".mjs",
}
# Classic example identities. Applied only in test/source files — a
# snapshot that recorded alice is still alice's visa.
TEXTBOOK_USERS = {
    "user",
    "alice",
    "bob",
    "foo",
    "bar",
    "baz",
    "john",
    "jane",
    "john doe",
    "jane doe",
    "ubuntu",
    "nobody",
    "testuser",
}
# More-specific layout wins instead of UNSAT.
LAYOUT_JOIN = {
    frozenset({"linux-home", "gha-runner"}): "gha-runner",
    frozenset({"macos-home", "darwin-scratch"}): "macos-home",
}

PYTEST_PM_RE = re.compile(
    r"^E\s+(?:AssertionError:\s*)?(?:assert\s+)?(?P<a>.*) (?:==|!=) (?P<b>.*)$"
)
PYTEST_DIFF_MINUS = re.compile(r"^E\s+-\s+(?P<v>.*)$")
CARGO_LEFT_RE = re.compile(r"^\s*left:\s*(?P<v>.+)$")
UNITTEST_RE = re.compile(r"AssertionError:\s*(?P<a>.+?) (?:!=|==) (?P<b>.+)$")
SWIFT_RE = re.compile(
    r"XCTAssert(Equal|NotEqual).* - (?P<a>.+?) is not equal to (?P<b>.+)$"
)


@dataclass(frozen=True)
class Witness:
    axis: str
    value: str
    kind: str  # path | label | platform | assign
    role: str  # record | payload | fixture
    start: int
    end: int
    line: int
    col: int
    raw: str = ""


@dataclass
class Visa:
    path: str
    status: str  # OPEN | BOUND | SPEC | FIXTURE | UNSAT
    require: dict[str, str] = field(default_factory=dict)
    soft: dict[str, str] = field(default_factory=dict)
    witnesses: list[Witness] = field(default_factory=list)
    contradictions: list[dict[str, object]] = field(default_factory=list)
    match: str = ""  # MATCH | MISS | ""
    misses: list[dict[str, str]] = field(default_factory=list)


def line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_nl = text.rfind("\n", 0, index)
    col = index - last_nl
    return line, col


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return s[1:-1]
    return s


def _surrounding_token(text: str, start: int, end: int) -> str:
    lo, hi = start, end
    while lo > 0 and text[lo - 1] not in " \t\n'\"<>(),;|":
        lo -= 1
    while hi < len(text) and text[hi] not in " \t\n'\"<>(),;|":
        hi += 1
    return text[lo:hi]


def _is_github_fixture(tok: str) -> bool:
    if re.search(r"https?://|github\.com|gist\.github", tok, re.I):
        return True
    # `home:/Users/alice` and quoted `/Users/John Doe` contain slashes but
    # are filesystem paths, not owner/repo identity-as-data.
    if re.search(r"/(?:Users|home|tmp|var/folders)/", tok):
        return False
    if "/" in tok and not tok.startswith(("/", "~", "\\")):
        return True
    if "@" in tok and "." in tok:
        return True
    return False


def _usable_id(value: str) -> bool:
    v = value.strip()
    if len(v) < 2:
        return False
    if v.lower() in STOP_ID:
        return False
    if v.isdigit() and len(v) < 6:
        return False
    return True


def is_snapshot(path: str) -> bool:
    name = Path(path).name.lower()
    return bool(re.search(r"(\.snap$|golden|expected|oracle|snapshot)", name))


def is_test_source(path: str) -> bool:
    if not path or path in {"-", ""}:
        return False
    if is_snapshot(path):
        return False
    s = path.replace("\\", "/").lower()
    if re.search(r"(test_|_test\.|_tests\.|tests\.|/tests/|tests/)", s, re.I):
        return True
    return Path(path).suffix.lower() in SOURCE_SUFFIX


def layout_of(home: str) -> str:
    n = home.replace("\\", "/")
    if n.startswith("/Users/"):
        return "macos-home"
    if "/runner/work/" in n or n.startswith("/home/runner"):
        return "gha-runner"
    if n.startswith("/home/"):
        return "linux-home"
    if re.match(r"^[A-Za-z]:/Users/", n):
        return "windows-home"
    return "other"


def derive_from_path(p: str) -> dict[str, str]:
    """Map an absolute path to the axes it implies. Empty = weak (tmp)."""
    raw = p.strip()
    n = raw.replace("\\", "/")
    out: dict[str, str] = {}
    m = re.match(r"^/Users/([^/]+)", n)
    if m:
        user = m.group(1)
        out["platform"] = "Darwin"
        out["layout"] = "macos-home"
        out["HOME"] = f"/Users/{user}"
        if _usable_id(user):
            out["USER"] = user
        return out
    m = re.match(r"^/home/([^/]+)", n)
    if m:
        user = m.group(1)
        out["platform"] = "Linux"
        out["HOME"] = f"/home/{user}"
        if _usable_id(user):
            out["USER"] = user
        # GHA's default HOME is /home/runner even before GITHUB_WORKSPACE.
        if user == "runner":
            out["layout"] = "gha-runner"
            out["CI"] = "github-actions"
        else:
            out["layout"] = "linux-home"
        return out
    m = re.match(r"^([A-Za-z]:)/Users/([^/]+)", n)
    if m:
        user = m.group(2)
        drive = m.group(1)
        out["platform"] = "Windows"
        out["layout"] = "windows-home"
        out["HOME"] = f"{drive}/Users/{user}".replace("/", "\\")
        if _usable_id(user):
            out["USER"] = user
        return out
    if "/var/folders/" in n:
        out["platform"] = "Darwin"
        out["layout"] = "darwin-scratch"
        return out
    if n.startswith("/tmp/"):
        out["tmp"] = "unix"
        return out
    return out


def _canon_platform(word: str) -> str | None:
    return PLATFORM_CANON.get(word.lower())


def _ident_tail(value: str) -> str:
    return value.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def _is_textbook(axis: str, value: str) -> bool:
    ident = _ident_tail(value) if axis in {"HOME", "CWD", "TMPDIR"} else value
    if ident.lower() in TEXTBOOK_USERS:
        return True
    if " " in ident or "'" in ident:
        return True
    if len(ident) <= 2:
        return True
    return False


def classify_path_role(path: str, raw: str, text: str, start: int, end: int) -> str:
    """One role for every axis derived from a single path span.

    Otherwise HOME=/home/user becomes payload while platform=Linux from
    the same string stays a Darwin/Linux skip.
    """
    derived = derive_from_path(raw)
    if "tmp" in derived:
        return "payload"
    if not is_test_source(path):
        return "record"
    if " " in raw or "'" in raw:
        return "payload"
    for axis in ("HOME", "USER"):
        if axis in derived and _is_textbook(axis, derived[axis]):
            return "payload"
    return "record"


def classify_role(
    path: str,
    axis: str,
    value: str,
    kind: str,
    text: str,
    start: int,
    end: int,
) -> str:
    """Recording vs payload vs identity-as-data.

    Snapshots treat path/home shapes as the machine that recorded them.
    Test/source files construct textbook paths (`/home/user`, `/Users/John
    Doe`) as the spec of a parser/quoter — those are not a skip.
    """
    tok = _surrounding_token(text, start, end)
    if axis == "USER" and _is_github_fixture(tok):
        return "fixture"
    if axis == "tmp":
        return "payload"
    src = is_test_source(path)
    if src and kind == "platform":
        return "payload"
    if src and _is_textbook(axis, value):
        return "payload"
    if src and ("'" in tok or " " in value):
        return "payload"
    return "record"


def _add_witness(
    out: list[Witness],
    text: str,
    axis: str,
    value: str,
    kind: str,
    start: int,
    end: int,
    path: str,
    raw: str,
    role: str | None = None,
) -> None:
    if not value:
        return
    if role is None:
        role = classify_role(path, axis, value, kind, text, start, end)
    if axis == "USER" and _is_github_fixture(_surrounding_token(text, start, end)):
        role = "fixture"
    ln, col = line_col(text, start)
    out.append(
        Witness(
            axis=axis,
            value=value,
            kind=kind,
            role=role,
            start=start,
            end=end,
            line=ln,
            col=col,
            raw=raw,
        )
    )


def _add_path(
    out: list[Witness],
    text: str,
    raw: str,
    kind: str,
    start: int,
    end: int,
    path: str,
) -> None:
    role = classify_path_role(path, raw, text, start, end)
    for axis, val in derive_from_path(raw).items():
        _add_witness(out, text, axis, val, kind, start, end, path, raw, role=role)


def extract_witnesses(text: str, path: str = "") -> list[Witness]:
    occupied = bytearray(len(text))
    hits: list[Witness] = []

    def occupy(i: int, j: int) -> bool:
        if i < 0 or j > len(text) or i >= j:
            return False
        if any(occupied[i:j]):
            return False
        occupied[i:j] = b"\x01" * (j - i)
        return True

    for m in QUOTED_PATH_RE.finditer(text):
        p = m.group("pd") or m.group("ps") or m.group("pb")
        if not p:
            continue
        occupy(m.start(), m.end())
        i, j = m.start(), m.end()
        _add_path(hits, text, p, "path", i, j, path)

    for m in PATH_RE.finditer(text):
        i, j = m.start(), m.end()
        if any(occupied[i:j]):
            continue
        occupy(i, j)
        _add_path(hits, text, m.group(0), "path", i, j, path)

    for m in LABEL_RE.finditer(text):
        key = m.group("k").lower()
        val = _strip_quotes(m.group("v"))
        i, j = m.start("v"), m.end("v")
        if key in {"home", "cwd", "pwd", "tmp", "tmpdir"}:
            derived = derive_from_path(val)
            if derived:
                _add_path(hits, text, val, "label", i, j, path)
            elif key in {"home"} and val.startswith("~"):
                _add_witness(hits, text, "HOME", val, "label", i, j, path, val)
        elif key in {"user", "username", "logname"}:
            if _usable_id(val) and not _is_github_fixture(val):
                _add_witness(hits, text, "USER", val, "label", i, j, path, val)
        elif key in {"host", "hostname"}:
            if _usable_id(val):
                _add_witness(hits, text, "HOST", val, "label", i, j, path, val)
        elif key in {"platform", "os"}:
            plat = _canon_platform(val)
            if plat:
                _add_witness(hits, text, "platform", plat, "label", i, j, path, val)

    for m in ASSIGN_RE.finditer(text):
        key = m.group("k")
        val = m.group("v")
        i, j = m.start("v"), m.end("v")
        if key in {"HOME", "PWD", "TMPDIR"}:
            derived = derive_from_path(val)
            if derived:
                _add_path(hits, text, val, "assign", i, j, path)
        elif key in {"USER", "USERNAME", "LOGNAME"}:
            if _usable_id(val) and not _is_github_fixture(
                _surrounding_token(text, i, j)
            ):
                _add_witness(hits, text, "USER", val, "assign", i, j, path, val)
        elif key == "HOSTNAME":
            if _usable_id(val):
                _add_witness(hits, text, "HOST", val, "assign", i, j, path, val)
        elif key == "RUNNER_OS":
            plat = _canon_platform(val)
            if plat:
                _add_witness(hits, text, "platform", plat, "assign", i, j, path, val)
                _add_witness(
                    hits, text, "CI", "github-actions", "assign", i, j, path, val
                )
        elif key == "GITHUB_ACTIONS":
            if val.lower() in {"true", "1"}:
                _add_witness(
                    hits, text, "CI", "github-actions", "assign", i, j, path, val
                )

    for m in PLATFORM_RE.finditer(text):
        i, j = m.start(), m.end()
        if any(occupied[i:j]):
            continue
        plat = _canon_platform(m.group(0))
        if not plat:
            continue
        # Bare arch words are not a visa; OS words in dumps are.
        if m.group(0).lower() in {"aarch64", "x86_64", "amd64", "arm64"}:
            continue
        # Skip cfg(target_os = "macos") style — that's source, not a recording.
        tok = _surrounding_token(text, i, j)
        if "target_os" in tok or "cfg(" in text[max(0, i - 20) : i]:
            continue
        occupy(i, j)
        _add_witness(hits, text, "platform", plat, "platform", i, j, path, m.group(0))

    hits.sort(key=lambda w: (w.start, w.axis))
    return hits


def _dedupe_witnesses(hits: list[Witness]) -> list[Witness]:
    seen: set[tuple[str, str, str]] = set()
    out: list[Witness] = []
    for w in hits:
        key = (w.axis, w.value, w.role)
        if key in seen:
            continue
        seen.add(key)
        out.append(w)
    return out


def merge_visa(path: str, hits: list[Witness]) -> Visa:
    hits = _dedupe_witnesses(hits)
    by_axis: dict[str, dict[str, str]] = {}  # axis -> value -> role
    for w in hits:
        if w.axis == "tmp":
            continue
        by_axis.setdefault(w.axis, {})
        # record wins over payload/fixture for the same value
        prev = by_axis[w.axis].get(w.value)
        if prev == "record":
            continue
        by_axis[w.axis][w.value] = w.role

    require: dict[str, str] = {}
    soft: dict[str, str] = {}
    contradictions: list[dict[str, object]] = []

    for axis, values in sorted(by_axis.items()):
        recorded = {v: r for v, r in values.items() if r == "record"}
        if len(recorded) > 1:
            if axis == "layout":
                joined = LAYOUT_JOIN.get(frozenset(recorded))
                if joined:
                    require[axis] = joined
                    continue
            contradictions.append({"axis": axis, "values": sorted(recorded)})
            continue
        if len(recorded) == 1:
            val = next(iter(recorded))
            if axis in SOFT_AXES:
                soft[axis] = val
            else:
                require[axis] = val
            continue
        # only payload/fixture for this axis — not a requirement

    fixtures = [w for w in hits if w.role == "fixture"]
    payloads = [w for w in hits if w.role == "payload"]

    if contradictions:
        status = "UNSAT"
    elif require:
        status = "BOUND"
    elif fixtures and not payloads:
        status = "FIXTURE"
    elif payloads and not fixtures:
        status = "SPEC"
    elif fixtures or payloads:
        status = "SPEC"
    else:
        status = "OPEN"

    return Visa(
        path=path,
        status=status,
        require=require,
        soft=soft,
        witnesses=hits,
        contradictions=contradictions,
    )


def infer(text: str, path: str = "") -> Visa:
    return merge_visa(path or "-", extract_witnesses(text, path))


def live_axes() -> dict[str, str]:
    home = str(Path.home()).rstrip("/\\")
    user = getpass.getuser()
    plat = platform.system()
    axes = {
        "HOME": home,
        "USER": user,
        "platform": plat,
        "layout": layout_of(home),
        "HOST": platform.node().split(".")[0],
        "CWD": os.getcwd(),
    }
    if os.environ.get("GITHUB_ACTIONS"):
        axes["CI"] = "github-actions"
    elif os.environ.get("CI"):
        axes["CI"] = "ci"
    return {k: v for k, v in axes.items() if v}


def match_visa(visa: Visa, live: dict[str, str] | None = None) -> Visa:
    live = live_axes() if live is None else live
    visa = Visa(
        path=visa.path,
        status=visa.status,
        require=dict(visa.require),
        soft=dict(visa.soft),
        witnesses=list(visa.witnesses),
        contradictions=list(visa.contradictions),
    )
    if visa.status in {"OPEN", "SPEC", "FIXTURE"}:
        visa.match = "MATCH"
        visa.misses = []
        return visa
    if visa.status == "UNSAT":
        visa.match = "MISS"
        visa.misses = [
            {
                "axis": c["axis"] if isinstance(c, dict) else "*",
                "want": "consistent",
                "have": "contradiction",
            }
            for c in visa.contradictions
        ] or [{"axis": "*", "want": "consistent", "have": "contradiction"}]
        return visa
    misses: list[dict[str, str]] = []
    for axis, want in visa.require.items():
        have = live.get(axis, "")
        if axis == "HOME":
            if have.rstrip("/\\") != want.rstrip("/\\"):
                misses.append({"axis": axis, "want": want, "have": have or "(unset)"})
            continue
        if have != want:
            misses.append({"axis": axis, "want": want, "have": have or "(unset)"})
    visa.match = "MISS" if misses else "MATCH"
    visa.misses = misses
    return visa


def emit_shell(require: dict[str, str]) -> str:
    if not require:
        return "true"
    parts: list[str] = []
    plat = require.get("platform")
    if plat:
        parts.append(f'[ "$(uname -s)" = {shlex.quote(plat)} ]')
    home = require.get("HOME")
    if home:
        parts.append(f'[ "${{HOME}}" = {shlex.quote(home)} ]')
    elif require.get("USER"):
        parts.append(f'[ "${{USER}}" = {shlex.quote(require["USER"])} ]')
    if require.get("CI") == "github-actions":
        parts.append('[ -n "${GITHUB_ACTIONS:-}" ]')
    elif require.get("layout") == "gha-runner" and not home:
        parts.append('[ -n "${GITHUB_ACTIONS:-}" ]')
    if not parts:
        layout = require.get("layout", "")
        if layout == "macos-home":
            parts.append('[ "$(uname -s)" = Darwin ]')
        elif layout == "linux-home":
            parts.append('[ "$(uname -s)" = Linux ]')
        elif layout == "windows-home":
            parts.append('[ "$(uname -s)" = Windows_NT ]')
    return " && ".join(parts) if parts else "true"


def emit_pytest(require: dict[str, str]) -> str:
    """Expression that is true when the test should SKIP."""
    if not require:
        return "False"
    apply: list[str] = []
    plat = require.get("platform")
    if plat == "Darwin":
        apply.append("sys.platform == 'darwin'")
    elif plat == "Linux":
        apply.append("sys.platform.startswith('linux')")
    elif plat == "Windows":
        apply.append("sys.platform == 'win32'")
    home = require.get("HOME")
    if home:
        apply.append(f"pathlib.Path.home().as_posix() == {home!r}")
    elif require.get("USER"):
        apply.append(f"getpass.getuser() == {require['USER']!r}")
    if require.get("CI") == "github-actions":
        apply.append("os.environ.get('GITHUB_ACTIONS')")
    if not apply:
        return "False"
    return "not (" + " and ".join(apply) + ")"


def emit_gha(require: dict[str, str]) -> str:
    plat = require.get("platform")
    if plat == "Darwin":
        return "macos-latest"
    if plat == "Windows":
        return "windows-latest"
    if plat == "Linux" or require.get("CI") == "github-actions":
        return "ubuntu-latest"
    if not require:
        return "any"
    return "any"


def visa_to_dict(v: Visa) -> dict:
    return {
        "file": v.path,
        "status": v.status,
        "require": v.require,
        "soft": v.soft,
        "witnesses": [asdict(w) for w in v.witnesses],
        "contradictions": v.contradictions,
        "match": v.match,
        "misses": v.misses,
        "predicate": {
            "shell": emit_shell(v.require) if v.status != "UNSAT" else "false",
            "pytest": emit_pytest(v.require) if v.status != "UNSAT" else "True",
            "gha": emit_gha(v.require) if v.status != "UNSAT" else "none",
        },
    }


def format_human(v: Visa, *, show_match: bool = False) -> str:
    lines = [f"visa  {v.path}  {v.status}"]
    if v.status == "UNSAT":
        lines.append("  (contradictory machine conditions — oracle cannot apply)")
        for c in v.contradictions:
            vals = c.get("values") if isinstance(c, dict) else None
            axis = c.get("axis") if isinstance(c, dict) else "?"
            lines.append(f"  conflict {axis}  {' | '.join(map(str, vals or []))}")
    elif v.require:
        for axis, val in v.require.items():
            lines.append(f"  require  {axis}={val}")
    else:
        if v.status == "OPEN":
            lines.append("  (portable — apply on any machine)")
        elif v.status == "SPEC":
            lines.append("  (path/user strings are spec payload, not a skip)")
        elif v.status == "FIXTURE":
            lines.append("  (identity-as-data — not a machine demand)")
    for axis, val in v.soft.items():
        lines.append(f"  soft     {axis}={val}")
    for w in v.witnesses:
        shown = w.raw if w.raw else w.value
        if len(shown) > 72:
            shown = shown[:69] + "..."
        lines.append(
            f"  witness  {w.role:7} {w.kind:8} {w.axis}={w.value}  L{w.line}:{w.col}  {shown}"
        )
    pred = emit_shell(v.require) if v.status != "UNSAT" else "false"
    lines.append(f"  apply    {pred}")
    if show_match or v.match:
        if v.match == "MATCH":
            lines.append("  match    MATCH  this host satisfies the visa")
        elif v.match == "MISS":
            lines.append("  match    MISS   skip — this host is not the recording machine")
            for m in v.misses:
                lines.append(f"           {m['axis']} want={m['want']} have={m['have']}")
    return "\n".join(lines)


def porcelain(v: Visa) -> str:
    rows = [f"status\t{v.status}\t{v.path}"]
    for axis, val in v.require.items():
        rows.append(f"require\t{axis}\t{val}\t{v.path}")
    for axis, val in v.soft.items():
        rows.append(f"soft\t{axis}\t{val}\t{v.path}")
    for w in v.witnesses:
        rows.append(
            f"witness\t{w.role}\t{w.kind}\t{w.axis}\t{w.value}\t{v.path}\t{w.line}\t{w.col}"
        )
    for c in v.contradictions:
        rows.append(f"conflict\t{c.get('axis')}\t{'|'.join(map(str, c.get('values', [])))}")
    if v.match:
        rows.append(f"match\t{v.match}\t{v.path}")
        for m in v.misses:
            rows.append(f"miss\t{m['axis']}\t{m['want']}\t{m['have']}")
    pred = emit_shell(v.require) if v.status != "UNSAT" else "false"
    rows.append(f"predicate\tshell\t{pred}")
    return "\n".join(rows)


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


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


def parse_fail(text: str) -> list[tuple[str, str, str]]:
    """(kind, expected, actual) — visa the expected side (the oracle)."""
    pairs: list[tuple[str, str, str]] = []
    minus: str | None = None
    left: str | None = None

    def add(kind: str, a: str, b: str) -> None:
        a, b = _strip_quotes(a), _strip_quotes(b)
        if pairs and pairs[-1][1] == a and pairs[-1][2] == b:
            return
        pairs.append((kind, a, b))

    for line in text.splitlines():
        m = PYTEST_DIFF_MINUS.match(line)
        if m:
            minus = m.group("v")
            continue
        m = re.match(r"^E\s+\+\s+(?P<v>.*)$", line)
        if m and minus is not None:
            add("pytest", minus, m.group("v"))
            minus = None
            continue
        m = PYTEST_PM_RE.match(line)
        if m:
            add("pytest", m.group("a"), m.group("b"))
            continue
        m = UNITTEST_RE.search(line)
        if m:
            add("unittest", m.group("a"), m.group("b"))
            continue
        m = CARGO_LEFT_RE.match(line)
        if m:
            left = m.group("v")
            continue
        m = re.match(r"^\s*right:\s*(?P<v>.+)$", line)
        if m and left is not None:
            add("cargo", left, m.group("v"))
            left = None
            continue
        m = SWIFT_RE.search(line)
        if m:
            add("swift", m.group("a"), m.group("b"))
    return pairs


def infer_file(path: Path) -> Visa | None:
    text = read_text(path)
    if text is None:
        return None
    return infer(text, str(path))


def cmd_emit(v: Visa, kind: str) -> int:
    if v.status == "UNSAT":
        print("false" if kind == "shell" else ("True" if kind == "pytest" else "none"))
        return 0
    if kind == "shell":
        print(emit_shell(v.require))
    elif kind == "pytest":
        print(emit_pytest(v.require))
    elif kind == "gha":
        print(emit_gha(v.require))
    else:
        print(f"visa: unknown emit {kind}", file=sys.stderr)
        return 2
    return 0


def report(visas: list[Visa], args: argparse.Namespace) -> int:
    if args.emit and len(visas) == 1 and not args.json and not args.porcelain:
        return cmd_emit(visas[0], args.emit)
    if args.json:
        payload = {
            "mode": "visa",
            "files": [visa_to_dict(v) for v in visas],
        }
        if len(visas) == 1:
            payload.update(visa_to_dict(visas[0]))
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    elif args.porcelain:
        for v in visas:
            print(porcelain(v))
    else:
        for i, v in enumerate(visas):
            if i:
                print()
            print(format_human(v, show_match=args.match or args.apply))
            if args.emit:
                print(f"  emit     {args.emit}  ", end="")
                cmd_emit(v, args.emit)
    if args.apply:
        if any(v.status == "UNSAT" for v in visas):
            return 2
        if any(v.match == "MISS" for v in visas):
            return 1
        return 0
    return 0


def self_test() -> int:
    failed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal failed
        if cond:
            print(f"ok  {name}")
        else:
            failed += 1
            print(f"FAIL  {name}  {detail}", file=sys.stderr)

    local = (
        "build: ok\n"
        "user: alice\n"
        "home: /Users/alice\n"
        "host: alice-mbp\n"
        "cwd: /Users/alice/proj\n"
        "when: 2026-08-20T01:14:03Z\n"
        "timeout: 30\n"
        "status: green\n"
    )
    v = infer(local, "fixtures/local.snap")
    check("local BOUND", v.status == "BOUND", v.status)
    check("local HOME", v.require.get("HOME") == "/Users/alice", str(v.require))
    check("local platform Darwin", v.require.get("platform") == "Darwin", str(v.require))
    check("local USER alice", v.require.get("USER") == "alice", str(v.require))
    check("local HOST soft", v.soft.get("HOST") == "alice-mbp", str(v.soft))
    check("timeout is not a visa", "30" not in v.require.values(), str(v.require))
    sh = emit_shell(v.require)
    check("shell mentions Darwin", "Darwin" in sh, sh)
    check("shell mentions HOME", "/Users/alice" in sh, sh)
    check("pytest skip polarity", emit_pytest(v.require).startswith("not ("), emit_pytest(v.require))
    check("gha macos", emit_gha(v.require) == "macos-latest", emit_gha(v.require))

    ci = (
        "build: ok\n"
        "user: runner\n"
        "home: /home/runner\n"
        "host: fv-az123\n"
        "cwd: /home/runner/work/proj\n"
        "when: 2026-08-20T09:00:11Z\n"
        "timeout: 30\n"
    )
    c = infer(ci, "fixtures/ci.snap")
    check("ci BOUND", c.status == "BOUND", c.status)
    check("ci Linux", c.require.get("platform") == "Linux", str(c.require))
    check("ci GHA", c.require.get("CI") == "github-actions", str(c.require))
    check("ci HOME runner", c.require.get("HOME") == "/home/runner", str(c.require))
    check("gha ubuntu", emit_gha(c.require) == "ubuntu-latest")

    spec = "build: ok\ntimeout: 30\nstatus: green\n"
    s = infer(spec, "fixtures/spec_only.snap")
    check("spec OPEN", s.status == "OPEN", s.status)
    check("spec empty require", s.require == {}, str(s.require))
    check("spec shell true", emit_shell(s.require) == "true")

    conflict = "home: /Users/alice\nhome: /home/runner\n"
    u = infer(conflict, "fixtures/conflict.snap")
    check("conflict UNSAT", u.status == "UNSAT", u.status + str(u.contradictions))

    tmp = 'let p = PathBuf::from("/tmp/foo.rs");\n'
    t = infer(tmp, "fixtures/tmp_only.rs")
    check("tmp-only not BOUND", t.status in {"OPEN", "SPEC"}, t.status)
    check("tmp-only no HOME", "HOME" not in t.require, str(t.require))

    title = 'from: "GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome"\n'
    g = infer(title, "WindowTitleParserTests.swift")
    check("github title OPEN", g.status in {"OPEN", "FIXTURE"}, g.status)
    check("github title no USER require", "USER" not in g.require, str(g.require))

    ugly = "home: /Users/alice/日本語/dir with spaces/snap.txt\n"
    ug = infer(ugly, "ugly.snap")
    check("unicode path HOME", ug.require.get("HOME") == "/Users/alice", str(ug.require))

    quoted = 'let p = "/Users/John Doe/.cargo/bin/kizu";\n'
    q = infer(quoted, "quote.rs")
    # .rs is source: John Doe is a quoting fixture, not a skip.
    check("quoted space is payload in source", q.status in {"SPEC", "OPEN"}, q.status)
    check("quoted space no HOME require", "HOME" not in q.require, str(q.require))
    snap_jd = infer("home: /Users/John Doe\n", "john.snap")
    check(
        "John Doe in a snapshot is still BOUND",
        snap_jd.status == "BOUND" and snap_jd.require.get("HOME") == "/Users/John Doe",
        str(snap_jd.require),
    )

    payload = (
        'let mac = "/Users/John Doe/.cargo/bin/kizu";\n'
        'let linux = "/home/ev\'an/kizu";\n'
        'let textbook = "/home/user/project";\n'
    )
    pl = infer(payload, "fixtures/payload.rs")
    check("two layouts in source are SPEC not UNSAT", pl.status == "SPEC", pl.status)
    check("payload has no require", pl.require == {}, str(pl.require))

    hook = 'cwd: "/home/user/project"\npath: "/tmp/foo.rs"\n'
    hk = infer(hook, "src/hook/tests.rs")
    check("textbook /home/user in tests.rs is SPEC", hk.status == "SPEC", hk.status + str(hk.require))

    macos_cmt = "// when the macOS PollWatcher fallback is active.\n"
    mc = infer(macos_cmt, "tests/e2e/reactive.test.ts")
    check("bare macOS in a test comment is not BOUND", mc.status != "BOUND", mc.status)

    leak = 'assert_eq!(home, "/Users/annenpolka/proj");\n'
    lk = infer(leak, "src/hook/tests.rs")
    check(
        "non-textbook home in tests.rs stays a recording",
        lk.status == "BOUND" and lk.require.get("HOME") == "/Users/annenpolka",
        str(lk.require),
    )

    live = live_axes()
    alice_vs_live = match_visa(v, live)
    if live.get("HOME") == "/Users/alice":
        check("alice MATCH on alice host", alice_vs_live.match == "MATCH", str(live))
    else:
        check("alice MISS on this host", alice_vs_live.match == "MISS", alice_vs_live.match)
        check(
            "alice miss names HOME",
            any(m["axis"] == "HOME" for m in alice_vs_live.misses),
            str(alice_vs_live.misses),
        )

    mine = f"home: {live['HOME']}\nuser: {live['USER']}\n"
    mine_v = match_visa(infer(mine, "live.snap"), live)
    check("live snap MATCH", mine_v.match == "MATCH", mine_v.match + str(mine_v.require))

    open_m = match_visa(s, live)
    check("OPEN always MATCH", open_m.match == "MATCH")

    fail = (
        "E   AssertionError: '/Users/alice/proj' != '/home/runner/work/proj'\n"
        "E   - /Users/alice/proj\n"
        "E   + /home/runner/work/proj\n"
    )
    pairs = parse_fail(fail)
    check("parse pytest pair", len(pairs) >= 1, str(pairs))
    if pairs:
        ev = infer(pairs[0][1] + "\n", "<pytest expected>")
        check("from-fail expected BOUND Darwin", ev.require.get("platform") == "Darwin", str(ev.require))

    check("live axes nonempty", len(live) >= 3, str(live))
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="visa",
        description=(
            "Emit the machine condition a test oracle implies "
            "(required env/paths/users) as a skip/apply predicate."
        ),
    )
    p.add_argument("paths", nargs="*", help="oracle files (or a directory with --scan)")
    p.add_argument("-C", metavar="DIR", default=None, help="working directory / scan root")
    p.add_argument("--scan", action="store_true", help="walk a tree for test/golden/snapshot files")
    p.add_argument("--all", action="store_true", help="with --scan, consider every text file")
    p.add_argument(
        "--from-fail",
        action="store_true",
        help="parse expected/actual pairs from stdin; visa the expected (oracle) side",
    )
    p.add_argument(
        "--match",
        action="store_true",
        help="compare the visa against this host (MATCH / MISS)",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="exit 0 if this host may apply the oracle, 1 to skip, 2 if UNSAT",
    )
    p.add_argument(
        "--emit",
        choices=("shell", "pytest", "gha"),
        help="print only a predicate: shell apply / pytest skipif / GHA runs-on",
    )
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--porcelain", action="store_true", help="stable TSV")
    p.add_argument("--self-test", action="store_true", help="run built-in tests")
    p.add_argument("--version", action="version", version=f"visa {VERSION}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(list(sys.argv[1:] if argv is None else argv))

    if args.self_test:
        return self_test()

    if args.C:
        os.chdir(args.C)

    if args.from_fail:
        text = sys.stdin.read()
        pairs = parse_fail(text)
        if not pairs:
            v = infer(text, "-")
            if args.match or args.apply:
                v = match_visa(v)
            return report([v], args)
        visas: list[Visa] = []
        for kind, exp, _act in pairs:
            v = infer(exp + "\n", f"<{kind} expected>")
            if args.match or args.apply:
                v = match_visa(v)
            visas.append(v)
        return report(visas, args)

    files: list[Path] = []
    if args.scan:
        root = Path(args.paths[0]) if args.paths else Path(".")
        files = list(iter_oracle_files(root, all_files=args.all))
        if not files:
            print("visa: no oracle-like files", file=sys.stderr)
            return 1
    else:
        for p in args.paths:
            if p == "-":
                text = sys.stdin.read()
                v = infer(text, "-")
                if args.match or args.apply:
                    v = match_visa(v)
                return report([v], args)
            files.append(Path(p))

    if not files:
        build_parser().print_help()
        return 2

    visas = []
    for path in files:
        if path.is_dir() and not args.scan:
            print(f"visa: {path} is a directory (use --scan)", file=sys.stderr)
            return 2
        v = infer_file(path)
        if v is None:
            print(f"visa: skip binary/unreadable {path}", file=sys.stderr)
            continue
        if args.match or args.apply:
            v = match_visa(v)
        visas.append(v)
    if not visas:
        print("visa: no readable oracles", file=sys.stderr)
        return 1
    return report(visas, args)


if __name__ == "__main__":
    sys.exit(main())
