# Coordinator tick (this run only)

Read `lab-runs/specimen-hdd-20260909-1730/STATE.md`, `jobs.jsonl`, `r1-ledger.json`, `clock-start.txt`, and `docs/execplans/20260909-1730-hdd.md`.

Live clock: `TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S %Z'`.

Rules that never change:

- Run id `specimen-hdd-20260909-1730`. Do not re-init `corpus-hdd-20260909-1130` or `specimen-hdd-20260902-1112`.
- Dreamer is `deepseek/deepseek-r1` only. Host is Red Pen. Public bundle only.
- HTTP success is not tool success.
- Do not pass old candidate names, `unlike runpair`, 原文, PRIVATE審査, collector root, `.git`, or the execplan to the Dreamer.
- 32113 is discovery, not 未知holdout. If still 1 input, keep the 小規模試行 label.
- HOLD/FAIL are not rewritten to PASS. reviewer_type is agent, not human.
- Do not mix new candidates into coordinator main. Do not leave worktrees inside the run directory.
- After 17:30 JST, clock milestones are deadlines, not wait-to-start. A freed inference slot takes the next ready job. No isomorphic-Dream filler.

If now >= 2026-09-10 09:00 JST:

    python3 lab-runs/specimen-hdd-20260909-1730/scripts/day_end.py hard-stop

Stop this run's `hdd.py`/`dream.sh` only. Do not kill 9/2 or `lab-hdd/` PIDs. Write 採否/費用/入力hash/再実行/HARD_STOP. Then stop ticking.

If now >= 2026-09-10 08:00 JST and < 09:00:

    python3 lab-runs/specimen-hdd-20260909-1730/scripts/day_end.py save

No new wide exploration. No new R1 except already in-flight.

If now < 08:00 JST: fill vacancy.

1. If a Dream just finished and Red Pen is pending, write host Red Pen JSON and `hdd.py record-redpen`. Do not treat HTTP 200 as tool success.
2. If R1 slot is free, budget `r1_budget.py gate` allows it, contamination is 0, and phase is before broad freeze: `scripts/dream.sh <trial> <phase>` for a non-isomorphic next turn. Preview `--check-meta` first.
3. Else collect/resume (200 req / 600 s slices), screen issue bodies, HOLD if no View. Host 実機 of public snippets is allowed; do not pass 実機 or 正解 to Dreamer.
4. Implement a harvest candidate only in a worktree outside the run directory; refute immediately; harvest into `lab-runs/specimen-hdd-20260909-1730/lineages/`; remove the worktree.

Update `STATE.md`, `heartbeat.md`, `jobs.jsonl` (`intentional_idle: false`). Run `python3 lab-runs/specimen-hdd-20260909-1730/scripts/jobs.py`.
