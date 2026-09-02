# HDD Ledger

Iteration: 1

## Preserve

- The only observed difference between paired runs can be test order plus a leaked global

## Established

- Owned run_orders.py: A test_b then test_a PASS; B test_a then test_b FAIL acc

## Rejected

- Invented --inspect-state flag is not installed

## Constraints

- Transfer onto pairaxis / leakorder. No new binary

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- the single differing field between the two order traces

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name the order-only difference without reading both traces
Nearest existing operation: pairaxis
Observable delta: only_axis order / acc
Reason: duplicate of specimen-012 / pairaxis
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
