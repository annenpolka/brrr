#!/usr/bin/env python3
"""writ — splice tests onto old production, then oath the splice failure.

The object is LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-BOUND.
Skip is not a lock. Comments are not oaths. Not a fourth cinch.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.2.0"

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".writ-tmp",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "dist",
    "build",
    ".build",
    "DerivedData",
    ".idea",
    ".vscode",
}
LINK_DIR_NAMES = {
    "node_modules",
    "target",
    ".venv",
    "venv",
    "vendor",
    ".build",
    "DerivedData",
}
TEST_DIR_NAMES = {
    "test",
    "tests",
    "spec",
    "specs",
    "testing",
    "__tests__",
}
FIXTURE_DIR_NAMES = {
    "fixtures",
    "golden",
    "testdata",
    "test_data",
    "snapshots",
    "__snapshots__",
    "expected",
}
SOURCE_EXTENSIONS = {
    ".py",
    ".pyi",
    ".rs",
    ".go",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".cxx",
    ".hpp",
    ".m",
    ".mm",
    ".swift",
    ".rb",
    ".java",
    ".kt",
    ".kts",
    ".cs",
    ".php",
    ".scala",
    ".hs",
    ".lua",
    ".sh",
    ".bash",
    ".zsh",
    ".sql",
    ".proto",
    ".vue",
    ".svelte",
}
TEST_FILE_RE = re.compile(
    r"""
    (
        ^test\.py$
      | ^tests\.py$
      | ^test_.*\.py$
      | ^test_.*\.rs$
      | .*_test\.py$
      | .*_test\.go$
      | .*_test\.rs$
      | .*_tests?\.rb$
      | .*\.test\.(js|jsx|ts|tsx|mjs|cjs)$
      | .*\.spec\.(js|jsx|ts|tsx|mjs|cjs)$
      | ^conftest\.py$
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)
FAIL_LINE_RE = re.compile(r"^(FAIL|ERROR|FAILED):\s+(\S+)", re.MULTILINE)
PYTEST_FAILED_RE = re.compile(r"^FAILED\s+(\S+::\S+|\S+\.py\S*)", re.MULTILINE)
CARGO_FAILED_RE = re.compile(r"^test\s+(\S+)\s+\.\.\.\s+FAILED", re.MULTILINE)
IMPORTISH_RE = re.compile(
    r"(ImportError|ModuleNotFoundError|SyntaxError|cannot find (crate|value|type|module)|"
    r"error: could not compile|unresolved import|cannot find type)",
    re.IGNORECASE,
)
EMPTY_RE = re.compile(
    r"(Ran 0 tests|NO TESTS RAN|collected 0 items|no tests ran)",
    re.IGNORECASE,
)
SKIPPED_OUT_RE = re.compile(r"\b(skipped|SKIPPED)\b")

PATH_RE = re.compile(
    r"(?:"
    r"/Users/[^/\s'\"\\`]+(?: [^/\s'\"\\`]+)*(?:/[^/\s'\"\\`]+)*"
    r"|/home/[^/\s'\"\\`]+(?: [^/\s'\"\\`]+)*(?:/[^/\s'\"\\`]+)*"
    r"|/tmp/[^/\s'\"\\`]+"
    r"|/private/var/folders/[^/\s'\"\\]+(?:/[^/\s'\"\\]+)*"
    r"|/var/folders/[^/\s'\"\\]+(?:/[^/\s'\"\\]+)*"
    r")"
)
ENV_TIED_RE = re.compile(
    r"(?ix)os\.environ|getenv|std::env|env::var|Path\.home|expanduser|"
    r"getpass|\$\{?(?:HOME|USER|LOGNAME|HOSTNAME)\}?|"
    r"platform\.system|sys\.platform|uname|gethostname|whoami|getuser"
)
GITHUB_RE = re.compile(r"github\.com|gist\.github|GitHub\s+-", re.I)

PYTEST_PM_RE = re.compile(
    r"^E\s+(?:AssertionError:\s*)?(?:assert\s+)?(?P<a>.*) (?:==|!=) (?P<b>.*)$"
)
PYTEST_DIFF_MINUS = re.compile(r"^E\s+-\s+(?P<v>.*)$")
PYTEST_DIFF_PLUS = re.compile(r"^E\s+\+\s+(?P<v>.*)$")
UNITTEST_RE = re.compile(r"AssertionError:\s*(?P<a>.+?) (?:!=|==) (?P<b>.+)$")
ASSERT_LINE_RE = re.compile(r"^AssertionError:\s*(?:assert\s+)?(?P<a>.+?) (?:==|!=) (?P<b>.+)$")
CARGO_LEFT_RE = re.compile(r"^\s*left:\s*(?P<v>.+)$")
CARGO_RIGHT_RE = re.compile(r"^\s*right:\s*(?P<v>.+)$")
SWIFT_RE = re.compile(
    r"XCTAssert(?:Equal|NotEqual)(?:\s+failed:?\s*:?)?\s*"
    r"(?:\((?P<qa>[^)]+)\)|(?P<a>.+?)) "
    r"is not equal to (?:\((?P<qb>[^)]+)\)|(?P<b>.+))$"
)
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
ASSERT_EQUAL_RE = re.compile(
    r"(?:self\.)?assertEqual\s*\(\s*(?P<a>.+?)\s*,\s*(?P<b>.+)\s*\)\s*$"
)
ASSERT_CMP_RE = re.compile(r"^assert\s+(?P<a>.+?)\s*==\s*(?P<b>.+?)\s*$")
SKIP_UNLESS_RE = re.compile(
    r"@(?:unittest\.)?skipUnless\s*\((?P<pred>.*),\s*(?P<msg>.*)\)\s*$"
)
SKIP_IF_RE = re.compile(
    r"@(?:(?:unittest\.)?skipIf|pytest\.mark\.skipif)\s*\((?P<pred>[^,\)]+)"
)
TEST_DEF_RE = re.compile(r"^def\s+(test_\w+)")

STOP_ID = {
    "true",
    "false",
    "none",
    "null",
    "test",
    "user",
    "home",
    "path",
    "root",
    "local",
    "localhost",
    "ok",
    "src",
    "lib",
    "tmp",
    "dev",
}
PAYLOAD_IDENTS = {
    "user",
    "john",
    "jane",
    "john doe",
    "jane doe",
    "ubuntu",
    "nobody",
    "testuser",
    "foo",
    "bar",
    "baz",
}
PORTABLE_STATUS = {"OPEN", "SPEC", "FIXTURE"}


@dataclass
class RunResult:
    exit_code: int
    seconds: float
    output: str
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


@dataclass
class FilePlan:
    path: str
    role: str
    source: str


