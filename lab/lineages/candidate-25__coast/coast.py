#!/usr/bin/env python3
"""coast — the machine after waitpid: late writes, stragglers, file layers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

VERSION = "0.2.0"

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".coast",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    ".nox",
}
MAX_HASH_BYTES = 4 * 1024 * 1024
DEFAULT_STORE = ".coast"


def now_wall() -> float:
    return time.time()


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def walk_files(root: Path, ignore_dirs: set[str]) -> Iterable[Path]:
    root = root.resolve()
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = os.scandir(current)
        except OSError:
            continue
        with entries:
            for ent in entries:
                if ent.name in ignore_dirs:
                    continue
                try:
                    if ent.is_symlink():
                        continue
                    if ent.is_dir(follow_symlinks=False):
                        stack.append(Path(ent.path))
                    elif ent.is_file(follow_symlinks=False):
                        yield Path(ent.path)
                except OSError:
                    continue


def file_digest(path: Path) -> tuple[int, int, str | None]:
    """Return (mtime_ns, size, sha256-or-None)."""
    st = path.stat()
    size = int(st.st_size)
    mtime_ns = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
    if size > MAX_HASH_BYTES:
        return mtime_ns, size, None
    h = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(64 * 1024)
                if not chunk:
                    break
                h.update(chunk)
    except OSError:
        return mtime_ns, size, None
    return mtime_ns, size, h.hexdigest()


def snapshot_roots(
    roots: list[tuple[str, Path]],
    ignore_dirs: set[str],
) -> dict[str, dict[str, Any]]:
    multi = len(roots) > 1
    out: dict[str, dict[str, Any]] = {}
    for label, root in roots:
        root = root.resolve()
        for path in walk_files(root, ignore_dirs):
            rel = relpath(path, root)
            key = f"{label}:{rel}" if multi else rel
            try:
                mtime_ns, size, digest = file_digest(path)
            except OSError:
                continue
            out[key] = {
                "mtime_ns": mtime_ns,
                "size": size,
                "sha256": digest,
                "watch": label,
                "abspath": str(path),
            }
    return out


def diff_snapshots(
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    keys = set(before) | set(after)
    for key in sorted(keys):
        a = before.get(key)
        b = after.get(key)
        if a == b:
            continue
        if a is None and b is not None:
            kind = "create"
        elif a is not None and b is None:
            kind = "delete"
        else:
            kind = "write"
            if a.get("sha256") and b.get("sha256") and a["sha256"] == b["sha256"]:
                # mtime-only; not a new generation
                continue
        rec = {
            "path": key,
            "op": kind,
            "size": None if b is None else b["size"],
            "sha256": None if b is None else b["sha256"],
            "mtime_ns": None if b is None else b["mtime_ns"],
            "watch": (b or a or {}).get("watch"),
            "abspath": (b or a or {}).get("abspath"),
        }
        if a is not None and b is not None and a.get("sha256") and b.get("sha256"):
            rec["content_changed"] = a["sha256"] != b["sha256"]
        elif kind == "write":
            rec["content_changed"] = a != b
        else:
            rec["content_changed"] = kind != "delete"
        events.append(rec)
    return events


def iter_processes() -> list[dict[str, Any]]:
    try:
        raw = subprocess.check_output(
            ["ps", "-ax", "-o", "pid=,pgid=,ppid=,stat=,command="],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    rows: list[dict[str, Any]] = []
    for line in raw.splitlines():
        parts = line.strip().split(None, 4)
        if len(parts) < 4:
            continue
        try:
            rows.append(
                {
                    "pid": int(parts[0]),
                    "pgid": int(parts[1]),
                    "ppid": int(parts[2]),
                    "stat": parts[3],
                    "command": parts[4] if len(parts) > 4 else "",
                }
            )
        except ValueError:
            continue
    return rows


def group_members(
    pgid: int,
    exclude: set[int],
    *,
    leader_pid: int | None = None,
    known: set[int] | None = None,
) -> list[dict[str, Any]]:
    known = known or set()
    rows = []
    for p in iter_processes():
        if p["pid"] in exclude:
            continue
        if (
            p["pgid"] == pgid
            or p["pid"] in known
            or (leader_pid is not None and p["ppid"] == leader_pid)
        ):
            rows.append(p)
    return rows


def classify_path(rel: str) -> str:
    if ":" in rel:
        maybe, rest = rel.split(":", 1)
        if maybe in {"tree", "tmp"} or rest:
            rel = rest
    name = Path(rel).name.lower()
    parts = set(Path(rel).parts)
    if (
        "__pycache__" in parts
        or name.endswith((".pyc", ".pyo"))
        or name.endswith(".py[cod]")
    ):
        return "bytecode"
    cache_dirs = {
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".cache",
        ".tox",
        ".nox",
        ".eggs",
        "htmlcov",
        ".coverage",
    }
    if parts & cache_dirs or name in {".coverage", ".ds_store"}:
        return "cache"
    if name.endswith((".log", ".tmp", ".swp", ".swo")) or name.startswith("."):
        return "ephemeral"
    return "artifact"


def phase_from_mtime(mtime_ns: int | None, wall_exit: float, in_coast_loop: bool) -> str:
    if not in_coast_loop:
        return "run"
    if mtime_ns is None:
        return "coast"
    # First flush after waitpid often contains files written during the run.
    if (mtime_ns / 1e9) <= wall_exit + 0.03:
        return "run"
    return "coast"


def inspect_pid(pid: int) -> dict[str, Any]:
    """Best-effort lsof: cwd, command, and a few open files."""
    info: dict[str, Any] = {"pid": pid, "cwd": None, "lsof_cmd": None, "files": []}
    try:
        raw = subprocess.check_output(
            ["lsof", "-p", str(pid), "-Fn"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=0.7,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return info
    fd = None
    files: list[str] = []
    for line in raw.splitlines():
        if not line:
            continue
        tag, val = line[0], line[1:]
        if tag == "c":
            info["lsof_cmd"] = val
        elif tag == "f":
            fd = val
        elif tag == "n":
            if fd == "cwd":
                info["cwd"] = val
            elif val and not val.startswith("->"):
                files.append(val)
    seen: set[str] = set()
    uniq: list[str] = []
    for item in files:
        if item in seen:
            continue
        seen.add(item)
        uniq.append(item)
        if len(uniq) >= 24:
            break
    info["files"] = uniq
    return info


def is_hazard(kind: str) -> bool:
    return kind == "artifact"


class Tracker:
    def __init__(self, roots: list[tuple[str, Path]], ignore_dirs: set[str], interval_s: float):
        self.roots = [(label, path.resolve()) for label, path in roots]
        self.ignore_dirs = ignore_dirs
        self.interval_s = interval_s
        self.t0 = time.perf_counter()
        self.snap = snapshot_roots(self.roots, ignore_dirs)
        self.events: list[dict[str, Any]] = []
        self.layers: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.stragglers: dict[int, dict[str, Any]] = {}

    def elapsed(self) -> float:
        return time.perf_counter() - self.t0

    def poll_fs(self, *, in_coast_loop: bool, wall_exit: float | None) -> list[dict[str, Any]]:
        current = snapshot_roots(self.roots, self.ignore_dirs)
        raw = diff_snapshots(self.snap, current)
        self.snap = current
        t = self.elapsed()
        stamped: list[dict[str, Any]] = []
        for ev in raw:
            phase = phase_from_mtime(ev.get("mtime_ns"), wall_exit or 0.0, in_coast_loop)
            kind = classify_path(ev["path"])
            rec = {
                **ev,
                "t": round(t, 6),
                "phase": phase,
                "kind": kind,
                "hazard": bool(phase == "coast" and is_hazard(kind)),
            }
            self.events.append(rec)
            self.layers[ev["path"]].append(rec)
            stamped.append(rec)
        return stamped

    def poll_procs(
        self,
        pgid: int,
        exclude: set[int],
        phase: str,
        *,
        leader_pid: int | None = None,
        known: set[int] | None = None,
    ) -> list[dict[str, Any]]:
        members = group_members(pgid, exclude, leader_pid=leader_pid, known=known)
        if known is not None:
            known.update(p["pid"] for p in members)
        t = self.elapsed()
        alive_ids = {p["pid"] for p in members}
        for p in members:
            rec = self.stragglers.get(p["pid"])
            if rec is None:
                command = p["command"]
                rec = {
                    "pid": p["pid"],
                    "ppid": p["ppid"],
                    "command": command,
                    "first_t": round(t, 6),
                    "last_t": round(t, 6),
                    "died_t": None,
                    "phase_first": phase,
                }
                stub = command in {"(Python)", "Python", "(bash)", "bash", "sleep"} or len(command) < 6
                if stub:
                    info = inspect_pid(p["pid"])
                    rec["cwd"] = info.get("cwd")
                    rec["open_files"] = info.get("files")
                    if info.get("lsof_cmd"):
                        rec["command"] = f"{info['lsof_cmd']} {command}".strip()
                self.stragglers[p["pid"]] = rec
            else:
                rec["last_t"] = round(t, 6)
                rec["command"] = p["command"] or rec["command"]
                rec["died_t"] = None
        for pid, rec in self.stragglers.items():
            if rec["died_t"] is None and pid not in alive_ids:
                rec["died_t"] = round(t, 6)
        return members


def run_watched(
    cmd: list[str],
    *,
    roots: list[tuple[str, Path]],
    cwd: Path | None,
    ignore_dirs: set[str],
    interval_s: float,
    quiet_s: float,
    max_coast_s: float,
    passthrough: bool,
    kill_stragglers: bool,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    tracker = Tracker(roots, ignore_dirs, interval_s)
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []
    popen_kwargs: dict[str, Any] = {
        "cwd": str(cwd) if cwd else None,
        "start_new_session": True,
    }
    if env is not None:
        popen_kwargs["env"] = env
    if not passthrough:
        popen_kwargs["stdout"] = subprocess.PIPE
        popen_kwargs["stderr"] = subprocess.PIPE
        popen_kwargs["text"] = True

    proc = subprocess.Popen(cmd, **popen_kwargs)
    exclude = {proc.pid, os.getpid()}
    known_pids: set[int] = set()
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        pgid = proc.pid

    pumps: list[threading.Thread] = []
    if not passthrough:
        # Do not communicate() after waitpid: children inherit the pipes and
        # holding them open *is* coast. Drain in the background instead.
        def _pump(stream: Any, bucket: list[str]) -> None:
            if stream is None:
                return
            try:
                while True:
                    chunk = stream.read(4096)
                    if not chunk:
                        break
                    bucket.append(chunk)
            except (OSError, ValueError):
                pass

        pumps = [
            threading.Thread(target=_pump, args=(proc.stdout, stdout_chunks), daemon=True),
            threading.Thread(target=_pump, args=(proc.stderr, stderr_chunks), daemon=True),
        ]
        for thread in pumps:
            thread.start()

    def snap_procs(phase: str) -> list[dict[str, Any]]:
        return tracker.poll_procs(
            pgid,
            exclude,
            phase,
            leader_pid=proc.pid,
            known=known_pids,
        )

    while True:
        tracker.poll_fs(in_coast_loop=False, wall_exit=None)
        snap_procs("run")
        rc = proc.poll()
        if rc is not None:
            break
        time.sleep(interval_s)

    t_exit = tracker.elapsed()
    wall_exit = now_wall()
    exit_code = int(proc.returncode if proc.returncode is not None else rc or 0)

    # Catch writes that landed between the last mid-run poll and waitpid.
    tracker.poll_fs(in_coast_loop=True, wall_exit=wall_exit)
    snap_procs("coast")

    last_activity = t_exit
    had_post_exit = False
    settled = False
    t_end = t_exit

    while True:
        now = tracker.elapsed()
        if now - t_exit >= max_coast_s:
            t_end = now
            break
        fs_events = tracker.poll_fs(in_coast_loop=True, wall_exit=wall_exit)
        members = snap_procs("coast")
        late_fs = [e for e in fs_events if e["phase"] == "coast"]
        if late_fs or members:
            had_post_exit = True
            last_activity = now
        if not members and (now - last_activity) >= quiet_s:
            settled = True
            t_end = now
            break
        time.sleep(interval_s)

    # Final sweep
    tracker.poll_fs(in_coast_loop=True, wall_exit=wall_exit)
    leftover = snap_procs("coast")
    leftover_info = []
    for proc_row in leftover:
        info = inspect_pid(proc_row["pid"])
        leftover_info.append({**proc_row, **info})
        rec = tracker.stragglers.get(proc_row["pid"])
        if rec is not None:
            rec["cwd"] = info.get("cwd")
            rec["open_files"] = info.get("files")
            if info.get("lsof_cmd") and (
                not rec.get("command") or rec["command"] in {"(Python)", "Python"}
            ):
                rec["command"] = info["lsof_cmd"]

    if leftover:
        settled = False
        had_post_exit = True

    if kill_stragglers and leftover:
        try:
            os.killpg(pgid, signal.SIGTERM)
        except OSError:
            for p in leftover:
                try:
                    os.kill(p["pid"], signal.SIGTERM)
                except OSError:
                    pass
        time.sleep(min(0.15, quiet_s))
        leftover = snap_procs("coast")
        if leftover:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except OSError:
                for p in leftover:
                    try:
                        os.kill(p["pid"], signal.SIGKILL)
                    except OSError:
                        pass
            time.sleep(0.05)
            leftover = snap_procs("coast")
        leftover_info = leftover
        if not leftover:
            settled = True

    for thread in pumps:
        thread.join(timeout=0.2)

    stdout_data = "".join(stdout_chunks)
    stderr_data = "".join(stderr_chunks)

    late = [e for e in tracker.events if e["phase"] == "coast"]
    run_events = [e for e in tracker.events if e["phase"] == "run"]
    if late:
        last_late = max(float(e["t"]) for e in late)
        last_activity = max(last_activity, last_late)
        had_post_exit = True
    coast_s = 0.0 if not had_post_exit else max(0.0, last_activity - t_exit)

    straggler_rows = []
    for rec in sorted(tracker.stragglers.values(), key=lambda r: r["first_t"]):
        # A process that died before exit is a worker, not a straggler.
        if rec["first_t"] <= t_exit and rec["died_t"] is not None and rec["died_t"] <= t_exit + 0.08:
            role = "worker"
        else:
            role = "straggler"
        straggler_rows.append({**rec, "role": role, "alive_after_exit": rec["died_t"] is None})

    rewritten = sorted(
        path
        for path, layers in tracker.layers.items()
        if sum(1 for layer in layers if layer["op"] != "delete") >= 2
    )

    hazards = [e for e in late if e.get("hazard")]
    return {
        "tool": "coast",
        "version": VERSION,
        "argv": cmd,
        "roots": [{"label": label, "path": str(path)} for label, path in roots],
        "exit_code": exit_code,
        "t_exit_s": round(t_exit, 6),
        "t_watch_s": round(t_end, 6),
        "coast_s": round(coast_s, 6),
        "settled": settled,
        "had_post_exit": had_post_exit,
        "stdout": stdout_data,
        "stderr": stderr_data,
        "run_events": run_events,
        "late_writes": late,
        "hazards": hazards,
        "layers": {k: v for k, v in sorted(tracker.layers.items())},
        "rewritten": rewritten,
        "processes": straggler_rows,
        "stragglers": [p for p in straggler_rows if p["role"] == "straggler"],
        "leftover": leftover_info,
    }


def human_report(result: dict[str, Any]) -> str:
    lines: list[str] = []
    status = "settled" if result["settled"] else "UNSETTLED"
    lines.append(
        f"exit {result['exit_code']} in {result['t_exit_s']:.3f}s"
        f"  COAST {result['coast_s']:.3f}s  {status}"
    )
    hazards = result.get("hazards") or [e for e in result["late_writes"] if e.get("hazard")]
    late = result["late_writes"]
    if hazards:
        lines.append("HAZARD late artifacts:")
        for ev in hazards:
            digest = (ev.get("sha256") or "")[:10]
            size = ev.get("size")
            size_s = "-" if size is None else f"{size}b"
            lines.append(
                f"  +{ev['t'] - result['t_exit_s']:.3f}s  {size_s:>8}  "
                f"{ev['op']:6}  {ev['path']}  {digest}"
            )
    notes = [e for e in late if not e.get("hazard")]
    if notes:
        lines.append("late notes (cache/bytecode/ephemeral):")
        for ev in notes:
            lines.append(
                f"  +{ev['t'] - result['t_exit_s']:.3f}s  {ev['kind']:9}  {ev['path']}"
            )
    if not late:
        lines.append("late writes: (none)")

    stragglers = result["stragglers"]
    if stragglers:
        lines.append("stragglers:")
        for p in stragglers:
            life = "alive" if p["alive_after_exit"] else f"died @{p['died_t']:.3f}s"
            lines.append(f"  pid {p['pid']:<7} {life:16}  {p['command']}")
            if p.get("cwd"):
                lines.append(f"           cwd  {p['cwd']}")
            opens = p.get("open_files") or []
            interesting = [
                f
                for f in opens
                if not f.startswith("/usr/")
                and not f.startswith("/System/")
                and not f.startswith("/Applications/")
                and " (stateless" not in f
            ]
            for of in interesting[:8]:
                lines.append(f"           open {of}")
    else:
        lines.append("stragglers: (none)")

    if result["rewritten"]:
        lines.append("rewritten during watch:")
        for path in result["rewritten"]:
            layers = result["layers"][path]
            phases = ",".join(layer["phase"][0] for layer in layers)
            lines.append(f"  {path}  {len(layers)} layers [{phases}]")
    return "\n".join(lines) + "\n"


def json_dump(result: dict[str, Any]) -> str:
    slim = dict(result)
    return json.dumps(slim, indent=2, sort_keys=True) + "\n"


def store_result(store: Path, result: dict[str, Any]) -> None:
    store.mkdir(parents=True, exist_ok=True)
    (store / "last.json").write_text(json_dump(result), encoding="utf-8")


def load_last(store: Path) -> dict[str, Any]:
    path = store / "last.json"
    if not path.is_file():
        raise SystemExit(f"coast: no stored run at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_cmd(remainder: list[str]) -> list[str]:
    cmd = list(remainder)
    while cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        raise SystemExit("coast: missing command after --")
    return cmd


def add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--root", type=Path, default=None, help="tree to watch (default: cwd)")
    p.add_argument(
        "--also",
        type=Path,
        action="append",
        default=[],
        help="extra tree to watch (repeatable)",
    )
    p.add_argument("--cwd", type=Path, default=None, help="command working directory")
    p.add_argument("--store", type=Path, default=Path(DEFAULT_STORE))
    p.add_argument("--ignore", action="append", default=[], help="extra directory name to ignore")
    p.add_argument("--interval-ms", type=int, default=15)
    p.add_argument("--quiet-ms", type=int, default=200, help="stillness required to declare settled")
    p.add_argument("--max-coast-ms", type=int, default=4000)
    p.add_argument("--json", action="store_true", help="write JSON report to stdout")
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--no-passthrough", action="store_true", help="capture command stdio")
    p.add_argument("--kill-stragglers", action="store_true")
    p.add_argument(
        "--isolate-tmp",
        action="store_true",
        help="give the command a private TMPDIR and watch it (catches /tmp leftovers)",
    )


def execute(args: argparse.Namespace) -> dict[str, Any]:
    cmd = parse_cmd(args.cmd)
    root = (args.root or Path.cwd()).resolve()
    cwd = (args.cwd or Path.cwd()).resolve()
    ignore = set(DEFAULT_IGNORE_DIRS)
    ignore.update(args.ignore)
    store = args.store.expanduser()
    if not store.is_absolute():
        store = (Path.cwd() / store).resolve()
    args.store = store

    used_labels = {"tree"}
    roots: list[tuple[str, Path]] = [("tree", root)]
    env = os.environ.copy()
    if args.isolate_tmp:
        tmpdir = store / "isolated-tmp"
        tmpdir.mkdir(parents=True, exist_ok=True)
        env["TMPDIR"] = str(tmpdir)
        env["TEMP"] = str(tmpdir)
        env["TMP"] = str(tmpdir)
        roots.append(("tmp", tmpdir))
        used_labels.add("tmp")
    for extra in args.also:
        extra = extra.expanduser().resolve()
        base = extra.name or "also"
        label = base
        n = 2
        while label in used_labels:
            label = f"{base}{n}"
            n += 1
        used_labels.add(label)
        roots.append((label, extra))

    result = run_watched(
        cmd,
        roots=roots,
        cwd=cwd,
        ignore_dirs=ignore,
        interval_s=max(args.interval_ms, 5) / 1000.0,
        quiet_s=max(args.quiet_ms, 20) / 1000.0,
        max_coast_s=max(args.max_coast_ms, 50) / 1000.0,
        passthrough=not args.no_passthrough,
        kill_stragglers=args.kill_stragglers,
        env=env,
    )
    store_result(args.store, result)
    if args.json_out:
        args.json_out.write_text(json_dump(result), encoding="utf-8")
    if args.json:
        sys.stdout.write(json_dump(result))
    else:
        sys.stdout.write(human_report(result))
    return result


def cmd_show(args: argparse.Namespace) -> int:
    result = load_last(args.store)
    path = args.path
    if path:
        layers = result.get("layers", {}).get(path)
        if not layers:
            # try suffix match
            matches = [
                k
                for k in result.get("layers", {})
                if k == path or k.endswith("/" + path) or k.endswith(":" + path)
            ]
            if not matches:
                raise SystemExit(f"coast: no layers for {path}")
            path = matches[0]
            layers = result["layers"][path]
        print(f"{path}  {len(layers)} layers")
        for i, layer in enumerate(layers, 1):
            digest = (layer.get("sha256") or "-")[:12]
            print(
                f"  {i:3}  t={layer['t']:.3f}s  {layer['phase']:5}  "
                f"{layer['op']:6}  {layer['kind']:9}  {digest}"
            )
        return 0
    if args.json:
        sys.stdout.write(json_dump(result))
    else:
        sys.stdout.write(human_report(result))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="coast",
        description="Watch what the machine still does after a command's waitpid returns.",
    )
    p.add_argument("--version", action="version", version=f"coast {VERSION}")
    sub = p.add_subparsers(dest="action", required=True)

    run_p = sub.add_parser("run", help="run a command and report its coast")
    add_common(run_p)
    run_p.add_argument("cmd", nargs=argparse.REMAINDER)

    def do_run(a: argparse.Namespace) -> int:
        execute(a)
        return 0

    run_p.set_defaults(func=do_run)

    wait_p = sub.add_parser("wait", help="run a command; exit 124 if the machine does not settle")
    add_common(wait_p)
    wait_p.add_argument("cmd", nargs=argparse.REMAINDER)

    def do_wait(a: argparse.Namespace) -> int:
        result = execute(a)
        if not result["settled"]:
            return 124
        return int(result["exit_code"])

    wait_p.set_defaults(func=do_wait)

    show_p = sub.add_parser("show", help="print the last stored run")
    show_p.add_argument("--store", type=Path, default=Path(DEFAULT_STORE))
    show_p.add_argument("--json", action="store_true")
    show_p.add_argument("path", nargs="?", default=None)
    show_p.set_defaults(func=cmd_show)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
