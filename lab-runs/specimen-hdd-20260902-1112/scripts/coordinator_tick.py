#!/usr/bin/env python3
"""Clock-aware coordinator tick: mode switches, backlog note, watchdog snapshot."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from paths import HDD_ROOT, RUN_DIR
from scheduler import (
    BROAD_FREEZE,
    HARD_END,
    PRESERVATION_START,
    load_state,
    now_jst,
    queue_depths,
    render_status,
    save_state,
    set_mode,
)
from watchdog import snapshot as wd_snapshot

JST = ZoneInfo("Asia/Tokyo")


def tick(scratch: Path | None = None) -> dict:
    now = datetime.now(JST)
    state = load_state()
    mode = state.get("mode")
    if now >= HARD_END and mode != "hard_stop":
        set_mode(state, "hard_stop", now=now)
        (RUN_DIR / "HARD_STOP.md").write_text(f"HARD STOP at {now_jst(now)}\n", encoding="utf-8")
    elif now >= PRESERVATION_START and mode == "running":
        set_mode(state, "preservation", now=now)
    rec = wd_snapshot(state, scratch / "throughput" if scratch else None)
    state["last_watchdog"] = rec["at_jst"]
    save_state(state)
    (RUN_DIR / "STATUS.md").write_text(render_status(state, now), encoding="utf-8")
    hb = RUN_DIR / "heartbeat.md"
    prev = hb.read_text(encoding="utf-8") if hb.exists() else "# Heartbeat\n\n"
    depths = queue_depths(state)
    prev += (
        f"- {now_jst(now)} mode={state.get('mode')} ready={sum(depths.values())} "
        f"r1_ready={depths.get('READY_R1_DREAM', 0)} "
        f"r1_inflight={rec.get('R1_calls_in_flight')} "
        f"sched_fail={rec.get('scheduling_failure')}\n"
    )
    hb.write_text(prev, encoding="utf-8")
    return {"mode": state.get("mode"), "at": now_jst(now), "watchdog": rec}


def main() -> None:
    scratch = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    print(json.dumps(tick(scratch), default=str, indent=2))


if __name__ == "__main__":
    main()
