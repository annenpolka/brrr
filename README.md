# brrr — Overnight Developer Tool Evolution Lab

Autonomous overnight search for developer tools that do not meaningfully exist yet.

Next run: follow [HDD v2](docs/protocols/hdd-v2.md) and the
[next execution prompt](docs/preparation/next-run-prompt.md). The 2026-09-09 17:30
run is closed (0 products, 3 Dreams, 1 discovery case). Do not resume its scripts.

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
One real reported-input case was reviewed and exported with the previous exporter; see
[the historical evidence pilot](docs/preparation/evidence-pilot.md).
The v2 seed changes the exporter hash: reprocess and review before a new export.
The new 24-case HDD input still requires content review and selection.

Experiment windows are frozen per run. No new run is scheduled by this change.

Coordinator stays in the parent workspace. Candidates live in isolated git worktrees. Do not merge a candidate into `main` unless a later generation explicitly promotes it.

## Layout

Coordinator product and corpus live here. Historical overnight boards stay read-only.

- `src/brrr_corpus/` — corpus store, collection, selection, review boundary, recovery and run admission
- `src/runpair/` — twice-run directory snapshot CLI (promoted 2026-09-09); entry `python3 scripts/runpair.py`
- `scripts/corpus.py`, `scripts/check_corpus.py` — corpus CLI and its tests
- `recipes/` — collection and selection recipes
- `docs/protocols/` — current HDD operating contract
- `docs/execplans/`, `docs/execution/`, `docs/preparation/` — dated plans, start prompts, corpus receipts
- `docs/archive/` — previous master prompts, collection design, and overnight jury reports (read-only)
- `lab-runs/<run-id>/` — one experiment's coordinator records; `lab-runs/current` points at the latest initialized run
- `.hdd-runs/<run-id>/` — Dreamer trial transcripts for that run
- `lab/`, `lab-hdd/`, `.hdd/` — previous overnight working trees; do not overwrite

## Continue only with progress

A free worker takes a job that can change input eligibility or the design decision.
Record concrete blockers, prepare a review package, and preserve separate discovery
and runtime evidence. The default v2 admission policy caps per-case attempts and
refuses new work after 30 minutes without a new evidence-backed milestone.

Use `admit-job` before each recovery, Dream or grounding job. Repeated tests and
heartbeat entries do not reset progress. If no admissible work remains, preserve
and close; an empty result is valid. See [HDD v2](docs/protocols/hdd-v2.md) for the
policy, commands, model-budget gates and process-stop responsibilities.
