# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B install-strategy=linked uninstall leaves .bin/rimraf (+ .cmd/.ps1) after top-level symlink and .store entry gone; cleanOrphanedStoreEntries skips dot-entries
- Case A hoisted uninstall removes the shim; surviving semver shims should stay

## Rejected

- Invented npm 10.5.0 linked uninstall / node failing_clean_orphaned.js transcripts are not host-executed
- Dreamer operated a post-PR9632 npm and cited the fix

## Constraints

- Do not send npm linked-arborist theater back to R1. Distinct from 004/082/095 and Honor-KILLed peerleft.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover .bin shim after linked uninstall removed the package
Nearest existing operation: ls node_modules/.bin vs ls node_modules/<pkg>
Observable delta: leftover_shim = bin_name present AND package absent
Reason: Dreamer restated the seed skip-dot-entries; two caller flags already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
