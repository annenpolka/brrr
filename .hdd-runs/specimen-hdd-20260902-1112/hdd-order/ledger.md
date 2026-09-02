# HDD Ledger

Iteration: 1

## Preserve

- The same two tests PASS or FAIL depending only on order
- Module-level acc is the leaked object in this fixture

## Established

- Host fixture: test_a then test_b FAIL; test_b then test_a PASS

## Rejected

- testflow-analyzer capture/permute JSON is Dreamer-generated

## Constraints

- No automatic whole-suite mutable-state oracle
- Observable evidence is the two run orders and assertion outcomes

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Ask which order exposes the leak and what name leaked

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: run a pair of tests in two orders and report what leaked when only order changed
Nearest existing operation: pytest in two explicit nodeid orders
Observable delta: one query that names the leaked binding and the sufficient order instead of two manual runs
Reason: ordinary pytest does not treat order-as-the-only-axis as a first-class question
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
