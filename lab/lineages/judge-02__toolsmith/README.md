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

## Final jury (08:20–08:40)

Independent ranks live in `lab/judges/FINAL_*.md`. Do not force consensus.

Toolsmith (this worktree, judge-02): **`lab/judges/FINAL_TOOLSMITH.md`** — utility-first. Tomorrow-install eight: invert, winnow, cinch 0.3, zanei, when, preen, noun, holt. Overbuilt toys: lurch, shoal, berth-as-product, hydra, rune, shim. Disagrees with FIRST_TOOLSMITH on held/pin/due PATH and on Gen3 peels as extra CLIs.

## Rule

Until 09:00 JST, a finished worker is a vacancy. Fill it.
