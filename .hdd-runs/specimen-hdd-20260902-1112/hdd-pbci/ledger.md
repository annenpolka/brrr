# HDD Ledger

Iteration: 1

## Preserve

- A compound command can exit 0 after a failing left-hand side because || ran a succeeding echo

## Established

- Dreamer script with set -ex; exit 1; || echo ... produced step status 0

## Rejected

- Bazel stale-file logs are not host-executed

## Constraints

- Ground as a tiny CLI over a recorded command list / shell snippet

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Which command's nonzero exit was swallowed by a later success

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: report a pipeline/list whose last success hid an earlier failure
Nearest existing operation: bash -x plus reading $?
Observable delta: names the swallowed status rather than the step's 0
Reason: CI green on echo after || is a recurring lie
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
