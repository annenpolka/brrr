# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B after leaving use_nix with leftover NIX_ATTRS_JSON_FILE / NIX_ATTRS_SH_FILE keeps previous paths because values_to_restore lists NIX_BUILD_TOP/TMP*/terminfo and omits those names on failing_ref
- Case C never-entered is unset; Case A inside nix-shell is current

## Rejected

- Invented grep / direnv dump / nested-shell transcripts are not host-executed

## Constraints

- Do not send direnv use_nix theater back to R1. Distinct from 010/149/150/158.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover NIX_ATTRS paths after leaving use_nix
Nearest existing operation: grep values_to_restore vs NIX_ATTRS names omitted
Observable delta: leftover_dirnix = dump kept AND names omitted from restore map AND files gone
Reason: Dreamer restated omitted restore-map names from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
