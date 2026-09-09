#!/usr/bin/env python3
"""Sleep until each remaining named gate, then run gate_tick. No re-init, no new R1."""
from __future__ import annotations

import time

import clock_gate
import gate_tick
from paths import RUN_DIR

# Named checkpoints that can be recorded after their clock without running save/drain/stop.
CHECKPOINT_ONLY = ("first_selection", "counterexample", "broad_end")


def catch_up() -> None:
    """Record any already-open checkpoint GATE files the current phase would skip."""
    at = clock_gate.now()
    for name in CHECKPOINT_ONLY:
        path = RUN_DIR / f"GATE-{name}.json"
        if clock_gate.GATES[name] <= at and not path.exists():
            written = clock_gate.checkpoint(name, at)
            print(f"catch-up {name} -> {written}", flush=True)


def main() -> None:
    while True:
        catch_up()
        at = clock_gate.now()
        action = clock_gate.due_action(at)
        upcoming = [(name, when) for name, when in clock_gate.GATES.items() if when > at]
        print(f"at={at.isoformat()} action={action} upcoming={[n for n,_ in upcoming]}", flush=True)
        if action == "hard_stop":
            gate_tick.tick()
            print("hard_stop done", flush=True)
            return
        if action != "wait":
            gate_tick.tick()
        if not upcoming:
            return
        name, when = upcoming[0]
        wait = (when - clock_gate.now()).total_seconds() + 2
        print(f"sleeping {wait:.1f}s until {name} {when.isoformat()}", flush=True)
        if wait > 0:
            time.sleep(wait)


if __name__ == "__main__":
    main()
