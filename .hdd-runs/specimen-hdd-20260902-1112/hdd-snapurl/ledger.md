# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B snapshot URL upgraded leftover previous Packages facts because pkg_fact_key is dist/component/architecture/Packages and omits URLs
- Case C empty facts is fresh; Case A same URLs is current

## Rejected

- Invented cachekey-analyzer generate omit-url / urlsha256 transcripts are not host-executed

## Constraints

- Do not send rules_distroless snapshot-URL fact-key theater back to R1. Distinct from bazel#29298 and 064/070/136.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover apt facts after snapshot URL change
Nearest existing operation: grep pkg_fact_key dist/component/arch vs URLs omitted
Observable delta: leftover_snapurl = facts cache hit AND snapshot URL changed AND URL omitted from key
Reason: Dreamer restated omitted snapshot URL from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
