#!/usr/bin/env python3
"""One host tick: work, save/保全, or HARD_STOP according to the live JST clock.

After 17:30 this never waits on a named clock. Vacant slots take ready jobs.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import clock_gate
import day_end
from clock_gate import now
from paths import RUN_DIR


def _append_state(line: str) -> None:
    path = RUN_DIR / "STATE.md"
    stamp = now().strftime("%Y-%m-%d %H:%M:%S %Z")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n- Checkpoint {stamp}: {line}\n")


def _copy_scratch(*names: str) -> None:
    raw = os.environ.get("GOAL_SCRATCH")
    if not raw:
        return
    dest = Path(raw)
    dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = RUN_DIR / name
        if src.exists():
            shutil.copy(src, dest / src.name)


def tick() -> dict:
    clock_gate.main()
    action = clock_gate.due_action()
    result: dict = {"action": action}
    if action == "refuse_start":
        result["status"] = "not_before"
    elif action == "work":
        result["status"] = "work"
        result["note"] = "deadline clocks are not wait-to-start; take the next ready job"
    elif action == "save":
        if not (RUN_DIR / "採否.md").exists() or not (RUN_DIR / "RERUN.md").exists():
            day_end.save()
            result["status"] = "saved"
            _append_state("08:00 保全: 採否/費用/入力hash/再実行. No new wide exploration.")
        else:
            result["status"] = "already_saved"
    elif action == "hard_stop":
        day_end.hard_stop()
        day_end.copy_scratch()
        result["status"] = "hard_stop"
        _append_state("09:00 HARD_STOP. This run dream/hdd.py PIDs 0.")
        result["scratch"] = "HARD_STOP.md,clock-stop.txt,hard-stop-ps.txt,credits-end.json"
    else:
        raise SystemExit(f"unknown action {action}")
    (RUN_DIR / "gate-tick-latest.json").write_text(json.dumps(result, indent=2) + "\n")
    extras = ["gate-tick-latest.json"]
    if result.get("scratch"):
        extras.extend(s.strip() for s in str(result["scratch"]).split(",") if s.strip())
    _copy_scratch(*extras)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    tick()
    sys.exit(0)
