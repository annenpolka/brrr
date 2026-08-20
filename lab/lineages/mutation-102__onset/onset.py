#!/usr/bin/env python3
"""onset — when an assertion newly acquired an actual-bound machine.

held occupies a boolean. mint occupies production clearance polarity.
troth names the legal apply set of one fail dump. onset walks git
history of *assertion windows* and emits the commit where the actual
side first names a machine (this host's $HOME, /Users/alice, …).

Comments are not oaths. GitHub titles stay FIXTURE, not TAINTED.
Expected-side BOUND is a different first. Nested call args are not
the actual.
"""
from __future__ import annotations

import argparse
import getpass
import io
import json
import os
import platform
import re
import stat
import subprocess
import sys
import tempfile
import tokenize
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

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

SOURCE_SUFFIX = {
    ".py",
    ".rs",
    ".swift",
    ".ts",
    ".js",
    ".tsx",
    ".jsx",
    ".mjs",
    ".go",
}

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
QUOTED_PATH_RE = re.compile(
    r'"(?P<pd>/(?:Users|home|tmp|private/var/folders|var/folders)/[^"]+|[A-Za-z]:\\[^"]+)"'
    r"|'(?P<ps>/(?:Users|home|tmp|private/var/folders|var/folders)/[^']+|[A-Za-z]:\\[^']+)'"
    r"|`(?P<pb>/(?:Users|home|tmp|private/var/folders|var/folders)/[^`]+|[A-Za-z]:\\[^`]+)`"
)

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
    "github",
    "https",
    "http",
    "com",
    "org",
    "src",
    "lib",
    "pkg",
    "app",
    "helpers",
    "target",
    "assets",
    "refs",
    "spec",
    "owner",
    "repo",
}

# Grammar / quoting fixtures, not a skip. alice is a recorded machine.
TEXTBOOK_TAILS = {
    "user",
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

FILEISH_RE = re.compile(r"\.[A-Za-z0-9]{1,8}$")
GITHUB_OWNER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9-]{2,38}$")

AXIS_FROM_EXPR = (
    (
        "USER",
        re.compile(
            r"(?ix)environ\[\s*['\"]USER(?:NAME)?['\"]|getenv\(\s*['\"]USER"
            r"|env::var\(\s*['\"]USER|NSUserName|getpass\.getuser|getuser\("
            r"|ProcessInfo.*userName|\$\{?USER\}?"
        ),
    ),
    (
        "HOME",
        re.compile(
            r"(?ix)environ\[\s*['\"]HOME['\"]|getenv\(\s*['\"]HOME"
            r"|env::var\(\s*['\"]HOME|Path\.home\(|expanduser|NSHomeDirectory"
            r"|\$\{?HOME\}?"
        ),
    ),
)

ENV_TIED_RE = re.compile(
    r"(?ix)os\.environ|getenv|env::var|NSUserName|NSHomeDirectory|"
    r"Path\.home|expanduser|getpass|\$\{?(?:HOME|USER)\}?"
)

RAN_ON_RE = re.compile(r"\bran\s+on\s+([A-Za-z][A-Za-z0-9._-]*)", re.I)

PY_ASSERT_FUNCS = {
    "assertEqual",
    "assertEquals",
    "assertNotEqual",
    "assert_equal",
    "assert_equals",
}

CALL_HEADS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"#expect\b"), "expect", "compare-parens"),
    (re.compile(r"#require\b"), "require", "compare-parens"),
    (re.compile(r"XCTAssertEqual\b"), "XCTAssertEqual", "second"),
    (re.compile(r"XCTAssertNotEqual\b"), "XCTAssertNotEqual", "second"),
    (re.compile(r"assert_eq!\s*"), "assert_eq!", "second"),
    (re.compile(r"assert_ne!\s*"), "assert_ne!", "second"),
    (re.compile(r"\bassertEqual\b"), "assertEqual", "second"),
    (re.compile(r"\bassertEquals\b"), "assertEquals", "second"),
    (re.compile(r"\bassertNotEqual\b"), "assertNotEqual", "second"),
    (re.compile(r"\bassert\.strictEqual\b"), "assert.strictEqual", "second"),
    (re.compile(r"\bassert\.equal\b"), "assert.equal", "second"),
    (re.compile(r"\bassert\.Equal\b"), "assert.Equal", "go"),
    (re.compile(r"\brequire\.Equal\b"), "require.Equal", "go"),
]

SWIFT_HASH_MACROS = (
    "expect",
    "require",
    "assert",
    "available",
    "selector",
    "keyPath",
    "if",
    "elseif",
    "else",
    "endif",
    "warning",
    "error",
)

SWIFT_FAIL_RE = re.compile(
    r"XCTAssert(?:Equal|NotEqual)(?:\s+failed:?\s*:?)?\s*"
    r"(?:\((?P<qa>[^)]+)\)|(?P<a>.+?)) "
    r"is not equal to (?:\((?P<qb>[^)]+)\)|(?P<b>.+))$"
)
PYTEST_DIFF_MINUS = re.compile(r"^E\s+-\s+(?P<v>.*)$")
PYTEST_DIFF_PLUS = re.compile(r"^E\s+\+\s+(?P<v>.*)$")
JUNIT_RE = re.compile(
    r"expected:\s*<(?P<a>.*?)>\s*but was:\s*<(?P<b>.*?)>",
    re.I,
)

BLOB_HINT = (
    b"assert",
    b"XCTAssert",
    b"#expect",
    b"#require",
    b"/Users/",
    b"/home/",
    b"GitHub",
    b"github.com",
    b"AssertionError",
    b"is not equal to",
)

MAX_BLOB = 2_000_000


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Window:
    kind: str  # assert | expect | fail
    form: str
    expected: str
    actual: str
    start: int
    end: int
    line: int
    col: int


@dataclass(frozen=True)
class Hit:
    path: str
    line: int
    form: str
    side: str  # actual | expected | fixture | comment
    status: str  # BOUND | OPEN | SPEC | FIXTURE | SILENT
    require: dict[str, str]
    raw: str
    kind: str = ""  # this-host | alice | runner | other | ""


@dataclass
class Census:
    path: str
    assertions: int = 0
    actual_bound: int = 0
    expected_bound: int = 0
    fixture: int = 0
    spec: int = 0
    silent: int = 0
    hits: list[Hit] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.actual_bound:
            return "ACTUAL-BOUND"
        if self.expected_bound:
            return "EXPECTED-BOUND"
        if self.fixture and not self.spec:
            return "FIXTURE"
        if self.spec and not self.fixture:
            return "SPEC"
        if self.fixture or self.spec:
            return "SPEC"
        if self.assertions:
            return "OPEN"
        return "EMPTY"


@dataclass(frozen=True)
class Stamp:
    sha: str
    short: str
    iso: str
    date: str
    subject: str
    path: str
    form: str
    require: dict[str, str]
    raw: str
    kind: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Era:
    value: bool
    start_sha: str
    end_sha: str
    start_short: str
    end_short: str
    count: int
    start_date: str = ""
    end_date: str = ""


@dataclass
class Walk:
    repo: str
    name: str
    first_parent: bool
    commits: int
    reachable: int
    first_assertion: Stamp | None = None
    first_expected: Stamp | None = None
    first_actual: Stamp | None = None
    first_fixture: Stamp | None = None
    first_spec: Stamp | None = None
    eras: list[Era] = field(default_factory=list)
    now: Census | None = None
    hints: list[str] = field(default_factory=list)


class OnsetError(Exception):
    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last = text.rfind("\n", 0, index)
    col = index - last
    return line, col


