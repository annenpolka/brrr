# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B leftover vendor from before abandon tag; lock now has abandoned; same version; installed.json omitted abandoned; audit reports none
- Case A fresh install writes abandoned; Case C wipe+install is a fresh identity; Case D version bump is already UpdateOperation

## Rejected

- Invented composer install / jq / composer audit transcripts are not host-executed
- Dreamer named Composer PR 12423 as verified in the environment; that is the sealed answer-key, not a host observation

## Constraints

- Do not send composer installed.json theater back to R1. Distinct from specimen-074/021/086.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover omitted-abandoned in installed.json after lock acquired abandoned for the same version
Nearest existing operation: jq abandoned in composer.lock vs vendor/composer/installed.json
Observable delta: leftover_omit = lock_abandoned AND installed_omits_abandoned
Reason: Dreamer restated calculateOperations version/dist/source from the seed; two JSON greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
