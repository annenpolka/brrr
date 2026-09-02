# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B two git deps sharing one submodule URL; failing_ref GitCheckout::update_submodule fetch+reset into the working copy, not GitDatabase
- Case A parent git deps use git/db; Case C offline after rm checkouts cannot reconstruct; Case D already-at-head still recurses without db write

## Rejected

- Invented cargo-inspect / cargo-fixture fetch transcripts are not host-executed

## Constraints

- Do not send cargo git-submodule theater back to R1. Distinct from Honor-KILLed pathdup and specimen-091.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover checkout-only submodule with no git/db ident
Nearest existing operation: ls $CARGO_HOME/git/db vs ls git/checkouts
Observable delta: leftover_checkout = checkout_present AND NOT db_present
Reason: Dreamer restated the seed; two caller flags already are the harvest sentence
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
