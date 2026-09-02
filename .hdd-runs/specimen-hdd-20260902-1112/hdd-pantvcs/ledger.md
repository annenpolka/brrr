# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B amend/commit with leftover process cache keeps previous git describe because VenvPexProcess omits git hash on failing_ref
- Case C delete ~/.cache/pants is fresh; enclosing MaybeGitWorktree reruns; child process reused

## Rejected

- Invented pants dependencies --target-type=process / --no-cache-rules / --session-id / setuptools_scm_process cache path transcripts are not host-executed

## Constraints

- Do not send pants vcs_version process-cache theater back to R1. Distinct from 075. Not #23645 OPEN.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover generated version after git amend/commit
Nearest existing operation: grep MaybeGitWorktree uncacheable vs VenvPexProcess without cache_scope
Observable delta: leftover_pantvcs = process cache hit AND git hash changed AND git state omitted from VenvPexProcess identity
Reason: Dreamer restated omitted git hash from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
