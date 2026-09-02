# HDD Ledger

Iteration: 1

## Preserve

- A pretty-printer can sort keys while the failing assertion used insertion order

## Established

- Packet: hypothesis dict pretty vs list(d) order

## Rejected

- Specific pytest output in this turn is unverified

## Constraints

- No hypothesis checkout required; an owned dict printer fixture is enough

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Label each displayed dict as sorted-keys vs insertion-order

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show which printed mapping is sorted and which preserves insertion order
Nearest existing operation: print(d) vs print(list(d))
Observable delta: one query naming the printer that reordered keys
Reason: three conflicting views of the same dict
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
