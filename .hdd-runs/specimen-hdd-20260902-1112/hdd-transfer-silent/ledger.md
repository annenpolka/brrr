# HDD Ledger

Iteration: 1

## Preserve

- Two pair traces can share the extra map and still disagree on resolved extra deps
- The discriminating field in this fixture is whether requires still contains that extra dependency

## Established

- Host fixture: pair_A recognized [B] resolved [B] PASS; pair_B recognized [B] resolved [] FAIL; only_axis requires_contains_extra_dep

## Rejected

- unseen-cli is not installed; generate-question output is Dreamer-generated
- A citation of poetry issue numbers is not a host observation

## Constraints

- No poetry checkout, no network resolver
- Observable evidence is the two pair prints already in the fixture

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Ask which single field differs between the two pair traces

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: given two otherwise-similar pair traces, name the one field that explains pass vs fail
Nearest existing operation: read both prints and diff by eye
Observable delta: one query that names the discriminating field instead of a two-trace manual diff
Reason: the traces already contain the axis; the remainder is making that axis first-class
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no unseen-cli. The pair fixture is the world.

## Pending

(none)
