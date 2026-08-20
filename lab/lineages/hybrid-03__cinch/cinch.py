#!/usr/bin/env python3
"""cinch — emit the production hunks the current tests actually lock.

alibi splices new tests onto old production and reports LOCKED vs LOOSE.
winnow 1-minimizes uncommitted hunks against a command fingerprint.

cinch is not the pipe. Tests stay at NEW and are never wheat. Search only
production hunks. The predicate is "do the tests pass?", not "does stdout
match WIP." Wheat is the 1-minimal production subset the tests require.
"""

from __future__ import annotations

import argparse
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
    ".cinch-tmp",
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


class CinchError(Exception):
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
class Report:
    status: str
    base: str
    cmd: list[str]
    trials: int = 0
    wheat: list[Hunk] = field(default_factory=list)
    chaff: list[Hunk] = field(default_factory=list)
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
        raise CinchError(f"not a git repository: {start}")
    return Path(proc.stdout.strip()).resolve()


def rev_parse(repo: Path, ref: str) -> str:
    proc = git(["rev-parse", "--verify", ref], cwd=repo, check=False)
    if proc.returncode != 0:
        raise CinchError(f"unknown revision {ref!r}")
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


def path_role(path: str, extra_keep: list[re.Pattern[str]] | None = None) -> str:
    if is_test_path(path, extra_keep):
        return "test"
    if is_source_path(path):
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
        if name and name not in seen:
            seen.add(name)
            found.append(name)

    for rx in (FAIL_LINE_RE, PYTEST_FAILED_RE, CARGO_FAILED_RE):
        for m in rx.finditer(output):
            add(m.group(m.lastindex or 1))
    return found


def empty_suite(result: RunResult) -> bool:
    """unittest/pytest exit 5 (and the 'Ran 0 tests' banner) is not a red suite."""
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
    except UnicodeDecodeError as e:
        raise CinchError(f"binary test output: {e}", 2) from e
    except subprocess.TimeoutExpired as e:
        out = ""
        if e.stdout:
            out += e.stdout if isinstance(e.stdout, str) else e.stdout.decode("utf-8", "replace")
        if e.stderr:
            out += "\n" + (e.stderr if isinstance(e.stderr, str) else e.stderr.decode("utf-8", "replace"))
        out += f"\n[cinch: timed out after {timeout}s]"
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
    tmp = path.with_name(f".cinch-tmp-{path.name}-{os.getpid()}")
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


def union_paths(repo: Path, base: str) -> list[str]:
    s = set(list_tree_files(repo, base)) | set(list_worktree_files(repo))
    return sorted(p for p in s if not should_skip_path(p) and not is_generated(p))


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


