# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B leftover previous bottle is reused because no_diff? diffs only the formula path against tap_git_revision; local patches are omitted
- Case C formula.rb edit invalidates; Case D wipe cache is fresh

## Rejected

- Invented tar/jq/git/brew install transcripts are not host-executed
- Dreamer restated leftover previous bottle / omitted patch from the seed

## Constraints

- Do not send brew bottle-patch theater back to R1. Distinct from Homebrew#20936 auditor revision.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover bottle reused after a local patch change
Nearest existing operation: grep no_diff? formula.path vs formula.patchlist LocalPatch
Observable delta: leftover_bottle = no_diff? true AND patch hash changed
Reason: Dreamer restated leftover previous bottle from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
