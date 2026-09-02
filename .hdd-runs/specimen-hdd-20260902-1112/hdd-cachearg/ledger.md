# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B CACHE --id $something with a new ARG value reuses leftover cache because opts.ID is not expanded through expandArgs on failing_ref
- Case C fixed --id is a different key; Case D --no-cache is fresh

## Rejected

- Invented earthly --build-arg / CACHE --id $something transcripts are not host-executed
- Dreamer restated unexpanded token from the seed

## Constraints

- Do not send earthly CACHE theater back to R1. Distinct from specimen-115. specimen-124 is the same PR 3810.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover CACHE --id that keeps the unexpanded token after ARG changes
Nearest existing operation: grep expandArgs vs opts.ID in handleCache
Observable delta: leftover_id = opts.ID unexpanded AND arg_a != arg_b
Reason: Dreamer restated unexpanded --id from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
