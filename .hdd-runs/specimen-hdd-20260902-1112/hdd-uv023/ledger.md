# HDD Ledger

Iteration: 2

## Preserve

- A linked worktree can record commit null in a cache key while HEAD still moves
- pack-refs can make a regular clone behave the same if only loose refs were read
- A cache key that lists git commit/tags can miss linked worktree identity
- A cache key of commit+tags can stay FRESH while worktree path changed

## Established

- Packet: uv cache-keys git commit true from a git worktree; .git is a gitdir file; unit test for loose refs passes
- Packet: uv cache-keys git commit/tags
- Owned specimen-062: same key if worktree omitted

## Rejected

- A recommended resolve_ref packed-refs implementation is a Dreamer patch, not host evidence
- No uv/git2 checkout was run here
- Invented hatch-vcs project and uv-cache-info patches are not host evidence
- Invented /path/to/worktree listings are not host evidence

## Constraints

- No uv crate rebuild
- An owned gitdir/HEAD/packed-refs fixture is the world
- No uv/git worktree required; owned key components fixture
- Ground on owned key-component fixture

## Open Questions

- (none)

## Human Pressure

- No uv. Continue on an owned key-component list. Show which identity was omitted.

## Harvest Candidates

- Ask which git identity was hashed: worktree HEAD, loose ref, or packed-refs
- Which identity component was omitted from the cache key
- Which identity component was omitted from the key

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a freshness component omitted from the cache key
Nearest existing operation: freshmiss / lockident
Observable delta: omitted worktree vs listed commit/tags
Reason: adjacent to freshmiss
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
