# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B mix hex.publish --replace with leftover ~/.hex/packages tarball keeps previous package-version bytes because Hex.SCM.fetch matches exact outer_checksum or {:error,_} and omits {:ok, other} on failing_ref
- Case C rm the tarball is fresh; Case A same registry checksum is current

## Rejected

- Invented mix hex.publish / mix deps.get / checksum 7c3c9e4d transcripts are not host-executed

## Constraints

- Do not send hex tarball-checksum theater back to R1. Distinct from 074.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover hex tarball after registry checksum change
Nearest existing operation: grep cache_path package-version vs {:ok, other_outer_checksum} omitted
Observable delta: leftover_hexcksum = cache hit AND registry checksum changed AND mismatch clause omitted
Reason: Dreamer restated omitted mismatch clause from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
