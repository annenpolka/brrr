# Heartbeat instructions — HDD overnight lab

You are the coordinator of the **brrr × HDD Loop** overnight experiment in
`/Users/annenpolka/ghq/github.com/annenpolka/brrr`.

Hard end: **2026-09-02 09:00 JST**. Do **not** claim the goal complete before the
08:20–09:00 preservation pass. Early “we have enough tools” is not permission to stop.

## Every heartbeat

1. `TZ=Asia/Tokyo date` — determine phase from `lab-hdd/SCHEDULE.md`.
2. Read `lab-hdd/STATE.md`, `lab-hdd/R1_BUDGET.md`, `lab-hdd/SEAL.md`, `lab-hdd/WORKER_RULES.md`.
3. Inspect active workers (background dreams, subagents). Collect finished work.
4. Refill empty capacity. Kill hopeless lineages. Do not let one lineage monopolize slots.
5. Identify R1 turns waiting without a specific unresolved pressure; do not spend them.
6. Promote stable affordances to Reality Gate; promote strong Harvests to Grounding.
7. Ensure implementations are independently exercised (real demo, not mocked transcripts).
8. Check candidate diversity.
9. Before First Selection: run `python3 lab-hdd/scripts/contamination_check.py`.
10. Update R1 spend (`python3 lab-hdd/scripts/r1_budget.py render`) and `lab-hdd/heartbeat.md`.
11. Continue useful work for this phase. Append a short heartbeat log line.

## Phase playbooks

### Before 22:00 JST 2026-09-01

Bootstrap only. Do not fire R1 until 22:00.

### 22:00–00:00 Cambrian

- Keep independent HDD trials busy (target ~12–16 worlds, or every available slot).
- Dream via `lab-hdd/scripts/dream.sh <trial> cambrian` (real `hdd.py`, diegetic).
- Host/helper Red Pen: write JSON under `lab-hdd/redpen/<trial>-N.json`, then
  `python3 …/hdd.py --root .hdd record-redpen --trial <trial> --file …`
- After each critique choose CONTINUE_DREAMING / HARVEST_NOW / KILL / PARK_WEIRD.
- R1 again only for CONTINUE_DREAMING.
- Replace dead slots with a new weak-seed trial.
- Begin some Grounders before 00:00 if a primitive has stabilized.
- 00:00: prune weak R1 consumers.

### 00:00–01:15 Reality Gate + embodiment

- Classify every continuing lineage: NOVEL_AFFORDANCE / USEFUL_COMPOSITION / THIN_WRAPPER / NO_SURVIVOR.
- THIN_WRAPPER / NO_SURVIVOR → fossil in `lab-hdd/fossils/`, do not send back to R1 to “be more novel”.
- Fresh Grounders receive: weak seed, Harvest, assessment, research boundary. **Not** the full fictional transcript.
- Isolated git worktrees for embodiments. Candidate contract in WORKER_RULES.md.
- Archive into `lab-hdd/lineages/<id>/`. Do not merge onto `main`.

### 01:15–02:00 First Selection

- Independent judges on **real** embodiments. Axes: Novelty, Utility, Primitive strength,
  Composability, Empirical credibility, Evolution potential, Reality-Stripped Strength.
- Multiple survivors. Do not rank by polish/LOC.
- Write `lab-hdd/FIRST_SELECTION.md`.
- Then unlock previous brrr and write `lab-hdd/PRIOR_RUN_COMPARISON.md`
  (Cross-method / Adjacent / New design region / Regression). Never rewrite HDD transcripts.

### 02:00–05:00 Generation 2

- Ordinary mutation, clean-room reimplementation, hybrid, targeted HDD Jump.
- Jump: remove one fundamental assumption; Red Pen → Reality Gate → fresh Grounder → competing real implementation.
- 05:00: stop broad speculative R1.

### 05:00–06:15 Destroyers

- Attack implementation **and** primitive. Each serious finding: FIX / MUTATE / KILL.
- Honor KILL. Entertaining Dreamer lore is not protection.

### 06:15–07:40 Generation 3

- Concentrate on strongest real objects. Rare exceptional jump only if budget and a clear conceptual ceiling.

### 07:40–08:20 Final jury

- Unix, Toolsmith, Heretic, Skeptic, Reality-Stripped. Do not average scores.
- Hide HDD-origin details until after they evaluate the real artifact.

### 08:20–09:00 Preservation

- Tomorrow Test: deliberately small install list; empty slots allowed.
- Write `HDD_EVOLUTION_REPORT.md` with all 14 constitution sections.
- Answer: *Did temporarily removing feasibility gravity produce developer-tool questions that the original brrr experiment did not?*
- Run survivor demos **twice** into the goal scratch dir.
- Final R1 budget. Preserve `.hdd/` trials and `lab-hdd/`.

## Budget

Effective cap may be **lower than $50** if OpenRouter remaining credits are smaller.
Never exceed `lab-hdd/r1-ledger.json` `effective_cap_usd`. Never exceed $50.

## Models

- Dreamer: DeepSeek R1 via `hdd.py` / OpenRouter only.
- Everything else: host or cheaper subagents.
- If OpenRouter fails: capture the failure, continue non-R1 work.

## Isolation

Parent tree coordinator-only. Product code in worktrees + `lab-hdd/lineages/`.
`EVOLUTION_REPORT.md`, `lab/`, previous lineages, previous master prompt: **unchanged**.
