#!/usr/bin/env python3
"""tock: 1-minimal production hunks the current tests require."""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

VERSION = "0.2.0"

SOURCE_EXTENSIONS = {
    ".bash",
    ".c",
    ".cc",
    ".cjs",
    ".cpp",
    ".cs",
    ".cxx",
    ".go",
    ".graphql",
    ".h",
    ".hpp",
    ".hs",
    ".java",
    ".jl",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".lua",
    ".m",
    ".mjs",
    ".mm",
    ".php",
    ".proto",
    ".py",
    ".pyi",
    ".r",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".sql",
    ".svelte",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
    ".zsh",
}
SPECIAL_SOURCE_NAMES = {"makefile", "justfile", "dockerfile", "cmakelists.txt"}

TEST_DIR_NAMES = {"__tests__", "spec", "specs", "test", "testing", "tests"}
FIXTURE_DIR_NAMES = {
    "__snapshots__",
    "expected",
    "fixtures",
    "golden",
    "snapshots",
    "test_data",
    "testdata",
}
GENERATED_DIR_NAMES = {
    ".eggs",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    "__pycache__",
}
GENERATED_SUFFIXES = (".pyc", ".pyo", ".pyd")
SKIP_DIR_NAMES = {
    ".build",
    ".cinch-tmp",
    ".git",
    ".hg",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    ".vscode",
    "DerivedData",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "venv",
}
LINK_DIR_NAMES = (".build", ".venv", "DerivedData", "node_modules", "target", "vendor", "venv")

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
    re.IGNORECASE | re.VERBOSE,
)
EMPTY_SUITE_RE = re.compile(
    r"(NO TESTS RAN|collected 0 items|Ran 0 tests in|running 0 tests)",
    re.IGNORECASE,
)
FAIL_LINE_RE = re.compile(r"^(FAIL|ERROR|FAILED):\s+(\S+)", re.MULTILINE)
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")
CARGO_FAILED_RE = re.compile(r"^test\s+(\S+)\s+\.\.\.\s+FAILED", re.MULTILINE)
PYTEST_FAILED_RE = re.compile(r"^FAILED\s+(\S+::\S+|\S+\.py\S*)", re.MULTILINE)
IMPORTISH_RE = re.compile(
    r"(ImportError|ModuleNotFoundError|SyntaxError|cannot find (crate|value|type|module)|"
    r"error: could not compile|unresolved import|cannot find type)",
    re.IGNORECASE,
)


class TockError(Exception):
    pass


class PatchError(Exception):
    pass


@dataclass
class Hunk:
    path: str
    kind: str
    role: str
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


@dataclass
class RunResult:
    exit_code: int
    seconds: float
    output: str
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    @property
    def failed(self) -> bool:
        """Assertion/load failure. A timeout is neither pass nor fail."""
        return not self.ok and not self.timed_out


@dataclass
class Report:
    status: str
    base: str
    cmd: list[str]
    trials: int
    wheat: list[Hunk]
    chaff: list[Hunk]
    held_tests: list[str]
    ignored: list[str]
    witnesses: dict[str, list[str]]
    new_run: RunResult | None
    splice_run: RunResult | None
    notes: list[str]
    granularity: str
    production_units: int


class Sandbox:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="tock-")
        self.path = Path(self._tmp.name)

    def cleanup(self) -> None:
        self._tmp.cleanup()


def git(
    args: list[str], cwd: Path, check: bool = True, text: bool = True
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=text,
    )


