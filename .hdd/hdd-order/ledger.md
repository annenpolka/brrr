# HDD Ledger

Iteration: 2

## Preserve

- The operator asked whether one development event could have caused another.
- resolve refused to answer before traces existed, which is at least an honesty gesture inside the fiction.
- resolve --temporal warned that proximity is not causation.
- The useful correlation was a shared token (email) across a commit and a failure line.

## Established

- Commands: inspect, trace, list, resolve.
- source add, list --filter, inspect, trace, resolve --temporal.

## Rejected

- Event IDs, timestamps, and parent-child links were generated, not observed.
- commit a1b2c3d, timestamps, and test_run.log were not this repository.

## Constraints

- There is no event database and no trace cache.
- The CLI may only look at files, git history, and logs that actually exist in this tree.
- Do not invent identifiers.

## Open Questions

- On two real git commits or two log lines, can the tool say more than 'A is earlier than B'?

## Human Pressure

- (none)

## Harvest Candidates

- Ask whether change A could have caused observation B using only in-tree evidence.

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: ask whether earlier change A could have caused later observation B
Nearest existing operation: git show plus grep of a log for identifiers from the diff
Observable delta: none demonstrated beyond what git+rg already do; the CLI did not automate the link
Reason: no untested delta remains that would change the class; do not send back to R1
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
