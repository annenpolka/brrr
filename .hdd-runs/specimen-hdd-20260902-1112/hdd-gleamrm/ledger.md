# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B a.gleam moved out then restored with leftover artefact cache keeps previous compile because PackageLoader marks removed modules stale without deleting cache files and ModuleLoader reuses fingerprint match on failing_ref
- Case C cache dir deleted is fresh; Case A source never removed is current

## Rejected

- Invented gleam compile / package_loader stale-without-delete transcripts are not host-executed beyond the seed excerpts

## Constraints

- Do not send gleam cache-stale theater back to R1. Distinct from 054/154/155.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover gleam artefact after same-name restore
Nearest existing operation: grep stale_modules.add without cache delete vs fingerprint reuse
Observable delta: leftover_gleamrm = cache file remains AND fingerprint matches AND stale did not delete
Reason: Dreamer restated omitted cache-file delete from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
