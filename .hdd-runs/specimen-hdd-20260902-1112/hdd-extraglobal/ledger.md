# HDD Ledger

Iteration: 1

## Preserve

- Order-only paired runs can leak more than one binding; the question is naming both without reading both traces
- Paired orders of the same two tests can leak more than one object (acc and flag) with only order changing

## Established

- Host pairaxis on owned traces: diff acc [] vs ['a']; diff flag False vs True; only_axis multiple
- Owned run_orders_extra.py: order test_b then test_a PASS; order test_a then test_b FAIL ['a']; both end acc ['a'] flag True

## Rejected

- dev-cli capture-state is not installed
- Invented dev-cli capture-state / report-leaks is not installed

## Constraints

- Transfer pairaxis. Nested tests are not leakorder module tests. No new leak binary.
- Transfer onto pairaxis. No new binary. Do not re-dream hdd-s072

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- both leaked objects acc and flag as pairaxis diffs
- the order-only difference naming both leaked objects

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name order-only leaked objects without reading both traces
Nearest existing operation: pairaxis
Observable delta: only_axis multiple (order, acc, flag)
Reason: duplicate of specimen-012 / pairaxis with one extra global
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
