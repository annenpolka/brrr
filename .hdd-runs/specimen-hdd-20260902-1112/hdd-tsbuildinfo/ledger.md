# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case C resolveJsonModule incremental warm build restores valid JSON while tsbuildinfo still replays the missing-property diagnostic
- fileInfos content-hash can move while semanticDiagnosticsPerFile still names the old JSON shape

## Rejected

- Invented tsc -p / tsbuildinfo-dump / --force-diagnostic-revalidation transcripts are not host-executed

## Constraints

- Do not send tsc incremental theater back to R1. Distinct from specimen-111 tsdtsig.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover JSON-module diagnostic after fileInfos hash moved
Nearest existing operation: diff semanticDiagnosticsPerFile vs fileInfos hash for data.json
Observable delta: leftover_diag = diagnostic still TS2741 for {} AND current JSON has title
Reason: Dreamer restated the seed Case C tables; two tsbuildinfo greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
