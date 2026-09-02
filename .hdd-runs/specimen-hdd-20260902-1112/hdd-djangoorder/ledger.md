# HDD Ledger

Iteration: 1

## Preserve

- Tests can assert row order the SQL did not promise

## Established

- specimen-008 Django unordered SELECT

## Rejected

- djanorder CLI is not installed

## Constraints

- Transfer; no new binary

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- assertions that depend on unspecified order

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name assertions that require an order the query did not ask for
Nearest existing operation: read the test and the SQL
Observable delta: order-dependent without ORDER BY
Reason: duplicate of specimen-008
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
