# Resume this run

cwd: repository root.

Do **not** `hdd.py init` for `case-001-a`. Do **not** init `corpus-hdd-20260909-1130` or `specimen-hdd-20260902-1112`.

    python3 lab-runs/specimen-hdd-20260909-1730/scripts/start_run.py
    python3 /Users/annenpolka/.codex/skills/hdd-loop/scripts/hdd.py --root .hdd-runs/specimen-hdd-20260909-1730 status --trial case-001-a

Dreamer remains `deepseek/deepseek-r1`. Host is Red Pen. HTTP success is not tool success.

Clock: hard_end 2026-09-10 09:00 JST, not extended. 保全 from 08:00 JST. After 17:30, named clocks are deadlines.

    python3 lab-runs/specimen-hdd-20260909-1730/scripts/gate_tick.py
    python3 lab-runs/specimen-hdd-20260909-1730/scripts/day_end.py save      # only at/after 08:00 JST
    python3 lab-runs/specimen-hdd-20260909-1730/scripts/day_end.py hard-stop # only at/after 09:00 JST

Vacancy: take the next ready collect/review/reconstitute/refute/implement job. Do not sleep on a clock. Do not fill with isomorphic Dreams. Worktrees outside the run directory; remove before HARD_STOP. Do not merge candidates onto coordinator main during the experiment.
