#!/usr/bin/env python3
"""One host tick: checkpoint, save, drain, or hard-stop according to the live JST clock."""
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
    if action == "wait":
        result["status"] = "waiting_for_1530"
    elif action == "checkpoint_1530":
        path = clock_gate.checkpoint("first_selection")
        result["status"] = "checkpoint"
        result["path"] = str(path)
        _append_state("15:30 gate live. FIRST_SELECTION already on disk. No new R1.")
        result["scratch"] = "GATE-first_selection.json"
    elif action == "checkpoint_1700":
        path = clock_gate.checkpoint("counterexample")
        result["status"] = "checkpoint"
        result["path"] = str(path)
        _append_state("17:00 gate live. runpair 反証 already recorded. No new R1.")
        result["scratch"] = "GATE-counterexample.json"
    elif action == "checkpoint_2245":
        path = clock_gate.checkpoint("broad_end")
        result["status"] = "checkpoint"
        result["path"] = str(path)
        _append_state("22:45 gate live. Broad exploration already ended. No new R1.")
        result["scratch"] = "GATE-broad_end.json"
    elif action == "save":
        day_end.save()
        result["status"] = "saved"
        _append_state("23:25 save: 採否/費用/入力hash/再実行 + restore.")
    elif action == "drain":
        day_end.drain()
        result["status"] = "drained"
        _append_state("23:50 drain. No new spawn/R1/collect.")
    elif action == "hard_stop":
        day_end.hard_stop()
        day_end.copy_scratch()
        result["status"] = "hard_stop"
        _append_state("00:00 HARD_STOP. This run dream/hdd.py PIDs 0.")
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
