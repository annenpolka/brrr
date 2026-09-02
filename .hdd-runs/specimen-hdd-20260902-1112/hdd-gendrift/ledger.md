# HDD Ledger

Iteration: 1

## Preserve

- A generated header can disagree with make regen-all after the generator changed
- Numeric identity rows and named opcode ids can occupy the same index

## Established

- Packet: CI check-generated-files diff on Include/internal/pycore_opcode_metadata.h inside _PyOpcode_Deopt; identity rows 119/120/211 removed in the diff

## Rejected

- cpython-dev CLI and opcode name tables are Dreamer-generated
- A recommended generator patch is not a specimen observation

## Constraints

- No CPython checkout, no make regen-all on the host
- The packet diff plus opcode_ids names in the packet are the world

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Ask which generated file disagrees with regen and whether identity rows collide with named ids

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name the stale generated file and whether numeric identity rows collide with named opcode ids
Nearest existing operation: read the CI diff and the generator comment
Observable delta: one query that treats identity-row vs named-id collision as the object, not a generic stale file
Reason: the CI job already shows a diff; the remainder is relating those numbers to names
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no cpython-dev. Continue only from the packet diff and listed files.

## Pending

(none)
