#!/usr/bin/env python3
"""Scheduler watchdog: snapshot metrics, detect idle-slot failures, attempt refill notes."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from paths import HDD_ROOT, RUN_DIR, WATCHDOG_DIR
from r1_budget import load_ledger, remaining_usd, reported_spend
from scheduler import (
    MIN_ACTIVE_WORKERS,
    TARGET_ACTIVE_WORKERS,
    backlog_floor,
    load_state,
    now_jst,
    queue_depths,
    save_state,
)

JST = ZoneInfo("Asia/Tokyo")


def r1_in_flight(hdd_root: Path, state: dict | None = None) -> int:
    n = 0
    if state:
        n = len(
            [
                t
                for t in state.get("machine_tasks") or []
                if t.get("kind") == "r1" and t.get("status") == "running"
            ]
        )
    if n:
        return n
    if not hdd_root.exists():
        return 0
    for trial in hdd_root.iterdir():
        if not trial.is_dir() or trial.is_symlink() or trial.name == "current":
            continue
        lock = trial / "dream.lock"
        if lock.exists():
            n += 1
    return n


def snapshot(state: dict, scratch: Path | None = None) -> dict:
    depths = queue_depths(state)
    ready_total = sum(depths.values())
    workers = state.get("workers") or []
    active = [w for w in workers if w.get("status") == "active"]
    vacant = [w for w in workers if w.get("status") == "vacant"]
    blocked = [w for w in workers if w.get("status") == "blocked"]
    machine = [t for t in state.get("machine_tasks") or [] if t.get("status") == "running"]
    spend = 0.0
    remaining = None
    try:
        ledger = load_ledger()
        spend = reported_spend(ledger)
        remaining = remaining_usd(ledger)
    except FileNotFoundError:
        pass
    rec = {
        "at_jst": now_jst(),
        "mode": state.get("mode"),
        "active_reasoning_workers": len(active),
        "active_machine_tasks": len(machine),
        "blocked_reasoning_workers": len(blocked),
        "idle_slots": len(vacant),
        "ready_jobs_total": ready_total,
        "ready_jobs_by_queue": depths,
        "R1_calls_in_flight": r1_in_flight(HDD_ROOT, state),
        "R1_budget_spent": spend,
        "R1_budget_remaining": remaining,
        "specimens_ready_for_R1": depths.get("READY_R1_DREAM", 0),
        "backlog_floor": backlog_floor(max(0, TARGET_ACTIVE_WORKERS - len(active))),
        "scheduling_failure": False,
        "failure_reason": None,
    }
    if (
        len(active) < MIN_ACTIVE_WORKERS
        and ready_total > 0
        and state.get("mode") == "running"
    ):
        rec["scheduling_failure"] = True
        rec["failure_reason"] = (
            f"active_reasoning_workers {len(active)} < MIN {MIN_ACTIVE_WORKERS} "
            f"AND ready_jobs_total {ready_total} > 0"
        )
    WATCHDOG_DIR.mkdir(parents=True, exist_ok=True)
    latest = WATCHDOG_DIR / "latest.json"
    latest.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    hist = WATCHDOG_DIR / "history.jsonl"
    with hist.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    if scratch:
        scratch.mkdir(parents=True, exist_ok=True)
        (scratch / "latest.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        with (scratch / "history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    return rec


def apply_failure(state: dict, rec: dict) -> None:
    if not rec.get("scheduling_failure"):
        return
    failures = state.setdefault("scheduling_failures", [])
    failures.append(
        {
            "at": rec["at_jst"],
            "reason": rec["failure_reason"],
            "ready": rec["ready_jobs_total"],
            "active": rec["active_reasoning_workers"],
        }
    )
    consecutive = 0
    for item in reversed(failures):
        if item.get("reason"):
            consecutive += 1
        else:
            break
    rec["consecutive_failures"] = consecutive
    incidents = RUN_DIR / "INCIDENTS.md"
    existing = incidents.read_text(encoding="utf-8") if incidents.exists() else "# Incidents\n\n"
    existing += (
        f"- {rec['at_jst']} SCHEDULING_FAILURE consecutive={consecutive}: {rec['failure_reason']}\n"
    )
    incidents.write_text(existing, encoding="utf-8")


def render_throughput(rec: dict) -> str:
    return "\n".join(
        [
            "# Throughput",
            "",
            f"Updated: {rec['at_jst']}",
            "",
            f"- mode: {rec['mode']}",
            f"- active workers: {rec['active_reasoning_workers']}",
            f"- idle slots: {rec['idle_slots']}",
            f"- ready jobs: {rec['ready_jobs_total']}",
            f"- R1 in flight: {rec['R1_calls_in_flight']}",
            f"- R1 remaining: {rec['R1_budget_remaining']}",
            f"- specimens ready for R1: {rec['specimens_ready_for_R1']}",
            f"- scheduling_failure: {rec['scheduling_failure']}",
            "",
        ]
    )


def main() -> None:
    scratch = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    env_scratch = os.environ.get("BRRR_SCRATCH_THROUGHPUT")
    if scratch is None and env_scratch:
        scratch = Path(env_scratch)
    state = load_state()
    rec = snapshot(state, scratch)
    apply_failure(state, rec)
    state["last_watchdog"] = rec["at_jst"]
    save_state(state)
    (RUN_DIR / "THROUGHPUT.md").write_text(render_throughput(rec), encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("at_jst", "scheduling_failure", "ready_jobs_total", "active_reasoning_workers", "idle_slots")}))
    sys.exit(2 if rec["scheduling_failure"] else 0)


if __name__ == "__main__":
    main()
