# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B leftover .dart_tool/package_config.json without pkg_b is treated as current because missing workspace members are omitted from the up-to-date check
- Case A unchanged workspace is current mapping; Case C wipe is fresh; Case D post-repair invalidates

## Rejected

- Invented cat/jq/ls package_config transcripts are not host-executed
- Dreamer restated leftover mapping without pkg_b from the seed

## Constraints

- Do not send dart package_config theater back to R1. Distinct from 103/121/125/126.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover package_config mapping that omits a new workspace member
Nearest existing operation: grep extra mappings vs missing transitiveWorkspace names in isPackagePathsMappingUpToDateWithLockfile
Observable delta: leftover_mapping = pkg_b omitted AND check still true
Reason: Dreamer restated leftover mapping without pkg_b from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
