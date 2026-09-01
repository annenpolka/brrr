# Worker rules (all roles)

## Parent tree

The parent working tree (`brrr` on `main`) is coordinator/reporting-only.

- Do not merge candidate product code onto `main`.
- Do not edit `EVOLUTION_REPORT.md`, `lab/`, existing lineages, or the previous master prompt.
- New coordinator state lives under `lab-hdd/`.
- Raw HDD trials live under `.hdd/<trial>/`.
- Candidate implementations live in isolated git worktrees, then are archived under `lab-hdd/lineages/<id>/`.

## Contamination (until First Selection exists)

Do not read sealed previous-brrr materials listed in `lab-hdd/SEAL.md`.

Do not mention previous-run tool names as things to avoid.

## Dreamer channel

Dreamer turns go through the real `hdd-loop` runner:

```bash
set -a && source .env.hdd && set +a
export HDD_DREAMER_HTTP_TIMEOUT=900
python3 ~/ghq/github.com/annenpolka/skills/hdd-loop/scripts/hdd.py \
  --root .hdd dream --trial <name>
```

Diegetic prompts only. The Dreamer must never be told about HDD, Dreamer, Red Pen, Ledger, Harvest, novelty scores, or “respond to the critic”.

## Red Pen

Host agent (or a helper subagent following `hdd-loop` Red Pen policy) writes JSON and records it with `hdd.py record-redpen`. After every critique choose exactly one:

```text
CONTINUE_DREAMING
HARVEST_NOW
KILL
PARK_WEIRD
```

R1 is invoked again only for `CONTINUE_DREAMING`.

Do not send `THIN_WRAPPER` / `NO_SURVIVOR` back to R1 with “make this more novel”.

## Evidence boundary

Dreamer text is fictional design material. It is never execution evidence.

A number that appears only in a Dreamer transcript is not measured.

## Candidate contract (embodiments)

1. runnable tool (CLI preferred)
2. `README.md`
3. `CANDIDATE.md`
4. runnable demo (`./demo.sh`)
5. fixtures/tests
6. at least one working commit
7. actual execution transcript
8. at least one dogfood-driven improvement
9. origin metadata (`origin.method: hdd`, `origin.trial`)
10. pre-implementation Reality assessment preserved
