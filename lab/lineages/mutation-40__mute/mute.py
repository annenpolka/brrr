#!/usr/bin/env python3
"""mute — production hunks in a PR range that no NEW test locks.

hasp emits the 1-minimal production the new tests require. mute is the
complement: production the PR changed that those new tests never look at.

The lock is still only tests *born* in the range. An updated old assertion
is background, never a lock. The predicate is pass/fail, not a fingerprint
(a debug print is mute, not locked). A production-only PR with no new tests
is MUTE (the entire production range). A tests-only PR is empty mute.

Never rewrite the user worktree. Overlay in a temp tree.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.2.0"

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".mute-tmp",
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
    ".r",
    ".jl",
    ".sh",
    ".bash",
    ".zsh",
    ".sql",
    ".proto",
    ".graphql",
    ".vue",
    ".svelte",
}

TEST_FILE_RE = re.compile(
    r"""
    (
        ^test_.*\.py$
      | ^tests?\.py$
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
UNITTEST_VERBOSE_RE = re.compile(
    r"^(FAIL|ERROR):\s+(\S+)\s+\(([^)]+)\)",
    re.MULTILINE,
)
IMPORTISH_RE = re.compile(
    r"(ImportError|ModuleNotFoundError|SyntaxError|cannot find (crate|value|type|module)|"
    r"error: could not compile|unresolved import|cannot find type)",
    re.IGNORECASE,
)
EMPTY_SUITE_RE = re.compile(
    r"(NO TESTS RAN|collected 0 items|Ran 0 tests in|running 0 tests)",
    re.IGNORECASE,
)
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")
SWIFT_TEST_RE = re.compile(
    r"@Test(?:\s*\([^)]*\))?\s*(?:public\s+|private\s+|internal\s+)?func\s+(\w+)",
    re.MULTILINE,
)
SWIFT_XCTEST_RE = re.compile(r"func\s+(test\w+)\s*\(")
JS_IT_RE = re.compile(r"""(?:\b(?:it|test)\()\s*['"`]([^'"`]+)""")
RUST_TEST_RE = re.compile(r"fn\s+(test_\w+)\s*\(")
GO_TEST_RE = re.compile(r"func\s+(Test\w+)\s*\(")
DUMMY_TEST_NAMES = {"__init__.py", "conftest.py", "mod.rs", "package.swift"}
GENERATED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".eggs",
    ".git",
}
GENERATED_SUFFIXES = (".pyc", ".pyo", ".pyd")

RUNNER_SRC = r'''#!/usr/bin/env python3
"""Run only the named tests mute selected. Lives in the sandbox, not the user tree."""
from __future__ import annotations

import importlib.util
import json
import sys
import traceback
import unittest
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))


def load_module(path: str):
    mod_name = "_mute_" + re_name(path)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def re_name(path: str) -> str:
    out = []
    for ch in path:
        out.append(ch if ch.isalnum() else "_")
    return "".join(out)


def main() -> int:
    specs_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".mute_specs.json")
    specs = json.loads(specs_path.read_text(encoding="utf-8"))
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    module_ok = 0
    for path, ident in specs:
        if ident == "<module>":
            try:
                ns = {"__name__": "__main__", "__file__": path}
                code = Path(path).read_text(encoding="utf-8")
                exec(compile(code, path, "exec"), ns, ns)
            except AssertionError:
                print(f"FAIL: {path}", file=sys.stderr)
                traceback.print_exc()
                return 1
            except Exception as e:
                print(f"ERROR: {path}: {e}", file=sys.stderr)
                traceback.print_exc()
                return 1
            module_ok += 1
            print(f"{path} ... ok")
            continue
        try:
            mod = load_module(path)
        except Exception as e:
            print(f"ERROR: {path}: {e}", file=sys.stderr)
            traceback.print_exc()
            return 1
        try:
            if "." in ident:
                suite.addTests(loader.loadTestsFromName(ident, module=mod))
            else:
                obj = getattr(mod, ident)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                    suite.addTests(loader.loadTestsFromTestCase(obj))
                elif callable(obj):
                    suite.addTest(unittest.FunctionTestCase(obj, description=ident))
                else:
                    suite.addTests(loader.loadTestsFromName(ident, module=mod))
        except Exception as e:
            print(f"ERROR: {path}::{ident}: {e}", file=sys.stderr)
            traceback.print_exc()
            return 1
    n = suite.countTestCases()
    if n:
        result = unittest.TextTestRunner(verbosity=2, buffer=True).run(suite)
        if result.testsRun == 0 and module_ok == 0:
            print("NO TESTS RAN")
            return 5
        return 0 if result.wasSuccessful() else 1
    if module_ok:
        return 0
    print("NO TESTS RAN")
    return 5


if __name__ == "__main__":
    sys.exit(main())
'''


class MuteError(Exception):
    def __init__(self, message: str, exit_code: int = 2) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class PatchError(Exception):
    pass


@dataclass(frozen=True)
class Hunk:
    path: str
    kind: str  # modify | add | delete
    role: str  # production | test | other
    head: bytes | None
    wip: bytes | None
    mode: int | None = None
    hunk_index: int | None = None
    hunk_header: str | None = None
    old_start: int = 0
    old_count: int = 0
    body: tuple[str, ...] = ()

    @property
    def id(self) -> str:
        if self.hunk_index is None:
            return self.path
        return f"{self.path}#{self.hunk_index}"

    def label(self) -> str:
        if self.hunk_index is None or not self.hunk_header:
            return f"{self.kind:6} {self.path}"
        return f"{self.kind:6} {self.path}  #{self.hunk_index} {self.hunk_header.strip()}"

    def added_lines(self) -> list[str]:
        return [ln[1:] for ln in self.body if ln.startswith("+")]


@dataclass(frozen=True)
class TestSpec:
    path: str
    ident: str

    @property
    def id(self) -> str:
        return f"{self.path}::{self.ident}"

    def pytest_nodeid(self) -> str:
        if self.ident == "<module>":
            return self.path
        if "." in self.ident:
            cls, meth = self.ident.split(".", 1)
            return f"{self.path}::{cls}::{meth}"
        return f"{self.path}::{self.ident}"


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
class Endpoints:
    old_sha: str
    new_sha: str | None  # None = worktree
    display: str
    old_name: str
    new_name: str
    mode: str  # three | two | worktree


