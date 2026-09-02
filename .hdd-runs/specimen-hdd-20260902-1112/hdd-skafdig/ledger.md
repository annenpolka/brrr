# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B inputs flipped same tag leftover Found Remotely because lookupRemote returns found whenever RemoteDigest(tag) succeeds and does not compare cached vs remote digest
- Case C --cache-artifacts=false is fresh; Case A same inputs same digest is current

## Rejected

- Invented skaffold build / debug dump cache / sha256:8e6f transcripts are not host-executed

## Constraints

- Do not send skaffold lookupRemote theater back to R1. Distinct from 097.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover remote image after input change
Nearest existing operation: grep RemoteDigest(tag) success returns found vs digest compare omitted
Observable delta: leftover_skafdig = remote tag hit AND input hash changed AND digest compare omitted
Reason: Dreamer restated omitted digest compare from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
