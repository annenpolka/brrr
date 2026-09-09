"""Run a command twice in one directory and report working-directory file deltas."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def snapshot_files(cwd: Path) -> dict[str, int]:
    """Non-recursive regular files in cwd, name -> size. Does not open file contents."""
    out: dict[str, int] = {}
    for path in cwd.iterdir():
        if path.is_file() and not path.is_symlink():
            out[path.name] = path.stat().st_size
    return out


def file_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, list[dict]]:
    added = [{"name": name, "size": after[name]} for name in sorted(set(after) - set(before))]
    removed = [{"name": name, "size": before[name]} for name in sorted(set(before) - set(after))]
    changed = [
        {"name": name, "before": before[name], "after": after[name]}
        for name in sorted(set(before) & set(after))
        if before[name] != after[name]
    ]
    return {"added": added, "removed": removed, "changed": changed}


def run_once(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict:
    proc = subprocess.run(command, cwd=cwd, capture_output=True, env=env)
    return {
        "argv": command,
        "rc": proc.returncode,
        "stdout": proc.stdout.decode("utf-8", errors="replace"),
        "stderr": proc.stderr.decode("utf-8", errors="replace"),
    }


def runpair(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict:
    if not command:
        raise ValueError("command is required")
    cwd = cwd.resolve()
    env = env if env is not None else os.environ.copy()
    before = snapshot_files(cwd)
    first = run_once(command, cwd, env)
    after_first = snapshot_files(cwd)
    second = run_once(command, cwd, env)
    after_second = snapshot_files(cwd)
    return {
        "cwd": str(cwd),
        "command": command,
        "before": before,
        "first": {**first, "delta": file_delta(before, after_first)},
        "second": {**second, "delta": file_delta(after_first, after_second)},
        "after": after_second,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Run COMMAND twice in one directory and report files that appeared or changed."
    )
    parser.add_argument("--cwd", default=".", help="working directory (default: .)")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command to run twice; prefix with --")
    args = parser.parse_args(argv)
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("command is required (runpair --cwd DIR -- CMD ...)")
    result = runpair(command, Path(args.cwd))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
