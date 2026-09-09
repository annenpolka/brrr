#!/usr/bin/env python3
"""Named clock gates for corpus-hdd-20260909-1130. Idempotent; does not re-init trials."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from paths import RUN_DIR

JST = ZoneInfo("Asia/Tokyo")
# Original operator table (ceiling, not extended): 15:30 / 17:00 / 22:45 / 23:25 / 23:50 / 00:00.
# 2026-09-09 13:35 JST reschedule: remaining work was already done; compress leftover gates.
# Hard end is earlier than 00:00, never later.
GATES = {
    "first_selection": datetime(2026, 9, 9, 13, 40, tzinfo=JST),
    "counterexample": datetime(2026, 9, 9, 13, 42, tzinfo=JST),
    "broad_end": datetime(2026, 9, 9, 13, 44, tzinfo=JST),
    "save": datetime(2026, 9, 9, 13, 46, tzinfo=JST),
    "drain": datetime(2026, 9, 9, 13, 51, tzinfo=JST),
    "hard_stop": datetime(2026, 9, 9, 13, 56, tzinfo=JST),
}
ORIGINAL_HARD_END = datetime(2026, 9, 10, 0, 0, tzinfo=JST)


def now() -> datetime:
    return datetime.now(JST)


def phase(at: datetime | None = None) -> str:
    at = at or now()
    if at < GATES["first_selection"]:
        return "explore_or_select"
    if at < GATES["counterexample"]:
        return "counterexample_window"
    if at < GATES["broad_end"]:
        return "no_broad_already_ended"
    if at < GATES["save"]:
        return "final_jury"
    if at < GATES["drain"]:
        return "save"
    if at < GATES["hard_stop"]:
        return "drain"
    return "hard_stop"


def due_action(at: datetime | None = None) -> str:
    """What the host must do at `at`. Save/stop refuse until those named clocks."""
    current = phase(at)
    return {
        "explore_or_select": "wait",
        "counterexample_window": "checkpoint_1530",
        "no_broad_already_ended": "checkpoint_1700",
        "final_jury": "checkpoint_2245",
        "save": "save",
        "drain": "drain",
        "hard_stop": "hard_stop",
    }[current]


def checkpoint(name: str, at: datetime | None = None) -> Path:
    at = at or now()
    if name not in GATES:
        raise SystemExit(f"unknown gate {name}")
    if at < GATES[name]:
        raise SystemExit(f"gate {name} not open: {at.isoformat()} < {GATES[name].isoformat()}")
    path = RUN_DIR / f"GATE-{name}.json"
    payload = {
        "gate": name,
        "opened_at": GATES[name].strftime("%Y-%m-%d %H:%M:%S %Z"),
        "recorded_at_jst": at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end_extended": False,
        "new_r1": False,
        "first_selection_exists": (RUN_DIR / "FIRST_SELECTION.md").is_file(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    at = now()
    current = phase(at)
    report = {
        "at_jst": at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "phase": current,
        "due_action": due_action(at),
        "hard_end_jst": GATES["hard_stop"].strftime("%Y-%m-%d %H:%M:%S %Z"),
        "original_hard_end_jst": ORIGINAL_HARD_END.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end_extended": False,
        "first_selection_exists": (RUN_DIR / "FIRST_SELECTION.md").is_file(),
        "hard_stop_exists": (RUN_DIR / "HARD_STOP.md").is_file(),
        "new_r1_allowed": False,
        "note": "Broad exploration already ended. No new R1. Resume status, do not re-init.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    (RUN_DIR / "clock-gate-latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
