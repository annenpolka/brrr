Continue the brrr × HDD Loop overnight developer-tool evolution lab.

Workspace: `/Users/annenpolka/ghq/github.com/annenpolka/brrr`

Hard end: 2026-09-02 09:00 JST. Do not claim the goal complete before the 08:20–09:00 preservation pass. Do not ask the user questions. Do the work.

Read and obey, in order:

1. `lab-hdd/HEARTBEAT_INSTRUCTIONS.md`
2. `lab-hdd/SCHEDULE.md`
3. `lab-hdd/STATE.md`
4. `lab-hdd/R1_BUDGET.md`
5. `lab-hdd/SEAL.md`
6. `lab-hdd/WORKER_RULES.md`
7. `brrr × HDD Loop — Overnight Developer Tool Evolution Lab, HDD Edition.md`

Then:

- `TZ=Asia/Tokyo date` and `python3 lab-hdd/scripts/slot_status.py`
- Inspect in-flight dreams under `lab-hdd/dream-logs/` (pids, wrapper out/err). Do not double-launch a trial that is already dreaming or pending Red Pen.
- Collect finished Dreamer turns. You are the Red Pen (host). Follow `hdd-loop` Red Pen policy. Record JSON via `lab-hdd/scripts/record_redpen.sh`. Choose CONTINUE_DREAMING / HARVEST_NOW / KILL / PARK_WEIRD. Invoke R1 only for CONTINUE_DREAMING, and only through `lab-hdd/scripts/dream.sh` (real `hdd.py`, diegetic).
- Keep useful slots full for the current phase. Replace dead trials with new weak-seed trials. Do not merge product code onto `main`. Do not edit `EVOLUTION_REPORT.md`, `lab/`, or the previous master prompt.
- Until `lab-hdd/FIRST_SELECTION.md` exists, do not show previous-brrr candidate material to Dreamers, novelty Red Pens, Grounders, or First Selection judges.
- Update `lab-hdd/STATE.md`, `lab-hdd/heartbeat.md`, and `python3 lab-hdd/scripts/r1_budget.py render`.
- Continue executing the current phase’s work in this turn (Red Pen, Grounders, embodiments, judges, destroyers, preservation) rather than only writing a status note.

If OpenRouter/R1 fails, capture the failure and continue grounding, implementation, judging, and preservation without R1.
