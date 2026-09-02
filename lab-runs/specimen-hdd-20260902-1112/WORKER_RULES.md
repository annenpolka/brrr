# Worker rules (this run)

## Parent tree

The parent working tree is coordinator/reporting-only.

- Do not merge candidate product code onto `main`.
- Do not edit historical `EVOLUTION_REPORT.md`, `HDD_EVOLUTION_REPORT.md`, `lab/`, `lab-hdd/`, `.hdd/`.
- New coordinator state lives under `lab-runs/specimen-hdd-20260902-1112/`.
- Raw HDD trials live under `.hdd-runs/specimen-hdd-20260902-1112/`.
- Candidate implementations live in isolated git worktrees, then are archived under `lineages/`.

## Contamination (until First Selection exists)

Do not read sealed materials listed in `SEAL.md`.
Do not mention previous-run tool names as things to avoid.

## Dreamer channel

```bash
/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/scripts/dream.sh <trial> <phase>
```

Uses `python3 /Users/annenpolka/ghq/github.com/annenpolka/skills/hdd-loop/scripts/hdd.py --root /Users/annenpolka/ghq/github.com/annenpolka/brrr/.hdd-runs/specimen-hdd-20260902-1112`. Diegetic prompts only.

## Red Pen

Host writes JSON and records it with `scripts/record_redpen.sh`. After every critique choose exactly one:

```
CONTINUE_WITH_TEXT_PRESSURE
CONTINUE_WITH_COUNTEREXAMPLE
HARVEST_NOW
KILL
PARK_WEIRD
```

Do not send THIN_WRAPPER / NO_SURVIVOR back to R1 with “make this more novel”.

## Evidence boundary

Dreamer text is fictional design material. It is never execution evidence.
