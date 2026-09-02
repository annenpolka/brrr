# HDD Ledger

Iteration: 1

## Preserve

- A patchedDependencies selector can be a {path,hash} object or a bare hash string; .hash on a string is empty

## Established

- Packet: pnpm 11 lockfile stores selector to hash string; pre-simplify stored {path, hash}
- isolate-package copyPatches read originalPatchFile?.hash and wrote empty

## Rejected

- Invented lockfile-inspector transcripts are not host-executed

## Constraints

- Owned two lock excerpts. No pnpm.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which identity patchedDependencies contained for a selector: path+hash object, hash-only string, empty hash, or omitted

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name patchedDependencies identity class for a selector: object, hash-only, empty, or omitted
Nearest existing operation: grep the selector in the lockfile
Observable delta: object vs hash-only vs empty vs omitted; legacy .hash empty on string
Reason: grep of the selector hits both shapes
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
