# HDD Ledger

Iteration: 1

## Preserve

- A named sentinel passed as dict.get default can be inferred as the shared class, not the named value

## Established

- Packet: assert_type wants str | Unknown, mypy says str | sentinel

## Rejected

- Invented mypy expandtype listings are not host evidence

## Constraints

- No mypy. Owned type records: expected identity vs inferred identity. Transfer bindname

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which identity the checker kept after TypeVar substitution, and where the literal attached to Unknown went

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name value identity vs class identity after a substitution
Nearest existing operation: bindname
Observable delta: Unknown vs sentinel
Reason: adjacent to bindname; do not mint mypy
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
