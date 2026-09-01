# HDD Ledger

Iteration: 2

## Preserve

- Conflict resolution operated on overlapping regions, not whole files.
- Hybrid edit rejected unmarked choices and demanded explicit current|incoming tagging per variant.
- ttl could not remain ambiguous; the tool required exactly one parent for a conflicting scalar.
- hybrid-edit rejected text that left untagged non-common spans.
- finalize printed per-file provenance of current vs incoming contributions.
- The tool accepted mixed expect/assert without 'understanding' tests.

## Established

- Commands: integrate branch-merge, then resolution-mode accept/hybrid-edit/flag/next/prev/abort-merge.
- inspect of conflict markers, hybrid-edit --text with [current:]/[incoming:] tags, finalize.

## Rejected

- The ASCII dashboard and invented lexer.js/config.yml conflict contents are not observations of a real merge.
- The conflict file contents remain fictional; grounding must use a real git conflict.

## Constraints

- No interactive TUI or editor. The interface must remain a one-shot CLI suitable for a pipe.
- There is no hidden semantic merge AI. Parent provenance must come from the conflict markers or the two sides.
- Operate on a real two-parent conflict in a git working tree.

## Open Questions

- Is 'emit a merge result where every conflicted token is labeled with its parent' a distinct operation from git mergetool?

## Human Pressure

- (none)

## Harvest Candidates

- Resolve a conflict only by explicit parent-tagged choices, so the result still says where each contested token came from.
- Resolve conflict markers only by parent-tagged choices and emit a provenance report alongside the resolved text.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: resolve conflict markers by explicit parent tags and report which parent kept each contested span
Nearest existing operation: git mergetool / editing conflict markers / git checkout --ours/--theirs
Observable delta: the merge product is accompanied by per-span parent provenance, which ordinary mergetools discard
Reason: not a new merge algorithm; the provenance contract is the surviving delta and is implementable from markers alone
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
