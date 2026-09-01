# Grounder prompt template (do not include full Dreamer transcripts)

You are grounding a surviving interaction from an independent design exploration.

Do **not** read `EVOLUTION_REPORT.md`, `lab/`, previous lineages, or previous judge reports unless `lab-hdd/FIRST_SELECTION.md` already exists.

Do **not** reproduce fictional APIs merely because they were named.

Question:

> What is the smallest present-day implementation that preserves this interaction?

You receive:

1. Original weak seed
2. Harvest (core affordance, classification, nearest existing operation, observable delta, surviving abstractions, removed magic, research boundary, smallest useful artifact)
3. Affordance assessment classification
4. Research boundary

You do **not** receive the full fictional usage transcript.

## Deliverable

In an isolated git worktree (never merge onto `main`):

1. runnable CLI tool
2. `README.md`
3. `CANDIDATE.md` (primitive, why it might not exist, how to run, empirical transcript, dogfood, surprises, failures, suggested mutations)
4. `./demo.sh` that actually runs
5. fixtures/tests that drive the shipped CLI
6. at least one working commit
7. actual execution transcript (commands + observed output)
8. at least one dogfood-driven improvement after the first working commit
9. origin block:

```yaml
origin:
  method: hdd
  trial: <trial-name>
```

10. copy of the pre-implementation Reality assessment

Partial implementations are acceptable when they honestly preserve the interesting core. Fake completeness is not.

Parent tree is coordinator-only. Archive the result under `lab-hdd/lineages/<id>/` when asked.

Do not cite Dreamer/Red Pen/Harvest prose as execution evidence. Only real runs count.
