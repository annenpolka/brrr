# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B nested pyproject ignore commented; cached ruff check leftover-ignores t2.py while t3.py may report; --no-cache names both
- failing_ref Resolver::add registers only {path}/{*filepath} so a directory query misses

## Rejected

- Invented ruff check / ruff clean / find ~/.cache/ruff transcripts are not host-executed
- Dreamer recommended PR #12727 as the repair; that is the sealed answer-key

## Constraints

- Do not send ruff cache theater back to R1. Distinct from specimen-107.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover nested-directory ignore cache after pyproject.toml changed
Nearest existing operation: diff ruff check . vs ruff check --no-cache .
Observable delta: leftover_ignore = cached silent AND nocache F821 for the same nested file
Reason: Dreamer restated the seed Case B leftover t2.py vs t3.py; two ruff invocations already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
