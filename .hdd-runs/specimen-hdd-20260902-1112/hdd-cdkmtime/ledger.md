# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B same-size rewrite leftover sha256 because contentFingerprint caches on getUTCDate()+getUTCMilliseconds()+inode+size
- Case C cache reset is fresh; Case A same bytes same mtime is current

## Rejected

- Invented cdk-fprint-inspect key-structure / set-mtime / sha256:6b86 transcripts are not host-executed

## Constraints

- Do not send CDK truncated-mtime fingerprint theater back to R1. Distinct from 075 and 139.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover fingerprint after rewrite
Nearest existing operation: grep getUTCDate getUTCMilliseconds vs fingerprintCache.obtain
Observable delta: leftover_cdkmtime = cache hit AND same inode/size AND truncated mtime collides
Reason: Dreamer restated truncated mtime from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
