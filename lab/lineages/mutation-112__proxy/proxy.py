#!/usr/bin/env python3
"""proxy — follow the expected name, then pair the two oaths.

vow (mutation-68) paired EXPECTED-BOUND vs ACTUAL-BOUND from a fail.
It did not follow `expected = home; assert got == expected`, so a dump
emitted two inverted pairs (pytest PM vs E +/-). proxy follows the
expected name to its bound value *before* classifying the pair.

One failing assertion is one pair. Comments are not oaths. HOST is
soft unless the bound value is a path or a user. sitbone stays FIXTURE.
"""
from __future__ import annotations

import argparse
import getpass
import io
import json
import os
import platform
import re
import shlex
import stat
import sys
import tokenize
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
    ".tsx",
    ".jsx",
    ".mjs",
    ".go",
    ".json",
    ".txt",
    ".snap",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
}

# Snapshots are themselves expected values. Do not treat "<pytest expected>"
# fail-windows or a Swift file named OraclesGenerated as goldens.
SNAPSHOT_NAME_RE = re.compile(
    r"(\.snap$|(^|/)golden[s]?(/|$)|/expected/|\.expected\.|snapshot)",
    re.I,
)

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

# Relative paths (`src/auth.rs`) are not owner/repo identity.
FILEISH_RE = re.compile(r"\.[A-Za-z0-9]{1,8}$")
MIME_OR_PATHY = {
    "application",
    "text",
    "image",
    "audio",
    "video",
    "multipart",
    "font",
    "model",
    "contracts",
    "testcases",
    "examples",
    "example",
    "docs",
    "src",
    "lib",
    "pkg",
    "app",
    "tests",
    "test",
    "helpers",
    "assets",
    "vendor",
    "dist",
    "build",
    "node_modules",
    "usr",
    "bin",
    "etc",
    "var",
    "tmp",
    "dev",
}
GITHUB_OWNER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9-]{2,38}$")
SKIP_ORACLE_BASENAMES = {
    ".gitignore",
    ".gitattributes",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
}

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

HARD_AXES = ("platform", "layout", "HOME", "USER", "CI")
SOFT_AXES = ("HOST", "CWD", "TMPDIR")
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
FOLLOW_STOP = {
    "True",
    "False",
    "None",
    "null",
    "nil",
    "self",
    "cls",
    "true",
    "false",
    "this",
    "super",
    "undefined",
}
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

LAYOUT_JOIN = {
    frozenset({"linux-home", "gha-runner"}): "gha-runner",
    frozenset({"macos-home", "darwin-scratch"}): "macos-home",
}

# Actual-side phrases that name a machine axis. The expected literal
# then becomes an oath even if the name is textbook (`alice`).
AXIS_FROM_ACTUAL = (
    (
        "USER",
        re.compile(
            r"(?ix)"
            r"environ\[\s*['\"]USER(?:NAME)?['\"]"
            r"|getenv\(\s*['\"]USER(?:NAME)?['\"]"
            r"|env::var\(\s*['\"]USER"
            r"|std::env::var"
            r"|os\.Getenv\(\s*['\"]USER"
            r"|ProcessInfo.*userName"
            r"|NSUserName"
            r"|getpass\.getuser"
            r"|getuser\("
            r"|\$\{?USER\}?"
            r"|LOGNAME"
        ),
    ),
    (
        "HOME",
        re.compile(
            r"(?ix)"
            r"environ\[\s*['\"]HOME['\"]"
            r"|getenv\(\s*['\"]HOME['\"]"
            r"|env::var\(\s*['\"]HOME"
            r"|os\.Getenv\(\s*['\"]HOME"
            r"|Path\.home\("
            r"|pathlib\.Path\.home"
            r"|expanduser"
            r"|NSHomeDirectory"
            r"|\$\{?HOME\}?"
        ),
    ),
    (
        "HOST",
        re.compile(
            r"(?ix)"
            r"environ\[\s*['\"]HOST(?:NAME)?['\"]"
            r"|getenv\(\s*['\"]HOST(?:NAME)?['\"]"
            r"|gethostname"
            r"|platform\.node"
            r"|\$\{?HOST(?:NAME)?\}?"
        ),
    ),
    (
        "platform",
        re.compile(
            r"(?ix)"
            r"sys\.platform"
            r"|platform\.system"
            r"|uname\("
            r"|RUNNER_OS"
            r"|ProcessInfo.*operatingSystem"
            r"|target_os"
        ),
    ),
)

ENV_TIED_RE = re.compile(
    r"(?ix)"
    r"os\.environ|getenv|std::env|env::var|os\.Getenv|"
    r"ProcessInfo|NSUserName|NSHomeDirectory|"
    r"Path\.home|expanduser|getpass|"
    r"\$\{?(?:HOME|USER|LOGNAME|HOSTNAME)\}?|"
    r"environ\[\s*['\"](?:HOME|USER|LOGNAME|HOSTNAME|USERNAME)['\"]|"
    r"platform\.system|sys\.platform|uname|"
    r"gethostname|whoami|getuser"
)

RAN_ON_RE = re.compile(r"\bran\s+on\s+([A-Za-z][A-Za-z0-9._-]*)", re.I)

PY_ASSERT_FUNCS = {
    "assertEqual",
    "assertEquals",
    "assertNotEqual",
    "assertAlmostEqual",
    "assertListEqual",
    "assertTupleEqual",
    "assertSetEqual",
    "assertDictEqual",
    "assertSequenceEqual",
    "assertMultiLineEqual",
    "assertCountEqual",
    "assert_equal",
    "assert_equals",
}
EXPECT_NAMES = {"expected", "want", "wanted", "golden", "oracle"}

# Call-form assertions: name → how to pick the expected argument.
# "second" = arg[1] is expected (unittest / XCTest / Rust / Node).
# "go" = skip leading t/tt, then expected.
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
    (re.compile(r"\bassert_equal\b"), "assert_equal", "second"),
    (re.compile(r"\bassert\.strictEqual\b"), "assert.strictEqual", "second"),
    (re.compile(r"\bassert\.deepEqual\b"), "assert.deepEqual", "second"),
    (re.compile(r"\bassert\.equal\b"), "assert.equal", "second"),
    (re.compile(r"\bassert\.Equal\b"), "assert.Equal", "go"),
    (re.compile(r"\brequire\.Equal\b"), "require.Equal", "go"),
    (re.compile(r"\bassert\.Equalf\b"), "assert.Equalf", "go"),
]

JEST_TAIL = re.compile(
    r"^\s*\)\s*\.\s*(toBe|toEqual|toStrictEqual|toMatch|toBeTruthy|toBeFalsy)\s*\(",
    re.I,
)

# --from-fail grammars (lees named this gap).
PYTEST_PM_RE = re.compile(
    r"^E\s+(?:AssertionError:\s*)?(?:assert\s+)?(?P<a>.*) (?:==|!=) (?P<b>.*)$"
)
PYTEST_DIFF_MINUS = re.compile(r"^E\s+-\s+(?P<v>.*)$")
PYTEST_DIFF_PLUS = re.compile(r"^E\s+\+\s+(?P<v>.*)$")
UNITTEST_RE = re.compile(r"AssertionError:\s*(?P<a>.+?) (?:!=|==) (?P<b>.+)$")
CARGO_LEFT_RE = re.compile(r"^\s*left:\s*(?P<v>.+)$")
CARGO_RIGHT_RE = re.compile(r"^\s*right:\s*(?P<v>.+)$")
SWIFT_RE = re.compile(
    r"XCTAssert(?:Equal|NotEqual)(?:\s+failed:?\s*:?)?\s*"
    r"(?:\((?P<qa>[^)]+)\)|(?P<a>.+?)) "
    r"is not equal to (?:\((?P<qb>[^)]+)\)|(?P<b>.+))$"
)
SWIFT_TESTING_RE = re.compile(
    r"Expectation failed:.*==\s*(?P<v>.+)$"
)
JEST_EXP_RE = re.compile(r"^\s*Expected:\s*(?P<v>.+)$")
JEST_GOT_RE = re.compile(r"^\s*(?:Received|Received:)\s*(?P<v>.+)$")
GO_EXP_RE = re.compile(r"^\s*expected:\s*(?P<v>.+)$", re.I)
GO_ACT_RE = re.compile(r"^\s*actual\s*:\s*(?P<v>.+)$", re.I)
JUNIT_RE = re.compile(
    r"expected:\s*<(?P<a>.*?)>\s*but was:\s*<(?P<b>.*?)>",
    re.I,
)
RSPEC_EXP_RE = re.compile(r"^\s*expected:\s*(?P<v>.+)$", re.I)
RSPEC_GOT_RE = re.compile(r"^\s*got:\s*(?P<v>.+)$", re.I)
VITEST_RE = re.compile(
    r"expected\s+(?P<a>.+?)\s+to (?:be|equal|strictly equal)\s+(?P<b>.+)$",
    re.I,
)
PHPUNIT_EXP = re.compile(r"^--- Expected$")
PHPUNIT_ACT = re.compile(r"^\+\+\+ Actual$")

# pytest -vv "where got =" / "and expected =" (labeled actual vs expected).
PYTEST_WHERE_ACT_RE = re.compile(
    r"^\s*(?:E\s+)?(?:\+\s*)?where\s+"
    r"(?:got|received|actual|result|left|value|obtained)\s*=\s*(?P<v>.+)$",
    re.I,
)
PYTEST_WHERE_EXP_RE = re.compile(
    r"^\s*(?:E\s+)?(?:\+\s*)?(?:and\s+)?"
    r"(?:expected|want|wanted|right|exp)\s*=\s*(?P<v>.+)$",
    re.I,
)

SWIFT_HASH_MACROS = (
    "expect",
    "require",
    "assert",
    "available",
    "selector",
    "keyPath",
    "colorLiteral",
    "imageLiteral",
    "fileLiteral",
    "warning",
    "error",
    "if",
    "elseif",
    "else",
    "endif",
    "sourceLocation",
)


@dataclass(frozen=True)
class Window:
    """One assertion-literal (or snapshot/fail expected) span."""

    kind: str  # assert | expect | label | snapshot | fail | assign | fixture
    form: str
    expected: str
    actual: str
    env_tied: bool
    start: int
    end: int
    line: int
    col: int
    axis_hint: str = ""
    proxy: str = ""  # expected→home→os.environ['HOME']


@dataclass(frozen=True)
class Witness:
    axis: str
    value: str
    kind: str  # path | label | platform | assign | literal
    role: str  # record | payload | fixture | comment
    start: int
    end: int
    line: int
    col: int
    raw: str = ""
    form: str = ""


@dataclass
class Oath:
    path: str
    status: str  # OPEN | BOUND | SPEC | FIXTURE | UNSAT
    require: dict[str, str] = field(default_factory=dict)
    soft: dict[str, str] = field(default_factory=dict)
    witnesses: list[Witness] = field(default_factory=list)
    windows: list[Window] = field(default_factory=list)
    silent: list[Witness] = field(default_factory=list)
    contradictions: list[dict[str, object]] = field(default_factory=list)
    match: str = ""
    misses: list[dict[str, str]] = field(default_factory=list)
    side: str = ""  # expected | actual | "" (unary file)


