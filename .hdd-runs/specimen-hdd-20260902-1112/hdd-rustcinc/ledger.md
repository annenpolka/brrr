# HDD Ledger

Iteration: 1

## Preserve

- A query can stay green across a revision when a first-run dependency was never recorded
- with_anon_task can return a DepNodeIndex that the caller does not read_index

## Established

- Packet: next-solver with_cached_task uses with_anon_task and does not read_index; old solver in_task does; cfail2 ICEs decoding a gone DefId while typeck of poll is reused

## Rejected

- Invented rustc incremental dumps and DefId tables are not host-executed

## Constraints

- No rustc. Owned two tables: recorded deps of a query vs identities that changed. Transfer is not visitid.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which query stayed green, and which first-run dependency that identity did not record

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a green query versus a changed identity missing from its recorded deps
Nearest existing operation: print two dep lists / visitid
Observable delta: green typeck_of poll; missing type_of Error
Reason: two dumps still leave the unrecorded edge as a hand join
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
