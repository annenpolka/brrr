# HDD Ledger

Iteration: 2

## Preserve

- An add can return success while a colliding file/dir entry remains
- The miss is associated with insertion position not being the start of the index
- Insert can report success while a colliding prefix entry remains
- Scan cursor not at zero matters

## Established

- Packet: existing tests with a single prior entry (position 0) do not see the failure
- Packet: sibling entries that force a non-zero insertion position miss the collision
- Owned index_scan.py / transfer_index.py

## Rejected

- srcinspector, idxdump, idxmod, lg2, and local make debug patches are not specimen evidence
- Recommending the public PR's approach is answer-key leakage; do not treat it as an observation
- pathtool debug neighbor scan is Dreamer-generated
- pathtool add/debug output is not host evidence
- Exit 128 control-case text is Dreamer-generated until the list fixture prints it

## Constraints

- You cannot rebuild libgit2 or dump a git index with invented tools
- A small ordered-list fixture of the same collision is the world you must use
- Ground on the Python list fixture
- libgit2 cannot be rebuilt here
- A small ordered-list fixture of the same collision is the world

## Open Questions

- Can the tool explain exit 0 while the colliding prefix still exists, using only the list fixture?

## Human Pressure

- libgit2 cannot be rebuilt here. A sorted path-list fixture of the same file/dir collision is present. Use the same tool. Show why add reported ok and which entries still collide when the scan does not start at zero. Do not apply a known C patch.

## Harvest Candidates

- Ask why an insert reported success and which remaining entries still collide, especially when the scan cursor is not zero
- Silent-success plus remaining collision, cursor-dependent
- Ask why an insert reported success and which remaining entries still collide when the scan cursor is not zero

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: report silent-success inserts that left a file/dir collision, including scan-cursor dependence
Nearest existing operation: print the ordered list before and after insert plus the process exit
Observable delta: one query that treats exit 0 plus remaining collision as the object, not a successful add
Reason: the remainder is failure-semantics of success, not a new git
Assessed at iteration: 2

## Latest Red Pen Pressure

- There is no pathtool. Use only the ordered path-list fixture.

## Pending

(none)
