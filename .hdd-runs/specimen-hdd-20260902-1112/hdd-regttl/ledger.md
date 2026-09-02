# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B post-TTL resolve of a new version reuses leftover metadata because MetadataCacheKey is (registry, package) and cached.expires < now returns the expired entry; ChecksumTOFU writes that leftover checksum as the new version fingerprint
- Case A first resolve of 1.1.0 is a miss; Case C version-keyed cache is not on failing_ref

## Rejected

- Invented swiftpm-debug fingerprints / registry-sandbox advance-time transcripts are not host-executed
- Dreamer recommended PR 9144 as the repair; that is the sealed answer-key

## Constraints

- Do not send SwiftPM registry-cache theater back to R1. Distinct from specimen-075/086/115.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover registry metadata checksum reused for a later version after inverted TTL
Nearest existing operation: grep MetadataCacheKey vs cached.expires < .now() vs ChecksumTOFU.writeToStorage
Observable delta: leftover_ttl = cache_key omits version AND inverted expiry returns leftover checksum
Reason: Dreamer restated inverted TTL plus omitted version from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
