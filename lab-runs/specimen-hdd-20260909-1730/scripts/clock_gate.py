#!/usr/bin/env python3
"""Named clock gates for specimen-hdd-20260909-1730.

17:30 JST is the only not-before gate. Later named clocks are deadlines, not
wait-to-start permissions. 保全 08:00 and HARD_STOP 09:00 never move later.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from paths import RUN_DIR

JST = ZoneInfo("Asia/Tokyo")
NOT_BEFORE = datetime(2026, 9, 9, 17, 30, tzinfo=JST)
WINDOW_START = NOT_BEFORE
PRESERVE_START = datetime(2026, 9, 10, 8, 0, tzinfo=JST)
HARD_STOP = datetime(2026, 9, 10, 9, 0, tzinfo=JST)
ORIGINAL_HARD_END = datetime(2026, 9, 10, 9, 0, tzinfo=JST)
HARD_END_EXTENDED = False

NOMINAL_GATES = {
    "first_packet_dream": datetime(2026, 9, 9, 19, 49, tzinfo=JST),
    "redpen_harvest": datetime(2026, 9, 9, 22, 9, tzinfo=JST),
    "first_selection": datetime(2026, 9, 10, 0, 28, tzinfo=JST),
    "counterexample": datetime(2026, 9, 10, 4, 21, tzinfo=JST),
    "broad_end": datetime(2026, 9, 10, 6, 40, tzinfo=JST),
    "final_jury": datetime(2026, 9, 10, 7, 27, tzinfo=JST),
    "save": PRESERVE_START,
    "hard_stop": HARD_STOP,
}
FIXED_GATES = frozenset({"save", "hard_stop"})
GATES = dict(NOMINAL_GATES)


def now() -> datetime:
    return datetime.now(JST)


def assert_start_allowed(at: datetime | None = None) -> datetime:
    at = at or now()
    if at < NOT_BEFORE:
        raise SystemExit(
            f"not-before gate: {at.isoformat()} < {NOT_BEFORE.isoformat()}; do not init the run"
        )
    return at


def assert_preserve_allowed(at: datetime | None = None) -> datetime:
    at = at or now()
    if at < PRESERVE_START:
        raise SystemExit(
            f"save/保全 refused before {PRESERVE_START.isoformat()}; now={at.isoformat()}"
        )
    return at


def assert_hard_stop_allowed(at: datetime | None = None) -> datetime:
    at = at or now()
    if at < HARD_STOP:
        raise SystemExit(
            f"hard_stop refused before {HARD_STOP.isoformat()}; now={at.isoformat()}"
        )
    return at


def compress_gates(started: datetime) -> dict[str, datetime]:
    """Late start compresses intermediate deadlines; 08:00 and 09:00 stay fixed."""
    total = ORIGINAL_HARD_END - WINDOW_START
    remaining = ORIGINAL_HARD_END - started
    if remaining.total_seconds() <= 0:
        remaining = timedelta(seconds=1)
    out: dict[str, datetime] = {}
    for name, when in NOMINAL_GATES.items():
        if name in FIXED_GATES:
            out[name] = when
            continue
        frac = (when - WINDOW_START) / total
        compressed = started + remaining * frac
        if compressed > PRESERVE_START:
            compressed = PRESERVE_START
        out[name] = compressed
    return out


def apply_compressed_gates(started: datetime) -> dict[str, datetime]:
    compressed = compress_gates(started)
    GATES.clear()
    GATES.update(compressed)
    return compressed


def phase(at: datetime | None = None) -> str:
    at = at or now()
    if at < NOT_BEFORE:
        return "not_started"
    if at < GATES["save"]:
        return "operate"
    if at < GATES["hard_stop"]:
        return "preserve"
    return "hard_stop"


def due_action(at: datetime | None = None) -> str:
    """What the host must do at `at`. After 17:30 this is never a wait-to-start."""
    at = at or now()
    if at < NOT_BEFORE:
        return "refuse_start"
    if at < GATES["save"]:
        return "work"
    if at < GATES["hard_stop"]:
        return "save"
    return "hard_stop"


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
        "hard_end_extended": HARD_END_EXTENDED,
        "hard_end_jst": HARD_STOP.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "note": "deadline, not wait-to-start",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    at = now()
    current = phase(at)
    report = {
        "at_jst": at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "phase": current,
        "due_action": due_action(at),
        "not_before_jst": NOT_BEFORE.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "preserve_start_jst": PRESERVE_START.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end_jst": HARD_STOP.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "original_hard_end_jst": ORIGINAL_HARD_END.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end_extended": HARD_END_EXTENDED,
        "first_selection_exists": (RUN_DIR / "FIRST_SELECTION.md").is_file(),
        "hard_stop_exists": (RUN_DIR / "HARD_STOP.md").is_file(),
        "note": "Clock milestones after 17:30 are deadlines. Vacant inference slots take the next ready job.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "clock-gate-latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
