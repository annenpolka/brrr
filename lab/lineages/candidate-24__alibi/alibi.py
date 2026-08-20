#!/usr/bin/env python3
"""alibi — transplant current tests onto another revision's production sources.

A production change is LOCKED when the current tests fail against the base
revision's non-test files. Coverage is not the question; veto-power is.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".alibi-tmp",
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

# Heavy dependency dirs: symlink from the original tree so spliced tests can run.
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

# Test-adjacent trees: keep from NEW, never overlay from base.
FIXTURE_DIR_NAMES = {
    "fixtures",
    "golden",
    "testdata",
    "test_data",
    "snapshots",
    "__snapshots__",
    "expected",
}

# Only these count as production (behavior). Docs/config stay at NEW
# so a dirty README cannot create a fake LOOSE/LOCKED.
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

FAIL_LINE_RE = re.compile(
    r"^(FAIL|ERROR|FAILED):\s+(\S+)",
    re.MULTILINE,
)
PYTEST_FAILED_RE = re.compile(
    r"^FAILED\s+(\S+::\S+|\S+\.py\S*)",
    re.MULTILINE,
)
CARGO_FAILED_RE = re.compile(
    r"^test\s+(\S+)\s+\.\.\.\s+FAILED",
    re.MULTILINE,
)
IMPORTISH_RE = re.compile(
    r"(ImportError|ModuleNotFoundError|SyntaxError|cannot find (crate|value|type|module)|error: could not compile|unresolved import|cannot find type)",
    re.IGNORECASE,
)


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
    """How a path is treated in the splice."""

    path: str
    role: str  # test | production | link
    source: str  # new | base | deleted | symlink


@dataclass
class Report:
    status: str
    base: str
    new: str
    cmd: list[str]
    production_changed: list[str]
    tests_kept: list[str]
    plan: list[FilePlan] = field(default_factory=list)
    new_run: RunResult | None = None
    splice_run: RunResult | None = None
    witnesses: list[str] = field(default_factory=list)
    per_path: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


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
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
    )


def repo_root(start: Path) -> Path:
    proc = git(["rev-parse", "--show-toplevel"], cwd=start, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"alibi: not a git repository: {start}")
    return Path(proc.stdout.strip()).resolve()


def rev_parse(repo: Path, ref: str) -> str:
    proc = git(["rev-parse", "--verify", ref], cwd=repo, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"alibi: unknown revision {ref!r}")
    return proc.stdout.strip()


def list_tree_files(repo: Path, ref: str) -> list[str]:
    proc = git(["ls-tree", "-r", "--name-only", ref], cwd=repo)
    return [ln for ln in proc.stdout.splitlines() if ln]


def list_worktree_files(repo: Path) -> list[str]:
    proc = git(["ls-files", "-co", "--exclude-standard"], cwd=repo)
    files = [ln for ln in proc.stdout.splitlines() if ln]
    # Also include tracked files that are deleted in the worktree? ls-files -co
    # still lists them if cached. Filter to those that exist or are staged.
    return files


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


def should_skip_path(path: str) -> bool:
    parts = Path(path.replace("\\", "/")).parts
    return any(p in SKIP_DIR_NAMES for p in parts)


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
    # Python 3.14+ unittest discover from '.' skips tests/ unless it is a
    # package or we pass -s. Prefer an explicit start directory.
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


def classify_splice_failure(output: str, witnesses: list[str]) -> str:
    """LOCKED if assertions fire; UNBUILDABLE if the suite cannot even load."""
    assertion = "AssertionError" in output or "FAIL:" in output or any("::" in w for w in witnesses)
    importish = bool(IMPORTISH_RE.search(output))
    compile_fail = bool(
        re.search(r"could not compile|error\[E\d+\]", output, re.IGNORECASE)
    )
    collection_error = any("FailedTest" in w or w.startswith("ERROR") for w in witnesses)
    if (importish or compile_fail or collection_error) and not assertion:
        return "UNBUILDABLE"
    return "LOCKED"


def run_cmd(cmd: list[str], cwd: Path, timeout: float, extra_env: dict[str, str] | None = None) -> RunResult:
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Isolated from the caller's cwd imports.
    env["PYTHONPATH"] = str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
    if extra_env:
        env.update(extra_env)
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        seconds = time.monotonic() - t0
        output = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        return RunResult(proc.returncode, seconds, output, timed_out=False)
    except FileNotFoundError as e:
        seconds = time.monotonic() - t0
        return RunResult(127, seconds, str(e), timed_out=False)
    except subprocess.TimeoutExpired as e:
        seconds = time.monotonic() - t0
        out = ""
        if e.stdout:
            out += e.stdout if isinstance(e.stdout, str) else e.stdout.decode("utf-8", "replace")
        if e.stderr:
            out += "\n" + (e.stderr if isinstance(e.stderr, str) else e.stderr.decode("utf-8", "replace"))
        out += f"\n[alibi: timed out after {timeout}s]"
        return RunResult(124, seconds, out, timed_out=True)


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
    return sorted(p for p in s if not should_skip_path(p))


def production_changed(repo: Path, base: str, new_ref: str | None, keep: list[re.Pattern]) -> list[str]:
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


def link_existing_deps(repo: Path, dest: Path) -> list[FilePlan]:
    plans: list[FilePlan] = []
    for name in sorted(LINK_DIR_NAMES):
        src = repo / name
        if src.exists():
            target = dest / name
            if not target.exists():
                target.symlink_to(src)
                plans.append(FilePlan(name, "link", "symlink"))
    # Cargo: reuse the original target dir even if we also symlink.
    return plans


def write_bytes(dest: Path, path: str, data: bytes) -> None:
    p = dest / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def materialize(
    repo: Path,
    dest: Path,
    base: str,
    new_ref: str | None,
    keep: list[re.Pattern],
    overlay: str,
    only_paths: set[str] | None = None,
) -> list[FilePlan]:
    """Build a tree in dest.

    overlay:
      'none' — current tests AND current production (the NEW tree)
      'all'  — current tests, production from base
      'paths' — current everything, then overlay only_paths from base
    """
    plans: list[FilePlan] = []
    new_paths = set(list_new_paths(repo, new_ref))
    base_paths = set(list_tree_files(repo, base))
    all_paths = sorted((new_paths | base_paths) - {".git"})

    for path in all_paths:
        if should_skip_path(path):
            continue
        role = path_role(path, keep)
        if overlay == "none":
            data = new_bytes(repo, new_ref, path)
            if data is None:
                continue
            write_bytes(dest, path, data)
            plans.append(FilePlan(path, role, "new"))
            continue

        if overlay == "all":
            if role != "production":
                data = new_bytes(repo, new_ref, path)
                if data is None:
                    continue
                write_bytes(dest, path, data)
                plans.append(FilePlan(path, role, "new"))
            else:
                data = git_show(repo, base, path)
                if data is None:
                    # added production file: omit it
                    plans.append(FilePlan(path, "production", "deleted"))
                    continue
                write_bytes(dest, path, data)
                plans.append(FilePlan(path, "production", "base"))
            continue

        # overlay == 'paths': start from NEW, overlay selected production paths from base
        if role != "production" or only_paths is None or path not in only_paths:
            data = new_bytes(repo, new_ref, path)
            if data is None:
                continue
            write_bytes(dest, path, data)
            plans.append(FilePlan(path, role, "new"))
        else:
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


def extract_status(new_run: RunResult, splice_run: RunResult, n_changed: int) -> tuple[str, list[str]]:
    if not new_run.ok:
        return "BROKEN", parse_witnesses(new_run.output)
    if n_changed == 0:
        return "CLEAN", []
    if splice_run.ok:
        return "LOOSE", []
    witnesses = parse_witnesses(splice_run.output)
    return classify_splice_failure(splice_run.output, witnesses), witnesses


def cmd_to_list(cmd: str | list[str]) -> list[str]:
    if isinstance(cmd, list):
        return cmd
    return __import__("shlex").split(cmd)


def format_human(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"alibi  base={report.base}  new={report.new}  status={report.status}")
    lines.append(f"cmd    {' '.join(report.cmd)}")
    n = len(report.production_changed)
    lines.append(f"prod   {n} path(s) differ from base (production source)")
    if report.production_changed:
        show = report.production_changed[:12]
        for p in show:
            tag = report.per_path.get(p, "")
            extra = f"  {tag}" if tag else ""
            lines.append(f"         {p}{extra}")
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
    meaning = {
        "LOCKED": "tests veto base production — the production diff is witnessed",
        "LOOSE": "tests still pass on base production — the production diff has no alibi",
        "BROKEN": "tests already fail on the new tree — fix them before asking alibi",
        "UNBUILDABLE": "spliced tree cannot load/compile tests — API shape changed, or tests import new symbols",
        "CLEAN": "no production files differ from base",
    }.get(report.status, "")
    if meaning:
        lines.append(meaning)
    if report.witnesses:
        lines.append("witnesses:")
        for w in report.witnesses[:20]:
            lines.append(f"  {w}")
    if report.per_path:
        lines.append("per-path:")
        width = max(len(p) for p in report.per_path) if report.per_path else 0
        for p, st in report.per_path.items():
            lines.append(f"  {st:12} {p:<{width}}")
    for note in report.notes:
        lines.append(f"note: {note}")
    if report.status == "BROKEN" and report.new_run and not report.new_run.ok:
        tail = report.new_run.output.strip().splitlines()[-16:]
        if tail:
            lines.append("new tail:")
            for ln in tail:
                lines.append(f"  {ln}")
    if report.splice_run and not report.splice_run.ok:
        tail = report.splice_run.output.strip().splitlines()[-16:]
        if tail:
            lines.append("splice tail:")
            for ln in tail:
                lines.append(f"  {ln}")
    return "\n".join(lines) + "\n"


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
        "base": report.base,
        "new": report.new,
        "cmd": report.cmd,
        "production_changed": report.production_changed,
        "tests_kept": report.tests_kept,
        "witnesses": report.witnesses,
        "per_path": report.per_path,
        "notes": report.notes,
        "new_run": run(report.new_run),
        "splice_run": run(report.splice_run),
        "plan": [{"path": p.path, "role": p.role, "source": p.source} for p in report.plan],
    }


def run_alibi(
    repo: Path,
    base: str,
    new_ref: str | None,
    cmd: list[str],
    timeout: float,
    keep: list[re.Pattern],
    per_path: bool,
    keep_tmp: bool = False,
) -> Report:
    repo = repo.resolve()
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
    if not changed:
        report.notes.append("no production source files differ from base; skipped test runs")
        return report

    tmp_root = Path(tempfile.mkdtemp(prefix="alibi-"))
    new_dir = tmp_root / "new"
    splice_dir = tmp_root / "splice"
    new_dir.mkdir()
    splice_dir.mkdir()

    try:
        materialize(repo, new_dir, base, new_ref, keep, overlay="none")
        plan = materialize(repo, splice_dir, base, new_ref, keep, overlay="all")
        report.plan = [p for p in plan if p.role != "link"]

        env_new = extra_env_for(repo, new_dir)
        env_sp = extra_env_for(repo, splice_dir)

        report.new_run = run_cmd(cmd, new_dir, timeout, env_new)
        if not report.new_run.ok:
            report.status = "BROKEN"
            report.witnesses = parse_witnesses(report.new_run.output)
            report.notes.append("refusing to splice while the new tree is already red")
            return report

        report.splice_run = run_cmd(cmd, splice_dir, timeout, env_sp)
        report.status, report.witnesses = extract_status(report.new_run, report.splice_run, len(changed))

        if per_path and report.status in {"LOCKED", "UNBUILDABLE", "LOOSE"}:
            report.per_path = attribute_paths(
                repo=repo,
                base=base,
                new_ref=new_ref,
                cmd=cmd,
                timeout=timeout,
                keep=keep,
                changed=changed,
                tmp_root=tmp_root,
                global_status=report.status,
            )
        return report
    finally:
        if keep_tmp:
            report.notes.append(f"kept tmp {tmp_root}")
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)


def attribute_paths(
    repo: Path,
    base: str,
    new_ref: str | None,
    cmd: list[str],
    timeout: float,
    keep: list[re.Pattern],
    changed: list[str],
    tmp_root: Path,
    global_status: str,
) -> dict[str, str]:
    """Leave-one-out: overlay a single production path from base onto NEW.

    If tests then fail, that path is LOCKED (its new bytes are necessary).
    If tests still pass, that path is LOOSE.
    """
    out: dict[str, str] = {}
    if global_status == "LOOSE":
        return {p: "LOOSE" for p in changed}

    for i, path in enumerate(changed):
        dest = tmp_root / f"loo-{i}"
        dest.mkdir()
        materialize(
            repo,
            dest,
            base,
            new_ref,
            keep,
            overlay="paths",
            only_paths={path},
        )
        result = run_cmd(cmd, dest, timeout, extra_env_for(repo, dest))
        if result.ok:
            out[path] = "LOOSE"
        else:
            kind, _ = extract_status(
                RunResult(0, 0.0, ""),
                result,
                1,
            )
            out[path] = kind
        shutil.rmtree(dest, ignore_errors=True)
    return out


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="alibi",
        description="Transplant current tests onto another revision's production sources. "
        "If they fail, the production diff has an alibi (it is LOCKED). "
        "If they still pass, the production diff is LOOSE — untested behavior.",
    )
    p.add_argument(
        "base",
        nargs="?",
        default="HEAD",
        help="revision whose production files are spliced in (default: HEAD)",
    )
    p.add_argument(
        "--new",
        default=None,
        metavar="REF",
        help="take tests from this ref instead of the worktree",
    )
    p.add_argument(
        "--cmd",
        default=None,
        help="test command (default: auto-detect unittest/pytest/cargo/npm/swift)",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="seconds per test run (default: 120)",
    )
    p.add_argument(
        "--keep",
        action="append",
        default=[],
        metavar="REGEX",
        help="additional regex of paths to treat as tests (repeatable)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="machine-readable report",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="print the splice plan and production diff; do not run tests",
    )
    p.add_argument(
        "--per-path",
        action="store_true",
        help="leave-one-out each changed production path (slow, N extra test runs)",
    )
    p.add_argument(
        "--keep-tmp",
        action="store_true",
        help="do not delete the spliced trees (debug)",
    )
    p.add_argument(
        "-C",
        "--repo",
        default=".",
        help="repository path",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
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
        }
        if args.json:
            json.dump(payload, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"alibi --list  base={args.base}  new={payload['new']}")
            print(f"cmd    {' '.join(cmd)}")
            print(f"prod   {len(changed)} changed production path(s)")
            for pth in changed:
                print(f"         {pth}")
            print("plan:")
            for row in plan_rows:
                if row["role"] == "test" or row["path"] in changed or row["source"] == "deleted":
                    print(f"  {row['role']:11} {row['source']:8} {row['path']}")
        return 0

    report = run_alibi(
        repo=repo,
        base=args.base,
        new_ref=new_ref,
        cmd=cmd,
        timeout=args.timeout,
        keep=keep,
        per_path=args.per_path,
        keep_tmp=args.keep_tmp,
    )
    if args.json:
        json.dump(report_to_json(report), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_human(report))

    # Exit codes for composition: 0 LOCKED/CLEAN, 2 LOOSE, 3 BROKEN, 4 UNBUILDABLE
    return {
        "LOCKED": 0,
        "CLEAN": 0,
        "LOOSE": 2,
        "BROKEN": 3,
        "UNBUILDABLE": 4,
    }.get(report.status, 1)


if __name__ == "__main__":
    sys.exit(main())