def hunks_for_file(
    repo: Path,
    base: str,
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
    r = git_bytes(["diff", "-U0", "--no-color", "--no-renames", base, "--", path], cwd=repo)
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


def list_changes(repo: Path, base: str, granularity: str, keep: list[re.Pattern[str]]) -> list[Hunk]:
    r = git_bytes(["diff", "--name-status", "--no-renames", "-z", base], cwd=repo)
    raw = split_z(r.stdout)
    if len(raw) % 2 != 0:
        raise CinchError("unexpected git diff --name-status -z output")
    tracked: list[tuple[str, str]] = []
    for i in range(0, len(raw), 2):
        status = raw[i].decode("ascii", "replace")
        path = os.fsdecode(raw[i + 1])
        kind = {"M": "modify", "A": "add", "D": "delete", "T": "modify"}.get(status[:1])
        if kind is None or is_generated(path) or should_skip_path(path):
            continue
        tracked.append((path, kind))

    r = git_bytes(["ls-files", "-z", "--others", "--exclude-standard"], cwd=repo)
    untracked = expand_untracked(repo, [os.fsdecode(p) for p in split_z(r.stdout)])

    files: list[tuple[str, str, bytes | None, bytes | None, int | None]] = []
    seen: set[str] = set()
    for path, kind in tracked:
        if path in seen:
            continue
        seen.add(path)
        head = git_show(repo, base, path)
        wip, mode = read_worktree(repo / path)
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
        role = path_role(path, keep)
        changes.extend(hunks_for_file(repo, base, path, kind, role, head, wip, mode, granularity))
    return changes


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


def materialize_new(repo: Path, dest: Path, base: str, keep: list[re.Pattern[str]]) -> None:
    """Copy the NEW tree (worktree) into dest, skipping generated/dep dirs."""
    for path in union_paths(repo, base):
        role = path_role(path, keep)
        # Include everything that exists at NEW. Deleted NEW files stay absent.
        data, mode = read_worktree(repo / path)
        if data is None:
            continue
        if role == "other" and not is_source_path(path) and is_test_path(path, keep):
            pass
        write_worktree(dest / path, data, mode)
    link_existing_deps(repo, dest)


class Sandbox:
    """NEW tree with production files rewritten per trial. Never touches the user repo."""

    def __init__(self, repo: Path, base: str, keep: list[re.Pattern[str]], production: list[Hunk]) -> None:
        self.repo = repo
        self.dest = Path(tempfile.mkdtemp(prefix="cinch-"))
        self.production = production
        self.by_path: dict[str, list[Hunk]] = {}
        for h in production:
            self.by_path.setdefault(h.path, []).append(h)
        materialize_new(repo, self.dest, base, keep)
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


def wheat_patch(wheat: list[Hunk], by_path: dict[str, list[Hunk]]) -> str:
    import difflib

    chunks: list[str] = []
    wanted = {c.id for c in wheat}
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
    w = witnesses.get(h.id)
    if w:
        d["witnesses"] = w
    return d


def dump_run(r: RunResult | None) -> dict[str, object] | None:
    if r is None:
        return None
    return {
        "exit_code": r.exit_code,
        "seconds": round(r.seconds, 4),
        "timed_out": r.timed_out,
        "output_tail": r.output.strip().splitlines()[-20:],
    }


def format_human(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"cinch  base={report.base}  status={report.status}  trials={report.trials}")
    lines.append(f"cmd    {' '.join(report.cmd)}")
    lines.append(f"prod   {report.production_units} production unit(s)  granularity={report.granularity}")
    if report.new_run:
        r = report.new_run
        state = "pass" if r.ok else ("timeout" if r.timed_out else f"fail({r.exit_code})")
        lines.append(f"NEW    {state:12} {r.seconds:.2f}s   (tests@new, production@new)")
    if report.splice_run:
        r = report.splice_run
        state = "pass" if r.ok else ("timeout" if r.timed_out else f"fail({r.exit_code})")
        lines.append(f"SPLICE {state:12} {r.seconds:.2f}s   (tests@new, production@base)")
    lines.append("")
    meaning = {
        "LOCKED": "tests require this production subset — it is the lockset, not the fingerprint wheat",
        "LOOSE": "tests still pass on base production — nothing is locked",
        "BROKEN": "tests already fail on the new tree — fix them before asking cinch",
        "CLEAN": "no production units differ from base (tests/docs may still be dirty)",
        "UNBUILDABLE": "no production subset makes the tests load — splice cannot even import",
        "EMPTY": "test command collected no tests — not a red suite; pass --cmd",
    }.get(report.status, "")
    if meaning:
        lines.append(meaning)
    if report.held_tests:
        lines.append("held tests (always NEW, never wheat):")
        for p in report.held_tests[:20]:
            lines.append(f"  {p}")
        if len(report.held_tests) > 20:
            lines.append(f"  … {len(report.held_tests) - 20} more")
    if report.ignored:
        lines.append("ignored (not production source):")
        for p in report.ignored[:12]:
            lines.append(f"  {p}")
        if len(report.ignored) > 12:
            lines.append(f"  … {len(report.ignored) - 12} more")
    nfiles_w = len({c.path for c in report.wheat})
    nfiles_c = len({c.path for c in report.chaff})
    lines.append(f"wheat ({len(report.wheat)} units / {nfiles_w} files):")
    if not report.wheat:
        lines.append("  (empty)")
    for c in report.wheat:
        extra = ""
        w = report.witnesses.get(c.id) or []
        if w:
            extra = "  locked by: " + ", ".join(w[:6])
        lines.append(f"  {c.label()}{extra}")
    lines.append(f"chaff ({len(report.chaff)} units / {nfiles_c} files):")
    if not report.chaff:
        lines.append("  (empty)")
    for c in report.chaff:
        lines.append(f"  {c.label()}")
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
        "base": report.base,
        "cmd": report.cmd,
        "trials": report.trials,
        "granularity": report.granularity,
        "production_units": report.production_units,
        "wheat": [dump_hunk(h, report.witnesses) for h in report.wheat],
        "chaff": [dump_hunk(h, report.witnesses) for h in report.chaff],
        "held_tests": report.held_tests,
        "ignored": report.ignored,
        "witnesses": report.witnesses,
        "notes": report.notes,
        "new_run": dump_run(report.new_run),
        "splice_run": dump_run(report.splice_run),
    }