def line_starts(text: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def pos_off(starts: list[int], line: int, col: int) -> int:
    """Map tokenize coords (1-based line, 0-based col) to a string index."""
    if line < 1:
        return 0
    if line > len(starts):
        return starts[-1] if starts else 0
    return starts[line - 1] + max(0, col)


def _strip_quotes(s: str) -> str:
    s = (s or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"`":
        return s[1:-1]
    if s.startswith('@"') and s.endswith('"') and len(s) >= 3:
        return s[2:-1]
    return s


def _is_quoted(s: str) -> bool:
    s = s.strip()
    return len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"`"


def _usable_id(value: str) -> bool:
    v = value.strip()
    if len(v) < 2:
        return False
    if v.lower() in STOP_ID:
        return False
    if v.isdigit() and len(v) < 6:
        return False
    return True


def lang_of(path: str) -> str:
    suf = Path(path).suffix.lower()
    return {
        ".py": "python",
        ".swift": "swift",
        ".rs": "rust",
        ".ts": "js",
        ".js": "js",
        ".tsx": "js",
        ".jsx": "js",
        ".mjs": "js",
        ".go": "go",
        ".txt": "dump",
    }.get(suf, "generic")


def _github_owner(name: str) -> str | None:
    if not GITHUB_OWNER_RE.match(name):
        return None
    if name.lower() in STOP_ID:
        return None
    return name


def fixture_identity(s: str) -> str | None:
    """Owner token inside a GitHub title/URL, or None."""
    m = re.search(r"github\.com/([A-Za-z0-9-]+)/", s, re.I)
    if m:
        return _github_owner(m.group(1))
    m = re.search(r"GitHub\s+-\s+([A-Za-z0-9-]+)/", s)
    if m:
        return _github_owner(m.group(1))
    if re.search(r"GitHub|github\.com", s, re.I):
        m = re.search(r"\b([A-Za-z][A-Za-z0-9-]*)/([A-Za-z0-9_.-]+)\b", s)
        if m and not FILEISH_RE.search(m.group(0)):
            return _github_owner(m.group(1))
    return None


def is_github_fixture(s: str) -> bool:
    return fixture_identity(s) is not None


def layout_of(home: str) -> str:
    n = home.replace("\\", "/")
    if n.startswith("/Users/"):
        return "macos-home"
    if "/runner/work/" in n or n.startswith("/home/runner"):
        return "gha-runner"
    if n.startswith("/home/"):
        return "linux-home"
    return "other"


def derive_from_path(p: str) -> dict[str, str]:
    raw = (p or "").strip()
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
        if user == "runner":
            out["layout"] = "gha-runner"
            out["CI"] = "github-actions"
        else:
            out["layout"] = "linux-home"
        return out
    if n.startswith("/tmp/"):
        out["tmp"] = "unix"
        return out
    return out


def _ident_tail(value: str) -> str:
    return value.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def is_textbook(require: dict[str, str]) -> bool:
    for axis in ("HOME", "USER"):
        if axis not in require:
            continue
        ident = _ident_tail(require[axis]) if axis == "HOME" else require[axis]
        if ident.lower() in TEXTBOOK_TAILS:
            return True
        if " " in ident or "'" in ident:
            return True
    return False


def live_axes() -> dict[str, str]:
    home = str(Path.home()).rstrip("/\\")
    try:
        user = getpass.getuser()
    except Exception:
        user = os.environ.get("USER", "")
    plat = platform.system()
    axes = {
        "HOME": home,
        "USER": user,
        "platform": plat,
        "layout": layout_of(home),
    }
    return {k: v for k, v in axes.items() if v}


def machine_kind(require: dict[str, str], live: dict[str, str] | None = None) -> str:
    live = live or live_axes()
    home = require.get("HOME", "")
    user = require.get("USER", "")
    if home and home == live.get("HOME"):
        return "this-host"
    if user and user == live.get("USER") and not home:
        return "this-host"
    if user and user == live.get("USER") and home == live.get("HOME"):
        return "this-host"
    if home.startswith("/Users/alice") or user == "alice":
        return "alice"
    if "runner" in home or user == "runner":
        return "runner"
    return "other"


def classify_literal(raw: str) -> tuple[str, dict[str, str]]:
    """BOUND / SPEC / FIXTURE / OPEN for one string."""
    s = _strip_quotes(raw)
    if not s:
        return "OPEN", {}
    if is_github_fixture(s):
        name = fixture_identity(s) or ""
        req = {"USER": name} if name else {}
        return "FIXTURE", req
    derived: dict[str, str] = {}
    for m in PATH_RE.finditer(s):
        d = derive_from_path(m.group(0))
        if "tmp" in d and not any(k in d for k in ("HOME", "USER")):
            continue
        derived.update({k: v for k, v in d.items() if k != "tmp"})
        break
    if not derived:
        d = derive_from_path(s)
        derived.update({k: v for k, v in d.items() if k != "tmp"})
    hard = {k: v for k, v in derived.items() if k in {"HOME", "USER", "platform", "CI"}}
    if not hard:
        return "OPEN", {}
    if is_textbook(hard):
        return "SPEC", hard
    if "HOME" in hard or "USER" in hard:
        return "BOUND", hard
    return "OPEN", hard


# ---------------------------------------------------------------------------
# Comment mask — comments are never assertion windows
# ---------------------------------------------------------------------------


def comment_mask(text: str, path: str = "") -> bytearray:
    lang = lang_of(path)
    if lang == "python":
        return _python_comment_mask(text)
    return _scan_comment_mask(text, lang)


def _python_comment_mask(text: str) -> bytearray:
    mask = bytearray(len(text))
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except tokenize.TokenError:
        return _scan_comment_mask(text, "python")
    starts = line_starts(text)
    for tok in toks:
        if tok.type != tokenize.COMMENT:
            continue
        sl, sc = tok.start
        el, ec = tok.end
        i = min(len(text), max(0, pos_off(starts, sl, sc)))
        j = min(len(text), max(i, pos_off(starts, el, ec)))
        mask[i:j] = b"\x01" * (j - i)
    return mask


def _scan_comment_mask(text: str, lang: str) -> bytearray:
    mask = bytearray(len(text))
    n = len(text)
    i = 0
    hash_ok = lang in {"python", "hash", "dump", "generic"}
    slash_ok = lang in {"swift", "rust", "js", "go", "generic", "dump"}
    while i < n:
        ch = text[i]
        if ch in "'\"`":
            q = ch
            i += 1
            while i < n:
                if text[i] == "\\" and q != "`":
                    i += 2
                    continue
                if text[i] == q:
                    i += 1
                    break
                i += 1
            continue
        if slash_ok and text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            mask[i:j] = b"\x01" * (j - i)
            i = j
            continue
        if slash_ok and text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            mask[i:j] = b"\x01" * (j - i)
            i = j
            continue
        if ch == "#" and hash_ok:
            rest = text[i + 1 : i + 24]
            if any(rest.startswith(m) for m in SWIFT_HASH_MACROS):
                i += 1
                continue
            j = text.find("\n", i)
            j = n if j < 0 else j
            mask[i:j] = b"\x01" * (j - i)
            i = j
            continue
        i += 1
    return mask


def in_comment(mask: bytearray, i: int) -> bool:
    return 0 <= i < len(mask) and mask[i] != 0


def _comment_spans(text: str, mask: bytearray) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    i = 0
    n = len(text)
    while i < n:
        if mask[i] == 0:
            i += 1
            continue
        j = i
        while j < n and mask[j]:
            j += 1
        spans.append((i, j, text[i:j]))
        i = j
    return spans


# ---------------------------------------------------------------------------
# Parens / args / surface literal
# ---------------------------------------------------------------------------


def match_paren(text: str, i: int) -> int:
    if i >= len(text) or text[i] != "(":
        return -1
    depth = 0
    n = len(text)
    k = i
    quote = ""
    while k < n:
        ch = text[k]
        if quote:
            if ch == "\\" and quote != "`":
                k += 2
                continue
            if ch == quote:
                quote = ""
            k += 1
            continue
        if ch in "'\"`":
            quote = ch
            k += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return k + 1
        k += 1
    return -1


def split_args(inner: str) -> list[str]:
    args: list[str] = []
    buf: list[str] = []
    depth = 0
    quote = ""
    i = 0
    n = len(inner)
    while i < n:
        ch = inner[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and quote != "`" and i + 1 < n:
                buf.append(inner[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in "'\"`":
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if ch in "([{":
            depth += 1
            buf.append(ch)
        elif ch in ")]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            args.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    if buf:
        args.append("".join(buf).strip())
    return [a for a in args if a]


def split_compare(expr: str) -> tuple[str, str, str] | None:
    depth = 0
    quote = ""
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if quote:
            if ch == "\\" and quote != "`":
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in "'\"`":
            quote = ch
            i += 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0:
            if expr.startswith("==", i) and not expr.startswith("===", i):
                return expr[:i].strip(), "==", expr[i + 2 :].strip()
            if expr.startswith("!=", i):
                return expr[:i].strip(), "!=", expr[i + 2 :].strip()
        i += 1
    return None


def unwrap_expr(expr: str) -> str:
    """Peel Some(...) / Path::new("...") so the surface literal is visible."""
    s = (expr or "").strip().rstrip(",").strip()
    for _ in range(4):
        m = re.match(r"^Some\s*\((.*)\)\s*$", s, re.S)
        if m:
            s = m.group(1).strip()
            continue
        m = re.match(
            r"^(?:std::)?(?:path::)?(?:PathBuf|Path|OsString)\s*"
            r"(?:::\s*)?(?:new|from|from_str)\s*\((.*)\)\s*$",
            s,
            re.S,
        )
        if m:
            s = m.group(1).strip()
            continue
        m = re.match(r"^PathBuf\s*::\s*from\s*\((.*)\)\s*$", s, re.S)
        if m:
            s = m.group(1).strip()
            continue
        break
    return s


def surface_literal(expr: str) -> str | None:
    """If the expression *is* a literal (or Path::new wrap), return it.

    Nested call arguments are not the actual. quote("/Users/John Doe")
    is not ACTUAL-BOUND; XCTAssertEqual("/Users/alice/Library", x) is.
    """
    s = unwrap_expr(expr)
    if not s:
        return None
    if _is_quoted(s):
        return _strip_quotes(s)
    if PATH_RE.fullmatch(s):
        return s
    return None


def axis_hint_of(expr: str) -> str:
    for axis, rx in AXIS_FROM_EXPR:
        if rx.search(expr or ""):
            return axis
    return ""


# ---------------------------------------------------------------------------
# Window extraction
# ---------------------------------------------------------------------------


def _window(
    kind: str, form: str, expected: str, actual: str, start: int, end: int, text: str
) -> Window:
    ln, col = line_col(text, start)
    return Window(
        kind=kind,
        form=form,
        expected=(expected or "").strip(),
        actual=(actual or "").strip(),
        start=start,
        end=end,
        line=ln,
        col=col,
    )


def extract_python_windows(text: str, path: str) -> tuple[list[Window], list[tuple[int, int, str]]]:
    windows: list[Window] = []
    comments: list[tuple[int, int, str]] = []
    starts = line_starts(text)
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except tokenize.TokenError:
        return extract_generic_windows(text, path)
    n = len(toks)
    i = 0
    while i < n:
        t = toks[i]
        if t.type == tokenize.COMMENT:
            a = pos_off(starts, *t.start)
            b = pos_off(starts, *t.end)
            comments.append((a, b, t.string))
            i += 1
            continue
        if t.type == tokenize.NAME and t.string == "assert":
            j = i + 1
            while j < n and toks[j].type not in (tokenize.NEWLINE, tokenize.ENDMARKER):
                j += 1
            a = pos_off(starts, *t.start)
            last = toks[j - 1] if j > i else t
            b = pos_off(starts, *last.end)
            expr = text[a + len("assert") : b]
            cmp_ = split_compare(expr)
            if cmp_:
                left, _op, right = cmp_
                windows.append(_window("assert", "assert", right, left, a, b, text))
            i = j
            continue
        if t.type == tokenize.NAME and t.string in PY_ASSERT_FUNCS:
            j = i + 1
            while j < n and not (toks[j].type == tokenize.OP and toks[j].string == "("):
                if toks[j].type in (tokenize.NEWLINE, tokenize.ENDMARKER):
                    break
                j += 1
            if j < n and toks[j].string == "(":
                a = pos_off(starts, *toks[j].start)
                end = match_paren(text, a)
                if end > 0:
                    args = split_args(text[a + 1 : end - 1])
                    if len(args) >= 2:
                        windows.append(
                            _window(
                                "assert",
                                t.string,
                                args[1],
                                args[0],
                                pos_off(starts, *t.start),
                                end,
                                text,
                            )
                        )
                    i = i + 1
                    continue
        i += 1
    return windows, comments


def extract_generic_windows(text: str, path: str) -> tuple[list[Window], list[tuple[int, int, str]]]:
    mask = comment_mask(text, path)
    comments = _comment_spans(text, mask)
    windows: list[Window] = []
    occupied = bytearray(len(text))

    def occupy(i: int, j: int) -> bool:
        if i < 0 or j > len(text) or i >= j:
            return False
        if any(occupied[i:j]):
            return False
        occupied[i:j] = b"\x01" * (j - i)
        return True

    for rx, form, how in CALL_HEADS:
        for m in rx.finditer(text):
            i = m.start()
            if in_comment(mask, i):
                continue
            k = m.end()
            while k < len(text) and text[k] in " \t\n":
                k += 1
            if k >= len(text) or text[k] != "(":
                continue
            end = match_paren(text, k)
            if end < 0:
                continue
            if not occupy(i, end):
                continue
            inner = text[k + 1 : end - 1]
            if how == "compare-parens":
                cmp_ = split_compare(inner)
                if cmp_:
                    left, _op, right = cmp_
                    windows.append(_window("expect", form, right, left, i, end, text))
                continue
            args = split_args(inner)
            if how == "go":
                if args and re.fullmatch(r"t+|tr|tb", args[0].strip()):
                    args = args[1:]
                if len(args) >= 2:
                    windows.append(_window("assert", form, args[0], args[1], i, end, text))
                continue
            if len(args) >= 2:
                windows.append(_window("assert", form, args[1], args[0], i, end, text))

    for m in re.finditer(r"(?m)^\s*assert\s+(.+?)\s*$", text):
        i = m.start()
        if in_comment(mask, i):
            continue
        if occupy(i, m.end()):
            cmp_ = split_compare(m.group(1))
            if cmp_:
                left, _op, right = cmp_
                windows.append(_window("assert", "assert", right, left, i, m.end(), text))

    return windows, comments


def extract_fail_windows(text: str, path: str) -> list[Window]:
    """Fail-dump actual/expected. Comments in the paste are skipped."""
    windows: list[Window] = []
    minus: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        stripped = line.strip()
        if stripped.startswith("//") or (
            stripped.startswith("#")
            and not stripped.startswith("#expect")
            and not stripped.startswith("#require")
        ):
            continue
        m = PYTEST_DIFF_MINUS.match(line)
        if m:
            minus = m.group("v")
            continue
        m = PYTEST_DIFF_PLUS.match(line)
        if m and minus is not None:
            i = text.find(line)
            windows.append(
                _window("fail", "pytest", minus, m.group("v"), max(0, i), max(0, i) + len(line), text)
            )
            minus = None
            continue
        m = SWIFT_FAIL_RE.search(line)
        if m:
            act = m.group("qa") or m.group("a") or ""
            exp = m.group("qb") or m.group("b") or ""
            i = text.find(line)
            windows.append(
                _window("fail", "xctest", _strip_quotes(exp), _strip_quotes(act), max(0, i), max(0, i) + len(line), text)
            )
            continue
        m = JUNIT_RE.search(line)
        if m:
            i = text.find(line)
            windows.append(
                _window(
                    "fail",
                    "junit",
                    m.group("a"),
                    m.group("b"),
                    max(0, i),
                    max(0, i) + len(line),
                    text,
                )
            )
    return windows


def looks_like_fail_dump(text: str, path: str) -> bool:
    if Path(path).suffix.lower() not in {".txt", ".xml", ".log", ""}:
        if "is not equal to" not in text and "E   -" not in text:
            return False
    return bool(
        SWIFT_FAIL_RE.search(text)
        or "E   -" in text
        or "but was:" in text.lower()
        or "AssertionError" in text
    )


def extract_windows(text: str, path: str = "") -> tuple[list[Window], list[tuple[int, int, str]]]:
    if looks_like_fail_dump(text, path) and lang_of(path) in {"dump", "generic"}:
        mask = comment_mask(text, path or "x.txt")
        return extract_fail_windows(text, path), _comment_spans(text, mask)
    lang = lang_of(path)
    if lang == "python":
        windows, comments = extract_python_windows(text, path)
    else:
        windows, comments = extract_generic_windows(text, path)
    if looks_like_fail_dump(text, path):
        windows.extend(extract_fail_windows(text, path))
    windows.sort(key=lambda w: (w.start, w.kind))
    return windows, comments


def extract_fixture_strings(text: str, path: str) -> list[tuple[int, str]]:
    """GitHub title/URL strings in test source — identity-as-data, not oaths."""
    mask = comment_mask(text, path)
    out: list[tuple[int, str]] = []
    for m in re.finditer(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', text):
        if in_comment(mask, m.start()):
            continue
        raw = _strip_quotes(m.group(0))
        if is_github_fixture(raw):
            ln, _ = line_col(text, m.start())
            out.append((ln, raw))
    return out


# ---------------------------------------------------------------------------
# Classify a file
# ---------------------------------------------------------------------------


def _hit(
    path: str,
    line: int,
    form: str,
    side: str,
    status: str,
    require: dict[str, str],
    raw: str,
) -> Hit:
    kind = ""
    if status == "BOUND":
        kind = machine_kind(require)
    return Hit(
        path=path,
        line=line,
        form=form,
        side=side,
        status=status,
        require=require,
        raw=_short(raw, 80),
        kind=kind,
    )


def _short(s: str, n: int = 72) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def classify_side(expr: str, *, other: str = "", as_expected: bool = False) -> tuple[str, dict[str, str], str]:
    """Return (status, require, raw_used) for one side of an assertion."""
    lit = surface_literal(expr)
    hint = axis_hint_of(other if as_expected else expr)
    if lit is None:
        # env-tied expected username: assert environ['USER'] == 'alice'
        if as_expected:
            inner = _strip_quotes(unwrap_expr(expr))
            if hint == "USER" and _usable_id(inner) and "/" not in inner:
                st, req = classify_literal("/Users/" + inner if inner else "")
                # bare username of an env compare
                if inner.lower() in TEXTBOOK_TAILS:
                    return "SPEC", {"USER": inner}, inner
                if inner:
                    return "BOUND", {"USER": inner}, inner
        return "OPEN", {}, expr
    status, require = classify_literal(lit)
    if status == "OPEN" and as_expected and hint == "USER" and _usable_id(lit) and "/" not in lit:
        if lit.lower() in TEXTBOOK_TAILS:
            return "SPEC", {"USER": lit}, lit
        return "BOUND", {"USER": lit}, lit
    return status, require, lit


def classify_text(text: str, path: str = "") -> Census:
    windows, comments = extract_windows(text, path)
    c = Census(path=path or "-")
    seen_fix: set[tuple[int, str]] = set()

    for w in windows:
        c.assertions += 1
        a_st, a_req, a_raw = classify_side(w.actual, other=w.expected, as_expected=False)
        e_st, e_req, e_raw = classify_side(w.expected, other=w.actual, as_expected=True)
        if a_st == "BOUND":
            c.actual_bound += 1
            c.hits.append(_hit(path, w.line, w.form, "actual", "BOUND", a_req, a_raw))
        elif a_st == "SPEC":
            c.spec += 1
            c.hits.append(_hit(path, w.line, w.form, "actual", "SPEC", a_req, a_raw))
        elif a_st == "FIXTURE":
            c.fixture += 1
            c.hits.append(_hit(path, w.line, w.form, "actual", "FIXTURE", a_req, a_raw))
        if e_st == "BOUND":
            c.expected_bound += 1
            c.hits.append(_hit(path, w.line, w.form, "expected", "BOUND", e_req, e_raw))
        elif e_st == "SPEC":
            c.spec += 1
            c.hits.append(_hit(path, w.line, w.form, "expected", "SPEC", e_req, e_raw))
        elif e_st == "FIXTURE":
            c.fixture += 1
            c.hits.append(_hit(path, w.line, w.form, "expected", "FIXTURE", e_req, e_raw))

    for ln, raw in extract_fixture_strings(text, path):
        key = (ln, raw)
        if key in seen_fix:
            continue
        # Skip if this string is already an assertion-side fixture hit.
        if any(h.status == "FIXTURE" and h.raw in raw for h in c.hits):
            continue
        seen_fix.add(key)
        name = fixture_identity(raw) or ""
        c.fixture += 1
        c.hits.append(
            _hit(path, ln, "string", "fixture", "FIXTURE", {"USER": name} if name else {}, raw)
        )

    for start, _end, blob in comments:
        ln, _ = line_col(text, start)
        silent_here = False
        for m in PATH_RE.finditer(blob):
            d = derive_from_path(m.group(0))
            if "HOME" in d or "USER" in d:
                c.silent += 1
                c.hits.append(_hit(path, ln, "comment", "comment", "SILENT", d, m.group(0)))
                silent_here = True
                break
        if silent_here:
            continue
        m = RAN_ON_RE.search(blob)
        if m and _usable_id(m.group(1)):
            c.silent += 1
            c.hits.append(
                _hit(path, ln, "comment", "comment", "SILENT", {"USER": m.group(1)}, m.group(0))
            )
    return c


def merge_census(path: str, items: Iterable[Census]) -> Census:
    out = Census(path=path)
    for c in items:
        out.assertions += c.assertions
        out.actual_bound += c.actual_bound
        out.expected_bound += c.expected_bound
        out.fixture += c.fixture
        out.spec += c.spec
        out.silent += c.silent
        out.hits.extend(c.hits)
    return out


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------


def run_git(repo: str, *args: str, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", repo, *args],
        input=input_bytes,
        capture_output=True,
        check=False,
    )


def git_text(repo: str, *args: str) -> str:
    r = run_git(repo, *args)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip() or r.stdout.decode("utf-8", "replace").strip()
        raise OnsetError(err or f"git {' '.join(args)} failed")
    return r.stdout.decode("utf-8", "replace")


def is_git_root(path: str) -> bool:
    r = run_git(path, "rev-parse", "--show-toplevel")
    if r.returncode != 0:
        return False
    top = Path(r.stdout.decode().strip())
    try:
        return top.resolve() == Path(path).resolve()
    except OSError:
        return False


def resolve_repo(path: str | None) -> str:
    start = os.path.abspath(path or os.getcwd())
    if not os.path.isdir(start):
        raise OnsetError(f"not a directory: {start}")
    r = run_git(start, "rev-parse", "--show-toplevel")
    if r.returncode != 0:
        raise OnsetError(f"not a git repository: {start}")
    return r.stdout.decode().strip()


def reachable_count(repo: str, spec: str) -> int:
    r = run_git(repo, "rev-list", "--count", spec)
    if r.returncode != 0:
        return 0
    try:
        return int(r.stdout.decode().strip() or "0")
    except ValueError:
        return 0


def list_commits(
    repo: str,
    spec: str,
    *,
    first_parent: bool,
    limit: int | None,
) -> list[dict[str, str]]:
    fmt = "%H%x09%ct%x09%ci%x09%s"
    # topo-order + reverse: parents before children. Equal-timestamp
    # merges otherwise steal first-assertion from the root.
    cmd = ["log", "--reverse", "--topo-order", f"--format={fmt}"]
    if first_parent:
        cmd.append("--first-parent")
    cmd.append(spec)
    text = git_text(repo, *cmd)
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 3)
        if len(parts) < 3:
            continue
        iso = parts[2]
        date = iso[:10] if len(iso) >= 10 else iso
        rows.append(
            {
                "sha": parts[0],
                "short": parts[0][:7],
                "ts": parts[1],
                "iso": iso,
                "date": date,
                "subject": parts[3] if len(parts) > 3 else "",
            }
        )
    if limit is not None and limit >= 0 and len(rows) > limit:
        rows = rows[-limit:]
    return rows


def list_source_blobs(repo: str, sha: str) -> list[tuple[str, str]]:
    """(path, blob_sha) for source / dump files at SHA."""
    r = run_git(repo, "ls-tree", "-r", sha)
    if r.returncode != 0:
        return []
    out: list[tuple[str, str]] = []
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        # <mode> <type> <sha>\t<path>
        try:
            meta, path = line.split("\t", 1)
        except ValueError:
            continue
        bits = meta.split()
        if len(bits) < 3 or bits[1] != "blob":
            continue
        suf = Path(path).suffix.lower()
        if suf in SOURCE_SUFFIX or suf in {".txt", ".xml", ".log"}:
            out.append((path, bits[2]))
    return out


def cat_blobs(repo: str, shas: list[str]) -> dict[str, bytes]:
    if not shas:
        return {}
    r = run_git(repo, "cat-file", "--batch", input_bytes=("".join(s + "\n" for s in shas).encode()))
    if r.returncode != 0:
        raise OnsetError("git cat-file --batch failed")
    data = r.stdout
    out: dict[str, bytes] = {}
    i = 0
    n = len(data)
    while i < n:
        nl = data.find(b"\n", i)
        if nl < 0:
            break
        header = data[i:nl].decode("utf-8", "replace")
        i = nl + 1
        parts = header.split()
        if len(parts) >= 2 and parts[1] == "missing":
            continue
        if len(parts) < 3:
            break
        sha, _typ, size_s = parts[0], parts[1], parts[2]
        try:
            size = int(size_s)
        except ValueError:
            break
        blob = data[i : i + size]
        out[sha] = blob
        i = i + size
        if i < n and data[i : i + 1] == b"\n":
            i += 1
    return out


def blob_worth_parsing(blob: bytes) -> bool:
    if not blob or len(blob) > MAX_BLOB:
        return False
    if b"\0" in blob[:4096]:
        return False
    return any(h in blob for h in BLOB_HINT)


_CENSUS_CACHE: dict[tuple[str, str], Census] = {}


def census_blob(path: str, blob_sha: str, blob: bytes) -> Census:
    key = (blob_sha, path)
    if key in _CENSUS_CACHE:
        return _CENSUS_CACHE[key]
    if not blob_worth_parsing(blob):
        c = Census(path=path)
        _CENSUS_CACHE[key] = c
        return c
    text = blob.decode("utf-8", "replace")
    c = classify_text(text, path)
    _CENSUS_CACHE[key] = c
    return c


def _stamp(commit: dict[str, str], hit: Hit) -> Stamp:
    return Stamp(
        sha=commit["sha"],
        short=commit["short"],
        iso=commit["iso"],
        date=commit["date"],
        subject=commit["subject"],
        path=hit.path,
        form=hit.form,
        require=dict(hit.require),
        raw=hit.raw,
        kind=hit.kind,
    )


def walk_repo(
    repo: str,
    spec: str = "HEAD",
    *,
    first_parent: bool = True,
    limit: int | None = None,
) -> Walk:
    name = Path(repo).name
    commits = list_commits(repo, spec, first_parent=first_parent, limit=limit)
    reachable = reachable_count(repo, spec)
    walk = Walk(
        repo=repo,
        name=name,
        first_parent=first_parent,
        commits=len(commits),
        reachable=reachable,
    )
    if not commits:
        raise OnsetError("no commits at HEAD (empty repository?)")

    actual_flags: list[bool] = []
    pending_blobs: dict[str, None] = {}
    per_commit_files: list[list[tuple[str, str]]] = []

    for commit in commits:
        files = list_source_blobs(repo, commit["sha"])
        per_commit_files.append(files)
        for _path, bsha in files:
            if (bsha, _path) not in _CENSUS_CACHE:
                pending_blobs[bsha] = None

    # Fetch unknown blobs in chunks.
    unknown = [s for s in pending_blobs if s]
    blob_map: dict[str, bytes] = {}
    chunk = 200
    for i in range(0, len(unknown), chunk):
        blob_map.update(cat_blobs(repo, unknown[i : i + chunk]))

    for commit, files in zip(commits, per_commit_files):
        censuses: list[Census] = []
        has_assert = False
        actual_hit: Hit | None = None
        expected_hit: Hit | None = None
        fixture_hit: Hit | None = None
        spec_hit: Hit | None = None
        for path, bsha in files:
            blob = blob_map.get(bsha)
            if blob is None:
                # already cached, or missing; try cache via empty
                if (bsha, path) in _CENSUS_CACHE:
                    c = _CENSUS_CACHE[(bsha, path)]
                else:
                    continue
            else:
                c = census_blob(path, bsha, blob)
            if c.assertions or c.fixture or c.spec or c.silent:
                censuses.append(c)
            if c.assertions:
                has_assert = True
            if actual_hit is None:
                for h in c.hits:
                    if h.side == "actual" and h.status == "BOUND":
                        actual_hit = h
                        break
            if expected_hit is None:
                for h in c.hits:
                    if h.side == "expected" and h.status == "BOUND":
                        expected_hit = h
                        break
            if fixture_hit is None:
                for h in c.hits:
                    if h.status == "FIXTURE":
                        fixture_hit = h
                        break
            if spec_hit is None:
                for h in c.hits:
                    if h.status == "SPEC":
                        spec_hit = h
                        break

        if has_assert and walk.first_assertion is None:
            path = next((c.path for c in censuses if c.assertions), "")
            form = next(
                (h.form for c in censuses for h in c.hits if h.side in {"actual", "expected"}),
                "assert",
            )
            dummy = Hit(path=path, line=1, form=form, side="actual", status="OPEN", require={}, raw="")
            walk.first_assertion = _stamp(commit, dummy)
        if actual_hit and walk.first_actual is None:
            walk.first_actual = _stamp(commit, actual_hit)
        if expected_hit and walk.first_expected is None:
            walk.first_expected = _stamp(commit, expected_hit)
        if fixture_hit and walk.first_fixture is None:
            walk.first_fixture = _stamp(commit, fixture_hit)
        if spec_hit and walk.first_spec is None:
            walk.first_spec = _stamp(commit, spec_hit)
        actual_flags.append(actual_hit is not None)

    walk.eras = compress_eras(commits, actual_flags)
    if commits:
        # now = last commit census summary
        last_files = per_commit_files[-1]
        last_items = []
        for path, bsha in last_files:
            if (bsha, path) in _CENSUS_CACHE:
                last_items.append(_CENSUS_CACHE[(bsha, path)])
        walk.now = merge_census("(HEAD)", last_items)
    _hint_full(walk, repo)
    return walk


def is_merge(repo: str, sha: str) -> bool:
    r = run_git(repo, "rev-list", "--parents", "-n1", sha)
    if r.returncode != 0:
        return False
    return len(r.stdout.decode().split()) > 2


def _hint_full(walk: Walk, repo: str) -> None:
    """first-parent names the merge; --full names the feature commit.

    kizu 24 vs 244: first-assertion is Merge PR #2, not feat(git).
    sitbone fixture is Merge PR #1, not WindowTitleParserTests.
    """
    if not walk.first_parent:
        return
    if walk.reachable and walk.reachable != walk.commits:
        walk.hints.append(
            f"{walk.commits} of {walk.reachable} commits on first-parent"
        )
    for label, st in (
        ("first-assertion", walk.first_assertion),
        ("first-expected", walk.first_expected),
        ("first-actual", walk.first_actual),
        ("first-fixture", walk.first_fixture),
        ("first-spec", walk.first_spec),
    ):
        if st is None:
            continue
        merge = is_merge(repo, st.sha) or st.subject.lower().startswith("merge ")
        if merge:
            walk.hints.append(
                f"{label} is a merge ({st.short}). rerun with --full to name the feature commit"
            )


def compress_eras(commits: list[dict[str, str]], flags: list[bool]) -> list[Era]:
    if not commits:
        return []
    eras: list[Era] = []
    start = 0
    cur = flags[0] if flags else False
    for i in range(1, len(flags)):
        if flags[i] != cur:
            eras.append(
                Era(
                    value=cur,
                    start_sha=commits[start]["sha"],
                    end_sha=commits[i - 1]["sha"],
                    start_short=commits[start]["short"],
                    end_short=commits[i - 1]["short"],
                    count=i - start,
                    start_date=commits[start]["date"],
                    end_date=commits[i - 1]["date"],
                )
            )
            start = i
            cur = flags[i]
    eras.append(
        Era(
            value=cur,
            start_sha=commits[start]["sha"],
            end_sha=commits[-1]["sha"],
            start_short=commits[start]["short"],
            end_short=commits[-1]["short"],
            count=len(commits) - start,
            start_date=commits[start]["date"],
            end_date=commits[-1]["date"],
        )
    )
    return eras


def distinct(walk: Walk) -> bool:
    a = walk.first_assertion
    b = walk.first_actual
    if a is None:
        return True
    if b is None:
        return True
    return a.sha != b.sha


# ---------------------------------------------------------------------------
# Format
# ---------------------------------------------------------------------------


def _stamp_line(label: str, st: Stamp | None) -> str:
    if st is None:
        return f"  {label:<16} (none)"
    req = " ".join(f"{k}={v}" for k, v in st.require.items() if k in {"HOME", "USER"})
    extra = f"  {req}" if req else ""
    kind = f"  {st.kind}" if st.kind else ""
    subj = _short(st.subject, 50)
    return f"  {label:<16} {st.short}  {st.date}  {st.path}  {st.form}{kind}{extra}\n                    {subj}"


def format_walk(walk: Walk, *, eras: bool = False) -> str:
    walk_kind = "first-parent" if walk.first_parent else "full"
    if walk.reachable and walk.reachable != walk.commits:
        head = f"onset  {walk.name}  {walk.commits} of {walk.reachable} commits  {walk_kind}"
    else:
        head = f"onset  {walk.name}  {walk.commits} commits  {walk_kind}"
    lines = [head]
    lines.append(_stamp_line("first-assertion", walk.first_assertion))
    lines.append(_stamp_line("first-expected", walk.first_expected))
    lines.append(_stamp_line("first-actual", walk.first_actual))
    lines.append(_stamp_line("first-fixture", walk.first_fixture))
    lines.append(_stamp_line("first-spec", walk.first_spec))
    if walk.now:
        n = walk.now
        lines.append(
            f"  now              assertions={n.assertions}  actual-bound={n.actual_bound}  "
            f"expected-bound={n.expected_bound}  fixture={n.fixture}  spec={n.spec}  silent={n.silent}"
        )
        lines.append(f"  now-status       {n.status}")
    d = distinct(walk)
    if walk.first_actual is None and walk.first_assertion is not None:
        why = "first-actual is none (never ACTUAL-BOUND)"
    elif walk.first_assertion is None:
        why = "no assertion window in range"
    elif d:
        why = "first-actual ≠ first-assertion"
    else:
        why = "same commit — actual-bound born with the assertion"
    lines.append(f"  distinct         {'yes' if d else 'no'}  {why}")
    if walk.first_fixture and walk.first_actual is None:
        lines.append("  note             FIXTURE is not TAINTED; comments are not oaths")
    if eras:
        lines.append("  eras of ACTUAL-BOUND:")
        for e in walk.eras:
            flag = "TRUE " if e.value else "FALSE"
            dates = ""
            if e.start_date:
                if e.start_date == e.end_date:
                    dates = f"  {e.start_date}"
                else:
                    dates = f"  {e.start_date} → {e.end_date}"
            rng = e.start_short if e.start_short == e.end_short else f"{e.start_short}..{e.end_short}"
            lines.append(f"    {flag}  {e.count} commits  {rng}{dates}")
    for h in walk.hints:
        lines.append(f"hint: {h}")
    return "\n".join(lines)


def format_census(c: Census) -> str:
    lines = [f"onset  {c.path}  {c.status}"]
    if c.assertions == 0 and c.fixture == 0 and c.silent == 0 and c.spec == 0:
        lines.append("  (no assertion window)")
        return "\n".join(lines)
    lines.append(
        f"  assertions {c.assertions}  actual-bound {c.actual_bound}  "
        f"expected-bound {c.expected_bound}  fixture {c.fixture}  spec {c.spec}  silent {c.silent}"
    )
    for h in c.hits:
        req = " ".join(f"{k}={v}" for k, v in h.require.items() if k in {"HOME", "USER", "platform"})
        kind = f" {h.kind}" if h.kind else ""
        lines.append(f"  {h.side:<10} L{h.line} {h.form} {h.status}{kind}  {req}  {h.raw}".rstrip())
    if c.silent and not c.actual_bound:
        lines.append("  note: comments are not oaths")
    if c.fixture and not c.actual_bound:
        lines.append("  note: FIXTURE is identity-as-data, not TAINTED")
    return "\n".join(lines)


def porcelain_walk(walk: Walk) -> str:
    def row(name: str, st: Stamp | None) -> str:
        if st is None:
            return f"{name}\t"
        req = ",".join(f"{k}={v}" for k, v in st.require.items())
        return f"{name}\t{st.sha}\t{st.path}\t{st.form}\t{st.kind}\t{req}"

    lines = [
        row("first-assertion", walk.first_assertion),
        row("first-expected", walk.first_expected),
        row("first-actual", walk.first_actual),
        row("first-fixture", walk.first_fixture),
        row("first-spec", walk.first_spec),
        f"distinct\t{'yes' if distinct(walk) else 'no'}",
        f"commits\t{walk.commits}\t{walk.reachable}",
    ]
    return "\n".join(lines)


def walk_to_dict(walk: Walk) -> dict:
    def sd(st: Stamp | None) -> dict | None:
        return st.as_dict() if st else None

    return {
        "repo": walk.repo,
        "name": walk.name,
        "first_parent": walk.first_parent,
        "commits": walk.commits,
        "reachable": walk.reachable,
        "first_assertion": sd(walk.first_assertion),
        "first_expected": sd(walk.first_expected),
        "first_actual": sd(walk.first_actual),
        "first_fixture": sd(walk.first_fixture),
        "first_spec": sd(walk.first_spec),
        "distinct": distinct(walk),
        "now": {
            "assertions": walk.now.assertions if walk.now else 0,
            "actual_bound": walk.now.actual_bound if walk.now else 0,
            "expected_bound": walk.now.expected_bound if walk.now else 0,
            "fixture": walk.now.fixture if walk.now else 0,
            "spec": walk.now.spec if walk.now else 0,
            "silent": walk.now.silent if walk.now else 0,
            "status": walk.now.status if walk.now else "EMPTY",
        },
        "eras": [asdict(e) for e in walk.eras],
        "hints": walk.hints,
    }


def census_to_dict(c: Census) -> dict:
    return {
        "path": c.path,
        "status": c.status,
        "assertions": c.assertions,
        "actual_bound": c.actual_bound,
        "expected_bound": c.expected_bound,
        "fixture": c.fixture,
        "spec": c.spec,
        "silent": c.silent,
        "hits": [asdict(h) for h in c.hits],
    }


def iter_scan_files(root: Path) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            suf = p.suffix.lower()
            if suf in SOURCE_SUFFIX or suf in {".txt", ".xml"}:
                try:
                    if p.stat().st_size > MAX_BLOB:
                        continue
                    if not p.stat().st_mode & stat.S_IFREG:
                        continue
                except OSError:
                    continue
                yield p


def scan_tree(root: Path) -> Census:
    items: list[Census] = []
    for p in iter_scan_files(root):
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if not blob_worth_parsing(data):
            continue
        rel = str(p.relative_to(root))
        items.append(classify_text(data.decode("utf-8", "replace"), rel))
    return merge_census(str(root), items)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def self_test() -> int:
    failed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal failed
        if cond:
            print(f"ok  {name}")
        else:
            failed += 1
            print(f"FAIL  {name}  {detail}", file=sys.stderr)

    comment = "# ran on alice\n# HOME=/Users/alice\nassert result == 42\n"
    c = classify_text(comment, "tests/test_comment.py")
    check("comment file has an assertion", c.assertions >= 1, str(c.assertions))
    check("comment is not actual-bound", c.actual_bound == 0, str(c.actual_bound))
    check("comment is not expected-bound", c.expected_bound == 0, str(c.expected_bound))
    check("comment is silent", c.silent >= 1, str(c.silent))
    check("comment status OPEN", c.status == "OPEN", c.status)

    env_a = "assert os.environ['USER'] == 'alice'\n"
    e = classify_text(env_a, "tests/test_user.py")
    check("env assert is an assertion", e.assertions == 1, str(e.assertions))
    check("env assert EXPECTED-BOUND", e.expected_bound == 1, str(e.hits))
    check("env assert not ACTUAL-BOUND", e.actual_bound == 0, str(e.hits))
    check("env USER=alice", any(h.require.get("USER") == "alice" for h in e.hits), str(e.hits))

    both = "# ran on alice\nassert os.environ['USER'] == 'alice'\n"
    b = classify_text(both, "tests/test_both.py")
    check("both: expected-bound from assert", b.expected_bound == 1)
    check("both: comment still silent", b.silent >= 1)
    check("both: not actual-bound", b.actual_bound == 0)

    actual_src = 'XCTAssertEqual("/Users/alice/Library", "/tmp/x")\n'
    a = classify_text(actual_src, "Tests/FooTests.swift")
    check("xctest actual-bound", a.actual_bound == 1, str(a.hits))
    check("xctest expected not bound (tmp)", a.expected_bound == 0, str(a.hits))
    check(
        "xctest HOME=alice",
        any(h.require.get("HOME") == "/Users/alice" and h.side == "actual" for h in a.hits),
        str(a.hits),
    )
    check("xctest kind alice", any(h.kind == "alice" for h in a.hits), str(a.hits))

    live = live_axes()
    me = live.get("HOME", "/Users/annenpolka")
    host_src = f'assert "{me}/proj" == got\n'
    h = classify_text(host_src, "tests/test_me.py")
    check("this-host as actual literal is ACTUAL-BOUND", h.actual_bound == 1, str(h.hits))
    check("this-host kind", any(x.kind == "this-host" for x in h.hits), str(h.hits))

    title = (
        'func testChromeTitle() {\n'
        '    let result = WindowTitleParser.extractSiteName(\n'
        '        from: "GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome",\n'
        '        app: "Google Chrome"\n'
        "    )\n"
        '    XCTAssertEqual(result, "GitHub")\n'
        "}\n"
    )
    t = classify_text(title, "Tests/WindowTitleParserTests.swift")
    check("title has assertion", t.assertions >= 1)
    check("title is FIXTURE not actual-bound", t.actual_bound == 0 and t.fixture >= 1, t.status)
    check("title USER=annenpolka fixture", any(h.require.get("USER") == "annenpolka" for h in t.hits), str(t.hits))
    check("title status FIXTURE", t.status == "FIXTURE", t.status)

    payload = (
        'let mac = "/Users/John Doe/.cargo/bin/kizu";\n'
        'assert_eq!(quote(mac), "\'/Users/John Doe/.cargo/bin/kizu\'");\n'
        'assert_eq!(cwd, Path::new("/home/user/project"));\n'
    )
    p = classify_text(payload, "src/init/tests.rs")
    check("payload assertions", p.assertions >= 2, str(p.assertions))
    check("payload not actual-bound (nested / textbook)", p.actual_bound == 0, str(p.hits))
    check("payload SPEC on expected Path::new", p.spec >= 1, str(p.hits))

    nested = 'assert_eq!(shell_single_quote("/Users/alice/kizu"), "\'/Users/alice/kizu\'");\n'
    n = classify_text(nested, "src/init.rs")
    check(
        "nested call arg is not actual-bound",
        n.actual_bound == 0,
        str(n.hits),
    )

    dump = (
        'SitboneCoreTests.WindowTitleParserTests testChromeTitle: '
        'XCTAssertEqual failed: ("/Users/alice/Library") is not equal to ("/tmp/x")\n'
    )
    d = classify_text(dump, "fail.txt")
    check("fail dump actual-bound alice", d.actual_bound == 1, str(d.hits))
    check("fail dump expected tmp not bound", d.expected_bound == 0, str(d.hits))

    pytest_dump = "E   - /tmp/x\nE   + /Users/alice/proj\n"
    pd = classify_text(pytest_dump, "pytest.txt")
    check("pytest dump actual alice", pd.actual_bound == 1, str(pd.hits))
    check("pytest dump expected tmp not bound", pd.expected_bound == 0, str(pd.hits))

    # Synthetic git: first-assertion ≠ first-actual
    tmp = tempfile.mkdtemp(prefix="onset-self-")
    try:
        def g(*args: str, env: dict | None = None) -> None:
            e = os.environ.copy()
            e.update(
                {
                    "GIT_AUTHOR_NAME": "onset",
                    "GIT_AUTHOR_EMAIL": "onset@lab",
                    "GIT_COMMITTER_NAME": "onset",
                    "GIT_COMMITTER_EMAIL": "onset@lab",
                }
            )
            if env:
                e.update(env)
            subprocess.run(["git", "-C", tmp, *args], check=True, capture_output=True, env=e)

        g("init", "-q", "-b", "main")
        os.makedirs(os.path.join(tmp, "tests"), exist_ok=True)
        Path(tmp, "tests/test_open.py").write_text("assert got == 1\n", encoding="utf-8")
        g("add", "tests/test_open.py")
        g("commit", "-q", "-m", "t0: assertion born OPEN")
        Path(tmp, "tests/test_open.py").write_text(
            "# ran on alice\nassert got == 1\n", encoding="utf-8"
        )
        g("add", "tests/test_open.py")
        g("commit", "-q", "-m", "t1: comment is not an oath")
        Path(tmp, "tests/test_user.py").write_text(
            "assert os.environ['USER'] == 'alice'\n", encoding="utf-8"
        )
        g("add", "tests/test_user.py")
        g("commit", "-q", "-m", "t2: EXPECTED-BOUND alice")
        Path(tmp, "tests/test_title.swift").write_text(title, encoding="utf-8")
        g("add", "tests/test_title.swift")
        g("commit", "-q", "-m", "t3: FIXTURE annenpolka title")
        Path(tmp, "tests/test_actual.swift").write_text(
            f'XCTAssertEqual("{me}/Library", "/tmp/x")\n', encoding="utf-8"
        )
        g("add", "tests/test_actual.swift")
        g("commit", "-q", "-m", "t4: ACTUAL-BOUND this host")
        w = walk_repo(tmp, "HEAD", first_parent=True)
        check("git first-assertion t0", bool(w.first_assertion), str(w.first_assertion))
        check("git first-expected t2", bool(w.first_expected), str(w.first_expected))
        check("git first-actual t4", bool(w.first_actual), str(w.first_actual))
        check("git first-fixture t3", bool(w.first_fixture), str(w.first_fixture))
        check(
            "git firsts are four distinct shas",
            len(
                {
                    w.first_assertion.sha if w.first_assertion else "",
                    w.first_expected.sha if w.first_expected else "",
                    w.first_actual.sha if w.first_actual else "",
                    w.first_fixture.sha if w.first_fixture else "",
                }
            )
            == 4,
            str(
                {
                    "a": w.first_assertion.short if w.first_assertion else None,
                    "e": w.first_expected.short if w.first_expected else None,
                    "x": w.first_actual.short if w.first_actual else None,
                    "f": w.first_fixture.short if w.first_fixture else None,
                }
            ),
        )
        check("git distinct first-actual ≠ first-assertion", distinct(w))
        check(
            "git actual is this-host",
            bool(w.first_actual and w.first_actual.kind == "this-host"),
            str(w.first_actual),
        )
        check(
            "git expected is alice",
            bool(w.first_expected and w.first_expected.require.get("USER") == "alice"),
            str(w.first_expected),
        )
        check("report names first-spec", "first-spec" in format_walk(w))
    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)

    # first-parent names a merge; --full names the feature commit
    tmp2 = tempfile.mkdtemp(prefix="onset-merge-")
    try:
        def g2(*args: str) -> None:
            e = os.environ.copy()
            e.update(
                {
                    "GIT_AUTHOR_NAME": "onset",
                    "GIT_AUTHOR_EMAIL": "onset@lab",
                    "GIT_COMMITTER_NAME": "onset",
                    "GIT_COMMITTER_EMAIL": "onset@lab",
                }
            )
            subprocess.run(["git", "-C", tmp2, *args], check=True, capture_output=True, env=e)

        g2("init", "-q", "-b", "main")
        os.makedirs(os.path.join(tmp2, "tests"), exist_ok=True)
        Path(tmp2, "tests/open.py").write_text("assert got == 1\n", encoding="utf-8")
        g2("add", "tests/open.py")
        g2("commit", "-q", "-m", "main: assertion")
        g2("checkout", "-q", "-b", "topic")
        Path(tmp2, "tests/actual.swift").write_text(
            f'XCTAssertEqual("{live.get("HOME", "/Users/annenpolka")}/Library", "/tmp/x")\n',
            encoding="utf-8",
        )
        g2("add", "tests/actual.swift")
        g2("commit", "-q", "-m", "topic: ACTUAL-BOUND")
        g2("checkout", "-q", "main")
        g2("merge", "-q", "--no-ff", "-m", "Merge topic", "topic")
        wm = walk_repo(tmp2, "HEAD", first_parent=True)
        check(
            "merge first-actual is a merge",
            bool(wm.first_actual and wm.first_actual.subject.lower().startswith("merge")),
            str(wm.first_actual),
        )
        check(
            "merge walk hints --full",
            any("rerun with --full" in h for h in wm.hints),
            str(wm.hints),
        )
        wf = walk_repo(tmp2, "HEAD", first_parent=False)
        check(
            "full first-actual is the topic commit",
            bool(wf.first_actual and "ACTUAL-BOUND" in wf.first_actual.subject),
            str(wf.first_actual),
        )
        check(
            "full first-actual ≠ first-assertion",
            distinct(wf) and wf.first_actual is not None and wf.first_assertion is not None,
        )
    finally:
        import shutil

        shutil.rmtree(tmp2, ignore_errors=True)

    if failed:
        print(f"self-test {failed} failed", file=sys.stderr)
        return 1
    print("self-test ok")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="onset",
        description=(
            "When did an assertion newly acquire an actual-bound machine? "
            "Walks git history of assertion windows (not comments, not the "
            "whole file). OPEN expected is not ACTUAL-BOUND. sitbone titles "
            "stay FIXTURE, not TAINTED."
        ),
    )
    p.add_argument("paths", nargs="*", help="files to classify (skip history)")
    p.add_argument("-C", metavar="DIR", default=None, help="git repository / scan root")
    p.add_argument("--walk", action="store_true", help="walk git history (default when -C is a repo root)")
    p.add_argument("--full", action="store_true", help="all reachable commits, not first-parent")
    p.add_argument("--max", type=int, default=0, help="max commits from HEAD backwards (0 = all)")
    p.add_argument("--scan", action="store_true", help="classify the working tree, no history")
    p.add_argument("--from-fail", action="store_true", help="parse a fail dump on stdin")
    p.add_argument("--eras", action="store_true", help="print held-style TRUE/FALSE eras of ACTUAL-BOUND")
    p.add_argument("--json", action="store_true", help="JSON")
    p.add_argument("--porcelain", action="store_true", help="stable TSV")
    p.add_argument("--self-test", action="store_true", help="run built-in tests")
    p.add_argument("--version", action="version", version=f"onset {VERSION}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(list(sys.argv[1:] if argv is None else argv))
    if args.self_test:
        return self_test()

    root = os.path.abspath(args.C or os.getcwd())

    if args.from_fail:
        text = sys.stdin.read()
        c = classify_text(text, "-")
        if args.json:
            print(json.dumps(census_to_dict(c), indent=2))
        else:
            print(format_census(c))
        return 0 if c.actual_bound else 1

    if args.paths:
        items = []
        for raw in args.paths:
            p = Path(raw)
            if not p.is_absolute():
                p = Path(root) / raw
            if not p.exists():
                eprint(f"onset: not found: {raw}")
                return 2
            text = p.read_text(encoding="utf-8", errors="replace")
            items.append(classify_text(text, str(p)))
        c = items[0] if len(items) == 1 else merge_census(root, items)
        if args.json:
            print(json.dumps(census_to_dict(c), indent=2))
        else:
            print(format_census(c))
        return 0

    if args.scan:
        c = scan_tree(Path(root))
        if args.json:
            print(json.dumps(census_to_dict(c), indent=2))
        else:
            print(format_census(c))
        return 0

    # History walk.
    try:
        repo = resolve_repo(root)
        if not is_git_root(repo):
            # still ok — resolve_repo returns toplevel
            pass
        if args.C and Path(root).resolve() != Path(repo).resolve():
            # -C must be the worktree root (mint's nested-folder trap)
            raise OnsetError(f"not a git repository root: {root} (toplevel {repo})")
        limit = args.max if args.max and args.max > 0 else None
        walk = walk_repo(repo, "HEAD", first_parent=not args.full, limit=limit)
    except OnsetError as exc:
        eprint(f"onset: {exc}")
        return exc.code

    if args.json:
        print(json.dumps(walk_to_dict(walk), indent=2))
    elif args.porcelain:
        print(porcelain_walk(walk))
    else:
        print(format_walk(walk, eras=args.eras))
    return 0 if distinct(walk) else 1


if __name__ == "__main__":
    sys.exit(main())