def git_bytes(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return git(args, cwd=cwd, check=False, text=False)


def repo_root(start: Path) -> Path:
    proc = git(["rev-parse", "--show-toplevel"], cwd=start, check=False)
    if proc.returncode != 0:
        raise TockError(f"not a git repository: {start}")
    return Path(proc.stdout.strip())


def rev_parse(repo: Path, ref: str) -> str:
    proc = git(["rev-parse", "--short=12", ref], cwd=repo, check=False)
    if proc.returncode != 0:
        raise TockError(f"unknown ref: {ref}")
    return proc.stdout.strip()


def split_z(data: bytes) -> list[bytes]:
    if not data:
        return []
    return [p for p in data.split(b"\0") if p]


def posix_path(path: str) -> str:
    return path.replace("\\", "/")


def is_generated(path: str) -> bool:
    p = posix_path(path)
    parts = Path(p).parts
    if any(part in GENERATED_DIR_NAMES or part in SKIP_DIR_NAMES for part in parts):
        return True
    return Path(p).suffix in GENERATED_SUFFIXES


def should_skip_path(path: str) -> bool:
    return is_generated(path)


def is_test_path(path: str, extra_keep: list[re.Pattern[str]] | None = None) -> bool:
    p = posix_path(path)
    if extra_keep:
        for pat in extra_keep:
            if pat.search(p):
                return True
    parts = p.split("/")
    for part in parts[:-1]:
        if part in TEST_DIR_NAMES or part in FIXTURE_DIR_NAMES:
            return True
    base = parts[-1] if parts else p
    return bool(TEST_FILE_RE.search(base))


def is_source_path(path: str) -> bool:
    name = Path(posix_path(path)).name
    if name.lower() in SPECIAL_SOURCE_NAMES:
        return True
    return Path(name).suffix.lower() in SOURCE_EXTENSIONS


def path_role(path: str, extra_keep: list[re.Pattern[str]] | None = None) -> str:
    if is_test_path(path, extra_keep=extra_keep):
        return "test"
    if is_source_path(path):
        return "production"
    return "other"


def empty_suite(result: RunResult) -> bool:
    if result.exit_code == 5:
        return True
    return bool(EMPTY_SUITE_RE.search(result.output))


def parse_u0_hunks(diff_text: str) -> list[tuple[str, int, int, tuple[str, ...]]]:
    found: list[tuple[str, int, int, tuple[str, ...]]] = []
    header: str | None = None
    old_start = 0
    old_count = 0
    body: list[str] = []

    def flush() -> None:
        nonlocal header, body
        if header is None:
            return
        found.append((header, old_start, old_count, tuple(body)))
        header = None
        body = []

    for raw in diff_text.splitlines():
        line = raw.rstrip("\n")
        m = HUNK_RE.match(line)
        if m:
            flush()
            header = line
            old_start = int(m.group(1))
            old_count = int(m.group(2) if m.group(2) is not None else 1)
            body = []
            continue
        if header is None:
            continue
        if line.startswith("\\"):
            continue
        if line.startswith(("+", "-", " ")):
            body.append(line)
    flush()
    return found


def apply_hunks(head: bytes, hunks: list[Hunk]) -> bytes:
    try:
        text = head.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PatchError("binary head") from exc
    newline = "\n"
    if "\r\n" in text:
        newline = "\r\n"
    # Preserve whether the original ended with a newline by using splitlines(True)
    # then normalizing to a list of line bodies.
    raw_lines = text.splitlines()
    trailing_nl = text.endswith("\n") or text.endswith("\r")
    lines = list(raw_lines)
    ordered = sorted(
        hunks,
        key=lambda h: (h.old_start, h.hunk_index or 0),
        reverse=True,
    )
    for h in ordered:
        plus = [b[1:] for b in h.body if b.startswith("+")]
        if h.old_count == 0:
            idx = max(h.old_start, 0)
            lines[idx:idx] = plus
        else:
            start = max(h.old_start - 1, 0)
            end = start + h.old_count
            lines[start:end] = plus
    if not lines:
        out = ""
    else:
        out = newline.join(lines)
        if trailing_nl or plus_should_end(head, hunks):
            if not out.endswith(("\n", "\r")):
                out += newline
    return out.encode("utf-8")


def plus_should_end(head: bytes, hunks: list[Hunk]) -> bool:
    # Keep a trailing newline for ordinary text files that already had one.
    return head.endswith(b"\n") or head.endswith(b"\r\n") or bool(head)


def parse_witnesses(output: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()

    def add(name: str) -> None:
        name = name.strip().rstrip(",")
        if not name or name in seen:
            return
        seen.add(name)
        names.append(name)

    for m in FAIL_LINE_RE.finditer(output):
        add(m.group(2))
    for m in PYTEST_FAILED_RE.finditer(output):
        add(m.group(1))
    for m in CARGO_FAILED_RE.finditer(output):
        add(m.group(1))
    return names


def unbuildable(output: str, witnesses: list[str]) -> bool:
    if witnesses:
        return False
    return bool(IMPORTISH_RE.search(output))


def extra_env_for(repo: Path) -> dict[str, str]:
    return {}


def status_exit(status: str) -> int:
    return {
        "LOCKED": 0,
        "CLEAN": 0,
        "LOOSE": 2,
        "BROKEN": 3,
        "UNBUILDABLE": 4,
        "EMPTY": 5,
        "TIMEOUT": 6,
    }.get(status, 1)


def split_n(items: list, n: int) -> list[list]:
    if not items:
        return []
    n = max(1, min(n, len(items)))
    size, rem = divmod(len(items), n)
    out: list[list] = []
    i = 0
    for k in range(n):
        take = size + (1 if k < rem else 0)
        out.append(items[i : i + take])
        i += take
    return [part for part in out if part]


def detect_cmd(root: Path) -> list[str]:
    py = sys.executable
    if (root / "Cargo.toml").exists():
        return ["cargo", "test", "--offline", "--quiet"]
    if (root / "Package.swift").exists():
        return ["swift", "test"]
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        test = str((data.get("scripts") or {}).get("test") or "")
        if "vitest" in test:
            return ["npx", "--no-install", "vitest", "run"]
        if "jest" in test:
            return ["npx", "--no-install", "jest", "--ci"]
        if test.strip():
            return ["npm", "test", "--silent"]
    if (root / "pytest.ini").is_file():
        return [py, "-m", "pytest", "-q"]
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            text = pyproject.read_text(encoding="utf-8")
        except OSError:
            text = ""
        if "[tool.pytest" in text:
            return [py, "-m", "pytest", "-q"]
    if (root / "tests").is_dir():
        return [py, "-m", "unittest", "discover", "-s", "tests", "-q"]
    return [py, "-m", "unittest", "discover", "-q"]


def list_tree_files(repo: Path, ref: str) -> list[str]:
    proc = git_bytes(["ls-tree", "-r", "-z", "--name-only", ref], cwd=repo)
    if proc.returncode != 0:
        return []
    return [p.decode("utf-8", "surrogateescape") for p in split_z(proc.stdout)]


def list_worktree_files(repo: Path) -> list[str]:
    proc = git_bytes(
        ["ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo,
    )
    names = [p.decode("utf-8", "surrogateescape") for p in split_z(proc.stdout)]
    return expand_untracked(repo, names)


def expand_untracked(repo: Path, entries: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for rel in entries:
        rel = posix_path(rel)
        if rel in seen:
            continue
        full = repo / rel
        if full.is_dir() and not full.is_symlink():
            for dirpath, dirnames, filenames in os.walk(full):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
                for fn in filenames:
                    fp = Path(dirpath) / fn
                    try:
                        rel_f = fp.relative_to(repo).as_posix()
                    except ValueError:
                        continue
                    if rel_f not in seen and not should_skip_path(rel_f):
                        seen.add(rel_f)
                        out.append(rel_f)
            continue
        seen.add(rel)
        out.append(rel)
    return out


def union_paths(repo: Path, base: str) -> list[str]:
    names = set(list_tree_files(repo, base)) | set(list_worktree_files(repo))
    return sorted(p for p in names if p and not should_skip_path(p))


def git_show(repo: Path, ref: str, path: str) -> bytes | None:
    proc = git_bytes(["show", f"{ref}:{path}"], cwd=repo)
    if proc.returncode != 0:
        return None
    return proc.stdout


def read_worktree(path: Path) -> tuple[bytes | None, int | None]:
    if not path.exists() or path.is_dir():
        return None, None
    try:
        data = path.read_bytes()
    except OSError:
        return None, None
    try:
        mode = path.stat().st_mode
    except OSError:
        mode = None
    return data, mode


def write_worktree(path: Path, data: bytes | None, mode: int | None) -> None:
    if data is None:
        if path.exists() or path.is_symlink():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    if mode is not None:
        path.chmod(mode & 0o777)


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
    if granularity == "file":
        return [
            Hunk(
                path=path,
                kind=kind,
                role=role,
                head=head,
                wip=wip,
                mode=mode,
                hunk_index=None,
                hunk_header=None,
                old_start=1 if head else 0,
                old_count=(head or b"").count(b"\n") or (1 if head else 0),
                body=(),
            )
        ]
    if kind == "add":
        plus = []
        if wip is not None:
            try:
                text = wip.decode("utf-8")
            except UnicodeDecodeError:
                text = None
            if text is not None:
                lines = text.splitlines()
                plus = ["+" + ln for ln in lines]
        return [
            Hunk(
                path=path,
                kind=kind,
                role=role,
                head=head,
                wip=wip,
                mode=mode,
                hunk_index=1,
                hunk_header="(new file)",
                old_start=0,
                old_count=0,
                body=tuple(plus),
            )
        ]
    if kind == "delete":
        minus = []
        if head is not None:
            try:
                text = head.decode("utf-8")
            except UnicodeDecodeError:
                text = None
            if text is not None:
                minus = ["-" + ln for ln in text.splitlines()]
        nlines = len(minus) if minus else 1
        return [
            Hunk(
                path=path,
                kind=kind,
                role=role,
                head=head,
                wip=wip,
                mode=mode,
                hunk_index=1,
                hunk_header="(deleted)",
                old_start=1,
                old_count=nlines,
                body=tuple(minus),
            )
        ]
    proc = git(
        ["diff", "-U0", "--no-color", "--no-ext-diff", base, "--", path],
        cwd=repo,
        check=False,
    )
    parsed = parse_u0_hunks(proc.stdout or "")
    if not parsed:
        return [
            Hunk(
                path=path,
                kind=kind,
                role=role,
                head=head,
                wip=wip,
                mode=mode,
                hunk_index=1,
                hunk_header="(binary or whole file)",
                old_start=1,
                old_count=0,
                body=(),
            )
        ]
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


def list_changes(
    repo: Path, base: str, granularity: str, keep: list[re.Pattern[str]]
) -> list[Hunk]:
    changes: list[Hunk] = []
    for path in union_paths(repo, base):
        if should_skip_path(path):
            continue
        head = git_show(repo, base, path)
        wip, mode = read_worktree(repo / path)
        if head == wip:
            continue
        if head is None:
            kind = "add"
        elif wip is None:
            kind = "delete"
        else:
            kind = "modify"
        role = path_role(path, extra_keep=keep)
        changes.extend(
            hunks_for_file(repo, base, path, kind, role, head, wip, mode, granularity)
        )
    return changes


def reconstruct(chosen: list[Hunk], all_hunks: list[Hunk]) -> tuple[bytes | None, int | None]:
    if not all_hunks:
        return None, None
    sample = all_hunks[0]
    mode = sample.mode
    chosen_ids = {id(h) for h in chosen}
    selected = [h for h in all_hunks if id(h) in chosen_ids]
    if not selected:
        return sample.head, mode
    if len(selected) == len(all_hunks):
        return sample.wip, mode
    if sample.kind == "add":
        return sample.wip, mode
    if sample.kind == "delete":
        return None, mode
    if sample.head is None:
        return sample.wip, mode
    try:
        return apply_hunks(sample.head, selected), mode
    except (PatchError, UnicodeDecodeError, ValueError):
        return sample.wip if selected else sample.head, mode


def wheat_patch(wheat: list[Hunk], by_path: dict[str, list[Hunk]]) -> str:
    chunks: list[str] = []
    seen: set[str] = set()
    for h in wheat:
        if h.path in seen:
            continue
        seen.add(h.path)
        all_h = by_path.get(h.path) or [h]
        chosen = [x for x in wheat if x.path == h.path]
        new, _mode = reconstruct(chosen, all_h)
        old = all_h[0].head
        chunks.append(_unified(h.path, old, new))
    return "".join(chunks)


def _unified(path: str, old: bytes | None, new: bytes | None) -> str:
    def to_lines(data: bytes | None) -> list[str]:
        if data is None:
            return []
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-8", "replace")
        if text == "":
            return []
        lines = text.splitlines(keepends=True)
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        elif text.endswith("\n") and (not lines or lines[-1].endswith("\n")):
            pass
        return lines

    a = to_lines(old)
    b = to_lines(new)
    fromfile = "/dev/null" if old is None else f"a/{path}"
    tofile = "/dev/null" if new is None else f"b/{path}"
    diff = list(
        difflib.unified_diff(a, b, fromfile=fromfile, tofile=tofile, lineterm="\n")
    )
    return "".join(diff)


def link_existing_deps(repo: Path, dest: Path) -> None:
    for name in LINK_DIR_NAMES:
        src = repo / name
        if src.exists():
            target = dest / name
            if target.exists() or target.is_symlink():
                continue
            try:
                target.symlink_to(src)
            except OSError:
                pass


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest, follow_symlinks=True)


def materialize_new(repo: Path, dest: Path, base: str, keep: list[re.Pattern[str]]) -> None:
    for rel in union_paths(repo, base):
        if should_skip_path(rel):
            continue
        src = repo / rel
        if src.is_file():
            _copy_file(src, dest / rel)
    link_existing_deps(repo, dest)


def materialize_subset(
    repo: Path,
    dest: Path,
    base: str,
    keep: list[re.Pattern[str]],
    chosen: list[Hunk],
    all_hunks: list[Hunk],
) -> None:
    by_path: dict[str, list[Hunk]] = {}
    for h in all_hunks:
        by_path.setdefault(h.path, []).append(h)
    chosen_by_path: dict[str, list[Hunk]] = {}
    for h in chosen:
        chosen_by_path.setdefault(h.path, []).append(h)
    for rel in union_paths(repo, base):
        if should_skip_path(rel):
            continue
        role = path_role(rel, extra_keep=keep)
        dest_path = dest / rel
        if role == "test":
            src = repo / rel
            if src.is_file():
                _copy_file(src, dest_path)
            continue
        if rel in by_path:
            hunks = by_path[rel]
            if hunks[0].role != "production":
                # ignored: leave at BASE
                head = hunks[0].head
                write_worktree(dest_path, head, hunks[0].mode)
                continue
            data, mode = reconstruct(chosen_by_path.get(rel, []), hunks)
            write_worktree(dest_path, data, mode)
            continue
        # unchanged path
        head = git_show(repo, base, rel)
        wip, mode = read_worktree(repo / rel)
        # tests already handled; production/other unchanged from base
        write_worktree(dest_path, head if head is not None else None, mode)
        if head is None and wip is not None and role == "test":
            write_worktree(dest_path, wip, mode)
    link_existing_deps(repo, dest)


def _kill_process_group(proc: subprocess.Popen[str]) -> None:
    def send(sig: int) -> None:
        try:
            os.killpg(proc.pid, sig)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.send_signal(sig)
            except (ProcessLookupError, OSError):
                pass

    send(signal.SIGTERM)
    try:
        proc.wait(timeout=1.0)
        return
    except subprocess.TimeoutExpired:
        pass
    send(signal.SIGKILL)
    try:
        proc.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        pass


def run_cmd(
    cmd: list[str],
    cwd: Path,
    timeout: float,
    extra_env: dict[str, str] | None = None,
) -> RunResult:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if extra_env:
        env.update(extra_env)
    t0 = time.perf_counter()
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            start_new_session=True,
        )
    except OSError as exc:
        return RunResult(127, time.perf_counter() - t0, str(exc), False)
    try:
        out, _ = proc.communicate(timeout=timeout)
        seconds = time.perf_counter() - t0
        code = proc.returncode if proc.returncode is not None else 0
        return RunResult(code, seconds, out or "", False)
    except subprocess.TimeoutExpired:
        _kill_process_group(proc)
        extra = ""
        try:
            leftover, _ = proc.communicate(timeout=0.5)
            extra = leftover or ""
        except (subprocess.TimeoutExpired, OSError, UnicodeDecodeError):
            extra = ""
        seconds = time.perf_counter() - t0
        msg = extra + f"[tock: timed out after {timeout}s]\n"
        return RunResult(124, seconds, msg, True)
    except UnicodeDecodeError as exc:
        _kill_process_group(proc)
        raise TockError(f"binary test output: {exc}") from exc


def _fmt_ids(hunks: list[Hunk]) -> str:
    return "[" + ", ".join(repr(h.id) for h in hunks) + "]"


def _run_arrow(result: RunResult) -> str:
    if result.timed_out:
        word = "timeout"
    elif result.exit_code == 0:
        word = "pass"
    else:
        word = f"fail({result.exit_code})"
    return f"  -> {word} {result.seconds:.2f}s"


def ddmin(
    changes: list[Hunk],
    interesting: Callable[[list[Hunk]], bool],
    log: Callable[[str], None],
) -> list[Hunk]:
    if not changes:
        return []
    cache: dict[frozenset[str], bool] = {}

    def test(subset: list[Hunk], kind: str) -> bool:
        key = frozenset(h.id for h in subset)
        log(f"try {len(subset)}/{len(changes)} {kind} {_fmt_ids(subset)}")
        if key in cache:
            return cache[key]
        ok = interesting(subset)
        cache[key] = ok
        return ok

    current = list(changes)
    n = 2
    while True:
        if len(current) == 1:
            return current
        subsets = split_n(current, min(n, len(current)))
        progressed = False
        for part in subsets:
            if test(part, "subset"):
                current = part
                n = 2
                changes = current
                progressed = True
                break
        if progressed:
            continue
        for part in subsets:
            comp = [h for h in current if h.id not in {x.id for x in part}]
            if not comp:
                continue
            if test(comp, "complement"):
                current = comp
                n = max(n - 1, 2)
                changes = current
                progressed = True
                break
        if progressed:
            continue
        if n >= len(current):
            return current
        n = min(len(current), n * 2)
        log(f"increase granularity n={n}")


def dump_hunk(h: Hunk, witnesses: dict[str, list[str]]) -> dict[str, object]:
    d: dict[str, object] = {
        "path": h.path,
        "kind": h.kind,
        "role": h.role,
        "id": h.id,
    }
    if h.hunk_index is not None:
        d["hunk"] = h.hunk_index
    if h.hunk_header:
        d["header"] = h.hunk_header
    w = witnesses.get(h.id) or []
    if w:
        d["witnesses"] = w
    return d


def dump_run(r: RunResult | None) -> dict[str, object] | None:
    if r is None:
        return None
    lines = r.output.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n").split("\n")
    if lines == [""]:
        tail: list[str] = []
    else:
        tail = lines[-8:]
    return {
        "exit_code": r.exit_code,
        "seconds": r.seconds,
        "timed_out": r.timed_out,
        "output_tail": tail,
    }


def report_to_json(report: Report) -> dict[str, object]:
    return {
        "status": report.status,
        "base": report.base,
        "cmd": report.cmd,
        "trials": report.trials,
        "granularity": report.granularity,
        "production_units": report.production_units,
        "wheat": [dump_hunk(h, {}) for h in report.wheat],
        "chaff": [dump_hunk(h, {}) for h in report.chaff],
        "held_tests": report.held_tests,
        "ignored": report.ignored,
        "witnesses": report.witnesses,
        "notes": report.notes,
        "new_run": dump_run(report.new_run),
        "splice_run": dump_run(report.splice_run),
    }


def _human_run_word(r: RunResult) -> str:
    if r.timed_out:
        return "timeout"
    if r.exit_code == 0:
        return "pass"
    return f"fail({r.exit_code})"


def _hunk_line(h: Hunk, witnesses: dict[str, list[str]]) -> str:
    kind = f"{h.kind:<7}"
    extra = ""
    if h.hunk_index is not None:
        header = h.hunk_header or ""
        extra = f"  #{h.hunk_index} {header}".rstrip()
    w = witnesses.get(h.id) or []
    locked = f"  locked by: {', '.join(w)}" if w else ""
    return f"  {kind}{h.path}{extra}{locked}"


def format_human(report: Report) -> str:
    lines: list[str] = []
    lines.append(
        f"tock  base={report.base}  status={report.status}  trials={report.trials}"
    )
    lines.append(f"cmd    {' '.join(report.cmd)}")
    lines.append(
        f"prod   {report.production_units} production unit(s)  granularity={report.granularity}"
    )
    if report.new_run is not None:
        word = _human_run_word(report.new_run)
        lines.append(
            f"NEW    {word:<12} {report.new_run.seconds:.2f}s   (tests@new, production@new)"
        )
    if report.splice_run is not None:
        word = _human_run_word(report.splice_run)
        lines.append(
            f"SPLICE {word:<12} {report.splice_run.seconds:.2f}s   (tests@new, production@base)"
        )
    lines.append("")
    blurbs = {
        "LOCKED": "tests require this production subset — it is the lockset, not the fingerprint wheat",
        "LOOSE": "tests still pass on base production — nothing is locked",
        "CLEAN": "no production units differ from base (tests/docs may still be dirty)",
        "BROKEN": "tests already fail on the new tree — fix them before asking tock",
        "EMPTY": "test command collected no tests — not a red suite; pass --cmd",
        "UNBUILDABLE": "no production subset could be spliced into a green suite",
        "TIMEOUT": "a splice trial timed out — timeout is unknown, not guilt; no wheat minted",
    }
    if report.status in blurbs:
        lines.append(blurbs[report.status])
    if report.held_tests:
        lines.append("held tests (always NEW, never wheat):")
        for p in report.held_tests:
            lines.append(f"  {p}")
    if report.ignored:
        lines.append("ignored (not production source):")
        for p in report.ignored:
            lines.append(f"  {p}")
    w_files = len({h.path for h in report.wheat})
    c_files = len({h.path for h in report.chaff})
    lines.append(f"wheat ({len(report.wheat)} units / {w_files} files):")
    if report.wheat:
        for h in report.wheat:
            lines.append(_hunk_line(h, report.witnesses))
    else:
        lines.append("  (empty)")
    lines.append(f"chaff ({len(report.chaff)} units / {c_files} files):")
    if report.chaff:
        for h in report.chaff:
            lines.append(_hunk_line(h, {}))
    else:
        lines.append("  (empty)")
    for n in report.notes:
        lines.append(f"note: {n}")
    if report.status in {"BROKEN", "EMPTY"} and report.new_run and report.new_run.output.strip():
        lines.append("new tail:")
        tail = report.new_run.output.replace("\r\n", "\n").rstrip("\n").split("\n")[-8:]
        for row in tail:
            lines.append(f"  {row}")
    if report.status == "TIMEOUT" and report.splice_run and report.splice_run.output.strip():
        lines.append("splice tail:")
        tail = report.splice_run.output.replace("\r\n", "\n").rstrip("\n").split("\n")[-8:]
        for row in tail:
            lines.append(f"  {row}")
    return "\n".join(lines) + "\n"


def format_list_human(
    base: str, cmd: list[str], changes: list[Hunk]
) -> str:
    prod = [h for h in changes if h.role == "production"]
    lines = [
        f"tock --list  base={base}",
        f"cmd    {' '.join(cmd)}",
        f"prod   {len(prod)} production unit(s)",
    ]
    for h in prod:
        header = h.hunk_header or ""
        idx = f"  #{h.hunk_index}" if h.hunk_index is not None else ""
        lines.append(f"  {'production':<12}{h.kind:<7}{h.path}{idx} {header}".rstrip())
    seen_test: set[str] = set()
    for h in changes:
        if h.role != "test" or h.path in seen_test:
            continue
        seen_test.add(h.path)
        lines.append(f"  {'test':<12}{h.path}  (held)")
    seen_ign: set[str] = set()
    for h in changes:
        if h.role != "other" or h.path in seen_ign:
            continue
        seen_ign.add(h.path)
        lines.append(f"  {'ignored':<12}{h.path}")
    return "\n".join(lines) + "\n"


def emit(report: Report, fmt: str, sandbox_by_path: dict[str, list[Hunk]] | None) -> int:
    if fmt == "json":
        json.dump(report_to_json(report), sys.stdout, indent=2)
        sys.stdout.write("\n")
    elif fmt == "paths":
        seen: set[str] = set()
        for h in report.wheat:
            if h.path not in seen:
                seen.add(h.path)
                sys.stdout.write(h.path + "\n")
    elif fmt == "patch":
        sys.stdout.write(wheat_patch(report.wheat, sandbox_by_path or {}))
    else:
        sys.stdout.write(format_human(report))
    return status_exit(report.status)


def run_tock(
    repo: Path,
    base: str,
    cmd: list[str],
    timeout: float,
    keep: list[re.Pattern[str]],
    granularity: str,
    max_trials: int,
    log: Callable[[str], None],
) -> Report:
    changes = list_changes(repo, base, granularity, keep)
    prod = [h for h in changes if h.role == "production"]
    held = sorted({h.path for h in changes if h.role == "test"})
    ignored = sorted({h.path for h in changes if h.role == "other"})
    by_path: dict[str, list[Hunk]] = {}
    for h in changes:
        by_path.setdefault(h.path, []).append(h)
    sha = rev_parse(repo, base)
    base_label = f"{base} ({sha})"
    trials = 0
    notes: list[str] = []
    witnesses: dict[str, list[str]] = {}

    def count_run(result: RunResult) -> RunResult:
        nonlocal trials
        trials += 1
        log(_run_arrow(result))
        return result

    def trial(chosen: list[Hunk], copy_new: bool) -> RunResult:
        nonlocal trials
        if trials >= max_trials:
            raise TockError(f"exceeded --max-trials {max_trials}")
        box = Sandbox()
        try:
            if copy_new:
                materialize_new(repo, box.path, base, keep)
            else:
                materialize_subset(repo, box.path, base, keep, chosen, prod)
            return count_run(run_cmd(cmd, box.path, timeout, extra_env_for(repo)))
        finally:
            box.cleanup()

    if not prod:
        log(
            f"snapshot 0 production units ({granularity}); holding {len(held)} test path(s)"
        )
        new_run = trial([], copy_new=True)
        if empty_suite(new_run):
            return Report(
                status="EMPTY",
                base=base_label,
                cmd=cmd,
                trials=trials,
                wheat=[],
                chaff=[],
                held_tests=held,
                ignored=ignored,
                witnesses={},
                new_run=new_run,
                splice_run=None,
                notes=[
                    "test command collected no tests (unittest/pytest exit 5 or 'Ran 0 tests'); "
                    "not BROKEN — pass --cmd for this repo's real suite"
                ],
                granularity=granularity,
                production_units=0,
            )
        if not new_run.ok:
            w = parse_witnesses(new_run.output)
            return Report(
                status="BROKEN",
                base=base_label,
                cmd=cmd,
                trials=trials,
                wheat=[],
                chaff=[],
                held_tests=held,
                ignored=ignored,
                witnesses={"NEW": w},
                new_run=new_run,
                splice_run=None,
                notes=["refusing to isolate while the new tree is already red"],
                granularity=granularity,
                production_units=0,
            )
        return Report(
            status="CLEAN",
            base=base_label,
            cmd=cmd,
            trials=trials,
            wheat=[],
            chaff=[],
            held_tests=held,
            ignored=ignored,
            witnesses={},
            new_run=new_run,
            splice_run=None,
            notes=["no production source units differ from base"],
            granularity=granularity,
            production_units=0,
        )

    log(f"snapshot {len(prod)} production units ({granularity}); holding {len(held)} test path(s)")
    new_run = trial(prod, copy_new=True)
    if empty_suite(new_run):
        return Report(
            status="EMPTY",
            base=base_label,
            cmd=cmd,
            trials=trials,
            wheat=[],
            chaff=prod,
            held_tests=held,
            ignored=ignored,
            witnesses={},
            new_run=new_run,
            splice_run=None,
            notes=[
                "test command collected no tests (unittest/pytest exit 5 or 'Ran 0 tests'); "
                "not BROKEN — pass --cmd for this repo's real suite"
            ],
            granularity=granularity,
            production_units=len(prod),
        )
    if not new_run.ok:
        w = parse_witnesses(new_run.output)
        if w:
            witnesses["NEW"] = w
        else:
            witnesses["NEW"] = []
        return Report(
            status="BROKEN",
            base=base_label,
            cmd=cmd,
            trials=trials,
            wheat=[],
            chaff=prod,
            held_tests=held,
            ignored=ignored,
            witnesses=witnesses,
            new_run=new_run,
            splice_run=None,
            notes=["refusing to isolate while the new tree is already red"],
            granularity=granularity,
            production_units=len(prod),
        )

    splice_run = trial([], copy_new=False)
    splice_w = parse_witnesses(splice_run.output)
    if splice_run.ok:
        return Report(
            status="LOOSE",
            base=base_label,
            cmd=cmd,
            trials=trials,
            wheat=[],
            chaff=prod,
            held_tests=held,
            ignored=ignored,
            witnesses={},
            new_run=new_run,
            splice_run=splice_run,
            notes=["tests pass with every production hunk reverted"],
            granularity=granularity,
            production_units=len(prod),
        )

    fail_witness: dict[str, list[str]] = {}
    saw_timeout = splice_run.timed_out
    if splice_run.timed_out:
        notes.append(
            "base production timed out; timeout is unknown, not a test failure"
        )
    elif unbuildable(splice_run.output, splice_w):
        notes.append("splice is unbuildable (new tests import new production); isolating anyway")
    if splice_run.failed:
        for h in prod:
            fail_witness[h.id] = splice_w

    def interesting(subset: list[Hunk]) -> bool:
        nonlocal saw_timeout
        result = trial(subset, copy_new=False)
        if result.timed_out:
            saw_timeout = True
            # Unknown: not sufficient, and not a fail witness. Do not mint wheat.
            return False
        w = parse_witnesses(result.output)
        if result.failed:
            missing = [h.id for h in prod if h.id not in {x.id for x in subset}]
            for hid in missing:
                fail_witness[hid] = w
            return False
        return True

    wheat = ddmin(prod, interesting, log)
    if saw_timeout:
        dropped = [h for h in wheat if h.id not in fail_witness]
        if dropped:
            notes.append(
                "timed-out splice trials were not treated as failures; "
                "a timeout is not a fingerprint change and must not mint wheat"
            )
            wheat = [h for h in wheat if h.id in fail_witness]
        if not wheat:
            return Report(
                status="TIMEOUT",
                base=base_label,
                cmd=cmd,
                trials=trials,
                wheat=[],
                chaff=list(prod),
                held_tests=held,
                ignored=ignored,
                witnesses={},
                new_run=new_run,
                splice_run=splice_run,
                notes=notes
                + [
                    "splice timed out; refusing to name a hunk guilty on a killed child"
                ],
                granularity=granularity,
                production_units=len(prod),
            )

    wheat_ids = {h.id for h in wheat}
    chaff = [h for h in prod if h.id not in wheat_ids]
    wmap: dict[str, list[str]] = {}
    for h in wheat:
        wmap[h.id] = fail_witness.get(h.id, [])
    return Report(
        status="LOCKED",
        base=base_label,
        cmd=cmd,
        trials=trials,
        wheat=wheat,
        chaff=chaff,
        held_tests=held,
        ignored=ignored,
        witnesses=wmap,
        new_run=new_run,
        splice_run=splice_run,
        notes=notes,
        granularity=granularity,
        production_units=len(prod),
    )


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tock",
        description=(
            "Emit the 1-minimal production hunks that the current tests require. "
            "Tests stay at NEW. A splice timeout is unknown, not fail — it must not mint wheat."
        ),
        epilog="Example: tock -- python3 -m unittest discover -s tests -q",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--base", default="HEAD", help="baseline ref (default: HEAD)")
    p.add_argument("-C", "--repo", default=".", help="repository path")
    p.add_argument(
        "--cmd",
        default=None,
        help="test command (default: auto-detect, or pass after --)",
    )
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
    p.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="seconds per test run (a timeout is unknown, not fail; it must not mint wheat)",
    )
    p.add_argument(
        "--keep",
        action="append",
        default=[],
        metavar="REGEX",
        help="treat matching paths as tests",
    )
    p.add_argument("--list", action="store_true", help="classify dirty paths; do not run tests")
    p.add_argument("--max-trials", type=int, default=200, dest="max_trials")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--version", action="version", version=f"tock {VERSION}")
    p.add_argument("command", nargs=argparse.REMAINDER, help="test command after --")
    return p


def _parse_cmd(args: argparse.Namespace, repo: Path) -> list[str]:
    rest = list(args.command or [])
    if rest[:1] == ["--"]:
        rest = rest[1:]
    if rest:
        return rest
    if args.cmd:
        return shlex.split(args.cmd)
    return detect_cmd(repo)


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    fmt = "json" if args.json else args.format
    log: Callable[[str], None]
    if args.verbose:
        log = lambda m: print(m, file=sys.stderr)
    else:
        log = lambda m: None
    try:
        repo = repo_root(Path(args.repo).resolve())
        keep: list[re.Pattern[str]] = []
        for raw in args.keep:
            try:
                keep.append(re.compile(raw))
            except re.error as exc:
                raise TockError(f"invalid --keep regex {raw!r}: {exc}") from exc
        cmd = _parse_cmd(args, repo)
        if args.list:
            changes = list_changes(repo, args.base, args.granularity, keep)
            # collapse --list test/ignored to unique paths while keeping production hunks
            shown: list[Hunk] = []
            seen_nonprod: set[tuple[str, str]] = set()
            for h in changes:
                if h.role == "production":
                    shown.append(h)
                    continue
                key = (h.role, h.path)
                if key in seen_nonprod:
                    continue
                seen_nonprod.add(key)
                shown.append(h)
            if fmt == "json":
                payload = {
                    "base": args.base,
                    "cmd": cmd,
                    "units": [
                        {
                            "id": h.id,
                            "path": h.path,
                            "kind": h.kind,
                            "role": h.role,
                            **({"header": h.hunk_header} if h.hunk_header else {}),
                        }
                        for h in changes
                    ],
                    "production": [h.id for h in changes if h.role == "production"],
                    "held_tests": sorted({h.path for h in changes if h.role == "test"}),
                    "ignored": sorted({h.path for h in changes if h.role == "other"}),
                }
                json.dump(payload, sys.stdout, indent=2)
                sys.stdout.write("\n")
            else:
                sys.stdout.write(format_list_human(args.base, cmd, shown))
            return 0
        report = run_tock(
            repo=repo,
            base=args.base,
            cmd=cmd,
            timeout=args.timeout,
            keep=keep,
            granularity=args.granularity,
            max_trials=args.max_trials,
            log=log,
        )
        by_path: dict[str, list[Hunk]] = {}
        for h in report.wheat + report.chaff:
            by_path.setdefault(h.path, []).append(h)
        return emit(report, fmt, by_path)
    except TockError as exc:
        print(f"tock: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
