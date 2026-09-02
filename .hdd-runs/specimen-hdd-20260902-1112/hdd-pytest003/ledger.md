# HDD Ledger

Iteration: 1

## Preserve

- Overlapping collection paths can bind fixtures to a Directory node that is no longer the lookup node
- The same directory path can be collected as a new node after an unrelated path, and fixtures registered on the first node miss on the second

## Established

- specimen-003 already encodes this
- Packet: pytest path/a path/b path/a --collect-only; fixture closure depends on CLI order

## Rejected

- Invented dir1/dir2 tree is not host-executed pytest
- Invented pytest --trace-config and numeric node IDs are not host evidence

## Constraints

- Transfer, no new binary required
- No pytest. Owned collection events: path, node id, fixture register, fixture lookup

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Which collection object identity the fixture bound
- Whether the same path is still the same collection object, and which fixture is bound to which object identity

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name path-vs-node identity and which fixture definition is bound to which node
Nearest existing operation: bindname / ordleak
Observable delta: same path, two node ids, fixture miss on the later node
Reason: path equality is the wrong object; node identity is the question
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
