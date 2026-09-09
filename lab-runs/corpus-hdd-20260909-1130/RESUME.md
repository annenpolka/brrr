# Resume this run (do not re-init live trials)

Run id: `corpus-hdd-20260909-1130`
Hard end (rescheduled): 2026-09-09 13:56 JST. Original ceiling 2026-09-10 00:00 JST not extended.
Dreamer: `deepseek/deepseek-r1` only
No 9/2 scheduler.

```
export PYTHONPATH=lab-runs/corpus-hdd-20260909-1130/scripts
python3 lab-runs/corpus-hdd-20260909-1130/scripts/clock_gate.py
python3 /Users/annenpolka/.codex/skills/hdd-loop/scripts/hdd.py --root .hdd-runs/corpus-hdd-20260909-1130 status --trial case-001-a
```

Single tick (refuses save/stop before the named JST clock):

    PYTHONPATH=lab-runs/corpus-hdd-20260909-1130/scripts python3 lab-runs/corpus-hdd-20260909-1130/scripts/gate_tick.py

- 13:40 first-selection GATE
- 13:42 反証 GATE
- 13:44 broad-end GATE
- 13:46 save
- 13:51 drain
- 13:56 HARD_STOP

Set GOAL_SCRATCH only in the live goal environment when copying captures. Do not hard-code a scratch path here.
