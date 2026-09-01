# HDD Ledger

Iteration: 1

## Preserve

- The operator distrusted an exit 0 and looked for what success actually claimed.

## Established

- system-status, probe, audit, deploy --force, release --rollback.

## Rejected

- v3.7.0, deploy #1873, 142ms latency, and orchestrator warnings are not observations.

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: after a successful deploy, probe a health endpoint and read a log
Nearest existing operation: the command plus a health check plus its logs
Observable delta: none that requires a new verb
Reason: false-success of deploy is an ordinary postcondition check
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
