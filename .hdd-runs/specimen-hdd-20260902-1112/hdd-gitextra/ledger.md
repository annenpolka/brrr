# HDD Ledger

Iteration: 2

## Preserve

- An extra on a git/VCS dependency can be recorded without changing the resolved extra set
- A declared extra on a reused package node can stay off the resolved extra set while lock still succeeds

## Established

- Packet: poetry git extra
- Packet: edit-lock has no psycopg2 fact; poetry add lock grows psycopg2; pyproject unchanged

## Rejected

- poetry lock transcripts are Dreamer-generated
- Invented poetry complete_package / PR 10987 patches are not host evidence

## Constraints

- No poetry; owned two-record pair
- No poetry. Owned two records: declared extras vs resolved extras

## Open Questions

- (none)

## Human Pressure

- No poetry. Continue on two records: declared extras vs resolved extras.

## Harvest Candidates

- declared extra vs resolved extra
- Which declared extra did not enter the resolved set on the reused package node

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a declared extra that did not attach to the resolved node
Nearest existing operation: read pyproject and the lock
Observable delta: same package version, extra present vs missing in resolved set
Reason: lock success hides the missed extra
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
