# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B cookieless request after server-component edit with leftover 'use cache' keeps previous page because getHmrRefreshHash on request stores reads NEXT_HMR_REFRESH_HASH_COOKIE and omits the server-authored hash on failing_ref
- Case C cold start is fresh; Case A cookie-present is current

## Rejected

- Invented source-query key-provenance / control-flow / issue-timeline transcripts are not host-executed

## Constraints

- Do not send next use-cache theater back to R1. Distinct from 090/156/157.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover 'use cache' after edit without HMR cookie
Nearest existing operation: grep getHmrRefreshHash cookie vs server hash omitted
Observable delta: leftover_nexthmr = cookieless AND edit AND hash omitted from cacheKeyParts
Reason: Dreamer restated omitted server HMR hash from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