@dataclass
class Report:
    status: str
    range: str
    base: str
    new: str
    cmd: list[str]
    trials: int = 0
    mute: list[Hunk] = field(default_factory=list)
    locked: list[Hunk] = field(default_factory=list)
    reason: str = ""
    new_tests: list[TestSpec] = field(default_factory=list)
    background_tests: list[TestSpec] = field(default_factory=list)
    new_fixtures: list[str] = field(default_factory=list)
    held_tests: list[str] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)
    witnesses: dict[str, list[str]] = field(default_factory=dict)
    new_run: RunResult | None = None
    splice_run: RunResult | None = None
    notes: list[str] = field(default_factory=list)
    granularity: str = "hunk"
    production_units: int = 0


def git(args: list[str], cwd: Path, check: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=text,
    )


def git_bytes(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, check=False, capture_output=True)


def repo_root(start: Path) -> Path:
    proc = git(["rev-parse", "--show-toplevel"], cwd=start, check=False)
    if proc.returncode != 0:
        raise MuteError(f"not a git repository: {start}")
    return Path(proc.stdout.strip()).resolve()


def rev_parse(repo: Path, ref: str) -> str:
    proc = git(["rev-parse", "--verify", ref], cwd=repo, check=False)
    if proc.returncode != 0:
        raise MuteError(f"unknown revision {ref!r}")
    return proc.stdout.strip()


def is_generated(path: str) -> bool:
    parts = Path(path).parts
    if any(p in GENERATED_DIR_NAMES or p in SKIP_DIR_NAMES for p in parts):
        return True
    return path.endswith(GENERATED_SUFFIXES)


def is_test_path(path: str, extra_keep: list[re.Pattern[str]] | None = None) -> bool:
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
    return lower.endswith((".expected.json", ".snap", ".snapshot"))


def is_source_path(path: str) -> bool:
    ext = Path(path.replace("\\", "/")).suffix.lower()
    if ext in SOURCE_EXTENSIONS:
        return True
    name = Path(path).name.lower()
    return name in {"justfile", "makefile", "dockerfile", "cmakelists.txt"}


def is_shebang_script(path: str, blob: bytes | None) -> bool:
    """Extensionless file whose first line is #! — wrappers like ./mute."""
    if blob is None:
        return False
    name = Path(path.replace("\\", "/")).name
    if "." in name:
        return False
    first = blob.split(b"\n", 1)[0]
    return first.startswith(b"#!")


def path_role(
    path: str,
    extra_keep: list[re.Pattern[str]] | None = None,
    blob: bytes | None = None,
) -> str:
    if is_test_path(path, extra_keep):
        return "test"
    if is_source_path(path):
        return "production"
    if is_shebang_script(path, blob):
        return "production"
    return "other"


def should_skip_path(path: str) -> bool:
    return any(p in SKIP_DIR_NAMES for p in Path(path.replace("\\", "/")).parts)


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
        if '"test"' in text:
            return ["npm", "test", "--silent"]
    if (root / "Package.swift").exists() and shutil.which("swift"):
        return ["swift", "test"]
    pyproject = root / "pyproject.toml"
    if (root / "pytest.ini").exists() or (root / "conftest.py").exists():
        return [sys.executable, "-m", "pytest", "-q"]
    if pyproject.exists():
        try:
            text = pyproject.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        if "[tool.pytest" in text:
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
        if name.startswith("_mute_"):
            if "." in name:
                name = name.split(".", 1)[1]
            else:
                return
        if name and name not in seen:
            seen.add(name)
            found.append(name)

    for m in UNITTEST_VERBOSE_RE.finditer(output):
        add(m.group(3))
        add(m.group(2))
    for rx in (FAIL_LINE_RE, PYTEST_FAILED_RE, CARGO_FAILED_RE):
        for m in rx.finditer(output):
            add(m.group(m.lastindex or 1))
    return found


def empty_suite(result: RunResult) -> bool:
    if result.timed_out:
        return False
    if result.exit_code == 5:
        return True
    if EMPTY_SUITE_RE.search(result.output) and result.exit_code in (0, 1, 5):
        return True
    return False


def unbuildable(output: str, witnesses: list[str]) -> bool:
    assertion = "AssertionError" in output or "FAIL:" in output or any("::" in w for w in witnesses)
    importish = bool(IMPORTISH_RE.search(output))
    compile_fail = bool(re.search(r"could not compile|error\[E\d+\]", output, re.IGNORECASE))
    collection_error = any("FailedTest" in w or w.startswith("ERROR") for w in witnesses)
    return (importish or compile_fail or collection_error) and not assertion


def run_cmd(cmd: list[str], cwd: Path, timeout: float, extra_env: dict[str, str] | None = None) -> RunResult:
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
    if extra_env:
        env.update(extra_env)
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
        seconds = time.monotonic() - t0
        output = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        return RunResult(proc.returncode, seconds, output, timed_out=False)
    except FileNotFoundError as e:
        return RunResult(127, time.monotonic() - t0, str(e), timed_out=False)
    except subprocess.TimeoutExpired as e:
        out = ""
        if e.stdout:
            out += e.stdout if isinstance(e.stdout, str) else e.stdout.decode("utf-8", "replace")
        if e.stderr:
            out += "\n" + (e.stderr if isinstance(e.stderr, str) else e.stderr.decode("utf-8", "replace"))
        out += f"\n[mute: timed out after {timeout}s]"
        return RunResult(124, time.monotonic() - t0, out, timed_out=True)


def git_show(repo: Path, ref: str, path: str) -> bytes | None:
    proc = git_bytes(["show", f"{ref}:{path}"], cwd=repo)
    if proc.returncode != 0:
        return None
    return proc.stdout


def read_worktree(path: Path) -> tuple[bytes | None, int | None]:
    try:
        st = path.lstat()
    except FileNotFoundError:
        return None, None
    if not stat.S_ISREG(st.st_mode):
        return None, st.st_mode
    return path.read_bytes(), st.st_mode


def write_worktree(path: Path, data: bytes | None, mode: int | None) -> None:
    if data is None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".mute-tmp-{path.name}-{os.getpid()}")
    tmp.write_bytes(data)
    if mode is not None:
        os.chmod(tmp, stat.S_IMODE(mode))
    tmp.replace(path)


def list_tree_files(repo: Path, ref: str) -> list[str]:
    proc = git(["ls-tree", "-r", "--name-only", ref], cwd=repo)
    return [ln for ln in proc.stdout.splitlines() if ln]


def split_z(data: bytes) -> list[bytes]:
    return [p for p in data.split(b"\0") if p]


