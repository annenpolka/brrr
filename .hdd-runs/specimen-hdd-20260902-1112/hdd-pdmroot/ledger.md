# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B pdm lock then --update-reuse rewrites extra path URL to file:///absolute; path field stays ../lib
- Case A no extras keeps portable URL; format_lockfile only rewrote when FileRequirement.path was already absolute

## Rejected

- Invented pdm lock --update-reuse / sed sanitize transcripts are not host-executed

## Constraints

- Do not send pdm lock theater back to R1. Distinct from extraedge and pipextra.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover machine-absolute file:/// extra URL after --update-reuse while path stays relative
Nearest existing operation: grep PROJECT_ROOT vs file:/// in pdm.lock
Observable delta: leftover_abs = extra_url is absolute AND path is relative
Reason: Dreamer restated the seed lock snippets; two caller strings already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
