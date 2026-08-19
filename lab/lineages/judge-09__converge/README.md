# brrr — Overnight Developer Tool Evolution Lab

Autonomous overnight search for developer tools that do not meaningfully exist yet.

Experiment window: **2026-08-19 23:45 JST → 2026-08-20 09:00 JST**.

Coordinator stays in the parent workspace. Candidates live in isolated git worktrees. Do not merge a candidate into `main` unless a later generation explicitly promotes it.

## This worktree (judge-09)

Convergent-evolution judge. Isolated. Never merge to main.

Deliverable: [`lab/judges/FINAL_CONVERGE.md`](lab/judges/FINAL_CONVERGE.md)

Ideas independently discovered twice are evidence of a real primitive. Bakeoff carry still holds for invert, ambit, and cinch 0.3. Reimpls that beat their ancestors: stencil (camera), dwelt/roost (merge-birth origin), nagori (JSON facts), snug vs cinch 0.2 (test-only red), reimpl-08 scree (repeated key=value), prove (LATENT bound). Name collision `scree` is two unrelated verbs.

## Layout

- `Overnight Developer Tool Evolution Lab — Master Prompt.md` — the night's constitution
- `lab/STATE.md` — live experiment board (generation, workers, decisions)
- `lab/PROTOCOL.md` — how candidates report, how judges score
- `lab/heartbeat.md` — heartbeat log
- `lab/lineages/` — collected candidate reports copied out of worktrees
- `lab/judges/` — first selection, bakeoffs, destroyers, final jury
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