@dataclass
class Pair:
    """Two unary oaths from one failing assertion — not a substitution."""

    kind: str
    expected_raw: str
    actual_raw: str
    source: str
    expected: Oath
    actual: Oath
    host: str = ""  # EXPECTED | ACTUAL | BOTH | NEITHER | ""
    proxy: str = ""  # expected→home→/Users/…  (name follow)

    @property
    def label(self) -> str:
        return f"EXPECTED-{self.expected.status} vs ACTUAL-{self.actual.status}"


def line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_nl = text.rfind("\n", 0, index)
    col = index - last_nl
    return line, col


def line_starts(text: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def pos_off(starts: list[int], line: int, col: int) -> int:
    if line < 1:
        return 0
    if line > len(starts):
        return starts[-1] + col
    return starts[line - 1] + col


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == "r" and s[1] in "'\"":
        s = s[1:]
    if s.startswith('r#') and s.endswith('#') and len(s) > 3:
        s = s[2:-1]
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        return s
    if s.startswith('#"') and s.endswith('"#'):
        return s[2:-2]
    if len(s) >= 6 and s[:3] == s[-3:] and s[:3] in ("'''", '"""'):
        return s[3:-3]
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"`":
        return s[1:-1]
    # Rust Some(Path::new("...")) leftovers
    m = re.search(r"""(?:Path(?:Buf)?::new\s*\(|Some\s*\()\s*['"](.+?)['"]\s*\)""", s)
    if m:
        return m.group(1)
    return s


def _surrounding_token(text: str, start: int, end: int) -> str:
    lo, hi = start, end
    while lo > 0 and text[lo - 1] not in " \t\n'\"<>(),;|":
        lo -= 1
    while hi < len(text) and text[hi] not in " \t\n'\"<>(),;|":
        hi += 1
    return text[lo:hi]


def _github_owner(name: str) -> str | None:
    n = name.strip()
    if not GITHUB_OWNER_RE.match(n):
        return None
    if n.lower() in STOP_ID or n.lower() in MIME_OR_PATHY:
        return None
    return n


def _is_github_fixture(tok: str) -> bool:
    """Identity-as-data: GitHub titles and github.com URLs, not `src/auth.rs`."""
    if re.search(r"github\.com|gist\.github", tok, re.I):
        return True
    if re.search(r"GitHub\s+-", tok):
        return True
    if re.search(r"/(?:Users|home|tmp|var/folders)/", tok):
        return False
    if tok.startswith(("./", "../")):
        return False
    head = tok.split()[0] if tok.split() else tok
    if FILEISH_RE.search(head):
        return False
    slash = re.search(r"\b([A-Za-z][A-Za-z0-9-]*)/([A-Za-z0-9_.-]+)\b", tok)
    if slash and _github_owner(slash.group(1)) and (
        re.search(r"Pull Request|Google Chrome|Firefox|Safari| · |\bGitHub\b", tok)
        or (
            re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", tok.strip())
            and not FILEISH_RE.search(tok)
        )
    ):
        return True
    return False


def fixture_identity(s: str) -> str | None:
    """Owner token inside a GitHub title/URL, or None."""
    m = re.search(r"github\.com/([A-Za-z0-9-]+)/", s, re.I)
    if m:
        return _github_owner(m.group(1))
    m = re.search(r"GitHub\s+-\s+([A-Za-z0-9-]+)/", s)
    if m:
        return _github_owner(m.group(1))
    # Only trust a bare owner/repo when the string is about GitHub.
    # Otherwise `async/await - Stack Overflow - Google Chrome` looks
    # like a user.
    if re.search(r"GitHub|github\.com", s, re.I):
        m = re.search(r"\b([A-Za-z][A-Za-z0-9-]*)/([A-Za-z0-9_.-]+)\b", s)
        if m and not FILEISH_RE.search(m.group(0)):
            return _github_owner(m.group(1))
    return None


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
    if not path or path in {"-", ""}:
        return False
    if path.startswith("<") and path.endswith(">"):
        return False
    s = path.replace("\\", "/")
    return bool(SNAPSHOT_NAME_RE.search(s))


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


def lang_of(path: str) -> str:
    suf = Path(path).suffix.lower()
    if suf == ".py":
        return "python"
    if suf == ".swift":
        return "swift"
    if suf == ".rs":
        return "rust"
    if suf in {".ts", ".js", ".tsx", ".jsx", ".mjs"}:
        return "js"
    if suf == ".go":
        return "go"
    if suf in {".yml", ".yaml", ".sh", ".rb", ".pl"}:
        return "hash"
    if suf in {".json"}:
        return "json"
    if suf in {".c", ".h", ".java", ".kt"}:
        return "c"
    if is_snapshot(path) or suf in {".snap", ".txt", ".md"}:
        return "snap"
    return "generic"


# ---------------------------------------------------------------------------
# Comment mask — the flip. Comments are never oath windows.
# ---------------------------------------------------------------------------


def comment_mask(text: str, path: str = "") -> bytearray:
    """1 = comment / not-code, 0 = live source."""
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
    hash_ok = lang in {"python", "hash", "snap", "generic"}
    slash_ok = lang in {"swift", "rust", "js", "go", "c", "generic", "snap"}
    while i < n:
        ch = text[i]
        # strings first so "#" inside them is not a comment
        if ch in "'\"`":
            q = ch
            i += 1
            while i < n:
                if text[i] == "\\":
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
            if rest.startswith("!"):
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


# ---------------------------------------------------------------------------
# Parens / args
# ---------------------------------------------------------------------------


def match_paren(text: str, i: int) -> int:
    """i points at '(', return index after matching ')' or -1."""
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


def axis_hint_of(actual: str) -> str:
    for axis, rx in AXIS_FROM_ACTUAL:
        if rx.search(actual):
            return axis
    return ""


def is_env_tied(actual: str) -> bool:
    return bool(actual and ENV_TIED_RE.search(actual))


def is_expr_not_literal(s: str) -> bool:
    """Followed name landed on getenv/Path.home, not a machine literal."""
    s = (s or "").strip()
    if not s:
        return False
    if s[0] in "'\"`" or s[:2] in ('r"', "r'", 'f"', "f'"):
        return False
    if s.startswith("/") or s.startswith("~") or re.match(r"^[A-Za-z]:\\", s):
        return False
    if is_env_tied(s) or "(" in s or "[" in s:
        return True
    return False


# ---------------------------------------------------------------------------
# Window extraction
# ---------------------------------------------------------------------------


def is_ident(s: str) -> bool:
    s = (s or "").strip()
    if not s or s in FOLLOW_STOP:
        return False
    return bool(IDENT_RE.fullmatch(s))


def collect_generic_bindings(text: str) -> list[tuple[str, str, int, int]]:
    """`name = rhs` lines (not `==`) that an expected name can follow."""
    out: list[tuple[str, str, int, int]] = []
    for m in re.finditer(
        r"(?m)^[ \t]*(?:let|var|const|val)?[ \t]*"
        r"([A-Za-z_][A-Za-z0-9_]*)[ \t]*(?::[^=\n]+)?=[ \t]*(.+?)\s*$",
        text,
    ):
        rhs = m.group(2).strip()
        if rhs.startswith("="):
            continue
        if rhs.startswith("//") or rhs.startswith("#"):
            continue
        rhs = re.split(r"\s+(?://|#)", rhs, maxsplit=1)[0].strip()
        out.append((m.group(1), rhs, m.start(1), m.end()))
    return out


def collect_python_bindings(text: str) -> list[tuple[str, str, int, int]]:
    """Assignments (`home = …`, `expected: str = home`) before an assert."""
    starts = line_starts(text)
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        return collect_generic_bindings(text)
    skip_lhs = {
        "def",
        "class",
        "if",
        "elif",
        "while",
        "for",
        "assert",
        "return",
        "import",
        "from",
        "with",
        "lambda",
        "as",
        "and",
        "or",
        "not",
        "in",
        "is",
        "yield",
        "await",
        "async",
        "global",
        "nonlocal",
        "raise",
        "except",
        "finally",
        "else",
        "try",
        "match",
        "case",
    }
    out: list[tuple[str, str, int, int]] = []
    n = len(toks)
    i = 0
    while i < n:
        t = toks[i]
        if t.type != tokenize.NAME or t.string in skip_lhs:
            i += 1
            continue
        j = i + 1
        if j < n and toks[j].type == tokenize.OP and toks[j].string == ":":
            depth = 0
            j += 1
            while j < n and toks[j].type not in (tokenize.NEWLINE, tokenize.ENDMARKER):
                if toks[j].type == tokenize.OP:
                    if toks[j].string in "([{":
                        depth += 1
                    elif toks[j].string in ")]}":
                        depth -= 1
                    elif toks[j].string == "=" and depth == 0:
                        break
                j += 1
        if j < n and toks[j].type == tokenize.OP and toks[j].string == "=":
            if j + 1 < n and toks[j + 1].type == tokenize.OP and toks[j + 1].string == "=":
                i += 1
                continue
            k = j + 1
            while k < n and toks[k].type not in (
                tokenize.NEWLINE,
                tokenize.ENDMARKER,
                tokenize.SEMI,
            ):
                k += 1
            rhs_toks = [x for x in toks[j + 1 : k] if x.type != tokenize.COMMENT]
            if rhs_toks:
                rhs_a = pos_off(starts, *rhs_toks[0].start)
                rhs_b = pos_off(starts, *rhs_toks[-1].end)
                rhs = text[rhs_a:rhs_b].strip()
                a = pos_off(starts, *t.start)
                out.append((t.string, rhs, a, rhs_b))
            i = k
            continue
        i += 1
    return out


def follow_name(
    name: str,
    bindings: list[tuple[str, str, int, int]],
    at: int | None = None,
    *,
    hops: int = 8,
) -> tuple[str, list[str]]:
    """Resolve an expected name through assignments before `at`.

    `expected = home; home = os.environ['HOME']` → os.environ['HOME'].
    A quoted rhs becomes the literal. HOST-only names stay names (soft).
    """
    cur = (name or "").strip()
    chain = [cur] if cur else []
    seen = {cur}
    for _ in range(hops):
        if not is_ident(cur):
            break
        cand: str | None = None
        cand_at = -1
        for n, rhs, start, _end in bindings:
            if n != cur:
                continue
            if at is not None and start >= at:
                continue
            if start >= cand_at:
                cand = rhs
                cand_at = start
        if cand is None:
            break
        nxt = cand.strip()
        if len(nxt) >= 2 and nxt[0] == nxt[-1] and nxt[0] in "'\"`":
            nxt = _strip_quotes(nxt)
        elif nxt[:1] in "'\"`" or nxt[:2] in ('r"', "r'", 'f"', "f'"):
            nxt = _strip_quotes(nxt)
        if not nxt or nxt in seen:
            break
        chain.append(nxt)
        seen.add(nxt)
        cur = nxt
    return cur, chain


def proxy_label(chain: list[str]) -> str:
    if len(chain) < 2:
        return ""
    return "→".join(chain)


def _blank_comments(text: str, a: int, b: int, comments: list[tuple[int, int, str]]) -> str:
    chunk = text[a:b]
    chars = list(chunk)
    for cs, ce, _blob in comments:
        if ce <= a or cs >= b:
            continue
        lo = max(0, cs - a)
        hi = min(len(chars), ce - a)
        for i in range(lo, hi):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def _window(
    kind: str,
    form: str,
    expected: str,
    actual: str,
    start: int,
    end: int,
    text: str,
    proxy: str = "",
) -> Window:
    ln, col = line_col(text, start)
    actual = actual.strip()
    expected = expected.strip()
    return Window(
        kind=kind,
        form=form,
        expected=expected,
        actual=actual,
        env_tied=is_env_tied(actual) or is_env_tied(expected),
        start=start,
        end=end,
        line=ln,
        col=col,
        axis_hint=axis_hint_of(actual) or axis_hint_of(expected),
        proxy=proxy,
    )


def extract_python_windows(text: str, path: str) -> tuple[list[Window], list[tuple[int, int, str]]]:
    windows: list[Window] = []
    comments: list[tuple[int, int, str]] = []
    starts = line_starts(text)
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        return extract_generic_windows(text, path)
    bindings = collect_python_bindings(text)
    for tok in toks:
        if tok.type == tokenize.COMMENT:
            a = pos_off(starts, *tok.start)
            b = pos_off(starts, *tok.end)
            comments.append((a, b, tok.string))
    n = len(toks)
    i = 0
    while i < n:
        t = toks[i]
        if t.type == tokenize.COMMENT:
            i += 1
            continue
        if t.type == tokenize.NAME and t.string == "assert":
            j = i + 1
            while j < n and toks[j].type not in (tokenize.NEWLINE, tokenize.ENDMARKER):
                j += 1
            a = pos_off(starts, *t.start)
            last = toks[j - 1] if j > i else t
            b = pos_off(starts, *last.end)
            expr = _blank_comments(text, a + len("assert"), b, comments)
            cmp_ = split_compare(expr)
            if cmp_:
                left, _op, right = cmp_
                right_s = right.strip()
                followed, chain = (
                    follow_name(right_s, bindings, at=a) if is_ident(right_s) else (right, [right_s])
                )
                windows.append(
                    _window(
                        "assert",
                        "assert",
                        followed,
                        left,
                        a,
                        b,
                        text,
                        proxy=proxy_label(chain),
                    )
                )
            i = j
            continue
        if t.type == tokenize.NAME and t.string in PY_ASSERT_FUNCS:
            # find '('
            j = i + 1
            while j < n and not (toks[j].type == tokenize.OP and toks[j].string == "("):
                if toks[j].type in (tokenize.NEWLINE, tokenize.ENDMARKER):
                    break
                j += 1
            if j < n and toks[j].string == "(":
                a = pos_off(starts, *toks[j].start)
                end = match_paren(text, a)
                if end > 0:
                    inner = text[a + 1 : end - 1]
                    args = split_args(inner)
                    if len(args) >= 2:
                        exp_s = args[1].strip()
                        followed, chain = (
                            follow_name(exp_s, bindings, at=pos_off(starts, *t.start))
                            if is_ident(exp_s)
                            else (args[1], [exp_s])
                        )
                        windows.append(
                            _window(
                                "assert",
                                t.string,
                                followed,
                                args[0],
                                pos_off(starts, *t.start),
                                end,
                                text,
                                proxy=proxy_label(chain),
                            )
                        )
                    i = i + 1
                    continue
        if t.type == tokenize.NAME and t.string.lower() in EXPECT_NAMES:
            j = i + 1
            while j < n and toks[j].type in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
                # stay on same logical assignment; skip only NL
                if toks[j].type == tokenize.NEWLINE:
                    break
                j += 1
            if j < n and toks[j].type == tokenize.OP and toks[j].string == "=":
                k = j + 1
                while k < n and toks[k].type not in (tokenize.NEWLINE, tokenize.ENDMARKER):
                    k += 1
                a = pos_off(starts, *t.start)
                last = toks[k - 1] if k > j else toks[j]
                b = pos_off(starts, *last.end)
                rhs = text[pos_off(starts, *toks[j + 1].start) : b] if j + 1 < k else ""
                rhs_s = rhs.strip()
                followed, chain = (
                    follow_name(rhs_s, bindings, at=a) if is_ident(rhs_s) else (rhs, [t.string, rhs_s])
                )
                if not is_ident(rhs_s):
                    chain = [t.string, rhs_s] if rhs_s else [t.string]
                else:
                    chain = [t.string] + [c for c in chain if c != t.string]
                windows.append(
                    _window(
                        "assign",
                        t.string + "=",
                        followed,
                        t.string,
                        a,
                        b,
                        text,
                        proxy=proxy_label(chain),
                    )
                )
                i = k
                continue
        i += 1
    return windows, comments


def extract_generic_windows(text: str, path: str) -> tuple[list[Window], list[tuple[int, int, str]]]:
    mask = comment_mask(text, path)
    comments = _comment_spans(text, mask)
    bindings = collect_generic_bindings(text)
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
            # find '(' after the head
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
                    right_s = right.strip()
                    followed, chain = (
                        follow_name(right_s, bindings, at=i)
                        if is_ident(right_s)
                        else (right, [right_s])
                    )
                    windows.append(
                        _window(
                            "expect",
                            form,
                            followed,
                            left,
                            i,
                            end,
                            text,
                            proxy=proxy_label(chain),
                        )
                    )
                continue
            args = split_args(inner)
            if how == "go":
                if args and re.fullmatch(r"t+|tr|tb", args[0].strip()):
                    args = args[1:]
                if len(args) >= 2:
                    exp_s = args[0].strip()
                    followed, chain = (
                        follow_name(exp_s, bindings, at=i)
                        if is_ident(exp_s)
                        else (args[0], [exp_s])
                    )
                    windows.append(
                        _window(
                            "assert",
                            form,
                            followed,
                            args[1],
                            i,
                            end,
                            text,
                            proxy=proxy_label(chain),
                        )
                    )
                continue
            # second
            if len(args) >= 2:
                exp_s = args[1].strip()
                followed, chain = (
                    follow_name(exp_s, bindings, at=i)
                    if is_ident(exp_s)
                    else (args[1], [exp_s])
                )
                windows.append(
                    _window(
                        "assert",
                        form,
                        followed,
                        args[0],
                        i,
                        end,
                        text,
                        proxy=proxy_label(chain),
                    )
                )

    # expect(actual).toBe(expected)
    for m in re.finditer(r"\bexpect\s*\(", text):
        i = m.start()
        if in_comment(mask, i):
            continue
        actual_end = match_paren(text, m.end() - 1)
        if actual_end < 0:
            continue
        tail = JEST_TAIL.match(text[actual_end:])
        if not tail:
            continue
        if tail.group(1).lower() in {"tobetruthy", "tobefalsy"}:
            continue
        call_at = actual_end + tail.end() - 1
        # tail ends at '(' of toBe(
        end = match_paren(text, call_at)
        if end < 0:
            continue
        if not occupy(i, end):
            continue
        actual = text[m.end() : actual_end - 1]
        expected = text[call_at + 1 : end - 1]
        windows.append(_window("expect", "expect." + tail.group(1), expected, actual, i, end, text))

    # pytest-style `assert a == b` in non-Python (rare) and `assert a == b` leftover
    for m in re.finditer(r"(?m)^\s*assert\s+(.+?)\s*$", text):
        i = m.start()
        if in_comment(mask, i):
            continue
        if occupy(i, m.end()):
            cmp_ = split_compare(m.group(1))
            if cmp_:
                left, _op, right = cmp_
                right_s = right.strip()
                followed, chain = (
                    follow_name(right_s, bindings, at=i)
                    if is_ident(right_s)
                    else (right, [right_s])
                )
                windows.append(
                    _window(
                        "assert",
                        "assert",
                        followed,
                        left,
                        i,
                        m.end(),
                        text,
                        proxy=proxy_label(chain),
                    )
                )

    # expected = "..."  (follow the rhs name)
    for m in re.finditer(
        r"(?m)^\s*(expected|want|wanted|golden|oracle)\s*=\s*(.+?)\s*$",
        text,
        re.I,
    ):
        i = m.start()
        if in_comment(mask, i):
            continue
        if occupy(i, m.end()):
            rhs = m.group(2).strip()
            followed, chain = (
                follow_name(rhs, bindings, at=i) if is_ident(rhs) else (m.group(2), [m.group(1), rhs])
            )
            if is_ident(rhs):
                chain = [m.group(1)] + [c for c in chain if c != m.group(1)]
            windows.append(
                _window(
                    "assign",
                    m.group(1) + "=",
                    followed,
                    m.group(1),
                    i,
                    m.end(),
                    text,
                    proxy=proxy_label(chain),
                )
            )

    return windows, comments


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


def extract_snapshot_windows(text: str, path: str) -> list[Window]:
    """Whole golden is expected, minus comments."""
    mask = comment_mask(text, path)
    windows: list[Window] = []
    for m in LABEL_RE.finditer(text):
        if in_comment(mask, m.start()):
            continue
        windows.append(
            _window(
                "label",
                "label:" + m.group("k").lower(),
                m.group("v"),
                m.group("k"),
                m.start("v"),
                m.end("v"),
                text,
            )
        )
    for m in ASSIGN_RE.finditer(text):
        if in_comment(mask, m.start()):
            continue
        windows.append(
            _window(
                "assign",
                m.group("k") + "=",
                m.group("v"),
                m.group("k"),
                m.start("v"),
                m.end("v"),
                text,
            )
        )
    # Bare paths in goldens (not already labeled).
    occupied = bytearray(len(text))
    for w in windows:
        occupied[w.start : w.end] = b"\x01" * max(0, w.end - w.start)
    for rx in (QUOTED_PATH_RE, PATH_RE):
        for m in rx.finditer(text):
            if in_comment(mask, m.start()):
                continue
            if any(occupied[m.start() : m.end()]):
                continue
            raw = m.group(0)
            if rx is QUOTED_PATH_RE:
                raw = m.group("pd") or m.group("ps") or m.group("pb") or raw
            occupied[m.start() : m.end()] = b"\x01" * (m.end() - m.start())
            windows.append(
                _window("snapshot", "path", raw, "", m.start(), m.end(), text)
            )
    # platform words in goldens
    for m in PLATFORM_RE.finditer(text):
        if in_comment(mask, m.start()):
            continue
        if m.group(0).lower() in {"aarch64", "x86_64", "amd64", "arm64"}:
            continue
        if any(occupied[m.start() : m.end()]):
            continue
        occupied[m.start() : m.end()] = b"\x01" * (m.end() - m.start())
        windows.append(
            _window("snapshot", "platform", m.group(0), "", m.start(), m.end(), text)
        )
    return windows


def extract_fixture_windows(text: str, path: str) -> list[Window]:
    """Identity-as-data strings (window titles, owner/repo) — not oaths."""
    mask = comment_mask(text, path)
    windows: list[Window] = []
    for m in re.finditer(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', text):
        if in_comment(mask, m.start()):
            continue
        raw = _strip_quotes(m.group(0))
        if _is_github_fixture(raw) and fixture_identity(raw):
            windows.append(
                _window("fixture", "string", raw, "", m.start(), m.end(), text)
            )
    return windows


def extract_windows(text: str, path: str = "") -> tuple[list[Window], list[tuple[int, int, str]]]:
    if is_snapshot(path) or lang_of(path) == "snap" and Path(path).suffix.lower() in {
        ".snap",
        ".txt",
        "",
    }:
        comments = _comment_spans(text, comment_mask(text, path or "x.snap"))
        return extract_snapshot_windows(text, path or "x.snap"), comments

    lang = lang_of(path)
    if lang == "python":
        windows, comments = extract_python_windows(text, path)
    else:
        windows, comments = extract_generic_windows(text, path)

    # Snapshots that are also test-like (rare) already returned.
    if is_snapshot(path):
        windows.extend(extract_snapshot_windows(text, path))

    # Fixture titles live in test source but are not expected values.
    if is_test_source(path) or lang in {"swift", "python", "js", "rust"}:
        have = {(w.start, w.end) for w in windows}
        for fw in extract_fixture_windows(text, path):
            if (fw.start, fw.end) not in have:
                windows.append(fw)

    windows.sort(key=lambda w: (w.start, w.kind))
    return windows, comments


# ---------------------------------------------------------------------------
# Witnesses from windows + silent comments
# ---------------------------------------------------------------------------


def path_span_role(path: str, window: Window, raw: str, derived: dict[str, str]) -> str | None:
    """One role for every axis derived from a single path.

    Otherwise HOME=/home/user becomes payload while platform=Linux from
    the same span stays a skip (visa v0.1's kizu lie).
    """
    if window.env_tied or window.axis_hint in {"HOME", "USER", "HOST", "platform"}:
        return None
    if window.kind in {"label", "snapshot"} or is_snapshot(path):
        return None
    if not (is_test_source(path) or window.kind in {"assert", "expect"}):
        return None
    if "tmp" in derived:
        return "payload"
    if " " in raw or "'" in raw:
        return "payload"
    for axis in ("HOME", "USER"):
        if axis in derived and _is_textbook(axis, derived[axis]):
            return "payload"
    return None


def classify_role(
    path: str,
    axis: str,
    value: str,
    window: Window,
    raw: str,
) -> str:
    if window.kind == "fixture" or _is_github_fixture(raw) or _is_github_fixture(value):
        if axis == "USER" or window.kind == "fixture":
            return "fixture"
    if window.env_tied or window.axis_hint:
        return "record"
    if window.kind in {"label", "snapshot"} or is_snapshot(path):
        return "record"
    if window.kind == "assign" and window.actual.lower() in {
        "home",
        "user",
        "username",
        "logname",
        "host",
        "hostname",
        "platform",
        "os",
        "cwd",
        "pwd",
    }:
        return "record"
    if is_test_source(path) or window.kind in {"assert", "expect"}:
        if _is_textbook(axis, value):
            return "payload"
        if " " in value or "'" in value:
            return "payload"
    return "record"


def _add_axis(
    out: list[Witness],
    text: str,
    axis: str,
    value: str,
    kind: str,
    window: Window,
    path: str,
    raw: str,
    role: str | None = None,
) -> None:
    if not value or axis == "tmp":
        return
    if role is None:
        role = classify_role(path, axis, value, window, raw)
    ln, col = line_col(text, window.start)
    out.append(
        Witness(
            axis=axis,
            value=value,
            kind=kind,
            role=role,
            start=window.start,
            end=window.end,
            line=window.line or ln,
            col=window.col or col,
            raw=raw,
            form=window.form,
        )
    )


def witnesses_from_window(text: str, window: Window, path: str) -> list[Witness]:
    if window.kind == "fixture":
        hits: list[Witness] = []
        name = fixture_identity(window.expected)
        if name:
            _add_axis(
                hits,
                text,
                "USER",
                name,
                "literal",
                window,
                path,
                window.expected,
                role="fixture",
            )
        return hits

    expected = _strip_quotes(window.expected)
    actual = window.actual
    hits: list[Witness] = []

    # Name followed to getenv/Path.home: no literal machine to require.
    if is_expr_not_literal(expected):
        return hits

    hint = window.axis_hint
    if hint == "USER" and _usable_id(expected) and "/" not in expected:
        _add_axis(hits, text, "USER", expected, "literal", window, path, expected)
        return hits
    if hint == "HOST" and _usable_id(expected) and "/" not in expected:
        _add_axis(hits, text, "HOST", expected, "literal", window, path, expected)
        return hits
    if hint == "platform":
        plat = _canon_platform(expected) or _canon_platform(expected.strip("'\""))
        if plat:
            _add_axis(hits, text, "platform", plat, "literal", window, path, expected)
            return hits
    if hint == "HOME":
        derived = derive_from_path(expected)
        if derived:
            role = path_span_role(path, window, expected, derived)
            for axis, val in derived.items():
                _add_axis(hits, text, axis, val, "path", window, path, expected, role=role)
            return hits
        if expected.startswith("~") or _usable_id(expected):
            _add_axis(hits, text, "HOME", expected, "literal", window, path, expected)
            return hits

    # Label windows name the axis explicitly.
    if window.kind in {"label", "assign"}:
        key = window.actual.lower().rstrip("=")
        val = expected
        if key in {"home", "cwd", "pwd", "tmp", "tmpdir"}:
            derived = derive_from_path(val)
            if derived:
                role = path_span_role(path, window, val, derived)
                for axis, v in derived.items():
                    _add_axis(hits, text, axis, v, "label", window, path, val, role=role)
            elif key == "home":
                _add_axis(hits, text, "HOME", val, "label", window, path, val)
        elif key in {"user", "username", "logname"}:
            if _usable_id(val) and not _is_github_fixture(val):
                _add_axis(hits, text, "USER", val, "label", window, path, val)
        elif key in {"host", "hostname"}:
            if _usable_id(val):
                _add_axis(hits, text, "HOST", val, "label", window, path, val)
        elif key in {"platform", "os"}:
            plat = _canon_platform(val)
            if plat:
                _add_axis(hits, text, "platform", plat, "label", window, path, val)
        elif key in {"runner_os"}:
            plat = _canon_platform(val)
            if plat:
                _add_axis(hits, text, "platform", plat, "assign", window, path, val)
                _add_axis(hits, text, "CI", "github-actions", "assign", window, path, val)
        elif key in {"github_actions"}:
            if val.lower() in {"true", "1"}:
                _add_axis(hits, text, "CI", "github-actions", "assign", window, path, val)
        if hits:
            return hits

    # Path / platform shapes inside the expected literal.
    blob = expected
    for m in QUOTED_PATH_RE.finditer(blob):
        p = m.group("pd") or m.group("ps") or m.group("pb")
        if p:
            derived = derive_from_path(p)
            role = path_span_role(path, window, p, derived)
            for axis, val in derived.items():
                _add_axis(hits, text, axis, val, "path", window, path, p, role=role)
    if not hits:
        for m in PATH_RE.finditer(blob):
            p = m.group(0)
            derived = derive_from_path(p)
            role = path_span_role(path, window, p, derived)
            for axis, val in derived.items():
                _add_axis(hits, text, axis, val, "path", window, path, p, role=role)
    if not hits:
        plat = _canon_platform(blob)
        if plat:
            _add_axis(hits, text, "platform", plat, "platform", window, path, blob)

    # Bare username expected of an env-tied USER compare already returned.
    if not hits and window.env_tied and _usable_id(expected) and "/" not in expected:
        _add_axis(hits, text, "USER", expected, "literal", window, path, expected)

    return hits


def silent_from_comments(
    text: str, comments: list[tuple[int, int, str]], path: str
) -> list[Witness]:
    """Machine-shaped comments: reported, never required."""
    out: list[Witness] = []
    seen: set[tuple[str, str]] = set()
    for start, end, blob in comments:
        ln, col = line_col(text, start)
        fake = Window(
            kind="comment",
            form="comment",
            expected=blob,
            actual="",
            env_tied=False,
            start=start,
            end=end,
            line=ln,
            col=col,
        )

        def add(axis: str, value: str, raw: str) -> None:
            key = (axis, value)
            if key in seen:
                return
            if not value:
                return
            seen.add(key)
            out.append(
                Witness(
                    axis=axis,
                    value=value,
                    kind="comment",
                    role="comment",
                    start=start,
                    end=end,
                    line=ln,
                    col=col,
                    raw=raw[:80],
                    form="comment",
                )
            )

        for m in QUOTED_PATH_RE.finditer(blob):
            p = m.group("pd") or m.group("ps") or m.group("pb")
            if p:
                for axis, val in derive_from_path(p).items():
                    add(axis, val, p)
        for m in PATH_RE.finditer(blob):
            for axis, val in derive_from_path(m.group(0)).items():
                add(axis, val, m.group(0))
        for m in ASSIGN_RE.finditer(blob):
            key = m.group("k")
            val = m.group("v")
            if key in {"HOME", "PWD"}:
                derived = derive_from_path(val)
                if derived:
                    for axis, v in derived.items():
                        add(axis, v, val)
            elif key in {"USER", "USERNAME", "LOGNAME"} and _usable_id(val):
                add("USER", val, val)
            elif key == "HOSTNAME" and _usable_id(val):
                add("HOST", val, val)
        for m in LABEL_RE.finditer(blob):
            key = m.group("k").lower()
            val = _strip_quotes(m.group("v"))
            if key in {"user", "username", "logname"} and _usable_id(val):
                add("USER", val, val)
            elif key == "home":
                derived = derive_from_path(val)
                if derived:
                    for axis, v in derived.items():
                        add(axis, v, val)
                else:
                    add("HOME", val, val)
        m = RAN_ON_RE.search(blob)
        if m and _usable_id(m.group(1)):
            add("USER", m.group(1), m.group(0))
        for m in PLATFORM_RE.finditer(blob):
            plat = _canon_platform(m.group(0))
            if plat:
                add("platform", plat, m.group(0))
    return out


def extract_all(text: str, path: str = "") -> tuple[list[Window], list[Witness], list[Witness]]:
    windows, comments = extract_windows(text, path)
    hits: list[Witness] = []
    for w in windows:
        hits.extend(witnesses_from_window(text, w, path))
    silent = silent_from_comments(text, comments, path)
    return windows, hits, silent


# ---------------------------------------------------------------------------
# Merge / match / emit
# ---------------------------------------------------------------------------


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


def merge_oath(
    path: str,
    hits: list[Witness],
    windows: list[Window] | None = None,
    silent: list[Witness] | None = None,
) -> Oath:
    hits = _dedupe_witnesses(hits)
    by_axis: dict[str, dict[str, str]] = {}
    for w in hits:
        if w.axis == "tmp" or w.role == "comment":
            continue
        by_axis.setdefault(w.axis, {})
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

    return Oath(
        path=path,
        status=status,
        require=require,
        soft=soft,
        witnesses=hits,
        windows=windows or [],
        silent=silent or [],
        contradictions=contradictions,
    )


def infer(text: str, path: str = "") -> Oath:
    windows, hits, silent = extract_all(text, path)
    return merge_oath(path or "-", hits, windows, silent)


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


def match_oath(oath: Oath, live: dict[str, str] | None = None) -> Oath:
    live = live_axes() if live is None else live
    oath = Oath(
        path=oath.path,
        status=oath.status,
        require=dict(oath.require),
        soft=dict(oath.soft),
        witnesses=list(oath.witnesses),
        windows=list(oath.windows),
        silent=list(oath.silent),
        contradictions=list(oath.contradictions),
        side=oath.side,
    )
    if oath.status in {"OPEN", "SPEC", "FIXTURE"}:
        oath.match = "MATCH"
        oath.misses = []
        return oath
    if oath.status == "UNSAT":
        oath.match = "MISS"
        oath.misses = [
            {
                "axis": str(c.get("axis", "*")) if isinstance(c, dict) else "*",
                "want": "consistent",
                "have": "contradiction",
            }
            for c in oath.contradictions
        ] or [{"axis": "*", "want": "consistent", "have": "contradiction"}]
        return oath
    misses: list[dict[str, str]] = []
    for axis, want in oath.require.items():
        have = live.get(axis, "")
        if axis == "HOME":
            if have.rstrip("/\\") != want.rstrip("/\\"):
                misses.append({"axis": axis, "want": want, "have": have or "(unset)"})
            continue
        if have != want:
            misses.append({"axis": axis, "want": want, "have": have or "(unset)"})
    oath.match = "MISS" if misses else "MATCH"
    oath.misses = misses
    return oath


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
    """True → skip (skipif polarity)."""
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


def oath_to_dict(v: Oath) -> dict:
    return {
        "file": v.path,
        "side": v.side,
        "status": v.status,
        "require": v.require,
        "soft": v.soft,
        "windows": [asdict(w) for w in v.windows],
        "witnesses": [asdict(w) for w in v.witnesses],
        "silent": [asdict(w) for w in v.silent],
        "contradictions": v.contradictions,
        "match": v.match,
        "misses": v.misses,
        "predicate": {
            "shell": emit_shell(v.require) if v.status != "UNSAT" else "false",
            "pytest": emit_pytest(v.require) if v.status != "UNSAT" else "True",
            "gha": emit_gha(v.require) if v.status != "UNSAT" else "none",
        },
    }


def pair_to_dict(p: Pair) -> dict:
    return {
        "kind": p.kind,
        "pair": p.label,
        "expected_raw": p.expected_raw,
        "actual_raw": p.actual_raw,
        "source": p.source,
        "host": p.host,
        "proxy": p.proxy,
        "expected": oath_to_dict(p.expected),
        "actual": oath_to_dict(p.actual),
    }


def format_human(v: Oath, *, show_match: bool = False) -> str:
    tag = f"proxy:{v.side}" if v.side else "proxy"
    lines = [f"{tag}  {v.path}  {v.status}"]
    if v.status == "UNSAT":
        lines.append("  (contradictory assertion machines — oracle cannot apply)")
        for c in v.contradictions:
            vals = c.get("values") if isinstance(c, dict) else None
            axis = c.get("axis") if isinstance(c, dict) else "?"
            lines.append(f"  conflict {axis}  {' | '.join(map(str, vals or []))}")
    elif v.require:
        for axis, val in v.require.items():
            lines.append(f"  require  {axis}={val}")
    else:
        if v.status == "OPEN":
            lines.append("  (portable — no assertion named a machine)")
        elif v.status == "SPEC":
            lines.append("  (assertion expecteds are path/user spec, not a skip)")
        elif v.status == "FIXTURE":
            lines.append("  (identity-as-data — not a machine demand)")
    for axis, val in v.soft.items():
        lines.append(f"  soft     {axis}={val}")
    for w in v.windows:
        exp = w.expected.replace("\n", " ")
        if len(exp) > 64:
            exp = exp[:61] + "..."
        extra = f"  proxy={w.proxy}" if w.proxy else ""
        lines.append(f"  window   {w.form:16} L{w.line}:{w.col}  expected={exp}{extra}")
    for s in v.silent:
        shown = s.raw.replace("\n", " ")
        if len(shown) > 56:
            shown = shown[:53] + "..."
        lines.append(
            f"  silent   comment L{s.line}:{s.col}  {s.axis}={s.value}  {shown}"
        )
    for w in v.witnesses:
        shown = w.raw if w.raw else w.value
        if len(shown) > 64:
            shown = shown[:61] + "..."
        lines.append(
            f"  witness  {w.role:7} {w.kind:8} {w.axis}={w.value}  L{w.line}:{w.col}  {shown}"
        )
    pred = emit_shell(v.require) if v.status != "UNSAT" else "false"
    lines.append(f"  apply    {pred}")
    if show_match or v.match:
        if v.match == "MATCH":
            lines.append("  match    MATCH  this host satisfies the oath")
        elif v.match == "MISS":
            lines.append("  match    MISS   skip — this host is not the asserted machine")
            for m in v.misses:
                lines.append(f"           {m['axis']} want={m['want']} have={m['have']}")
    return "\n".join(lines)


def _short(s: str, n: int = 72) -> str:
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[: n - 3] + "..."


def format_pair(p: Pair, *, show_match: bool = False) -> str:
    """The object: two unary oaths, labeled, not a substitution residue."""
    lines = [f"proxy  pair  {p.kind}  {p.label}"]
    lines.append(f"  expected {_short(p.expected_raw)}")
    lines.append(f"  actual   {_short(p.actual_raw)}")
    if p.source:
        lines.append(f"  source   {_short(p.source)}")
    if p.proxy:
        lines.append(f"  proxy    {p.proxy}")
    if p.host:
        gloss = {
            "EXPECTED": "this host is the oracle machine",
            "ACTUAL": "this host produced the fail",
            "BOTH": "this host holds both sides",
            "NEITHER": "this host is neither recorded machine",
        }.get(p.host, "")
        lines.append(f"  host     {p.host}" + (f"  {gloss}" if gloss else ""))

    def side_block(name: str, v: Oath) -> None:
        lines.append(f"  {name:8} {v.status}")
        if v.status == "UNSAT":
            for c in v.contradictions:
                vals = c.get("values") if isinstance(c, dict) else None
                axis = c.get("axis") if isinstance(c, dict) else "?"
                lines.append(f"    conflict {axis}  {' | '.join(map(str, vals or []))}")
        elif v.require:
            for axis, val in v.require.items():
                lines.append(f"    require  {axis}={val}")
        else:
            lines.append(f"    (no machine — {v.status})")
        for axis, val in v.soft.items():
            lines.append(f"    soft     {axis}={val}")
        pred = emit_shell(v.require) if v.status != "UNSAT" else "false"
        lines.append(f"    apply    {pred}")
        if show_match or v.match:
            if v.match == "MATCH":
                lines.append("    match    MATCH")
            elif v.match == "MISS":
                lines.append("    match    MISS")
                for m in v.misses:
                    lines.append(
                        f"             {m['axis']} want={m['want']} have={m['have']}"
                    )

    side_block("expected", p.expected)
    side_block("actual", p.actual)
    return "\n".join(lines)


def porcelain(v: Oath) -> str:
    rows = [f"status\t{v.status}\t{v.path}"]
    for axis, val in v.require.items():
        rows.append(f"require\t{axis}\t{val}\t{v.path}")
    for axis, val in v.soft.items():
        rows.append(f"soft\t{axis}\t{val}\t{v.path}")
    for w in v.windows:
        rows.append(f"window\t{w.kind}\t{w.form}\t{v.path}\t{w.line}\t{w.col}")
    for s in v.silent:
        rows.append(f"silent\tcomment\t{s.axis}\t{s.value}\t{v.path}\t{s.line}\t{s.col}")
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


def porcelain_pair(p: Pair) -> str:
    rows = [f"pair\t{p.expected.status}\t{p.actual.status}\t{p.kind}\t{p.label}"]
    if p.host:
        rows.append(f"host\t{p.host}")
    if p.proxy:
        rows.append(f"proxy\t{p.proxy}")
    rows.append(f"raw\texpected\t{p.expected_raw.replace(chr(9), ' ')}")
    rows.append(f"raw\tactual\t{p.actual_raw.replace(chr(9), ' ')}")
    for side, v in (("expected", p.expected), ("actual", p.actual)):
        rows.append(f"status\t{side}\t{v.status}\t{v.path}")
        for axis, val in v.require.items():
            rows.append(f"require\t{side}\t{axis}\t{val}")
        for axis, val in v.soft.items():
            rows.append(f"soft\t{side}\t{axis}\t{val}")
        if v.match:
            rows.append(f"match\t{side}\t{v.match}")
            for m in v.misses:
                rows.append(f"miss\t{side}\t{m['axis']}\t{m['want']}\t{m['have']}")
        pred = emit_shell(v.require) if v.status != "UNSAT" else "false"
        rows.append(f"predicate\t{side}\tshell\t{pred}")
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# --from-fail : expected oath × actual oath
# ---------------------------------------------------------------------------


def _looks_like_value(s: str) -> bool:
    """Dump literal vs leftover expression (`os.environ[...]`, `(1 + 1)`)."""
    s = (s or "").strip()
    if not s:
        return False
    if s[0] in "'\"`" or s[:2] in ('r"', "r'"):
        return True
    if s.startswith("/") or s.startswith("~") or re.match(r"^[A-Za-z]:\\", s):
        return True
    if re.fullmatch(r"[A-Za-z0-9._-]+", s):
        return True
    return False


def _html_unescape(s: str) -> str:
    return (
        s.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&apos;", "'")
    )


PAIR_RANK = {
    "pytest-vv": 50,
    "pytest-src": 45,
    "pytest-diff": 40,
    "xctest": 40,
    "junit": 40,
    "jest": 40,
    "go": 40,
    "rspec": 40,
    "vitest": 40,
    "phpunit": 40,
    "cargo": 40,
    "swift-testing": 30,
    "pytest": 20,
    "pytest-pm": 20,
    "unittest": 20,
}


def _norm_fail_val(s: str) -> str:
    return _strip_quotes(s or "").strip()


def resolve_fail_expected(
    pairs: list[tuple[str, str, str, str]],
    bindings: list[tuple[str, str, int, int]],
) -> list[tuple[str, str, str, str, str]]:
    """Follow the expected name to a bound value using dump assignments and sibling pairs."""
    out: list[tuple[str, str, str, str, str]] = []
    for kind, exp, act, src in pairs:
        chain: list[str] = []
        cur = exp
        if is_ident(cur):
            cur, chain = follow_name(cur, bindings)
        # Ident *or* getenv/Path.home expression: a sibling path with the
        # same actual is the bound value of that name.
        if is_ident(cur) or is_expr_not_literal(cur):
            act_n = _norm_fail_val(act)
            for _k, e2, a2, _s2 in pairs:
                e2n = _norm_fail_val(e2)
                a2n = _norm_fail_val(a2)
                if is_ident(e2n):
                    e2n_f, _c = follow_name(e2n, bindings)
                    if not is_ident(e2n_f) and not is_expr_not_literal(e2n_f):
                        e2n = _norm_fail_val(e2n_f)
                    else:
                        continue
                if is_expr_not_literal(e2n):
                    continue
                if a2n == act_n and e2n != _norm_fail_val(cur) and e2n:
                    if not chain:
                        chain = [exp]
                    if cur not in chain:
                        chain.append(cur)
                    chain.append(e2n)
                    cur = e2n
                    break
        proxy = proxy_label(chain) if chain else ""
        if proxy and cur != exp:
            pass
        elif chain and len(chain) > 1:
            proxy = proxy_label(chain)
        out.append((kind, cur, act, src, proxy))
    return out


def collapse_fail_pairs(
    items: list[tuple[str, str, str, str, str]],
) -> list[tuple[str, str, str, str, str]]:
    """One pair per assertion: drop inverted PM when E +/- / -vv already names it."""
    kept: list[tuple[str, str, str, str, str]] = []

    def rank(kind: str) -> int:
        return PAIR_RANK.get(kind, 10)

    for item in items:
        kind, e, a, src, proxy = item
        e_n, a_n = _norm_fail_val(e), _norm_fail_val(a)
        drop = False
        replace_i: int | None = None
        for i, (k2, e2, a2, _s2, _p2) in enumerate(kept):
            e2n, a2n = _norm_fail_val(e2), _norm_fail_val(a2)
            same = e_n == e2n and a_n == a2n
            inv = e_n == a2n and a_n == e2n and e_n != a_n
            if not same and not inv:
                continue
            if rank(kind) > rank(k2):
                replace_i = i
            else:
                # Keep the higher-rank proxy if the survivor has none.
                if not kept[i][4] and proxy:
                    kept[i] = (k2, e2, a2, _s2, proxy)
                drop = True
            break
        if drop:
            continue
        if replace_i is not None:
            old = kept[replace_i]
            if not proxy and old[4]:
                item = (kind, e, a, src, old[4])
            kept[replace_i] = item
        else:
            kept.append(item)
    out: list[tuple[str, str, str, str, str]] = []
    for kind, e, a, src, proxy in kept:
        if kind in {"pytest-diff", "pytest-pm"}:
            kind = "pytest"
        out.append((kind, e, a, src, proxy))
    return out


def parse_fail(text: str) -> list[tuple[str, str, str, str, str]]:
    """(kind, expected, actual, source, proxy). Both sides become oaths.

    pytest `assert left == right` → left is actual, right is expected.
    rustc `left:` is actual, `right:` is expected. Expected names follow
    before the pair is classified. Inverted PM + E +/- collapse to one pair.
    """
    pairs: list[tuple[str, str, str, str]] = []
    try:
        bindings = collect_python_bindings(text)
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        bindings = []
    if not bindings:
        bindings = collect_generic_bindings(text)
    minus: str | None = None
    left: str | None = None
    jest_exp: str | None = None
    go_exp: str | None = None
    rspec_exp: str | None = None
    php_mode: str | None = None
    php_exp: list[str] = []
    php_act: list[str] = []
    pending_assert: str = ""
    where_act: str | None = None
    where_exp: str | None = None

    def add(kind: str, a: str, b: str, src: str = "") -> None:
        a, b = _strip_quotes(a), _strip_quotes(b)
        if not a and not b:
            return
        src = src or pending_assert
        if any(p[1] == a and p[2] == b for p in pairs):
            return
        pairs.append((kind, a, b, src))

    def flush_vv() -> None:
        nonlocal where_act, where_exp
        if where_act is None or where_exp is None:
            return
        exp, act = _strip_quotes(where_exp), _strip_quotes(where_act)
        # Drop an unlabeled pytest pair of the same two values
        # (AssertionError 'actual' == 'expected' fires before where/and).
        # After name-follow an ident expected is *not* the same two values
        # as a path pair — keep both here; collapse_fail_pairs joins them.
        pairs[:] = [
            p
            for p in pairs
            if {p[1], p[2]} != {exp, act}
            or p[0] in {"pytest-vv", "pytest-src", "pytest-diff"}
        ]
        add("pytest-vv", exp, act)
        where_act = where_exp = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        unescaped = _html_unescape(line)

        stripped = line.strip()
        if stripped.startswith("//") or (
            stripped.startswith("#")
            and not stripped.startswith("#expect")
            and not stripped.startswith("#require")
        ):
            # Comments in a pasted dump are not fail windows.
            continue
        if stripped.startswith("assert ") and ("==" in stripped or "!=" in stripped):
            pending_assert = stripped
        if any(
            name in stripped
            for name in ("assertEqual", "XCTAssertEqual", "assert_eq!", "#expect")
        ) and "is not equal to" not in stripped:
            pending_assert = stripped

        m = PYTEST_WHERE_ACT_RE.match(line)
        if m:
            where_act = m.group("v")
            flush_vv()
            continue
        m = PYTEST_WHERE_EXP_RE.match(line)
        if m:
            where_exp = m.group("v")
            flush_vv()
            continue

        m = PYTEST_DIFF_MINUS.match(line)
        if m:
            minus = m.group("v")
            continue
        m = PYTEST_DIFF_PLUS.match(line)
        if m and minus is not None:
            # pytest ndiff / lees convention: minus is the recorded oracle.
            add("pytest-diff", minus, m.group("v"))
            minus = None
            continue

        m = PYTEST_PM_RE.match(line)
        if m:
            # If the source assertion names a literal expected, that
            # literal is the expected oath. The *other* dumped value is
            # the actual — not the left-hand expression (`os.environ[...]`).
            # An identifier expected is followed through dump bindings.
            src_exp = None
            if pending_assert:
                expr = (
                    pending_assert[7:].strip()
                    if pending_assert.startswith("assert ")
                    else pending_assert
                )
                cmp_ = split_compare(expr)
                if cmp_:
                    right_src = cmp_[2].strip()
                    if is_ident(_strip_quotes(right_src)):
                        followed, _chain = follow_name(_strip_quotes(right_src), bindings)
                        if not is_ident(followed):
                            src_exp = _strip_quotes(followed)
                    else:
                        src_exp = _strip_quotes(right_src)
            left_v = _strip_quotes(m.group("a"))
            right_v = _strip_quotes(m.group("b"))
            if src_exp:
                actual_v = right_v if left_v == src_exp else left_v
                if _looks_like_value(actual_v):
                    add("pytest-src", src_exp, actual_v)
                continue
            # pytest `assert left == right`: left is actual, right is expected.
            add("pytest-pm", right_v, left_v)
            continue

        m = UNITTEST_RE.search(line)
        if m:
            add("unittest", m.group("a"), m.group("b"))
            continue

        m = CARGO_LEFT_RE.match(line)
        if m:
            left = m.group("v")
            continue
        m = CARGO_RIGHT_RE.match(line)
        if m and left is not None:
            # rustc assert_eq!(got, expected) prints left: got / right: expected.
            add("cargo", m.group("v"), left)
            left = None
            continue

        m = SWIFT_RE.search(line)
        if m:
            # Apple: XCTAssertEqual failed: ("actual") is not equal to ("expected")
            act = m.group("qa") or m.group("a") or ""
            exp = m.group("qb") or m.group("b") or ""
            add("xctest", exp, act)
            continue

        m = SWIFT_TESTING_RE.search(line)
        if m:
            add("swift-testing", m.group("v"), "")
            continue

        m = JEST_EXP_RE.match(line)
        if m:
            jest_exp = m.group("v")
            continue
        m = JEST_GOT_RE.match(line)
        if m and jest_exp is not None:
            add("jest", jest_exp, m.group("v"))
            jest_exp = None
            continue

        m = GO_EXP_RE.match(line)
        if m and "expected:<" not in line:
            go_exp = m.group("v")
            continue
        m = GO_ACT_RE.match(line)
        if m and go_exp is not None:
            add("go", go_exp, m.group("v"))
            go_exp = None
            continue

        m = JUNIT_RE.search(unescaped)
        if m:
            add("junit", m.group("a"), m.group("b"))
            continue

        m = RSPEC_EXP_RE.match(line)
        if m and go_exp is None and jest_exp is None:
            rspec_exp = m.group("v")
            continue
        m = RSPEC_GOT_RE.match(line)
        if m and rspec_exp is not None:
            add("rspec", rspec_exp, m.group("v"))
            rspec_exp = None
            continue

        m = VITEST_RE.search(line)
        if m:
            add("vitest", m.group("b"), m.group("a"))
            continue

        if PHPUNIT_EXP.match(line):
            php_mode = "exp"
            php_exp, php_act = [], []
            continue
        if PHPUNIT_ACT.match(line):
            php_mode = "act"
            continue
        if php_mode == "exp" and line.startswith("-") and not line.startswith("---"):
            php_exp.append(line[1:])
            continue
        if php_mode == "act" and line.startswith("+") and not line.startswith("+++"):
            php_act.append(line[1:])
            continue
        if php_mode and not line.startswith(("-", "+")) and (php_exp or php_act):
            add("phpunit", "\n".join(php_exp), "\n".join(php_act))
            php_mode = None

    flush_vv()
    if php_mode and (php_exp or php_act):
        add("phpunit", "\n".join(php_exp), "\n".join(php_act))

    resolved = resolve_fail_expected(pairs, bindings)
    return collapse_fail_pairs(resolved)


def infer_fail_side(kind: str, literal: str, source: str, side: str) -> Oath:
    """Unary oath of one side of a failing assertion."""
    blob = (literal or "") + "\n"
    path = f"<{kind} {side}>"
    hint = axis_hint_of(source) or axis_hint_of(literal)
    windows = [
        Window(
            kind="fail",
            form=f"{kind}:{side}",
            expected=literal or "",
            actual=source or "",
            env_tied=is_env_tied(source) or is_env_tied(literal),
            start=0,
            end=len(literal or ""),
            line=1,
            col=1,
            axis_hint=hint,
        )
    ]
    extra, _c = extract_windows(blob, "fail.snap")
    windows.extend(extra)
    hits: list[Witness] = []
    for w in windows:
        hits.extend(witnesses_from_window(blob, w, path))
    v = merge_oath(path, hits, windows, [])
    v.side = side
    return v


def make_pair(
    kind: str, expected: str, actual: str, source: str = "", proxy: str = ""
) -> Pair:
    return Pair(
        kind=kind,
        expected_raw=expected,
        actual_raw=actual,
        source=source,
        expected=infer_fail_side(kind, expected, source, "expected"),
        actual=infer_fail_side(kind, actual, source, "actual"),
        proxy=proxy,
    )


def infer_fail_pair(
    kind: str, expected: str, actual: str, source: str = "", proxy: str = ""
) -> Oath:
    """Expected-side unary (oath's window). Prefer make_pair."""
    return infer_fail_side(kind, expected, source, "expected")


def host_role(pair: Pair, live: dict[str, str] | None = None) -> str:
    """Which machine is this host, given the pair.

    OPEN/SPEC/FIXTURE always MATCH, so they are not an identity.
    Only a BOUND side that holds can name the host EXPECTED or ACTUAL.
    """
    live = live_axes() if live is None else live
    e = match_oath(pair.expected, live)
    a = match_oath(pair.actual, live)
    e_is = pair.expected.status == "BOUND" and e.match == "MATCH"
    a_is = pair.actual.status == "BOUND" and a.match == "MATCH"
    if e_is and a_is:
        return "BOTH"
    if e_is:
        return "EXPECTED"
    if a_is:
        return "ACTUAL"
    return "NEITHER"


# ---------------------------------------------------------------------------
# IO / CLI
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def is_oracle_path(path: Path) -> bool:
    if path.name in SKIP_ORACLE_BASENAMES:
        return False
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


def infer_file(path: Path) -> Oath | None:
    text = read_text(path)
    if text is None:
        return None
    return infer(text, str(path))


def cmd_emit(v: Oath, kind: str) -> int:
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
        print(f"proxy: unknown emit {kind}", file=sys.stderr)
        return 2
    return 0


def _apply_exit(items: list[Oath]) -> int:
    if any(v.status == "UNSAT" for v in items):
        return 2
    if any(v.match == "MISS" for v in items):
        return 1
    return 0


def report(oaths: list[Oath], args: argparse.Namespace) -> int:
    if args.emit and len(oaths) == 1 and not args.json and not args.porcelain:
        return cmd_emit(oaths[0], args.emit)
    if args.json:
        payload = {
            "mode": "proxy",
            "files": [oath_to_dict(v) for v in oaths],
        }
        if len(oaths) == 1:
            payload.update(oath_to_dict(oaths[0]))
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    elif args.porcelain:
        for v in oaths:
            print(porcelain(v))
    else:
        for i, v in enumerate(oaths):
            if i:
                print()
            print(format_human(v, show_match=args.match or args.apply))
            if args.emit:
                print(f"  emit     {args.emit}  ", end="")
                cmd_emit(v, args.emit)
    if args.apply:
        return _apply_exit(oaths)
    return 0


def _pair_apply_sides(p: Pair, side: str) -> list[Oath]:
    if side == "actual":
        return [p.actual]
    if side == "both":
        return [p.expected, p.actual]
    return [p.expected]


def report_pairs(pairs: list[Pair], args: argparse.Namespace) -> int:
    side = getattr(args, "side", "expected") or "expected"
    if args.emit and len(pairs) == 1 and not args.json and not args.porcelain:
        return cmd_emit(_pair_apply_sides(pairs[0], side)[0], args.emit)
    if args.json:
        payload: dict = {
            "mode": "proxy",
            "pairs": [pair_to_dict(p) for p in pairs],
            "files": [
                oath_to_dict(v)
                for p in pairs
                for v in (p.expected, p.actual)
            ],
        }
        if len(pairs) == 1:
            payload["pair"] = pairs[0].label
            payload["kind"] = pairs[0].kind
            payload["host"] = pairs[0].host
            payload["proxy"] = pairs[0].proxy
            payload["expected"] = oath_to_dict(pairs[0].expected)
            payload["actual"] = oath_to_dict(pairs[0].actual)
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    elif args.porcelain:
        for p in pairs:
            print(porcelain_pair(p))
    else:
        for i, p in enumerate(pairs):
            if i:
                print()
            print(format_pair(p, show_match=args.match or args.apply))
            if args.emit:
                chosen = _pair_apply_sides(p, side)[0]
                print(f"  emit     {args.emit}  {side}  ", end="")
                cmd_emit(chosen, args.emit)
    if args.apply:
        items: list[Oath] = []
        for p in pairs:
            items.extend(_pair_apply_sides(p, side))
        return _apply_exit(items)
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

    comment = "# ran on alice\nassert result == 42\n"
    c = infer(comment, "tests/test_comment.py")
    check("comment is not an oath", "USER" not in c.require, str(c.require))
    check("comment file OPEN or no USER", c.status in {"OPEN", "SPEC"}, c.status)
    check(
        "comment is silent",
        any(s.role == "comment" and s.value == "alice" for s in c.silent),
        str(c.silent),
    )

    env_a = "assert os.environ['USER'] == 'alice'\n"
    e = infer(env_a, "tests/test_user.py")
    check("env assert USER=alice", e.require.get("USER") == "alice", str(e.require))
    check("env assert BOUND", e.status == "BOUND", e.status)

    both = "# ran on alice\nassert os.environ['USER'] == 'alice'\n"
    b = infer(both, "tests/test_both.py")
    check("both: require from assert", b.require.get("USER") == "alice", str(b.require))
    check("both: comment still silent", any(s.value == "alice" for s in b.silent), str(b.silent))

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
    check("timeout is not an oath", "30" not in v.require.values(), str(v.require))
    sh = emit_shell(v.require)
    check("shell mentions Darwin", "Darwin" in sh, sh)
    check("pytest skip polarity", emit_pytest(v.require).startswith("not ("), emit_pytest(v.require))
    check("gha macos", emit_gha(v.require) == "macos-latest", emit_gha(v.require))

    snap_cmt = "# ran on alice\ntimeout: 30\nstatus: green\n"
    sc = infer(snap_cmt, "fixtures/comment.snap")
    check("snap comment not USER", "USER" not in sc.require, str(sc.require))
    check("snap comment OPEN", sc.status == "OPEN", sc.status)

    ci = (
        "build: ok\n"
        "user: runner\n"
        "home: /home/runner\n"
        "host: fv-az123\n"
        "cwd: /home/runner/work/proj\n"
        "when: 2026-08-20T09:00:11Z\n"
        "timeout: 30\n"
    )
    cci = infer(ci, "fixtures/ci.snap")
    check("ci BOUND", cci.status == "BOUND", cci.status)
    check("ci Linux", cci.require.get("platform") == "Linux", str(cci.require))
    check("ci GHA", cci.require.get("CI") == "github-actions", str(cci.require))

    spec = "build: ok\ntimeout: 30\nstatus: green\n"
    s = infer(spec, "fixtures/spec_only.snap")
    check("spec OPEN", s.status == "OPEN", s.status)
    check("spec empty require", s.require == {}, str(s.require))

    conflict = "home: /Users/alice\nhome: /home/runner\n"
    u = infer(conflict, "fixtures/conflict.snap")
    check("conflict UNSAT", u.status == "UNSAT", u.status + str(u.contradictions))

    title = (
        "func testChromeTitle() {\n"
        '    let result = WindowTitleParser.extractSiteName(\n'
        '        from: "GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome",\n'
        '        app: "Google Chrome"\n'
        "    )\n"
        '    XCTAssertEqual(result, "GitHub")\n'
        "}\n"
    )
    g = infer(title, "WindowTitleParserTests.swift")
    check("github title not USER require", "USER" not in g.require, str(g.require))
    check("github title OPEN/FIXTURE", g.status in {"OPEN", "FIXTURE"}, g.status)
    check(
        "github title kind=fixture",
        any(w.role == "fixture" and w.value == "annenpolka" for w in g.witnesses),
        str(g.witnesses),
    )

    rel = infer('await session.waitForText("src/auth.rs");\n', "tests/e2e/nav.test.ts")
    check("relative src/auth.rs is not a fixture", rel.status != "FIXTURE", rel.status)
    check(
        "relative path has no fixture witness",
        not any(w.role == "fixture" for w in rel.witnesses),
        str(rel.witnesses),
    )
    mime = infer(
        'XCTAssertEqual(h, "application/json")\nlet p = "contracts/testcases"\n',
        "Engine/Tests/FooTests.swift",
    )
    check("mime/path is not fixture", not any(w.role == "fixture" for w in mime.witnesses), str(mime.witnesses))

    hook = (
        'assert_eq!(input.cwd.as_deref(), Some(Path::new("/home/user/project")));\n'
    )
    hk = infer(hook, "src/hook/tests.rs")
    check("textbook assert_eq is SPEC", hk.status in {"SPEC", "OPEN"}, hk.status + str(hk.require))
    check("textbook no HOME require", "HOME" not in hk.require, str(hk.require))

    leak = 'assert_eq!(home, "/Users/annenpolka/proj");\n'
    lk = infer(leak, "src/hook/tests.rs")
    check(
        "non-textbook home in tests.rs is a recording",
        lk.status == "BOUND" and lk.require.get("HOME") == "/Users/annenpolka",
        str(lk.require),
    )

    doc = (
        "// kizu binary lives at `/Users/John Doe/.cargo/bin/kizu`\n"
        "fn not_a_test() {}\n"
    )
    d = infer(doc, "src/attach.rs")
    check("doc comment not BOUND", d.status != "BOUND", d.status)
    check("doc comment no HOME require", "HOME" not in d.require, str(d.require))
    check(
        "doc comment is silent",
        any(s.role == "comment" and "John" in s.value for s in d.silent)
        or any(s.axis == "HOME" for s in d.silent),
        str(d.silent),
    )

    swift_exp = '#expect(os.getenv("USER") == "alice")\n'
    se = infer(swift_exp, "UserTests.swift")
    check("#expect USER=alice", se.require.get("USER") == "alice", str(se.require))

    macos_cmt = "// when the macOS PollWatcher fallback is active.\nexpect(1).toBe(1)\n"
    mc = infer(macos_cmt, "tests/e2e/reactive.test.ts")
    check("macOS in a comment is not BOUND", mc.status != "BOUND", mc.status)

    live = live_axes()
    alice_vs_live = match_oath(v, live)
    if live.get("HOME") == "/Users/alice":
        check("alice MATCH on alice host", alice_vs_live.match == "MATCH", str(live))
    else:
        check("alice MISS on this host", alice_vs_live.match == "MISS", alice_vs_live.match)

    mine = f"home: {live['HOME']}\nuser: {live['USER']}\n"
    mine_v = match_oath(infer(mine, "live.snap"), live)
    check("live snap MATCH", mine_v.match == "MATCH", mine_v.match + str(mine_v.require))
    check("OPEN always MATCH", match_oath(s, live).match == "MATCH")

    fail = (
        "E   AssertionError: '/Users/alice/proj' != '/home/runner/work/proj'\n"
        "E   - /Users/alice/proj\n"
        "E   + /home/runner/work/proj\n"
    )
    pairs = parse_fail(fail)
    check("parse pytest pair", len(pairs) >= 1, str(pairs))
    if pairs:
        ev = infer_fail_pair(*pairs[0])
        check(
            "from-fail expected Darwin",
            ev.require.get("platform") == "Darwin",
            str(ev.require),
        )
        pr = make_pair(*pairs[0])
        check(
            "pair EXPECTED-BOUND vs ACTUAL-BOUND",
            pr.label == "EXPECTED-BOUND vs ACTUAL-BOUND",
            pr.label + str(pr.actual.require),
        )
        check(
            "actual is runner HOME",
            pr.actual.require.get("HOME") == "/home/runner",
            str(pr.actual.require),
        )
        check(
            "actual is Linux",
            pr.actual.require.get("platform") == "Linux",
            str(pr.actual.require),
        )

    jest = "Expected: '/Users/alice/proj'\nReceived: '/home/runner/work/proj'\n"
    jp = parse_fail(jest)
    check("parse jest pair", any(p[0] == "jest" for p in jp), str(jp))

    go = "expected: /Users/alice\nactual  : /home/runner\n"
    gp = parse_fail(go)
    check("parse go pair", any(p[0] == "go" for p in gp), str(gp))

    junit = "expected:</Users/alice> but was:</home/runner>\n"
    ju = parse_fail(junit)
    check("parse junit pair", any(p[0] == "junit" for p in ju), str(ju))

    cargo = '  left: "/home/runner/work/proj"\n right: "/Users/alice/proj"\n'
    cp = parse_fail(cargo)
    check("parse cargo pair", any(p[0] == "cargo" for p in cp), str(cp))
    if cp:
        cargo_pr = make_pair(*cp[0])
        check(
            "cargo left is actual (rustc)",
            cargo_pr.actual.require.get("HOME") == "/home/runner"
            and cargo_pr.expected.require.get("HOME") == "/Users/alice",
            str((cargo_pr.expected.require, cargo_pr.actual.require)),
        )

    xct = 'XCTAssertEqual failed: ("/Users/alice/Library") is not equal to ("/tmp/x")\n'
    xp = parse_fail(xct)
    check("parse xctest pair", any(p[0] == "xctest" for p in xp), str(xp))
    if xp:
        xp_pair = make_pair(*xp[0])
        check(
            "xctest expected is tmp OPEN",
            xp_pair.expected.status == "OPEN",
            xp_pair.expected.status + str(xp_pair.expected.require),
        )
        check(
            "xctest actual is alice HOME",
            xp_pair.actual.require.get("HOME") == "/Users/alice",
            str(xp_pair.actual.require),
        )
        check(
            "xctest pair EXPECTED-OPEN vs ACTUAL-BOUND",
            xp_pair.label == "EXPECTED-OPEN vs ACTUAL-BOUND",
            xp_pair.label,
        )

    vv = (
        "# ran on alice\n"
        "E       AssertionError: assert '/Users/alice/proj' == '/tmp/pytest-of-runner/pytest-0'\n"
        "E        +  where got = '/Users/alice/proj'\n"
        "E        +    and expected = '/tmp/pytest-of-runner/pytest-0'\n"
    )
    vvp = parse_fail(vv)
    check("parse pytest -vv pair", any(p[0] == "pytest-vv" for p in vvp), str(vvp))
    ran = (
        "# ran on alice\n"
        "# HOME=/Users/alice\n"
        "E   AssertionError: 1 != 2\n"
        "E   - 1\n"
        "E   + 2\n"
    )
    rp = parse_fail(ran)
    if rp:
        ran_pair = make_pair(*rp[0])
        check(
            "# ran on does not bind USER/HOME",
            "USER" not in ran_pair.expected.require
            and "HOME" not in ran_pair.expected.require
            and "USER" not in ran_pair.actual.require
            and "HOME" not in ran_pair.actual.require,
            str(ran_pair.expected.require) + str(ran_pair.actual.require),
        )

    if vvp:
        vv_pair = make_pair(*vvp[0])
        check(
            "vv expected tmp OPEN",
            vv_pair.expected.status == "OPEN",
            vv_pair.expected.status + str(vv_pair.expected.require),
        )
        check(
            "vv actual alice HOME",
            vv_pair.actual.require.get("HOME") == "/Users/alice",
            str(vv_pair.actual.require),
        )
        check(
            "vv pair EXPECTED-OPEN vs ACTUAL-BOUND",
            vv_pair.label == "EXPECTED-OPEN vs ACTUAL-BOUND",
            vv_pair.label,
        )

    jtmp = "expected:</tmp/x> but was:</Users/alice/proj>\n"
    jt = parse_fail(jtmp)
    if jt:
        jtp = make_pair(*jt[0])
        check(
            "junit tmp vs alice pair",
            jtp.label == "EXPECTED-OPEN vs ACTUAL-BOUND",
            jtp.label,
        )

    check("live axes nonempty", len(live) >= 3, str(live))

    ar = make_pair(*pairs[0]) if pairs else None
    if ar:
        role = host_role(ar, live)
        if live.get("HOME") == "/Users/alice":
            check("alice-vs-runner host EXPECTED on alice", role == "EXPECTED", role)
        elif live.get("HOME") == "/home/runner":
            check("alice-vs-runner host ACTUAL on runner", role == "ACTUAL", role)
        else:
            check("alice-vs-runner host NEITHER here", role == "NEITHER", role)

    live_dump = f"E   - /tmp/x\nE   + {live['HOME']}/proj\n"
    lp = parse_fail(live_dump)
    check("parse live actual dump", len(lp) >= 1, str(lp))
    if lp:
        live_pair = make_pair(*lp[0])
        check(
            "dump actual=$HOME → host ACTUAL",
            host_role(live_pair, live) == "ACTUAL",
            host_role(live_pair, live) + " " + live_pair.label,
        )
        check(
            "live actual dump expected OPEN",
            live_pair.expected.status == "OPEN",
            live_pair.label,
        )

    nf_src = (
        "import os\n"
        "def test_home():\n"
        "    home = os.environ['HOME']\n"
        "    expected = home\n"
        "    got = '/tmp/x'\n"
        "    assert got == expected\n"
    )
    nfo = infer(nf_src, "tests/test_home.py")
    check("name-follow env HOME is OPEN (no literal)", nfo.status == "OPEN", nfo.status)
    check(
        "name-follow assert expected is environ HOME",
        any(
            w.kind == "assert" and "HOME" in w.expected and "environ" in w.expected
            for w in nfo.windows
        ),
        str([(w.form, w.expected, w.actual, w.proxy) for w in nfo.windows]),
    )
    check(
        "name-follow records the proxy chain",
        any(w.proxy and "expected" in w.proxy and "home" in w.proxy for w in nfo.windows),
        str([w.proxy for w in nfo.windows]),
    )

    nfl_src = (
        "def test_home():\n"
        "    home = '/Users/annenpolka'\n"
        "    expected = home\n"
        "    assert got == expected\n"
    )
    nfl = infer(nfl_src, "tests/test_home.py")
    check(
        "name-follow literal is BOUND",
        nfl.status == "BOUND" and nfl.require.get("HOME") == "/Users/annenpolka",
        nfl.status + str(nfl.require),
    )

    dump_diff = (
        "    assert got == expected\n"
        "E   AssertionError: assert '/tmp/x' == '/Users/annenpolka'\n"
        "E   - /Users/annenpolka\n"
        "E   + /tmp/x\n"
    )
    ddp = parse_fail(dump_diff)
    check("name-follow E+/- is one pair (not two inverted)", len(ddp) == 1, str(ddp))
    if ddp:
        dpr = make_pair(*ddp[0])
        check(
            "name-follow pair EXPECTED-BOUND vs ACTUAL-OPEN",
            dpr.label == "EXPECTED-BOUND vs ACTUAL-OPEN",
            dpr.label,
        )
        check(
            "name-follow expected HOME is the bound path",
            dpr.expected.require.get("HOME") == "/Users/annenpolka",
            str(dpr.expected.require),
        )

    dump_vv = (
        "    assert got == expected\n"
        "E   AssertionError: assert '/tmp/x' == '/Users/annenpolka'\n"
        "E    +  where got = '/tmp/x'\n"
        "E    +    and expected = home\n"
    )
    vvn = parse_fail(dump_vv)
    check("name-follow -vv is one pair (home follows)", len(vvn) == 1, str(vvn))
    if vvn:
        vpr = make_pair(*vvn[0])
        check(
            "name-follow -vv expected is the bound path",
            vpr.expected.require.get("HOME") == "/Users/annenpolka",
            vpr.label + " " + vpr.expected_raw + " proxy=" + vpr.proxy,
        )

    dump_src = (
        "    home = os.environ['HOME']\n"
        "    expected = home\n"
        "    assert got == expected\n"
        "E   AssertionError: assert '/tmp/x' == expected\n"
        "E   - /Users/annenpolka\n"
        "E   + /tmp/x\n"
    )
    dsp = parse_fail(dump_src)
    check("name-follow dump-src is one pair", len(dsp) == 1, str(dsp))
    if dsp:
        spr = make_pair(*dsp[0])
        check(
            "name-follow dump-src expected is the bound path",
            spr.expected.require.get("HOME") == "/Users/annenpolka"
            and spr.label == "EXPECTED-BOUND vs ACTUAL-OPEN",
            spr.label + " " + spr.expected_raw + " proxy=" + spr.proxy,
        )
        check(
            "name-follow dump-src proxy names the chain",
            "home" in spr.proxy or "environ" in spr.expected_raw or "annenpolka" in spr.expected_raw,
            spr.proxy,
        )

    dump_norepr = (
        "    assert got == expected\n"
        "E   AssertionError: assert '/tmp/x' == expected\n"
    )
    nrp = parse_fail(dump_norepr)
    check("name-follow no-repr is one pair", len(nrp) == 1, str(nrp))
    if nrp:
        check(
            "name-follow no-repr keeps left as actual",
            _norm_fail_val(nrp[0][2]) == "/tmp/x",
            str(nrp),
        )

    host_src = "assert os.environ['HOSTNAME'] == 'ci-mac-7'\n"
    ho = infer(host_src, "tests/test_host.py")
    check("HOST getenv is not a hard visa", "HOST" not in ho.require, str(ho.require))
    check(
        "HOST getenv is OPEN + soft",
        ho.status == "OPEN" and ho.soft.get("HOST") == "ci-mac-7",
        ho.status + str(ho.soft),
    )

    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="proxy",
        description=(
            "Follow the expected name to its bound value, then pair the "
            "expected-literal oath with the actual-side oath. One pair per "
            "assertion, not two inverted PM/diff pairs. Comments are not oaths."
        ),
    )
    p.add_argument("paths", nargs="*", help="test / golden files (or a directory with --scan)")
    p.add_argument("-C", metavar="DIR", default=None, help="working directory / scan root")
    p.add_argument("--scan", action="store_true", help="walk a tree for test/golden/snapshot files")
    p.add_argument("--all", action="store_true", help="with --scan, consider every text file")
    p.add_argument(
        "--from-fail",
        action="store_true",
        help="parse expected/actual from stdin; pair both oaths (pytest -vv / XCTest / junit)",
    )
    p.add_argument(
        "--side",
        choices=("expected", "actual", "both"),
        default="expected",
        help="with --from-fail, which side --apply/--emit talks about (default: expected)",
    )
    p.add_argument("--match", action="store_true", help="compare each oath against this host")
    p.add_argument(
        "--apply",
        action="store_true",
        help="exit 0 if this host may apply the chosen side, 1 to skip, 2 if UNSAT",
    )
    p.add_argument(
        "--emit",
        choices=("shell", "pytest", "gha"),
        help="print only a predicate: shell apply / pytest skipif / GHA runs-on (coarse)",
    )
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--porcelain", action="store_true", help="stable TSV")
    p.add_argument("--self-test", action="store_true", help="run built-in tests")
    p.add_argument("--version", action="version", version=f"proxy {VERSION}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(list(sys.argv[1:] if argv is None else argv))

    if args.self_test:
        return self_test()

    if args.C:
        os.chdir(args.C)

    if args.from_fail:
        text = sys.stdin.read()
        raw_pairs = parse_fail(text)
        if not raw_pairs:
            v = infer(text, "-")
            if args.match or args.apply:
                v = match_oath(v)
            return report([v], args)
        pairs: list[Pair] = []
        live = live_axes()
        for item in raw_pairs:
            pr = make_pair(*item)
            pr.host = host_role(pr, live)
            if args.match or args.apply:
                pr.expected = match_oath(pr.expected, live)
                pr.actual = match_oath(pr.actual, live)
            pairs.append(pr)
        return report_pairs(pairs, args)

    files: list[Path] = []
    if args.scan:
        root = Path(args.paths[0]) if args.paths else Path(".")
        files = list(iter_oracle_files(root, all_files=args.all))
        if not files:
            print("proxy: no oracle-like files", file=sys.stderr)
            return 1
    else:
        for p in args.paths:
            if p == "-":
                text = sys.stdin.read()
                v = infer(text, "-")
                if args.match or args.apply:
                    v = match_oath(v)
                return report([v], args)
            files.append(Path(p))

    if not files:
        build_parser().print_help()
        return 2

    oaths = []
    for path in files:
        if path.is_dir() and not args.scan:
            print(f"proxy: {path} is a directory (use --scan)", file=sys.stderr)
            return 2
        v = infer_file(path)
        if v is None:
            print(f"proxy: skip binary/unreadable {path}", file=sys.stderr)
            continue
        if args.match or args.apply:
            v = match_oath(v)
        oaths.append(v)
    if not oaths:
        print("proxy: no readable oracles", file=sys.stderr)
        return 1
    return report(oaths, args)


if __name__ == "__main__":
    sys.exit(main())