def expand_untracked(repo: Path, entries: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if is_generated(entry):
            continue
        abs_path = repo / entry
        if abs_path.is_file():
            if entry not in seen:
                out.append(entry)
                seen.add(entry)
            continue
        if not abs_path.is_dir():
            continue
        for f in abs_path.rglob("*"):
            if not f.is_file() or ".git" in f.parts:
                continue
            rel = str(f.relative_to(repo)).replace(os.sep, "/")
            if is_generated(rel) or rel in seen:
                continue
            out.append(rel)
            seen.add(rel)
    return out


def list_worktree_files(repo: Path) -> list[str]:
    proc = git_bytes(["ls-files", "-co", "--exclude-standard", "-z"], cwd=repo)
    entries = [os.fsdecode(p) for p in split_z(proc.stdout)]
    return expand_untracked(repo, entries)


def parse_u0_hunks(diff_text: str) -> list[tuple[str, int, int, tuple[str, ...]]]:
    hunks: list[tuple[str, int, int, tuple[str, ...]]] = []
    header: str | None = None
    old_start = 0
    old_count = 0
    body: list[str] = []

    def flush() -> None:
        nonlocal header, body
        if header is None:
            return
        hunks.append((header, old_start, old_count, tuple(body)))
        header = None
        body = []

    for line in diff_text.splitlines():
        if line.startswith("@@"):
            flush()
            m = HUNK_RE.match(line)
            if not m:
                continue
            header = line
            old_start = int(m.group(1))
            old_count = int(m.group(2) if m.group(2) is not None else "1")
            body = []
            continue
        if header is None:
            continue
        if line.startswith("diff --git"):
            flush()
            continue
        if line.startswith(("+", "-", " ")):
            body.append(line)
    flush()
    return hunks


def apply_hunks(head: bytes, hunks: list[Hunk]) -> bytes:
    try:
        text = head.decode("utf-8")
    except UnicodeDecodeError as e:
        raise PatchError("binary") from e
    ended_nl = text.endswith("\n") or text == ""
    lines = text.splitlines()
    ordered = sorted(hunks, key=lambda h: (h.old_start, h.hunk_index or 0), reverse=True)
    for h in ordered:
        old = [ln[1:] for ln in h.body if ln[:1] in "- "]
        new = [ln[1:] for ln in h.body if ln[:1] in "+ "]
        if h.old_count == 0:
            idx = h.old_start
            if idx < 0 or idx > len(lines) or old:
                raise PatchError(h.hunk_header or h.path)
            lines[idx:idx] = new
            continue
        idx = h.old_start - 1
        if idx < 0 or idx + len(old) > len(lines):
            raise PatchError(h.hunk_header or h.path)
        if lines[idx : idx + len(old)] != old:
            raise PatchError(h.hunk_header or h.path)
        lines[idx : idx + len(old)] = new
    out = "\n".join(lines)
    if ended_nl and (out or text):
        out += "\n"
    return out.encode("utf-8")


def is_test_fn(name: str) -> bool:
    return name.startswith("test")


def python_test_ids(source: bytes | None) -> list[str]:
    """Named tests in a Python file: 'TestCls.test_foo' or 'test_foo'."""
    if not source:
        return []
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return []
    ids: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_test_fn(node.name):
            ids.append(node.name)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_test_fn(item.name):
                    ids.append(f"{node.name}.{item.name}")
    return ids


def swift_test_ids(source: bytes) -> list[str]:
    text = source.decode("utf-8", "replace")
    ids: list[str] = []
    seen: set[str] = set()
    for rx in (SWIFT_TEST_RE, SWIFT_XCTEST_RE):
        for m in rx.finditer(text):
            name = m.group(1)
            if name not in seen:
                seen.add(name)
                ids.append(name)
    return ids


def js_test_ids(source: bytes) -> list[str]:
    text = source.decode("utf-8", "replace")
    ids: list[str] = []
    seen: set[str] = set()
    for m in JS_IT_RE.finditer(text):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            ids.append(name)
    return ids


def language_test_ids(path: str, source: bytes | None) -> list[str]:
    if not source:
        return []
    ext = Path(path).suffix.lower()
    if ext == ".py":
        return python_test_ids(source)
    if ext == ".swift":
        return swift_test_ids(source)
    if ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        return js_test_ids(source)
    if ext == ".rs":
        return RUST_TEST_RE.findall(source.decode("utf-8", "replace"))
    if ext == ".go":
        return GO_TEST_RE.findall(source.decode("utf-8", "replace"))
    return []


def is_fixture_path(path: str) -> bool:
    posix = path.replace("\\", "/")
    parts = [p.lower() for p in Path(posix).parts]
    if any(p in FIXTURE_DIR_NAMES for p in parts):
        return True
    name = Path(posix).name.lower()
    if name in DUMMY_TEST_NAMES:
        return True
    ext = Path(posix).suffix.lower()
    return ext in {".pkl", ".json", ".md", ".toml", ".txt", ".snap", ".snapshot"}


def is_runnable_test_path(path: str) -> bool:
    """A file that can *be* a named test, not a fixture sitting in tests/."""
    posix = path.replace("\\", "/")
    name = Path(posix).name
    if name in DUMMY_TEST_NAMES:
        return False
    if is_fixture_path(posix) and not TEST_FILE_RE.match(name):
        return False
    if TEST_FILE_RE.match(name):
        return True
    lower = name.lower()
    if lower.endswith(("tests.swift", "test.swift", "_test.rs", "_test.go", "_test.py")):
        return True
    ext = Path(name).suffix.lower()
    parts = [p.lower() for p in Path(posix).parts]
    if any(p in TEST_DIR_NAMES for p in parts) and ext in {
        ".py",
        ".rs",
        ".go",
        ".swift",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        ".rb",
    }:
        return True
    return False


def python_runnable(specs: list[TestSpec]) -> list[TestSpec]:
    return [s for s in specs if s.path.endswith(".py")]


def split_range_token(token: str) -> tuple[str, str | None, str] | None:
    """Parse BASE...NEW / BASE..NEW. Empty NEW means worktree."""
    if "..." in token:
        a, b = token.split("...", 1)
        return (a or "HEAD"), (b or None), "three"
    if ".." in token:
        a, b = token.split("..", 1)
        return (a or "HEAD"), (b or None), "two"
    return None


def _is_worktree_name(name: str | None) -> bool:
    if name is None:
        return True
    return name.lower() in {"worktree", "wip", ".", "tree"}


def resolve_endpoints(
    repo: Path,
    range_token: str | None,
    base_opt: str | None,
    new_opt: str | None,
) -> Endpoints:
    old_name = "HEAD"
    new_name: str | None = None
    mode = "worktree"
    parsed = split_range_token(range_token) if range_token else None
    if parsed:
        old_name, new_name, mode = parsed
    elif range_token:
        old_name = range_token
        new_name = None
        mode = "three"
    if base_opt:
        old_name = base_opt
    if new_opt is not None:
        new_name = None if _is_worktree_name(new_opt) else new_opt
        if mode == "worktree":
            mode = "three"
    if new_name and _is_worktree_name(new_name):
        new_name = None

    old_sha = rev_parse(repo, old_name)
    if new_name is None:
        head_sha = rev_parse(repo, "HEAD")
        if mode == "three":
            mb = git(["merge-base", old_sha, head_sha], cwd=repo, check=False)
            if mb.returncode == 0 and mb.stdout.strip():
                old_sha = mb.stdout.strip()
        display = f"{old_name}...worktree"
        return Endpoints(old_sha, None, display, old_name, "worktree", mode)

    new_sha = rev_parse(repo, new_name)
    if mode == "three":
        mb = git(["merge-base", old_sha, new_sha], cwd=repo, check=False)
        if mb.returncode == 0 and mb.stdout.strip():
            old_sha = mb.stdout.strip()
        display = f"{old_name}...{new_name}"
    else:
        display = f"{old_name}..{new_name}"
    return Endpoints(old_sha, new_sha, display, old_name, new_name, mode)


def hunks_for_file(
    repo: Path,
    old_ref: str,
    new_ref: str | None,
    path: str,
    kind: str,
    role: str,
    head: bytes | None,
    wip: bytes | None,
    mode: int | None,
    granularity: str,
) -> list[Hunk]:
    whole = Hunk(path=path, kind=kind, role=role, head=head, wip=wip, mode=mode, hunk_index=None, hunk_header="(file)")
    if granularity == "file":
        return [whole]
    if kind in ("add", "delete"):
        label = "(new file)" if kind == "add" else "(deleted)"
        return [Hunk(path=path, kind=kind, role=role, head=head, wip=wip, mode=mode, hunk_index=1, hunk_header=label)]
    if head is None or wip is None or b"\0" in head or b"\0" in wip:
        return [whole]
    if new_ref is None:
        r = git_bytes(["diff", "-U0", "--no-color", "--no-renames", old_ref, "--", path], cwd=repo)
    else:
        r = git_bytes(["diff", "-U0", "--no-color", "--no-renames", old_ref, new_ref, "--", path], cwd=repo)
    if r.returncode not in (0, 1):
        return [whole]
    parsed = parse_u0_hunks(r.stdout.decode("utf-8", "replace"))
    if not parsed:
        return [whole]
    out: list[Hunk] = []
    for i, (header, old_start, old_count, body) in enumerate(parsed, start=1):
        out.append(
            Hunk(
                path=path,
                kind=kind,
                role=role,
                head=head,
                wip=wip,
                mode=mode,
                hunk_index=i,
                hunk_header=header,
                old_start=old_start,
                old_count=old_count,
                body=body,
            )
        )
    return out


def reconstruct(chosen: list[Hunk], all_hunks: list[Hunk]) -> tuple[bytes | None, int | None]:
    proto = all_hunks[0]
    if proto.kind == "add":
        return (proto.wip, proto.mode) if chosen else (None, None)
    if proto.kind == "delete":
        return (None, None) if chosen else (proto.head, proto.mode)
    if not chosen:
        return proto.head, proto.mode
    if len(chosen) == len(all_hunks):
        return proto.wip, proto.mode
    if proto.head is None:
        raise PatchError(proto.path)
    return apply_hunks(proto.head, chosen), proto.mode


def blob_at(repo: Path, ref: str | None, path: str) -> tuple[bytes | None, int | None]:
    if ref is None:
        return read_worktree(repo / path)
    data = git_show(repo, ref, path)
    return data, (0o644 if data is not None else None)


def list_changes(
    repo: Path,
    old_ref: str,
    new_ref: str | None,
    granularity: str,
    keep: list[re.Pattern[str]],
) -> list[Hunk]:
    if new_ref is None:
        r = git_bytes(["diff", "--name-status", "--no-renames", "-z", old_ref], cwd=repo)
    else:
        r = git_bytes(["diff", "--name-status", "--no-renames", "-z", old_ref, new_ref], cwd=repo)
    raw = split_z(r.stdout)
    if len(raw) % 2 != 0:
        raise MuteError("unexpected git diff --name-status -z output")
    tracked: list[tuple[str, str]] = []
    for i in range(0, len(raw), 2):
        status = raw[i].decode("ascii", "replace")
        path = os.fsdecode(raw[i + 1])
        kind = {"M": "modify", "A": "add", "D": "delete", "T": "modify"}.get(status[:1])
        if kind is None or is_generated(path) or should_skip_path(path):
            continue
        tracked.append((path, kind))

    untracked: list[str] = []
    if new_ref is None:
        ur = git_bytes(["ls-files", "-z", "--others", "--exclude-standard"], cwd=repo)
        untracked = expand_untracked(repo, [os.fsdecode(p) for p in split_z(ur.stdout)])

    files: list[tuple[str, str, bytes | None, bytes | None, int | None]] = []
    seen: set[str] = set()
    for path, kind in tracked:
        if path in seen:
            continue
        seen.add(path)
        head = git_show(repo, old_ref, path)
        wip, mode = blob_at(repo, new_ref, path)
        if kind == "delete":
            wip = None
        if kind == "add" and head is not None:
            kind = "modify"
        if head == wip:
            continue
        files.append((path, kind, head, wip, mode))

    for path in untracked:
        if path in seen or is_generated(path) or should_skip_path(path):
            continue
        seen.add(path)
        wip, mode = read_worktree(repo / path)
        if wip is None:
            continue
        files.append((path, "add", None, wip, mode))

    files.sort(key=lambda t: t[0])
    changes: list[Hunk] = []
    for path, kind, head, wip, mode in files:
        role = path_role(path, keep, blob=wip if wip is not None else head)
        changes.extend(
            hunks_for_file(repo, old_ref, new_ref, path, kind, role, head, wip, mode, granularity)
        )
    return changes


def discover_new_tests(
    repo: Path,
    old_ref: str,
    new_ref: str | None,
    test_hunks: list[Hunk],
) -> tuple[list[TestSpec], list[TestSpec], list[str]]:
    """Return (new named tests, background named tests, new fixture/helper paths)."""
    paths = sorted({h.path for h in test_hunks})
    new_specs: list[TestSpec] = []
    background: list[TestSpec] = []
    fixtures: list[str] = []
    for path in paths:
        old_b = git_show(repo, old_ref, path)
        new_b, _mode = blob_at(repo, new_ref, path)
        if new_b is None:
            continue
        if not is_runnable_test_path(path):
            if old_b is None:
                fixtures.append(path)
            continue
        new_ids = language_test_ids(path, new_b)
        old_ids = set(language_test_ids(path, old_b))
        if not new_ids:
            # Python assert-script with no test_* names, and only if the file is new.
            if path.endswith(".py") and old_b is None and Path(path).name not in DUMMY_TEST_NAMES:
                new_specs.append(TestSpec(path, "<module>"))
            elif old_b is None:
                fixtures.append(path)
            continue
        for ident in new_ids:
            spec = TestSpec(path, ident)
            if ident in old_ids:
                background.append(spec)
            else:
                new_specs.append(spec)
    return new_specs, background, fixtures


def extra_env_for(repo: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    target = repo / "target"
    if target.exists():
        env["CARGO_TARGET_DIR"] = str(target)
    return env


def link_existing_deps(repo: Path, dest: Path) -> None:
    for name in sorted(LINK_DIR_NAMES):
        src = repo / name
        if src.exists():
            target = dest / name
            if not target.exists():
                target.symlink_to(src)


def materialize_ref(repo: Path, ref: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    arch = subprocess.Popen(
        ["git", "archive", "--format=tar", ref],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert arch.stdout is not None
    tar = subprocess.run(["tar", "-x", "-C", str(dest)], stdin=arch.stdout, capture_output=True)
    _stdout, err = arch.communicate()
    if arch.returncode != 0:
        raise MuteError(f"git archive {ref} failed: {err.decode('utf-8', 'replace')}")
    if tar.returncode != 0:
        raise MuteError(f"tar extract failed: {tar.stderr.decode('utf-8', 'replace')}")


def materialize_worktree(repo: Path, dest: Path, old_ref: str) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    paths = set(list_tree_files(repo, old_ref)) | set(list_worktree_files(repo))
    for path in sorted(p for p in paths if not should_skip_path(p) and not is_generated(p)):
        data, mode = read_worktree(repo / path)
        if data is None:
            continue
        write_worktree(dest / path, data, mode)


class Sandbox:
    """NEW tree with production rewritten per trial. Never touches the user repo."""

    def __init__(
        self,
        repo: Path,
        old_ref: str,
        new_ref: str | None,
        production: list[Hunk],
    ) -> None:
        self.repo = repo
        self.dest = Path(tempfile.mkdtemp(prefix="mute-"))
        self.production = production
        self.by_path: dict[str, list[Hunk]] = {}
        for h in production:
            self.by_path.setdefault(h.path, []).append(h)
        if new_ref is None:
            materialize_worktree(repo, self.dest, old_ref)
        else:
            materialize_ref(repo, new_ref, self.dest)
        link_existing_deps(repo, self.dest)
        self.env = extra_env_for(repo)

    def apply(self, subset: list[Hunk]) -> None:
        wanted = {h.id for h in subset}
        for path, hunks in self.by_path.items():
            chosen = [h for h in hunks if h.id in wanted]
            blob, mode = reconstruct(chosen, hunks)
            write_worktree(self.dest / path, blob, mode)

    def run(self, cmd: list[str], timeout: float) -> RunResult:
        return run_cmd(cmd, self.dest, timeout, self.env)

    def close(self) -> None:
        shutil.rmtree(self.dest, ignore_errors=True)


def split_n(items: list[Hunk], n: int) -> list[list[Hunk]]:
    n = max(1, min(n, len(items)))
    size, rem = divmod(len(items), n)
    out: list[list[Hunk]] = []
    i = 0
    for k in range(n):
        take = size + (1 if k < rem else 0)
        out.append(items[i : i + take])
        i += take
    return [part for part in out if part]


def ddmin(
    changes: list[Hunk],
    interesting: Callable[[list[Hunk]], bool],
    log: Callable[[str], None],
) -> list[Hunk]:
    current = list(changes)
    n = 2
    while len(current) >= 2:
        parts = split_n(current, n)
        found = False
        for part in parts:
            log(f"  try {len(part)}/{len(current)} subset {[c.id for c in part]}")
            if interesting(part):
                current = part
                n = 2
                found = True
                break
        if found:
            continue
        for part in parts:
            complement = [c for c in current if c.id not in {x.id for x in part}]
            if not complement or len(complement) == len(current):
                continue
            log(f"  try {len(complement)}/{len(current)} complement {[c.id for c in complement]}")
            if interesting(complement):
                current = complement
                n = max(n - 1, 2)
                found = True
                break
        if found:
            continue
        if n >= len(current):
            break
        n = min(len(current), n * 2)
        log(f"  increase granularity n={n}")
    return current


def subset_patch(subset: list[Hunk], by_path: dict[str, list[Hunk]]) -> str:
    import difflib

    chunks: list[str] = []
    wanted = {c.id for c in subset}
    for path in sorted(by_path):
        all_hunks = by_path[path]
        chosen = [h for h in all_hunks if h.id in wanted]
        if not chosen:
            continue
        proto = all_hunks[0]
        try:
            new_blob, _mode = reconstruct(chosen, all_hunks)
        except PatchError:
            new_blob = proto.wip if chosen else proto.head
        a = "" if proto.head is None else proto.head.decode("utf-8", "replace")
        b = "" if new_blob is None else new_blob.decode("utf-8", "replace")
        if a == b:
            continue
        a_lines = a.splitlines(keepends=True)
        b_lines = b.splitlines(keepends=True)
        if a_lines and not a_lines[-1].endswith("\n"):
            a_lines[-1] += "\n"
        if b_lines and not b_lines[-1].endswith("\n"):
            b_lines[-1] += "\n"
        from_name = "/dev/null" if proto.head is None else f"a/{path}"
        to_name = "/dev/null" if new_blob is None else f"b/{path}"
        text = "".join(difflib.unified_diff(a_lines, b_lines, fromfile=from_name, tofile=to_name))
        if text:
            chunks.append(text)
    return "".join(chunks)


def dump_hunk(h: Hunk, witnesses: dict[str, list[str]]) -> dict[str, object]:
    d: dict[str, object] = {"path": h.path, "kind": h.kind, "role": h.role, "id": h.id}
    if h.hunk_index is not None:
        d["hunk"] = h.hunk_index
        d["header"] = h.hunk_header
    added = h.added_lines()
    if added:
        d["added"] = added[:12]
    w = witnesses.get(h.id)
    if w:
        d["witnesses"] = w
    return d


def dump_spec(s: TestSpec) -> dict[str, str]:
    return {"path": s.path, "id": s.ident, "nodeid": s.id}


def dump_run(r: RunResult | None) -> dict[str, object] | None:
    if r is None:
        return None
    return {
        "exit_code": r.exit_code,
        "seconds": round(r.seconds, 4),
        "timed_out": r.timed_out,
        "output_tail": r.output.strip().splitlines()[-20:],
    }


def cmd_is_pytest(cmd: list[str]) -> bool:
    joined = " ".join(cmd)
    return "pytest" in joined


def python_lock_cmd(specs: list[TestSpec], user_cmd: list[str], sandbox: Path) -> list[str]:
    """Run only new tests. pytest nodeids if the user asked for pytest; else the runner."""
    if cmd_is_pytest(user_cmd):
        nodeids = [s.pytest_nodeid() for s in specs]
        base = [c for c in user_cmd if c != "--"]
        if not any(c == "-q" or str(c).startswith("-q") for c in base):
            base.append("-q")
        return base + nodeids
    specs_path = sandbox / ".mute_specs.json"
    specs_path.write_text(json.dumps([[s.path, s.ident] for s in specs]), encoding="utf-8")
    runner = sandbox / ".mute_run.py"
    runner.write_text(RUNNER_SRC, encoding="utf-8")
    return [sys.executable, str(runner), str(specs_path)]


def set_product(report: Report, production: list[Hunk], locked: list[Hunk], reason: str) -> None:
    """Unlocked production is the product. locked is contrast only."""
    locked_ids = {c.id for c in locked}
    report.locked = sorted(locked, key=lambda c: (c.path, c.hunk_index or 0))
    report.mute = [c for c in production if c.id not in locked_ids]
    report.reason = reason
    if report.status in {"BROKEN", "UNBUILDABLE", "EMPTY", "FOREIGN"}:
        # Isolation failed: do not claim a mute set.
        report.mute = []
        report.locked = []
        return
    if report.mute:
        report.status = "MUTE"
    elif production:
        report.status = "LOCKED"
    else:
        report.status = "CLEAN"


def format_human(report: Report) -> str:
    lines: list[str] = []
    lines.append(
        f"mute   range={report.range}  old={report.base}  new={report.new}  "
        f"status={report.status}  trials={report.trials}"
        + (f"  reason={report.reason}" if report.reason else "")
    )
    lines.append(f"cmd    {' '.join(report.cmd)}")
    lines.append(f"prod   {report.production_units} production unit(s)  granularity={report.granularity}")
    if report.new_run:
        r = report.new_run
        state = "pass" if r.ok else ("timeout" if r.timed_out else f"fail({r.exit_code})")
        lines.append(f"NEW    {state:12} {r.seconds:.2f}s   (new tests @ new production)")
    if report.splice_run:
        r = report.splice_run
        state = "pass" if r.ok else ("timeout" if r.timed_out else f"fail({r.exit_code})")
        lines.append(f"SPLICE {state:12} {r.seconds:.2f}s   (new tests @ old production)")
    lines.append("")
    meaning = {
        "LOCKED": "every production hunk is locked by new tests — mute set empty",
        "CLEAN": "no production units differ in the range — mute set empty",
        "MUTE": "unlocked production: new tests in the range never look at this",
        "FOREIGN": "new tests exist but none are Python-runnable — --list named them; isolation refused",
        "BROKEN": "new tests already fail on the new tree — cannot isolate mute",
        "UNBUILDABLE": "no production subset makes the new tests load — cannot isolate mute",
        "EMPTY": "new-test command collected no tests — cannot isolate mute",
    }.get(report.status, "")
    if meaning:
        lines.append(meaning)
    if report.new_tests:
        lines.append("new tests (the lock; only these run; updated old tests do not):")
        for s in report.new_tests[:30]:
            lines.append(f"  {s.id}")
        if len(report.new_tests) > 30:
            lines.append(f"  … {len(report.new_tests) - 30} more")
    if report.background_tests:
        lines.append("background tests (in range, not the lock, not run):")
        for s in report.background_tests[:20]:
            lines.append(f"  {s.id}")
        if len(report.background_tests) > 20:
            lines.append(f"  … {len(report.background_tests) - 20} more")
    if report.new_fixtures:
        lines.append("new fixtures (held, not the lock):")
        for p in report.new_fixtures[:12]:
            lines.append(f"  {p}")
        if len(report.new_fixtures) > 12:
            lines.append(f"  … {len(report.new_fixtures) - 12} more")
    if report.ignored:
        lines.append("ignored (not production source):")
        for p in report.ignored[:12]:
            lines.append(f"  {p}")
        if len(report.ignored) > 12:
            lines.append(f"  … {len(report.ignored) - 12} more")
    nfiles_m = len({c.path for c in report.mute})
    nfiles_l = len({c.path for c in report.locked})
    lines.append(f"mute ({len(report.mute)} units / {nfiles_m} files)  — the product:")
    if not report.mute:
        lines.append("  (empty)")
    for c in report.mute[:20]:
        added = c.added_lines()
        preview = f"  + {added[0][:80]}" if added else ""
        lines.append(f"  {c.label()}{preview}")
    if len(report.mute) > 20:
        lines.append(f"  … {len(report.mute) - 20} more")
    lines.append(f"locked ({len(report.locked)} units / {nfiles_l} files)  — new tests require:")
    if not report.locked:
        lines.append("  (empty)")
    for c in report.locked[:20]:
        extra = ""
        w = report.witnesses.get(c.id) or []
        if w:
            extra = "  locked by: " + ", ".join(w[:6])
        added = c.added_lines()
        preview = f"  + {added[0][:80]}" if added else ""
        lines.append(f"  {c.label()}{extra}{preview}")
    if len(report.locked) > 20:
        lines.append(f"  … {len(report.locked) - 20} more")
    for note in report.notes:
        lines.append(f"note: {note}")
    if report.status in {"BROKEN", "EMPTY"} and report.new_run and not report.new_run.ok:
        tail = report.new_run.output.strip().splitlines()[-12:]
        if tail:
            lines.append("new tail:")
            for ln in tail:
                lines.append(f"  {ln}")
    return "\n".join(lines) + "\n"


def report_to_json(report: Report) -> dict[str, object]:
    return {
        "status": report.status,
        "reason": report.reason,
        "range": report.range,
        "base": report.base,
        "new": report.new,
        "cmd": report.cmd,
        "trials": report.trials,
        "granularity": report.granularity,
        "production_units": report.production_units,
        "mute": [dump_hunk(h, report.witnesses) for h in report.mute],
        "locked": [dump_hunk(h, report.witnesses) for h in report.locked],
        "new_tests": [dump_spec(s) for s in report.new_tests],
        "background_tests": [dump_spec(s) for s in report.background_tests],
        "new_fixtures": report.new_fixtures,
        "held_tests": report.held_tests,
        "ignored": report.ignored,
        "witnesses": report.witnesses,
        "notes": report.notes,
        "new_run": dump_run(report.new_run),
        "splice_run": dump_run(report.splice_run),
    }


def run_mute(
    repo: Path,
    ends: Endpoints,
    user_cmd: list[str],
    timeout: float,
    keep: list[re.Pattern[str]],
    granularity: str,
    max_trials: int,
    log: Callable[[str], None],
) -> Report:
    repo = repo.resolve()
    old_ref = ends.old_sha
    new_ref = ends.new_sha
    changes = list_changes(repo, old_ref, new_ref, granularity, keep)
    production = [c for c in changes if c.role == "production"]
    tests = [c for c in changes if c.role == "test"]
    other = [c for c in changes if c.role == "other"]
    new_tests, background, fixtures = discover_new_tests(repo, old_ref, new_ref, tests)
    runnable = python_runnable(new_tests)

    new_label = ends.new_sha[:12] if ends.new_sha else "worktree"
    report = Report(
        status="CLEAN",
        range=ends.display,
        base=f"{ends.old_name} ({old_ref[:12]})",
        new=f"{ends.new_name} ({new_label})",
        cmd=["mute-run", *[s.id for s in runnable]],
        new_tests=new_tests,
        background_tests=background,
        new_fixtures=fixtures,
        held_tests=sorted({s.path for s in new_tests}),
        ignored=sorted({c.path for c in other}),
        granularity=granularity,
        production_units=len(production),
    )

    if not new_tests and production:
        report.notes.append(
            "no new tests in the range; entire production is mute. "
            "updated old tests are background, not a lock"
        )
        if fixtures:
            report.notes.append(f"{len(fixtures)} new fixture/helper path(s) are not a lock")
        set_product(report, production, [], "no-new-tests")
        return report

    if not new_tests and not production:
        report.notes.append("no production units and no new tests in the range")
        set_product(report, production, [], "")
        return report

    if not runnable:
        report.status = "FOREIGN"
        langs = sorted({Path(s.path).suffix.lstrip(".") or "unknown" for s in new_tests})
        report.notes.append(
            f"{len(new_tests)} new test(s) are not Python ({', '.join(langs) or 'unknown'}); "
            "refusing to exec them as Python. --list named them. cannot isolate mute."
        )
        set_product(report, production, [], "foreign")
        return report

    sandbox = Sandbox(repo, old_ref, new_ref, production)
    cache: dict[frozenset[str], RunResult] = {}
    trials = 0
    lock_cmd = python_lock_cmd(runnable, user_cmd, sandbox.dest)
    if len(runnable) < len(new_tests):
        report.notes.append(
            f"running {len(runnable)} Python new test(s); "
            f"skipped {len(new_tests) - len(runnable)} non-Python"
        )

    def trial(subset: list[Hunk]) -> RunResult:
        nonlocal trials
        key = frozenset(c.id for c in subset)
        if key in cache:
            return cache[key]
        if trials >= max_trials:
            raise MuteError(f"exceeded --max-trials {max_trials}", 2)
        trials += 1
        try:
            sandbox.apply(subset)
        except PatchError as e:
            fp = RunResult(exit_code=-1, seconds=0.0, output=f"hunks did not apply: {e}")
            cache[key] = fp
            log(f"  -> unapplicable {e}")
            return fp
        fp = sandbox.run(lock_cmd, timeout)
        cache[key] = fp
        state = "pass" if fp.ok else f"fail({fp.exit_code})"
        log(f"  -> {state} {fp.seconds:.2f}s")
        return fp

    try:
        log(
            f"range {ends.display}  {len(production)} production  "
            f"{len(new_tests)} new tests  {len(background)} background"
        )
        new_run = trial(production)
        report.new_run = new_run
        report.trials = trials
        if empty_suite(new_run):
            report.status = "EMPTY"
            report.notes.append(
                "new-test command collected no tests (exit 5 or 'Ran 0 tests'); "
                "cannot isolate mute"
            )
            set_product(report, production, [], "empty")
            return report
        if not new_run.ok:
            report.status = "BROKEN"
            report.witnesses = {"NEW": parse_witnesses(new_run.output)}
            report.notes.append("refusing to isolate while the new tests already fail on new production")
            set_product(report, production, [], "broken")
            return report

        if not production:
            report.notes.append("new tests pass; no production units in the range")
            set_product(report, production, [], "")
            return report

        splice_run = trial([])
        report.splice_run = splice_run
        report.trials = trials
        if splice_run.ok:
            report.notes.append("new tests pass with every production hunk reverted — none of it is locked")
            set_product(report, production, [], "loose")
            return report

        splice_witnesses = parse_witnesses(splice_run.output)
        if unbuildable(splice_run.output, splice_witnesses):
            report.notes.append("splice is unbuildable (new tests import new production); isolating anyway")

        def interesting(subset: list[Hunk]) -> bool:
            return trial(subset).ok

        locked = ddmin(production, interesting, log)
        confirmed: list[Hunk] = []
        for i, h in enumerate(locked):
            rest = locked[:i] + locked[i + 1 :]
            if rest and interesting(rest):
                continue
            confirmed.append(h)
            dropped = trial(rest)
            report.witnesses[h.id] = parse_witnesses(dropped.output)
        locked = sorted(confirmed or locked, key=lambda c: (c.path, c.hunk_index or 0))
        report.trials = trials
        if not locked:
            report.status = "UNBUILDABLE"
            report.notes.append("splice fails, but no production subset makes new tests pass")
            set_product(report, production, [], "unbuildable")
            return report
        unlocked = [c for c in production if c.id not in {h.id for h in locked}]
        reason = "partial" if unlocked else ""
        set_product(report, production, locked, reason)
        return report
    finally:
        report.trials = trials
        sandbox.close()


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mute",
        description=(
            "Emit production hunks in a PR range that no NEW test locks. "
            "The range is two revisions (A...B merge-base). Updated old tests "
            "are background, never a lock. Predicate is pass/fail."
        ),
        epilog=(
            "Exit 0 if mute is empty (every production hunk is locked),\n"
            "     1 if any unlocked production,\n"
            "     2 on error.\n"
            "Example: mute origin/main...HEAD\n"
            "         mute --format patch main...HEAD"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "range",
        nargs="?",
        help="BASE, BASE...NEW (merge-base, default), or BASE..NEW. NEW omitted = worktree",
    )
    p.add_argument("--base", default=None, help="override range base")
    p.add_argument("--new", default=None, help="override range new (ref or 'worktree')")
    p.add_argument("-C", "--repo", default=".", help="repository path")
    p.add_argument("--cmd", default=None, help="test command (default: run new tests via stdlib)")
    p.add_argument(
        "--format",
        choices=("text", "paths", "json", "patch"),
        default="text",
        help="text report, mute paths, json, or patch of the mute set",
    )
    p.add_argument("--json", action="store_true", help="alias for --format json")
    p.add_argument(
        "--granularity",
        choices=("hunk", "file"),
        default="hunk",
        help="isolate hunks (default) or whole files",
    )
    p.add_argument("--timeout", type=float, default=120.0, help="seconds per test run")
    p.add_argument("--keep", action="append", default=[], metavar="REGEX", help="treat matching paths as tests")
    p.add_argument("--list", action="store_true", help="classify the range; do not run tests")
    p.add_argument("--max-trials", type=int, default=200)
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--version", action="version", version=f"mute {VERSION}")
    p.add_argument("command", nargs=argparse.REMAINDER, help="test command after --")
    return p


def status_exit(status: str) -> int:
    # 0 mute empty, 1 any unlocked production, 2 error.
    if status in {"LOCKED", "CLEAN"}:
        return 0
    if status == "MUTE":
        return 1
    return 2


def emit(report: Report, fmt: str) -> int:
    if fmt == "paths":
        seen: set[str] = set()
        for c in report.mute:
            if c.path in seen:
                continue
            seen.add(c.path)
            print(c.path)
        return status_exit(report.status)
    if fmt == "patch":
        by_path: dict[str, list[Hunk]] = {}
        for h in report.mute + report.locked:
            by_path.setdefault(h.path, []).append(h)
        sys.stdout.write(subset_patch(report.mute, by_path))
        return status_exit(report.status)
    if fmt == "json":
        json.dump(report_to_json(report), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return status_exit(report.status)
    sys.stdout.write(format_human(report))
    return status_exit(report.status)


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    fmt = "json" if args.json else args.format
    try:
        repo = repo_root(Path(args.repo).resolve())
    except MuteError as e:
        print(f"mute: {e}", file=sys.stderr)
        return e.exit_code
    keep = [re.compile(rx) for rx in args.keep]
    cmd = list(args.command)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if args.cmd:
        import shlex

        cmd = shlex.split(args.cmd)
    if not cmd:
        cmd = detect_cmd(repo)

    log = (lambda m: print(m, file=sys.stderr)) if args.verbose else (lambda _m: None)

    try:
        ends = resolve_endpoints(repo, args.range, args.base, args.new)
    except MuteError as e:
        print(f"mute: {e}", file=sys.stderr)
        return e.exit_code

    if args.list:
        changes = list_changes(repo, ends.old_sha, ends.new_sha, args.granularity, keep)
        production = [c for c in changes if c.role == "production"]
        tests = [c for c in changes if c.role == "test"]
        other = [c for c in changes if c.role == "other"]
        new_tests, background, fixtures = discover_new_tests(repo, ends.old_sha, ends.new_sha, tests)
        payload = {
            "range": ends.display,
            "old": ends.old_sha,
            "new": ends.new_sha,
            "cmd": cmd,
            "units": [
                {
                    "id": c.id,
                    "path": c.path,
                    "kind": c.kind,
                    "role": c.role,
                    "header": c.hunk_header,
                    "added": c.added_lines()[:8],
                }
                for c in changes
            ],
            "production": [c.id for c in production],
            "new_tests": [dump_spec(s) for s in new_tests],
            "background_tests": [dump_spec(s) for s in background],
            "new_fixtures": fixtures,
            "ignored": sorted({c.path for c in other}),
        }
        if fmt == "json":
            json.dump(payload, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"mute --list  range={ends.display}  old={ends.old_sha[:12]}  new={ends.new_name}")
            print(f"prod   {len(production)} production unit(s)")
            print(
                f"new    {len(new_tests)} new test(s)  background {len(background)}  "
                f"fixtures {len(fixtures)}"
            )
            shown = 0
            for c in changes:
                if c.role == "production":
                    added = c.added_lines()
                    preview = f"  + {added[0][:80]}" if added else ""
                    print(f"  production  {c.label()}{preview}")
                    shown += 1
                    if shown >= 40:
                        rest = sum(1 for x in changes if x.role == "production") - shown
                        if rest > 0:
                            print(f"  production  … {rest} more")
                        break
            for s in new_tests[:40]:
                print(f"  new-test    {s.id}")
            if len(new_tests) > 40:
                print(f"  new-test    … {len(new_tests) - 40} more")
            for s in background[:20]:
                print(f"  background  {s.id}")
            if len(background) > 20:
                print(f"  background  … {len(background) - 20} more")
            for p in fixtures[:12]:
                print(f"  fixture     {p}")
            if len(fixtures) > 12:
                print(f"  fixture     … {len(fixtures) - 12} more")
            for p in payload["ignored"][:8]:
                print(f"  ignored     {p}")
        return 0

    try:
        report = run_mute(
            repo=repo,
            ends=ends,
            user_cmd=cmd,
            timeout=args.timeout,
            keep=keep,
            granularity=granularity if (granularity := args.granularity) else "hunk",
            max_trials=args.max_trials,
            log=log,
        )
    except MuteError as e:
        print(f"mute: {e}", file=sys.stderr)
        return e.exit_code
    return emit(report, fmt)


if __name__ == "__main__":
    sys.exit(main())
