# HDD Ledger

Iteration: 1

## Preserve

- A signed tree-note extension can carry a go.sum line that is not in the authenticated record text

## Established

- Packet: Lookup of golang.org/x/bad@v1.0.0 on failing_ref scans the full cache payload; checkRecord hashes only record text (golang.org/x/good)
- Honest Lookup of rsc.io/sampler@v1.3.0 returns the log record lines

## Rejected

- Invented tlog.FormatRecord / Client.Lookup transcripts are not host-executed

## Constraints

- Owned two labeled excerpts: authenticated record vs extension. No go toolchain.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether a module version's go.sum line is leftover in the unauthenticated extension or present in the authenticated record

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover identity in tree-note extension vs authenticated record for a module version
Nearest existing operation: grep the module path in the payload
Observable delta: extension-only vs in-record
Reason: grep of the path hits the extension line in the full body; the authenticated text is a different module
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
