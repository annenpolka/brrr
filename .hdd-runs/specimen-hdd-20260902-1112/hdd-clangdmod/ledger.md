# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B rewritten header with leftover C++20 module BMI keeps previous getValue because ASTReader is constructed without ValidateASTInputFilesContent=true on failing_ref
- Case C rebuild without BMI is fresh; Case A same header bytes is current

## Rejected

- Invented cli-tool ast-inspect / flag-trace transcripts are not host-executed

## Constraints

- Do not send clangd BMI theater back to R1. Distinct from bindname/075.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover module BMI after header rewrite
Nearest existing operation: grep HSOpts.ValidateASTInputFilesContent vs ASTReader constructor omitting that argument
Observable delta: leftover_clangdmod = canReuse true AND header rewritten AND ASTReader content validation omitted
Reason: Dreamer restated omitted ASTReader flag from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
