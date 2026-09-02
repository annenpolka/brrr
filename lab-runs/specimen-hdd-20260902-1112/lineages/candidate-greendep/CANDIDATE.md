# greendep

origin.method: hdd
origin.trial: hdd-rustcinc
specimens: [specimen-075]
classification: USEFUL_COMPOSITION

## Primitive

Name a green query whose *own* changed dependency was never recorded.

`changed` is per-query (`changed	QUERY	DEP`). An unrelated green is
not false_green. A recorded dep that also changed is `invalidation`,
rc=1, not rc=0 silence. A green with no `changed` pair is
`incomplete` (rc=2), not agreement. `-` is not a legal NAME.

## Smallest artifact

Python 3 stdlib CLI `greendep`. rc=1 on false_green or invalidation.
rc=2 on incomplete. Lists capped (32 / 256-char display); counts not.
