#!/usr/bin/env python3
"""Sleep until 22:00 JST 2026-09-01, then launch the first Cambrian Dreamer wave."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
ROOT = Path(__file__).resolve().parents[2]
TARGET = datetime(2026, 9, 1, 22, 0, 5, tzinfo=JST)
WAVE1 = [
    "unfamiliar-cli",
    "hdd-debug",
    "hdd-test",
    "hdd-review",
    "hdd-history",
    "hdd-log",
    "hdd-merge",
    "hdd-agent",
]


def main() -> None:
    now = datetime.now(JST)
    wait = (TARGET - now).total_seconds()
    print(f"now={now.isoformat()} target={TARGET.isoformat()} sleep={max(0, wait):.1f}s", flush=True)
    if wait > 0:
        time.sleep(wait)

    logdir = ROOT / "lab-hdd" / "dream-logs"
    logdir.mkdir(parents=True, exist_ok=True)
    print(f"launching wave1 at {datetime.now(JST).isoformat()}", flush=True)

    procs: list[tuple[str, subprocess.Popen]] = []
    pid_lines = []
    for trial in WAVE1:
        out = (logdir / f"{trial}-wrapper.out").open("w")
        err = (logdir / f"{trial}-wrapper.err").open("w")
        proc = subprocess.Popen(
            [str(ROOT / "lab-hdd/scripts/dream.sh"), trial, "cambrian"],
            cwd=str(ROOT),
            stdout=out,
            stderr=err,
            start_new_session=True,
        )
        procs.append((trial, proc))
        pid_lines.append(f"{trial} {proc.pid}")
        print(f"started {trial} pid={proc.pid}", flush=True)
    (logdir / "wave1.pids").write_text("\n".join(pid_lines) + "\n", encoding="utf-8")

    failures = []
    for trial, proc in procs:
        rc = proc.wait()
        print(f"finished {trial} pid={proc.pid} rc={rc}", flush=True)
        if rc != 0:
            failures.append((trial, rc))
    print("WAVE1_DONE", flush=True)
    if failures:
        print(f"WAVE1_FAILURES {failures}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
