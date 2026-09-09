# brrr — Overnight Developer Tool Evolution Lab

Autonomous overnight search for developer tools that do not meaningfully exist yet.

Issue collection redesign preparation (2026-09-09): see
[the implementation and migration report](docs/preparation/README.md) and
[the next execution prompt](docs/preparation/next-run-prompt.md).
The new corpus CLI is `python3 scripts/corpus.py`; its tests are
`python3 scripts/check_corpus.py`. GitHub collection and resume are ready:
`python3 scripts/corpus.py collect --recipe recipes/collection/github-pilot-v1.json`.
See [collection startup and verification](docs/preparation/collection-readiness.md).
Try the complete offline reuse loop with
`python3 scripts/corpus.py mini-demo --output .brrr-corpus/mini-demo-v2`.
See [the small trial and real-data review workflow](docs/preparation/mini-loop.md).
One real reported-input case is now reviewed and exported; see
[the ready evidence pilot](docs/preparation/evidence-pilot.md).
The new 24-case HDD input still requires content review and selection.

Experiment window: **2026-08-19 23:45 JST → 2026-08-20 09:00 JST**.

Coordinator stays in the parent workspace. Candidates live in isolated git worktrees. Do not merge a candidate into `main` unless a later generation explicitly promotes it.

## Layout

Coordinator product and corpus live here. Historical overnight boards stay read-only.

- `src/brrr_corpus/` — corpus store, collection, selection, review boundary
- `src/runpair/` — twice-run directory snapshot CLI (promoted 2026-09-09); entry `python3 scripts/runpair.py`
- `scripts/corpus.py`, `scripts/check_corpus.py` — corpus CLI and its tests
- `recipes/` — collection and selection recipes
- `docs/execplans/`, `docs/execution/`, `docs/preparation/` — live plans, start prompts, corpus receipts
- `docs/archive/` — previous master prompts, collection design, and overnight jury reports (read-only)
- `lab-runs/<run-id>/` — one experiment's coordinator records; `lab-runs/current` points at the latest initialized run
- `.hdd-runs/<run-id>/` — Dreamer trial transcripts for that run
- `lab/`, `lab-hdd/`, `.hdd/` — previous overnight working trees; do not overwrite

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
