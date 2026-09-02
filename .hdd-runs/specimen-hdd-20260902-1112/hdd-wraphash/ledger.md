# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B wrap file edited while leftover subprojects/<dir>/meson.build remains; Resolver.resolve returns that directory; PackageDefinition has no wrapfile_hash on failing_ref
- Case C delete leftover dir is a fresh fetch; Case D cmake leftover CMakeLists.txt is the same omitted wrap-file identity

## Rejected

- Invented meson-inspect environment / wrap resolve / code extract transcripts are not host-executed
- Dreamer recommended PR 10728 as the repair; that is the sealed answer-key

## Constraints

- Do not send meson wrap theater back to R1. Distinct from specimen-064/070/092.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover wrap checkout after wrap-file revision changed
Nearest existing operation: test -e subprojects/<dir>/meson.build vs wrap-file revision/source_hash
Observable delta: leftover_wrap = meson.build present AND wrapfile_hash omitted
Reason: Dreamer restated Resolver.resolve early-return from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
