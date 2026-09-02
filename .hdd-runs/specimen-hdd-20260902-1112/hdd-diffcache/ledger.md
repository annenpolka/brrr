# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B second diff of foo.ts hits cacheKey=filename and reuses first-body AST
- failing_ref FileDiff cacheKey defaults to name; no patch-content in the key

## Rejected

- Invented code-inspector extract/trace/diagnose/cache-scan transcripts are not host-executed

## Constraints

- Do not send coder DiffViewer theater back to R1. Distinct from specimen-090/094.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover filename-keyed highlight AST after the diff body changed
Nearest existing operation: grep cacheKey vs fileDiff.name in FileDiff.js
Observable delta: leftover_ast = cacheKey==name AND body_a!=body_b
Reason: Dreamer restated the seed cacheKey=name leftover; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
