# HDD Ledger

Iteration: 1

## Preserve

- The Dreamer started from a cross-file type mismatch, which matched the seed.

## Established

- Commands: mismatch scan, fix, explain, generate-mapper, attach-mapper, verify --changed.

## Rejected

- Auto-inferred attach to UserProfile.tsx and 'contract restored' without implementing the mapper.

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: report a type field that does not match between two files and offer a conversion stub
Nearest existing operation: tsc / mypy / an LSP quick-fix
Observable delta: stub file generation; not a new question
Reason: the compiler already exposes the two-ended mismatch
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
