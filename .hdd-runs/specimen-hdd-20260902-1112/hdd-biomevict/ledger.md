# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B close_file with leftover parsed-source map keeps previous parse because close removes documents/node_cache and omits db_remove_file on failing_ref
- Case C never-opened is empty; Case A still-open is current

## Rejected

- Invented biome db-query / db-inspect / db-remove transcripts are not host-executed

## Constraints

- Do not send biome close-eviction theater back to R1. Distinct from 157/159.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover parsed source after close_file
Nearest existing operation: grep close_file documents/node_cache vs db_remove_file omitted
Observable delta: leftover_biomevict = close AND files map HIT AND db_remove_file omitted
Reason: Dreamer restated omitted files-map eviction from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