@dataclass
class Oath:
    status: str
    raw: str = ""
    require: dict[str, str] = field(default_factory=dict)
    match: str = ""
    misses: list[dict[str, str]] = field(default_factory=list)
    side: str = ""


@dataclass
class Pair:
    kind: str
    expected_raw: str
    actual_raw: str
    source: str
    expected: Oath
    actual: Oath
    host: str = ""
    legal: list[str] = field(default_factory=list)
    apply: str = ""
    fixture: str = ""
    witness: str = ""

    @property
    def label(self) -> str:
        return f"EXPECTED-{self.expected.status} vs ACTUAL-{self.actual.status}"

    @property
    def lock(self) -> str:
        return (
            f"LOCKED-and-EXPECTED-{self.expected.status} "
            f"vs LOCKED-and-ACTUAL-{self.actual.status}"
        )


@dataclass
class Report:
    status: str
    base: str
    new: str
    cmd: list[str]
    production_changed: list[str]
    tests_kept: list[str]
    pair: Pair | None = None
    pairs: list[Pair] = field(default_factory=list)
    lock: str = ""
    host: str = ""
    legal: list[str] = field(default_factory=list)
    apply: str = ""
    fixture: str = ""
    witnesses: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    new_run: RunResult | None = None
    splice_run: RunResult | None = None
    plan: list[FilePlan] = field(default_factory=list)


# ---------------------------------------------------------------------------
# git / roles
# ---------------------------------------------------------------------------


def git(args: list[str], cwd: Path, check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=kwargs.pop("text", True),
        **kwargs,
    )


def git_bytes(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, check=False, capture_output=True)


def repo_root(start: Path) -> Path:
    proc = git(["rev-parse", "--show-toplevel"], cwd=start, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"writ: not a git repository: {start}")
    return Path(proc.stdout.strip()).resolve()


def rev_parse(repo: Path, ref: str) -> str:
    proc = git(["rev-parse", "--verify", ref], cwd=repo, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"writ: unknown revision {ref!r}")
    return proc.stdout.strip()


def list_tree_files(repo: Path, ref: str) -> list[str]:
    proc = git(["ls-tree", "-r", "--name-only", ref], cwd=repo)
    return [ln for ln in proc.stdout.splitlines() if ln]


def list_worktree_files(repo: Path) -> list[str]:
    proc = git(["ls-files", "-co", "--exclude-standard"], cwd=repo)
    return [ln for ln in proc.stdout.splitlines() if ln]


def git_show(repo: Path, ref: str, path: str) -> bytes | None:
    proc = git_bytes(["show", f"{ref}:{path}"], cwd=repo)
    if proc.returncode != 0:
        return None
    return proc.stdout


def worktree_bytes(repo: Path, path: str) -> bytes | None:
    p = repo / path
    if not p.is_file():
        return None
    return p.read_bytes()


def is_test_path(path: str, extra_keep: list[re.Pattern] | None = None) -> bool:
    posix = path.replace("\\", "/")
    if extra_keep:
        for rx in extra_keep:
            if rx.search(posix):
                return True
    parts = [p.lower() for p in Path(posix).parts]
    if any(p in TEST_DIR_NAMES or p in FIXTURE_DIR_NAMES for p in parts):
        return True
    name = Path(posix).name
    if TEST_FILE_RE.match(name):
        return True
    lower = name.lower()
    if lower.endswith((".expected.json", ".snap", ".snapshot")):
        return True
    return False


def is_source_path(path: str) -> bool:
    ext = Path(path.replace("\\", "/")).suffix.lower()
    if ext in SOURCE_EXTENSIONS:
        return True
    name = Path(path).name.lower()
    return name in {"justfile", "makefile", "dockerfile", "cmakelists.txt"}


def path_role(path: str, extra_keep: list[re.Pattern] | None = None) -> str:
    if is_test_path(path, extra_keep):
        return "test"
    if is_source_path(path):
        return "production"
    return "other"


def coordinator_lab(repo: Path) -> bool:
    """Parent experiment board copied into every worktree is not this tool's production."""
    return (repo / "lab" / "PROTOCOL.md").is_file()


def should_skip_path(path: str, *, skip_lab: bool = False) -> bool:
    parts = Path(path.replace("\\", "/")).parts
    if any(p in SKIP_DIR_NAMES for p in parts):
        return True
    if skip_lab and parts and parts[0] == "lab":
        return True
    return False


def detect_cmd(root: Path) -> list[str]:
    if (root / "Cargo.toml").exists() and shutil.which("cargo"):
        return ["cargo", "test", "--offline", "--quiet"]
    pkg = root / "package.json"
    if pkg.exists():
        try:
            text = pkg.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        if "vitest" in text:
            return ["npx", "--no-install", "vitest", "run"]
        if "jest" in text:
            return ["npx", "--no-install", "jest", "--ci"]
    if (root / "Package.swift").exists() and shutil.which("swift"):
        return ["swift", "test"]
    if (root / "pytest.ini").exists() or (root / "conftest.py").exists():
        return [sys.executable, "-m", "pytest", "-q"]
    for name in ("tests", "test", "Tests"):
        if (root / name).is_dir():
            return [sys.executable, "-m", "unittest", "discover", "-s", name, "-q"]
    return [sys.executable, "-m", "unittest", "discover", "-q"]


