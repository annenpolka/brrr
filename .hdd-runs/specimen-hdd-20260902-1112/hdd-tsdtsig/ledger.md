# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B incremental true; public->protected->public; d.ts text hash signature unchanged so importer is not rechecked; leftover error identity in .tsbuildinfo
- Case A incremental false has no leftover; Case C first tsc has no prior signature

## Rejected

- Invented tsc / sed / jq tsbuildinfo transcripts are not host-executed

## Constraints

- Do not send tsc incremental theater back to R1. Distinct from specimen-067.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover importer error identity after d.ts signature stayed the same
Nearest existing operation: diff tsc output before vs after deleting .tsbuildinfo
Observable delta: leftover_stale = signature_same AND diagnostic_present
Reason: Dreamer restated computeSignature from the seed; two caller facts already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
