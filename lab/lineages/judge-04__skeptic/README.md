# brrr — Overnight Developer Tool Evolution Lab

Autonomous overnight search for developer tools that do not meaningfully exist yet.

Experiment window: **2026-08-19 23:45 JST → 2026-08-20 09:00 JST**.

Coordinator stays in the parent workspace. Candidates live in isolated git worktrees. Do not merge a candidate into `main` unless a later generation explicitly promotes it.

## Layout

- `Overnight Developer Tool Evolution Lab — Master Prompt.md` — the night's constitution
- `lab/STATE.md` — live experiment board (generation, workers, decisions)
- `lab/PROTOCOL.md` — how candidates report, how judges score
- `lab/heartbeat.md` — heartbeat log
- `lab/lineages/` — collected candidate reports copied out of worktrees
- `EVOLUTION_REPORT.md` — written in the last twenty minutes

## Phases (JST)

| Window | Generation |
| --- | --- |
| 23:45–01:15 | Gen 1 Cambrian explosion |
| 01:15–03:00 | Gen 1 development / dogfood |
| 03:00–04:00 | First selection (independent judges) |
| 04:00–06:30 | Gen 2 mutations, hybrids, reimplementations |
| 06:30–07:30 | Adversarial destroyers |
| 07:30–08:20 | Gen 3 exploitation |
| 08:20–08:40 | Final jury |
| 08:40–09:00 | Preservation + `EVOLUTION_REPORT.md` |

## Rule

Until 09:00 JST, a finished worker is a vacancy. Fill it.

## This worktree — judge-04 FINAL_SKEPTIC

Independent tomorrow-test. Default **no**. Prefer `rg | awk`.

Install: **cinch 0.3**, **winnow**, **invert**, **ember**. Not STATUS.md's twelve. Not zanei (JSON-blind). Not cinch 0.2 (CLEAN-on-red). Not invert peels as products.

Verdict: `FINAL_SKEPTIC.md` (canonical copy `lab/judges/FINAL_SKEPTIC.md`). Isolated worktree only. Do not merge to parent main. Do not rewrite tools.
