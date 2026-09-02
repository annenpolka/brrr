# HDD Ledger

Iteration: 1

## Preserve

- The same callable can return different totals under pytest versus a direct python -c invocation
- The on-disk module paths can still be reported as identical

## Established

- Wild seed had no external specimen
- Packet: pytest asserts 15.00 vs expected 12.50; python -c prints total 12.50; both claim the same pricing.py/zones.py paths

## Rejected

- dv CLI, pricing.py/zones.py discrepancy, and Decimal 15.00 vs 12.50 are Dreamer-generated
- dv is not installed; envdiff/trace/inspect/test_mode output is Dreamer-generated
- BASE_SURCHARGE 5.00 vs 2.50 is unsupported precision until a host fixture prints it

## Constraints

- No invented runtime inspector
- Observable evidence is pytest stdout and python -c stdout already in the packet

## Open Questions

- Can the two-runtime delta be named without a hidden test_mode flag?

## Human Pressure

- (none)

## Harvest Candidates

- Ask which runtime produced which total for the same quote() arguments

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: compare pytest and direct-call results for one function and name the disagreement
Nearest existing operation: run pytest and python -c and diff by eye
Observable delta: one query that treats the two-runtime disagreement as the object
Reason: each command looks locally consistent; the remainder is the cross-runtime delta
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no dv. Continue only with pytest stdout and python -c stdout from the packet.

## Pending

(none)
