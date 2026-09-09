# Experiment state

- Run: `corpus-hdd-20260909-1130`
- Start: 2026-09-09 11:30:22 JST
- Not-before: 2026-09-09 11:30:00 JST
- Hard end: 2026-09-09 13:56:00 JST (rescheduled earlier; original 2026-09-10 00:00:00 JST not extended)
- Preservation start: 2026-09-09 13:46:00 JST (rescheduled; original 23:25 not used)
- Phase: HARD_STOP. Dream trial case-001-a stopped after 3 turns. KEEP runpair. Broad exploration ended early (no new trials). this-run live PIDs 0.
- R1 calls: 3. Observed spend ~$0.033. Conservative ~$0.082. Effective cap $16.1876.
- Input scale: **小規模試行** (1 discovery case). This case is not 未知holdout.
- Parent role: coordinator only (no candidate product merge onto main)
- Dreamer: `deepseek/deepseek-r1` via OpenRouter through `/Users/annenpolka/.codex/skills/hdd-loop/scripts/hdd.py` `--root /Users/annenpolka/ghq/github.com/annenpolka/brrr/.hdd-runs/corpus-hdd-20260909-1130`
- Critic: host Red Pen
- Effective R1 cap: **$16.1876** (available $17.6876 − $1.50 reserve, user cap $30)
- Isolation: `static_bundle_only` (not OS/network isolation; not 未知性)
- Input scale: starting with 1 discovery case; if still 1 after collect window, this is 小規模試行 and the case is not 未知holdout
- Previous 9/2 wrapper/scheduler: not started
- Day-end scheduler (this run only): cancelled 01a08413de457e93a34e002f81c49ec6 (old 00:00 prompt; leftover gates driven by wait_remaining_gates.py)
- Named-gate waiter: wait_remaining_gates.py finished 13:56:02 JST HARD_STOP (live dream/hdd.py PIDs 0; no new R1)
- Checkpoint 2026-09-09 11:51 JST: 3 R1 calls done; no live dream PIDs; waiting 23:25 save / 00:00 HARD_STOP. No new R1.
- Checkpoint 2026-09-09 12:31 JST: pulled 12:00–14:00 collect/review and extra runpair 反証 forward. No new R1. No early HARD_STOP.
- Checkpoint 2026-09-09 13:02 JST: 14971 host-reproduced (9.1.1 fail / 8.4.2 pass); runpair empty sidecar. other-ecosystems collect started (cargo/uv/npm/TS). No new R1. No HARD_STOP.

- Checkpoint 2026-09-09 13:44:47 JST: 22:45 gate live. Broad exploration already ended. No new R1.
- Checkpoint 2026-09-09 13:45:58 JST: 13:40 first_selection GATE recorded (catch-up). FIRST_SELECTION already on disk. No new R1.
- Checkpoint 2026-09-09 13:45:58 JST: 13:42 counterexample GATE recorded (catch-up). runpair 反証 already recorded. No new R1.

- Checkpoint 2026-09-09 13:46:02 JST: 23:25 save: 採否/費用/入力hash/再実行 + restore.

- Checkpoint 2026-09-09 13:51:02 JST: 23:50 drain. No new spawn/R1/collect.

- Checkpoint 2026-09-09 13:56:02 JST: 00:00 HARD_STOP. This run dream/hdd.py PIDs 0.
- Checkpoint 2026-09-09 14:31:30 JST: stale 30m resume fire. clock_gate phase hard_stop, HARD_STOP.md already on disk (13:56:02), this-run hdd.py/dream.sh PIDs 0. No re-init, no new R1, no 9/2 scheduler, runpair not merged. Did not rewrite HARD_STOP. Recurring scheduler list empty.
