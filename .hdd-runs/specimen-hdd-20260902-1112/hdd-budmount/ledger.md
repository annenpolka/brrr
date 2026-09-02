# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B rebuilt source stage with leftover RUN --mount cache keeps previous mounted file because StageMountDetails stores MountPoint only and omits DidExecute on failing_ref
- Case C --no-cache / --layers=false is fresh; Case A unchanged source stage is current

## Rejected

- Invented buildah build / Dockerfile v1 vs v2 / Using cache transcripts are not host-executed

## Constraints

- Do not send buildah RUN --mount theater back to R1. Distinct from 066/144/097.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover mounted stage after source rebuild
Nearest existing operation: grep StageMountDetails MountPoint-only vs DidExecute omitted from cache identity
Observable delta: leftover_budmount = RUN --mount cache hit AND source stage rebuilt AND DidExecute omitted
Reason: Dreamer restated omitted DidExecute from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