def parse_witnesses(output: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(name: str) -> None:
        name = name.strip().rstrip(":")
        if name and name not in seen:
            seen.add(name)
            found.append(name)

    for rx in (FAIL_LINE_RE, PYTEST_FAILED_RE, CARGO_FAILED_RE):
        for m in rx.finditer(output):
            add(m.group(m.lastindex or 1))
    return found


def new_bytes(repo: Path, new_ref: str | None, path: str) -> bytes | None:
    if new_ref is None:
        return worktree_bytes(repo, path)
    return git_show(repo, new_ref, path)


def list_new_paths(repo: Path, new_ref: str | None) -> list[str]:
    if new_ref is None:
        return list_worktree_files(repo)
    return list_tree_files(repo, new_ref)


def union_paths(repo: Path, base: str, new_ref: str | None) -> list[str]:
    s = set(list_tree_files(repo, base)) | set(list_new_paths(repo, new_ref))
    skip_lab = coordinator_lab(repo)
    return sorted(p for p in s if not should_skip_path(p, skip_lab=skip_lab))


def production_changed(
    repo: Path, base: str, new_ref: str | None, keep: list[re.Pattern]
) -> list[str]:
    changed: list[str] = []
    for path in union_paths(repo, base, new_ref):
        if path_role(path, keep) != "production":
            continue
        a = git_show(repo, base, path)
        b = new_bytes(repo, new_ref, path)
        if a != b:
            changed.append(path)
    return changed


def tests_in(paths: list[str], keep: list[re.Pattern]) -> list[str]:
    return [p for p in paths if is_test_path(p, keep)]


def write_bytes(dest: Path, path: str, data: bytes) -> None:
    p = dest / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def link_existing_deps(repo: Path, dest: Path) -> list[FilePlan]:
    plans: list[FilePlan] = []
    for name in sorted(LINK_DIR_NAMES):
        src = repo / name
        if src.exists():
            target = dest / name
            if not target.exists():
                target.symlink_to(src)
                plans.append(FilePlan(name, "link", "symlink"))
    return plans


def materialize(
    repo: Path,
    dest: Path,
    base: str,
    new_ref: str | None,
    keep: list[re.Pattern],
    overlay: str,
) -> list[FilePlan]:
    """overlay 'none' = NEW tree; 'all' = tests@NEW, production@base."""
    plans: list[FilePlan] = []
    new_paths = set(list_new_paths(repo, new_ref))
    base_paths = set(list_tree_files(repo, base))
    skip_lab = coordinator_lab(repo)
    for path in sorted((new_paths | base_paths) - {".git"}):
        if should_skip_path(path, skip_lab=skip_lab):
            continue
        role = path_role(path, keep)
        if overlay == "none" or role != "production":
            data = new_bytes(repo, new_ref, path)
            if data is None:
                continue
            write_bytes(dest, path, data)
            plans.append(FilePlan(path, role, "new"))
            continue
        data = git_show(repo, base, path)
        if data is None:
            plans.append(FilePlan(path, "production", "deleted"))
            continue
        write_bytes(dest, path, data)
        plans.append(FilePlan(path, "production", "base"))
    plans.extend(link_existing_deps(repo, dest))
    return plans


def extra_env_for(repo: Path, dest: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    target = repo / "target"
    if target.exists():
        env["CARGO_TARGET_DIR"] = str(target)
    return env


def run_cmd(
    cmd: list[str], cwd: Path, timeout: float, extra_env: dict[str, str] | None = None
) -> RunResult:
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
    if extra_env:
        env.update(extra_env)
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout
        )
        seconds = time.monotonic() - t0
        output = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        return RunResult(proc.returncode, seconds, output, timed_out=False)
    except FileNotFoundError as e:
        return RunResult(127, time.monotonic() - t0, str(e), timed_out=False)
    except subprocess.TimeoutExpired as e:
        seconds = time.monotonic() - t0
        out = ""
        if e.stdout:
            out += e.stdout if isinstance(e.stdout, str) else e.stdout.decode("utf-8", "replace")
        if e.stderr:
            out += "\n" + (
                e.stderr if isinstance(e.stderr, str) else e.stderr.decode("utf-8", "replace")
            )
        out += f"\n[writ: timed out after {timeout}s]"
        return RunResult(124, seconds, out, timed_out=True)


# ---------------------------------------------------------------------------
# oath of a fail literal (comments never bind)
# ---------------------------------------------------------------------------


def _strip_quotes(s: str) -> str:
    s = (s or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"`":
        return s[1:-1]
    return s


def _usable_id(value: str) -> bool:
    v = value.strip()
    if len(v) < 2:
        return False
    if v.lower() in STOP_ID:
        return False
    if v.isdigit() and len(v) < 6:
        return False
    return True


def _ident_tail(value: str) -> str:
    return value.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def is_payload_home(home: str) -> bool:
    ident = _ident_tail(home)
    return ident.lower() in PAYLOAD_IDENTS or " " in ident


def is_github_fixture(tok: str) -> bool:
    return bool(GITHUB_RE.search(tok or ""))


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
    n = (p or "").strip().replace("\\", "/")
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
    if "/var/folders/" in n:
        out["platform"] = "Darwin"
        out["layout"] = "darwin-scratch"
        return out
    if n.startswith("/tmp/"):
        out["tmp"] = "unix"
        return out
    return out


def is_env_tied(s: str) -> bool:
    return bool(ENV_TIED_RE.search(s or ""))


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


def oath_literal(raw: str, *, source: str = "", side: str = "") -> Oath:
    """Unary oath of one side of a failing assertion. Comments are not oaths."""
    text = _strip_quotes(raw or "")
    stripped = text.lstrip()
    if stripped.startswith("#") and not stripped.startswith(("#expect", "#require")):
        return Oath(status="OPEN", raw=text, side=side)
    if not text:
        return Oath(status="OPEN", raw=text, side=side)
    if is_github_fixture(text):
        return Oath(status="FIXTURE", raw=text, side=side)

    derived = derive_from_path(text)
    if derived.get("tmp") and set(derived) == {"tmp"}:
        return Oath(status="OPEN", raw=text, side=side)

    require: dict[str, str] = {}
    for axis in ("HOME", "USER", "platform", "layout", "CI"):
        if axis in derived:
            require[axis] = derived[axis]

    if require.get("HOME") and is_payload_home(require["HOME"]) and not is_env_tied(source):
        return Oath(status="SPEC", raw=text, side=side)

    if require:
        return Oath(status="BOUND", raw=text, require=require, side=side)

    if is_env_tied(source) and _usable_id(text) and "/" not in text:
        return Oath(status="BOUND", raw=text, require={"USER": text}, side=side)

    m = PATH_RE.search(text)
    if m:
        inner = oath_literal(m.group(0), source=source, side=side)
        inner.raw = text
        return inner
    return Oath(status="OPEN", raw=text, side=side)


def match_oath(oath: Oath, live: dict[str, str] | None = None) -> Oath:
    live = live_axes() if live is None else live
    out = Oath(
        status=oath.status,
        raw=oath.raw,
        require=dict(oath.require),
        side=oath.side,
    )
    if out.status in PORTABLE_STATUS:
        out.match = "MATCH"
        return out
    if out.status == "UNSAT":
        out.match = "MISS"
        out.misses = [{"axis": "*", "want": "consistent", "have": "contradiction"}]
        return out
    misses: list[dict[str, str]] = []
    for axis, want in out.require.items():
        have = live.get(axis, "")
        if axis == "HOME":
            if have.rstrip("/\\") != want.rstrip("/\\"):
                misses.append({"axis": axis, "want": want, "have": have or "(unset)"})
            continue
        if axis == "layout":
            continue
        if have != want:
            misses.append({"axis": axis, "want": want, "have": have or "(unset)"})
    out.match = "MISS" if misses else "MATCH"
    out.misses = misses
    return out


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
    if not parts:
        layout = require.get("layout", "")
        if layout == "macos-home":
            parts.append('[ "$(uname -s)" = Darwin ]')
        elif layout == "linux-home":
            parts.append('[ "$(uname -s)" = Linux ]')
        else:
            return "true"
    return " && ".join(parts)


def host_role(pair: Pair, live: dict[str, str] | None = None) -> str:
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


def legal_applies(pair: Pair, live: dict[str, str] | None = None) -> list[str]:
    """OR, never AND. OPEN expected always applies. Actual only if this host."""
    live = live_axes() if live is None else live
    e = match_oath(pair.expected, live)
    a = match_oath(pair.actual, live)
    legal: list[str] = []
    if e.status in PORTABLE_STATUS:
        legal.append("OPEN")
    elif e.status == "BOUND" and e.match == "MATCH":
        legal.append("EXPECTED")
    if a.status == "BOUND" and a.match == "MATCH":
        legal.append("ACTUAL")
    return legal


def apply_verdict(pair: Pair, live: dict[str, str] | None = None) -> tuple[str, int]:
    if pair.expected.status == "UNSAT":
        return "UNSAT", 2
    legal = pair.legal or legal_applies(pair, live)
    if legal:
        return "APPLY", 0
    return "SKIP", 1


def fixture_predicate(pair: Pair) -> str | None:
    legal = pair.legal or legal_applies(pair)
    if "ACTUAL" not in legal:
        return None
    if pair.actual.status == "UNSAT":
        return None
    return emit_shell(pair.actual.require)


def bind_host(pair: Pair, live: dict[str, str] | None = None) -> Pair:
    live = live_axes() if live is None else live
    pair.expected = match_oath(pair.expected, live)
    pair.actual = match_oath(pair.actual, live)
    pair.host = host_role(pair, live)
    pair.legal = legal_applies(pair, live)
    pair.apply = apply_verdict(pair, live)[0]
    pair.fixture = fixture_predicate(pair) or ""
    return pair


def make_pair(kind: str, expected: str, actual: str, source: str = "", witness: str = "") -> Pair:
    return Pair(
        kind=kind,
        expected_raw=expected,
        actual_raw=actual,
        source=source,
        expected=oath_literal(expected, source=source, side="expected"),
        actual=oath_literal(actual, source=source, side="actual"),
        witness=witness,
    )


# ---------------------------------------------------------------------------
# fail dump parser — expected from the assertion slot, not dump order
# ---------------------------------------------------------------------------


def _looks_like_value(s: str) -> bool:
    s = (s or "").strip()
    if not s:
        return False
    if s[0] in "'\"`" or s[:2] in ('r"', "r'"):
        return True
    if s.startswith("/") or s.startswith("~"):
        return True
    if re.fullmatch(r"[A-Za-z0-9._-]+", s):
        return True
    return False


def _last_top_arg(call: str) -> str | None:
    """Last top-level argument of `assertEqual(got, expected)` — not a nested comma."""
    i = call.find("(")
    if i < 0:
        return None
    depth = 0
    last_comma = None
    end = None
    for j, ch in enumerate(call[i:], i):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                end = j
                break
        elif ch == "," and depth == 1:
            last_comma = j
    if last_comma is None or end is None:
        return None
    return call[last_comma + 1 : end].strip()


def _source_expected(src: str) -> str | None:
    s = (src or "").strip().rstrip("\\").strip()
    if "assertEqual" in s or "assertEquals" in s:
        arg = _last_top_arg(s)
        if arg is not None:
            return _strip_quotes(arg)
    m = ASSERT_CMP_RE.search(s)
    if m:
        return _strip_quotes(m.group("b"))
    if s.startswith("assert ") and "==" in s:
        rhs = s.split("==", 1)[1].strip()
        if _looks_like_value(rhs) or rhs[:1] in "'\"":
            return _strip_quotes(rhs)
    return None


def parse_fail(text: str) -> list[tuple[str, str, str, str]]:
    """(kind, expected, actual, source). Comments in a dump are not windows."""
    pairs: list[tuple[str, str, str, str]] = []
    minus: str | None = None
    left: str | None = None
    pending_assert = ""
    where_act: str | None = None
    where_exp: str | None = None

    def add(kind: str, exp: str, act: str, src: str = "") -> None:
        exp, act = _strip_quotes(exp), _strip_quotes(act)
        if not exp and not act:
            return
        src = src or pending_assert
        src_exp = _source_expected(src)
        if src_exp:
            exp = src_exp
        if any(p[1] == exp and p[2] == act for p in pairs):
            return
        pairs.append((kind, exp, act, src))

    def flush_vv() -> None:
        nonlocal where_act, where_exp
        if where_act is None or where_exp is None:
            return
        exp, act = _strip_quotes(where_exp), _strip_quotes(where_act)
        pairs[:] = [p for p in pairs if {p[1], p[2]} != {exp, act}]
        add("pytest-vv", exp, act)
        where_act = where_exp = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if stripped.startswith("//") or (
            stripped.startswith("#")
            and not stripped.startswith("#expect")
            and not stripped.startswith("#require")
        ):
            continue
        if stripped.startswith("assert ") and ("==" in stripped or "!=" in stripped):
            pending_assert = stripped
        if "assertEqual" in stripped and "AssertionError" not in stripped:
            pending_assert = stripped.rstrip("\\").strip()
            if pending_assert.endswith(","):
                pending_assert = pending_assert[:-1]

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
            add("pytest", minus, m.group("v"))
            minus = None
            continue

        m = PYTEST_PM_RE.match(line)
        if m:
            src_exp = _source_expected(pending_assert)
            left_v = _strip_quotes(m.group("a"))
            right_v = _strip_quotes(m.group("b"))
            if src_exp:
                actual_v = right_v if left_v == src_exp else left_v
                if _looks_like_value(actual_v) or actual_v.startswith("/"):
                    add("pytest-src", src_exp, actual_v)
                continue
            add("pytest", left_v, right_v)
            continue

        m = UNITTEST_RE.search(line) or ASSERT_LINE_RE.search(line)
        if m:
            a, b = _strip_quotes(m.group("a")), _strip_quotes(m.group("b"))
            src_exp = _source_expected(pending_assert)
            if src_exp:
                actual_v = a if b == src_exp or src_exp in b else (b if a == src_exp or src_exp in a else a)
                add("unittest", src_exp, actual_v)
            else:
                # unittest assertEqual(got, expected) prints `got != expected`
                add("unittest", b, a)
            continue

        m = CARGO_LEFT_RE.match(line)
        if m:
            left = m.group("v")
            continue
        m = CARGO_RIGHT_RE.match(line)
        if m and left is not None:
            add("cargo", m.group("v"), left)
            left = None
            continue

        m = SWIFT_RE.search(line)
        if m:
            act = m.group("qa") or m.group("a") or ""
            exp = m.group("qb") or m.group("b") or ""
            add("xctest", exp, act)
            continue

    flush_vv()
    return pairs


def pairs_from_output(output: str, witnesses: list[str]) -> list[Pair]:
    raw = parse_fail(output)
    out: list[Pair] = []
    wit = witnesses[0] if witnesses else ""
    for kind, exp, act, src in raw:
        p = make_pair(kind, exp, act, src, witness=wit)
        out.append(p)
    return out


# ---------------------------------------------------------------------------
# skip is not a lock — comments are not skip oaths
# ---------------------------------------------------------------------------


def _pred_oath(pred: str) -> Oath | None:
    for hit in PATH_RE.findall(pred):
        o = oath_literal(hit, source=pred)
        if o.status == "BOUND":
            return o
    m = re.search(
        r"""(?:USER(?:NAME)?|LOGNAME)\s*['\"]?\s*\)?\s*==\s*['\"]([^'\"]+)['\"]""",
        pred,
    )
    if m:
        return oath_literal(m.group(1), source=pred)
    m = re.search(
        r"""(?:platform|uname).*==\s*['\"]([^'\"]+)['\"]""",
        pred,
        re.I,
    )
    if m:
        plat = {"darwin": "Darwin", "linux": "Linux", "win32": "Windows"}.get(
            m.group(1).lower(), m.group(1)
        )
        return Oath(status="BOUND", raw=m.group(1), require={"platform": plat})
    return None


def skip_would_fire(kind: str, pred: str, live: dict[str, str] | None = None) -> bool:
    live = live_axes() if live is None else live
    o = _pred_oath(pred)
    if o is None or o.status != "BOUND":
        return False
    o = match_oath(o, live)
    if kind == "unless":
        return o.match == "MISS"
    return o.match == "MATCH"


def tests_would_skip(texts: list[str], live: dict[str, str] | None = None) -> bool:
    """True when every test_ is behind a machine skip that fires here.

    A `# @skipUnless` comment is not an oath and does not count.
    """
    live = live_axes() if live is None else live
    test_count = 0
    skip_fire = 0
    for text in texts:
        pending: str | None = None
        pending_kind = ""
        for raw in text.splitlines():
            s = raw.strip()
            if s.startswith("#") or s.startswith("//"):
                continue
            m = SKIP_UNLESS_RE.search(s)
            if m:
                pending, pending_kind = m.group("pred"), "unless"
                continue
            m = SKIP_IF_RE.search(s)
            if m:
                pending, pending_kind = m.group("pred"), "if"
                continue
            tm = TEST_DEF_RE.search(s)
            if tm:
                test_count += 1
                if pending and skip_would_fire(pending_kind, pending, live):
                    skip_fire += 1
                pending = None
                pending_kind = ""
                continue
            if s and not s.startswith("@"):
                pending = None
                pending_kind = ""
    if test_count == 0:
        return False
    return skip_fire == test_count and skip_fire > 0


def collect_test_texts(
    repo: Path, new_ref: str | None, keep: list[re.Pattern]
) -> list[str]:
    texts: list[str] = []
    for path in list_new_paths(repo, new_ref):
        if not is_test_path(path, keep):
            continue
        data = new_bytes(repo, new_ref, path)
        if data is None:
            continue
        try:
            texts.append(data.decode("utf-8"))
        except UnicodeDecodeError:
            continue
    return texts


# ---------------------------------------------------------------------------
# splice then oath
# ---------------------------------------------------------------------------


def is_empty_suite(run: RunResult) -> bool:
    if EMPTY_RE.search(run.output):
        return True
    if run.exit_code == 5 and "AssertionError" not in run.output and "FAIL:" not in run.output:
        return True
    return False


def is_unbuildable(output: str, witnesses: list[str]) -> bool:
    assertion = (
        "AssertionError" in output
        or "FAIL:" in output
        or any("::" in w for w in witnesses)
    )
    importish = bool(IMPORTISH_RE.search(output))
    compile_fail = bool(re.search(r"could not compile|error\[E\d+\]", output, re.IGNORECASE))
    if (importish or compile_fail) and not assertion:
        return True
    return False


def summarize_pairs(pairs: list[Pair], live: dict[str, str] | None = None) -> Pair | None:
    if not pairs:
        return None
    bound = [
        p
        for p in pairs
        if p.expected.status == "BOUND" or p.actual.status == "BOUND"
    ]
    chosen = bound[0] if bound else pairs[0]
    return bind_host(chosen, live)


def merge_legal(pairs: list[Pair], live: dict[str, str] | None = None) -> tuple[str, list[str], str, str]:
    live = live_axes() if live is None else live
    host_bits: set[str] = set()
    legal: list[str] = []
    for p in pairs:
        bind_host(p, live)
        if p.host in {"EXPECTED", "ACTUAL", "BOTH"}:
            if p.host == "BOTH":
                host_bits.update({"EXPECTED", "ACTUAL"})
            else:
                host_bits.add(p.host)
        for item in p.legal:
            if item not in legal:
                legal.append(item)
    if "EXPECTED" in host_bits and "ACTUAL" in host_bits:
        host = "BOTH"
    elif "EXPECTED" in host_bits:
        host = "EXPECTED"
    elif "ACTUAL" in host_bits:
        host = "ACTUAL"
    else:
        host = "NEITHER"
    apply = "APPLY" if legal else "SKIP"
    fixture = ""
    for p in pairs:
        if p.fixture:
            fixture = p.fixture
            break
    return host, legal, apply, fixture


def lock_label(pairs: list[Pair]) -> str:
    if not pairs:
        return ""
    exp = "OPEN"
    act = "OPEN"
    for p in pairs:
        if p.expected.status == "BOUND":
            exp = "BOUND"
        elif exp == "OPEN" and p.expected.status in {"SPEC", "FIXTURE", "UNSAT"}:
            exp = p.expected.status
        if p.actual.status == "BOUND":
            act = "BOUND"
        elif act == "OPEN" and p.actual.status in {"SPEC", "FIXTURE", "UNSAT"}:
            act = p.actual.status
    return f"LOCKED-and-EXPECTED-{exp} vs LOCKED-and-ACTUAL-{act}"


def run_writ(
    repo: Path,
    base: str,
    new_ref: str | None,
    cmd: list[str],
    timeout: float,
    keep: list[re.Pattern],
    live: dict[str, str] | None = None,
) -> Report:
    repo = repo.resolve()
    live = live_axes() if live is None else live
    base_sha = rev_parse(repo, base)
    changed = production_changed(repo, base, new_ref, keep)
    new_paths = list_new_paths(repo, new_ref)
    kept_tests = tests_in(new_paths, keep)
    new_label = "worktree" if new_ref is None else new_ref
    report = Report(
        status="CLEAN",
        base=f"{base} ({base_sha[:12]})",
        new=new_label,
        cmd=cmd,
        production_changed=changed,
        tests_kept=kept_tests,
    )

    tmp_root = Path(tempfile.mkdtemp(prefix="writ-"))
    new_dir = tmp_root / "new"
    splice_dir = tmp_root / "splice"
    new_dir.mkdir()
    splice_dir.mkdir()
    try:
        materialize(repo, new_dir, base, new_ref, keep, overlay="none")
        report.new_run = run_cmd(cmd, new_dir, timeout, extra_env_for(repo, new_dir))

        if is_empty_suite(report.new_run):
            report.status = "EMPTY"
            report.notes.append("test command collected no tests — not a lock")
            return report
        if not report.new_run.ok:
            report.status = "BROKEN"
            report.witnesses = parse_witnesses(report.new_run.output)
            report.notes.append("refusing to oath a NEW fail as a lock")
            return report
        if not changed:
            report.status = "CLEAN"
            report.notes.append("no production source files differ from base")
            return report

        plan = materialize(repo, splice_dir, base, new_ref, keep, overlay="all")
        report.plan = [p for p in plan if p.role != "link"]
        report.splice_run = run_cmd(cmd, splice_dir, timeout, extra_env_for(repo, splice_dir))

        if report.splice_run.timed_out:
            report.status = "TIMEOUT"
            report.notes.append("splice timed out — timeout is not a fail oath")
            return report
        if report.splice_run.ok:
            texts = collect_test_texts(repo, new_ref, keep)
            if tests_would_skip(texts, live) or (
                SKIPPED_OUT_RE.search(report.splice_run.output) and tests_would_skip(texts, live)
            ):
                report.status = "SKIP"
                report.notes.append("skip is not a lock")
                return report
            report.status = "LOOSE"
            report.notes.append("tests still pass on base production — no fail to oath")
            return report

        witnesses = parse_witnesses(report.splice_run.output)
        report.witnesses = witnesses
        if is_unbuildable(report.splice_run.output, witnesses):
            report.status = "UNBUILDABLE"
            report.notes.append("spliced tree cannot load/compile tests")
            added = [p for p in changed if git_show(repo, base, p) is None]
            if added:
                report.notes.append(
                    "new production absent at base: " + ", ".join(added[:8])
                )
                report.notes.append(
                    "UNBUILDABLE is not a fail pair — no expected/actual to oath"
                )
            return report

        pairs = [bind_host(p, live) for p in pairs_from_output(report.splice_run.output, witnesses)]
        report.pairs = pairs
        report.pair = summarize_pairs(pairs, live)
        report.lock = lock_label(pairs) if pairs else "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-OPEN"
        if not pairs:
            report.notes.append("LOCKED but no assertion pair parsed; treated as OPEN vs OPEN")
        host, legal, apply, fixture = merge_legal(pairs, live) if pairs else ("NEITHER", ["OPEN"], "APPLY", "")
        report.host = host
        report.legal = legal
        report.apply = apply
        report.fixture = fixture
        report.status = "LOCKED"
        return report
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


# ---------------------------------------------------------------------------
# format / CLI
# ---------------------------------------------------------------------------


def _short(s: str, n: int = 72) -> str:
    s = (s or "").replace("\n", " ")
    return s if len(s) <= n else s[: n - 3] + "..."


def format_human(report: Report, *, due: bool = False) -> str:
    lines: list[str] = []
    lock = report.lock or report.status
    lines.append(f"writ  base={report.base}  new={report.new}  status={report.status}")
    lines.append(f"cmd    {' '.join(report.cmd)}")
    n = len(report.production_changed)
    lines.append(f"prod   {n} path(s) differ from base (production source)")
    for p in report.production_changed[:12]:
        lines.append(f"         {p}")
    if n > 12:
        lines.append(f"         … {n - 12} more")
    if report.new_run:
        r = report.new_run
        state = "pass" if r.ok else ("timeout" if r.timed_out else f"fail({r.exit_code})")
        lines.append(f"NEW    {state:12} {r.seconds:.2f}s")
    if report.splice_run:
        r = report.splice_run
        state = "pass" if r.ok else ("timeout" if r.timed_out else f"fail({r.exit_code})")
        lines.append(f"SPLICE {state:12} {r.seconds:.2f}s   (tests@new, production@base)")
    lines.append("")
    if report.status == "LOCKED":
        p = report.pair
        lines.append(f"lock   {lock}")
        if p:
            lines.append(f"pair   {p.kind}  {p.label}")
            lines.append(f"  expected {_short(p.expected_raw)}  {p.expected.status}")
            if p.expected.require:
                req = " ".join(f"{k}={v}" for k, v in p.expected.require.items() if k != "layout")
                lines.append(f"           {req}  {p.expected.match}")
            lines.append(f"  actual   {_short(p.actual_raw)}  {p.actual.status}")
            if p.actual.require:
                req = " ".join(f"{k}={v}" for k, v in p.actual.require.items() if k != "layout")
                lines.append(f"           {req}  {p.actual.match}")
        gloss = {
            "EXPECTED": "this host is the oracle machine",
            "ACTUAL": "this host produced the fail",
            "BOTH": "this host holds both sides",
            "NEITHER": "this host is neither recorded machine",
        }.get(report.host, "")
        lines.append(f"  host     {report.host}" + (f"  {gloss}" if gloss else ""))
        legal_s = " ".join(report.legal) if report.legal else "(none)"
        lines.append(f"  legal    {legal_s}")
        apply_g = {
            "APPLY": "this host may apply",
            "SKIP": "skip — no legal side on this host",
            "UNSAT": "oracle cannot apply",
        }.get(report.apply, "")
        lines.append(f"  apply    {report.apply}" + (f"  {apply_g}" if apply_g else ""))
        if "OPEN" in report.legal:
            lines.append("           OPEN expected still applies (portable golden)")
        if "ACTUAL" in report.legal:
            lines.append("           ACTUAL-BOUND skip/fixture is legal")
        if report.fixture:
            lines.append(f"  fixture  {report.fixture}")
        if not any(p.expected.status == "BOUND" or p.actual.status == "BOUND" for p in report.pairs):
            lines.append("note: portable lock — neither side named a machine")
            lines.append("note: not a cinch — whole production was spliced, no hunk peel")
    elif report.status == "SKIP":
        lines.append("skip is not a lock")
    elif report.status == "LOOSE":
        lines.append("tests still pass on base production — the production diff has no alibi")
    elif report.status == "BROKEN":
        lines.append("tests already fail on the new tree — not a lock of production")
    elif report.status == "CLEAN":
        lines.append("no production files differ from base")
    elif report.status == "UNBUILDABLE":
        lines.append("spliced tree cannot load/compile tests")
    elif report.status == "EMPTY":
        lines.append("test command collected no tests — not a red suite")
    elif report.status == "TIMEOUT":
        lines.append("splice timed out — timeout is not a fail oath, not a cinch budget")
    if report.witnesses:
        lines.append("witnesses:")
        for w in report.witnesses[:20]:
            lines.append(f"  {w}")
    for note in report.notes:
        lines.append(f"note: {note}")
    if report.status == "BROKEN" and report.new_run and not report.new_run.ok:
        tail = report.new_run.output.strip().splitlines()[-12:]
        if tail:
            lines.append("new tail:")
            for ln in tail:
                lines.append(f"  {ln}")
    if report.splice_run and not report.splice_run.ok and report.status in {"LOCKED", "UNBUILDABLE"}:
        tail = report.splice_run.output.strip().splitlines()[-12:]
        if tail:
            lines.append("splice tail:")
            for ln in tail:
                lines.append(f"  {ln}")
    if due and report.status == "SKIP":
        lines.append("due: SKIP is not a lock, but it hid a machine skip")
    return "\n".join(lines) + "\n"


def oath_to_dict(o: Oath) -> dict:
    return {
        "status": o.status,
        "raw": o.raw,
        "require": o.require,
        "match": o.match,
        "misses": o.misses,
        "side": o.side,
    }


def pair_to_dict(p: Pair) -> dict:
    return {
        "kind": p.kind,
        "pair": p.label,
        "lock": p.lock,
        "expected_raw": p.expected_raw,
        "actual_raw": p.actual_raw,
        "source": p.source,
        "host": p.host,
        "legal": list(p.legal),
        "apply": p.apply,
        "fixture": p.fixture or None,
        "witness": p.witness,
        "expected": oath_to_dict(p.expected),
        "actual": oath_to_dict(p.actual),
    }


def report_to_json(report: Report) -> dict:
    def run(r: RunResult | None) -> dict | None:
        if r is None:
            return None
        return {
            "exit_code": r.exit_code,
            "seconds": round(r.seconds, 4),
            "timed_out": r.timed_out,
            "output_tail": r.output.strip().splitlines()[-30:],
        }

    return {
        "status": report.status,
        "lock": report.lock,
        "pair": report.pair.label if report.pair else None,
        "host": report.host,
        "legal": report.legal,
        "apply": report.apply,
        "fixture": report.fixture or None,
        "base": report.base,
        "new": report.new,
        "cmd": report.cmd,
        "production_changed": report.production_changed,
        "tests_kept": report.tests_kept,
        "witnesses": report.witnesses,
        "notes": report.notes,
        "pairs": [pair_to_dict(p) for p in report.pairs],
        "primary": pair_to_dict(report.pair) if report.pair else None,
        "new_run": run(report.new_run),
        "splice_run": run(report.splice_run),
        "wheat": [],
        "hunks": [],
    }


def clearance_empty(report: Report) -> bool:
    """Empty stdout: no BOUND side on a lock. Skip is not a lock."""
    if report.status in {"CLEAN", "LOOSE", "SKIP", "EMPTY"}:
        return True
    if report.status != "LOCKED":
        return False
    return not any(
        p.expected.status == "BOUND" or p.actual.status == "BOUND" for p in report.pairs
    )


def exit_code(report: Report, *, due: bool = False, apply: bool = False, fixture: bool = False) -> int:
    if fixture:
        return 0 if report.fixture else 1
    if apply:
        if report.status != "LOCKED":
            if report.status in {"CLEAN", "LOOSE", "SKIP"}:
                return 1
            return {
                "BROKEN": 3,
                "UNBUILDABLE": 4,
                "EMPTY": 5,
                "TIMEOUT": 6,
            }.get(report.status, 1)
        return {"APPLY": 0, "SKIP": 1, "UNSAT": 2}.get(report.apply, 1)
    if report.status == "LOCKED":
        bound = any(
            p.expected.status == "BOUND" or p.actual.status == "BOUND" for p in report.pairs
        )
        return 1 if bound else 0
    if report.status == "SKIP":
        return 1 if due else 0
    return {
        "CLEAN": 0,
        "LOOSE": 2,
        "BROKEN": 3,
        "UNBUILDABLE": 4,
        "EMPTY": 5,
        "TIMEOUT": 6,
    }.get(report.status, 1)


def cmd_to_list(cmd: str | list[str]) -> list[str]:
    if isinstance(cmd, list):
        return cmd
    return shlex.split(cmd)


# ---------------------------------------------------------------------------
# self-test (the object, without a repo)
# ---------------------------------------------------------------------------


def self_test() -> None:
    failures: list[str] = []

    def check(cond: bool, label: str) -> None:
        if not cond:
            failures.append(label)

    tmp = oath_literal("/tmp/x")
    check(tmp.status == "OPEN", " /tmp is OPEN")
    alice = oath_literal("/Users/alice/proj")
    check(alice.status == "BOUND" and alice.require.get("HOME") == "/Users/alice", "alice HOME BOUND")
    payload = oath_literal("/home/user/project")
    check(payload.status == "SPEC", "/home/user is SPEC")
    gh = oath_literal("GitHub - annenpolka/sitbone - Google Chrome")
    check(gh.status == "FIXTURE", "GitHub title FIXTURE")
    comment = oath_literal("# ran on alice")
    check(comment.status == "OPEN", "comment is not an oath")
    five = oath_literal("5")
    check(five.status == "OPEN", "number OPEN")

    dump = (
        "  File \"test_who.py\", line 6, in test_tmp\n"
        "    self.assertEqual(who.who(), \"/tmp/x\")\n"
        "AssertionError: '/Users/alice/Library' != '/tmp/x'\n"
    )
    parsed = parse_fail(dump)
    check(len(parsed) == 1, "unittest dump one pair")
    if parsed:
        kind, exp, act, _src = parsed[0]
        check(exp == "/tmp/x", f"expected /tmp/x got {exp!r}")
        check("alice" in act, f"actual alice got {act!r}")
        p = bind_host(make_pair(kind, exp, act, _src), live={"HOME": "/Users/me", "USER": "me", "platform": "Darwin", "layout": "macos-home"})
        check(p.expected.status == "OPEN", "splice expected OPEN")
        check(p.actual.status == "BOUND", "splice actual BOUND")
        check(p.lock == "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-BOUND", p.lock)
        check("OPEN" in p.legal, "OPEN expected still legal on NEITHER")
        check(p.host == "NEITHER", f"host NEITHER got {p.host}")
        check(p.apply == "APPLY", "OPEN expected APPLY even when actual is Alice")

    live_home = str(Path.home())
    p2 = bind_host(
        make_pair("unittest", "/tmp/x", live_home + "/proj", "self.assertEqual(who(), '/tmp/x')")
    )
    check(p2.expected.status == "OPEN", "live actual expected OPEN")
    check(p2.actual.status == "BOUND", "live actual BOUND")
    check(p2.host == "ACTUAL", f"host ACTUAL got {p2.host}")
    check("OPEN" in p2.legal and "ACTUAL" in p2.legal, "legal OPEN ACTUAL")
    check(p2.fixture != "", "fixture gated on ACTUAL")

    p3 = bind_host(
        make_pair("unittest", "/Users/alice/proj", "/tmp/x", 'self.assertEqual(who(), "/Users/alice/proj")'),
        live={"HOME": live_home, "USER": getpass.getuser(), "platform": platform.system(), "layout": layout_of(live_home)},
    )
    check(p3.expected.status == "BOUND", "alice expected BOUND")
    check(p3.actual.status == "OPEN", "tmp actual OPEN")
    check(p3.host == "NEITHER", f"alice lock host NEITHER got {p3.host}")
    check(p3.apply == "SKIP", "alice expected SKIP on this host")
    check(p3.fixture == "", "fixture not legal when host is not ACTUAL")

    skip_src = (
        "import os, unittest\n"
        "@unittest.skipUnless(os.environ.get('HOME') == '/Users/alice', 'alice')\n"
        "def test_alice():\n"
        "    assert True\n"
    )
    check(tests_would_skip([skip_src]), "skipUnless alice fires here")
    comment_skip = "# @unittest.skipUnless(os.environ.get('HOME') == '/Users/alice', 'alice')\n" "def test_sum():\n    assert True\n"
    check(not tests_would_skip([comment_skip]), "comment skip is not an oath")

    cinchish = parse_fail("    self.assertEqual(adder.add(2, 3), 5)\nAssertionError: 0 != 5\n")
    check(len(cinchish) == 1 and cinchish[0][1] == "5" and cinchish[0][2] == "0", "numeric pair")
    pn = bind_host(make_pair("unittest", cinchish[0][1], cinchish[0][2], cinchish[0][3]))
    check(pn.expected.status == "OPEN" and pn.actual.status == "OPEN", "numeric lock OPEN vs OPEN")
    check("wheat" not in pn.lock, "not a cinch")

    if failures:
        raise SystemExit("self-test failed:\n  " + "\n  ".join(failures))
    print("self-test ok")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="writ",
        description=(
            "Splice current tests onto another revision's production, then oath "
            "the splice failure: LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-BOUND. "
            "Skip is not a lock. Comments are not oaths. Not a fourth cinch."
        ),
    )
    p.add_argument("base", nargs="?", default="HEAD", help="revision whose production is spliced")
    p.add_argument("--new", default=None, metavar="REF", help="take tests from this ref")
    p.add_argument("--cmd", default=None, help="test command (default: auto-detect)")
    p.add_argument("--timeout", type=float, default=120.0, help="seconds per test run")
    p.add_argument("--keep", action="append", default=[], metavar="REGEX", help="extra test-path regex")
    p.add_argument("--json", action="store_true", help="machine-readable report")
    p.add_argument("--list", action="store_true", help="splice plan only; do not run tests")
    p.add_argument("-C", "--repo", default=".", help="repository path")
    p.add_argument("--report", action="store_true", help="always print the pair (default already does on LOCKED)")
    p.add_argument(
        "--clearance",
        action="store_true",
        help="empty stdout when no BOUND side (portable lock / no lock)",
    )
    p.add_argument("--apply", action="store_true", help="host-role apply of the splice-fail pair")
    p.add_argument(
        "--fixture",
        action="store_true",
        help="emit actual-side skip iff this host is ACTUAL-BOUND of the splice fail",
    )
    p.add_argument("--due", action="store_true", help="exit 1 on SKIP (skip is still not a lock)")
    p.add_argument("--self-test", action="store_true", help="run internal assertions")
    p.add_argument("--version", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.version:
        print(f"writ {VERSION}")
        return 0
    if args.self_test:
        self_test()
        return 0

    repo = repo_root(Path(args.repo).resolve())
    keep = [re.compile(rx) for rx in args.keep]
    new_ref = args.new
    cmd = cmd_to_list(args.cmd) if args.cmd else detect_cmd(repo)

    if args.list:
        changed = production_changed(repo, args.base, new_ref, keep)
        new_paths = list_new_paths(repo, new_ref)
        plan_rows = []
        for path in union_paths(repo, args.base, new_ref):
            role = path_role(path, keep)
            if role != "production":
                src = "new" if new_bytes(repo, new_ref, path) is not None else "missing"
            else:
                src = "base" if git_show(repo, args.base, path) is not None else "deleted"
            plan_rows.append({"path": path, "role": role, "source": src})
        payload = {
            "base": args.base,
            "new": "worktree" if new_ref is None else new_ref,
            "cmd": cmd,
            "production_changed": changed,
            "tests_kept": tests_in(new_paths, keep),
            "plan": plan_rows,
            "wheat": [],
            "hunks": [],
        }
        if args.json:
            json.dump(payload, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"writ --list  base={args.base}  new={payload['new']}")
            print(f"cmd    {' '.join(cmd)}")
            print(f"prod   {len(changed)} changed production path(s)")
            for pth in changed:
                print(f"         {pth}")
            print("plan:")
            for row in plan_rows:
                if row["role"] == "test" or row["path"] in changed or row["source"] == "deleted":
                    print(f"  {row['role']:11} {row['source']:8} {row['path']}")
        return 0

    report = run_writ(
        repo=repo,
        base=args.base,
        new_ref=new_ref,
        cmd=cmd,
        timeout=args.timeout,
        keep=keep,
    )

    if args.fixture:
        sys.stdout.write((report.fixture or "false") + "\n")
        return exit_code(report, fixture=True)
    if args.apply:
        if args.json:
            json.dump(report_to_json(report), sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(format_human(report, due=args.due))
        return exit_code(report, apply=True)

    if args.clearance and clearance_empty(report) and not args.json:
        return exit_code(report, due=args.due)

    if args.json:
        json.dump(report_to_json(report), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_human(report, due=args.due))
    return exit_code(report, due=args.due)


if __name__ == "__main__":
    sys.exit(main())