def run_cinch(
    repo: Path,
    base: str,
    cmd: list[str],
    timeout: float,
    keep: list[re.Pattern[str]],
    granularity: str,
    max_trials: int,
    log: Callable[[str], None],
) -> Report:
    repo = repo.resolve()
    base_sha = rev_parse(repo, base)
    changes = list_changes(repo, base, granularity, keep)
    production = [c for c in changes if c.role == "production"]
    tests = [c for c in changes if c.role == "test"]
    other = [c for c in changes if c.role == "other"]

    report = Report(
        status="CLEAN",
        base=f"{base} ({base_sha[:12]})",
        cmd=cmd,
        held_tests=sorted({c.path for c in tests}),
        ignored=sorted({c.path for c in other}),
        granularity=granularity,
        production_units=len(production),
    )

    if not production:
        report.notes.append("no production source units differ from base; skipped test runs")
        return report

    sandbox = Sandbox(repo, base, keep, production)
    cache: dict[frozenset[str], RunResult] = {}
    trials = 0

    def trial(subset: list[Hunk]) -> RunResult:
        nonlocal trials
        key = frozenset(c.id for c in subset)
        if key in cache:
            return cache[key]
        if trials >= max_trials:
            raise CinchError(f"exceeded --max-trials {max_trials}", 2)
        trials += 1
        try:
            sandbox.apply(subset)
        except PatchError as e:
            fp = RunResult(exit_code=-1, seconds=0.0, output=f"hunks did not apply: {e}")
            cache[key] = fp
            log(f"  -> unapplicable {e}")
            return fp
        fp = sandbox.run(cmd, timeout)
        cache[key] = fp
        state = "pass" if fp.ok else f"fail({fp.exit_code})"
        log(f"  -> {state} {fp.seconds:.2f}s")
        return fp

    try:
        log(f"snapshot {len(production)} production units ({granularity}); holding {len(report.held_tests)} test path(s)")
        new_run = trial(production)
        report.new_run = new_run
        report.trials = trials
        if empty_suite(new_run):
            report.status = "EMPTY"
            report.chaff = production
            report.notes.append(
                "test command collected no tests (unittest/pytest exit 5 or 'Ran 0 tests'); "
                "not BROKEN — pass --cmd for this repo's real suite"
            )
            return report
        if not new_run.ok:
            report.status = "BROKEN"
            report.witnesses = {"NEW": parse_witnesses(new_run.output)}
            report.notes.append("refusing to isolate while the new tree is already red")
            report.chaff = production
            return report

        splice_run = trial([])
        report.splice_run = splice_run
        report.trials = trials
        if splice_run.ok:
            report.status = "LOOSE"
            report.chaff = production
            report.notes.append("tests pass with every production hunk reverted")
            return report

        splice_witnesses = parse_witnesses(splice_run.output)
        if unbuildable(splice_run.output, splice_witnesses):
            report.notes.append("splice is unbuildable (new tests import new production); isolating anyway")

        def interesting(subset: list[Hunk]) -> bool:
            return trial(subset).ok

        wheat = ddmin(production, interesting, log)
        confirmed: list[Hunk] = []
        for i, h in enumerate(wheat):
            rest = wheat[:i] + wheat[i + 1 :]
            if rest and interesting(rest):
                continue
            confirmed.append(h)
            dropped = trial(rest)
            report.witnesses[h.id] = parse_witnesses(dropped.output)
        wheat = sorted(confirmed or wheat, key=lambda c: (c.path, c.hunk_index or 0))
        wheat_ids = {c.id for c in wheat}
        report.wheat = wheat
        report.chaff = [c for c in production if c.id not in wheat_ids]
        report.status = "LOCKED" if wheat else "UNBUILDABLE"
        report.trials = trials
        if not wheat:
            report.notes.append("splice fails, but no production subset makes tests pass")
        return report
    finally:
        report.trials = trials
        sandbox.close()


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cinch",
        description="Emit the 1-minimal production hunks that the current tests require. "
        "Tests stay at NEW. Docs and debug prints that tests do not veto are chaff.",
        epilog="Example: cinch -- python3 -m unittest discover -s tests -q",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--base", default="HEAD", help="baseline ref (default: HEAD)")
    p.add_argument("-C", "--repo", default=".", help="repository path")
    p.add_argument("--cmd", default=None, help="test command (default: auto-detect, or pass after --)")
    p.add_argument(
        "--format",
        choices=("text", "paths", "json", "patch"),
        default="text",
        help="output format",
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
    p.add_argument("--list", action="store_true", help="classify dirty paths; do not run tests")
    p.add_argument("--max-trials", type=int, default=200)
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--version", action="version", version=f"cinch {VERSION}")
    p.add_argument("command", nargs=argparse.REMAINDER, help="test command after --")
    return p


def emit(report: Report, fmt: str, sandbox_by_path: dict[str, list[Hunk]] | None) -> int:
    if fmt == "paths":
        seen: set[str] = set()
        for c in report.wheat:
            if c.path in seen:
                continue
            seen.add(c.path)
            print(c.path)
        return status_exit(report.status)
    if fmt == "patch":
        by_path = sandbox_by_path or {}
        if not by_path:
            by_path = {}
            for h in report.wheat + report.chaff:
                by_path.setdefault(h.path, []).append(h)
        sys.stdout.write(wheat_patch(report.wheat, by_path))
        return status_exit(report.status)
    if fmt == "json":
        json.dump(report_to_json(report), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return status_exit(report.status)
    sys.stdout.write(format_human(report))
    return status_exit(report.status)


def status_exit(status: str) -> int:
    return {
        "LOCKED": 0,
        "CLEAN": 0,
        "LOOSE": 2,
        "BROKEN": 3,
        "UNBUILDABLE": 4,
        "EMPTY": 5,
    }.get(status, 1)


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    fmt = "json" if args.json else args.format
    try:
        repo = repo_root(Path(args.repo).resolve())
    except CinchError as e:
        print(f"cinch: {e}", file=sys.stderr)
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

    if args.list:
        changes = list_changes(repo, args.base, args.granularity, keep)
        payload = {
            "base": args.base,
            "cmd": cmd,
            "units": [
                {
                    "id": c.id,
                    "path": c.path,
                    "kind": c.kind,
                    "role": c.role,
                    "header": c.hunk_header,
                }
                for c in changes
            ],
            "production": [c.id for c in changes if c.role == "production"],
            "held_tests": sorted({c.path for c in changes if c.role == "test"}),
            "ignored": sorted({c.path for c in changes if c.role == "other"}),
        }
        if fmt == "json":
            json.dump(payload, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"cinch --list  base={args.base}")
            print(f"cmd    {' '.join(cmd)}")
            print(f"prod   {len(payload['production'])} production unit(s)")
            for c in changes:
                if c.role == "production":
                    print(f"  production  {c.label()}")
            for p in payload["held_tests"]:
                print(f"  test        {p}  (held)")
            for p in payload["ignored"]:
                print(f"  ignored     {p}")
        return 0

    try:
        report = run_cinch(
            repo=repo,
            base=args.base,
            cmd=cmd,
            timeout=args.timeout,
            keep=keep,
            granularity=args.granularity,
            max_trials=args.max_trials,
            log=log,
        )
    except CinchError as e:
        print(f"cinch: {e}", file=sys.stderr)
        return e.exit_code

    by_path: dict[str, list[Hunk]] = {}
    for h in report.wheat + report.chaff:
        by_path.setdefault(h.path, []).append(h)
    return emit(report, fmt, by_path)


if __name__ == "__main__":
    sys.exit(main())
