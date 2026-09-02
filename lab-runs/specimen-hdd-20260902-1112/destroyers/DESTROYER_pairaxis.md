# DESTROYER pairaxis

Target: `lineages/candidate-pairaxis/pairaxis`

Happy path: two record files, names differing keys, `only_axis` when n_diff==1.

## Attacks

| case | result |
| --- | --- |
| missing files | `pairaxis: file not found` rc=2 |
| identical records | `only_axis none` `n_diff 0` rc=0 |
| two diffs | `only_axis multiple` (does not invent a single axis) |
| unseen pair | names `recognized` as only_axis |

## Primitive

Does not run the underlying tools; diffs caller-supplied traces. That is honest for paired specimens.

## Decision

**KEEP** as a paired-specimen lens. **MUTATE** later if it should refuse `only_axis multiple` without listing diffs (it already lists them).

Do not KILL.
