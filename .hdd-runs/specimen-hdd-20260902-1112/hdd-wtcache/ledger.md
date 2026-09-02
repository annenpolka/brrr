# HDD Ledger

Iteration: 1

## Preserve

- commit+tags key is identical when worktree path is omitted
- A cache key of commit+tags can stay FRESH while worktree path changed and a worktree-local file is missing

## Established

- Owned specimen-062 prints same_if_worktree_omitted True
- Owned specimen-062 wt_cache.py: same key if worktree omitted

## Rejected

- tox-worktree-util is not installed
- Invented tox-worktree-util keygen/build/cache inspect is not host evidence

## Constraints

- Transfer, no new binary
- No tox. Ground on owned key-component fixture. Do not mint a third freshness CLI

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- omitted worktree identity
- Which identity component was omitted from the cache key (worktree)

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a freshness component omitted from the cache key
Nearest existing operation: freshmiss / lockident / uv023
Observable delta: omitted worktree vs listed commit/tags
Reason: duplicate of uv023/specimen-062; mutate lockident, not a new binary
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
