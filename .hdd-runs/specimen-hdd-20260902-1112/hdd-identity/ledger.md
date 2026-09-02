# HDD Ledger

Iteration: 1

## Preserve

- Two functions named parse exist; import path selects which body runs
- A stale from pkg_util import parse binds the leftover helper

## Established

- Host fixture prints util ('legacy', ...) vs parse ('moved', ...)

## Rejected

- trace-import v2.8.3 and bytecode signatures are Dreamer-generated

## Constraints

- No import tracer daemon
- Observable evidence is import statements plus function results

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Ask which definition a name-import actually bound

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: for a name, show the import path and the body that would run
Nearest existing operation: python -c import plus grep
Observable delta: one query that distinguishes leftover same-name helpers from the moved definition
Reason: grep hits both; the surviving question is bind identity not search
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
