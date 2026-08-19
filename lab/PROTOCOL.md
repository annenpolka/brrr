# Lab protocol

## Candidate identity

`candidate-NN`, later `mutation-NN`, `hybrid-NN`, `reimpl-NN`, `destroyer-NN`.

## Required files in a candidate worktree

1. A runnable tool (CLI preferred).
2. `README.md` — primitive, install/run, 3 examples.
3. `CANDIDATE.md` — idea, interaction model, empirical transcript, surprises, failures, next mutations.
4. A demo that actually runs: `./demo.sh` or equivalent.
5. At least one commit of working software.

## CANDIDATE.md shape

```
# <id> — <tool name>

## Primitive
One sentence. The new interaction, not the feature list.

## Why this might not exist
What recurring annoyance or missing verb.

## How to run
Exact commands from the worktree root.

## Empirical transcript
Commands run + observed output. Before-and-after the first improvement.

## Dogfood targets
Repos or fixtures used.

## Surprises
## Failures
## Suggested mutations
## Kill / keep
```

## Judge axes (do not rank by polish)

- Novelty
- Utility
- Primitive strength
- Composability
- Empirical credibility
- Evolution potential

## Parent workspace rule

The parent tree is coordinator-only. Candidate implementation happens in isolated worktrees. The parent may copy reports into `lab/lineages/` after a worker finishes.
