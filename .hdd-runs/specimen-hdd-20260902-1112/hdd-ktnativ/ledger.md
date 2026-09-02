# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B external dep rolled back to already-cached version with leftover per-file IC keeps previous cache because CacheMetadata stores compilerFingerprint only and omits dependenciesFingerprint on failing_ref
- Case C clean/miss is fresh; Case A same deps is current

## Rejected

- Invented kt-compiler-inspector fields / conditions / simulate transcripts are not host-executed

## Constraints

- Do not send kotlin Native IC theater back to R1. Distinct from 075/103/104.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover Native IC after external dep rollback
Nearest existing operation: grep CacheMetadata compilerFingerprint vs dependenciesFingerprint omitted
Observable delta: leftover_ktnativ = cache exists AND compiler fingerprint matches AND deps fingerprint omitted
Reason: Dreamer restated omitted dependenciesFingerprint from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
