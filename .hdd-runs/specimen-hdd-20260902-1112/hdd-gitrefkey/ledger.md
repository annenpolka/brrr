# HDD Ledger

Iteration: 1

## Preserve

- A keep-git-dir git source cache key can be only commit SHA plus .git, so two named refs at one commit share one snapshot whose .git may lack the second ref

## Established

- Packet: shaToCacheKey(sha) is SHA [+ .git] [+ :subdir]; CacheKey after ls-remote does not pass usedRef; keepGitDir false keys equal on identical trees
- Case C raw SHA identifier still has no named ref; case D different commits already split

## Rejected

- Invented BuildKit runtime / git rev-parse transcripts are not host-executed

## Constraints

- Owned labeled sha/ref/key records. No buildkit.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether keep-git-dir cache key stored leftover SHA-only so two refs collide, SHA#ref so they split, or omitted like keepGitDir false

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover SHA-only keep-git-dir cache key that omitted the named ref
Nearest existing operation: diff two cache keys and git rev-parse the second ref in the snapshot
Observable delta: leftover_ref = keep_git_dir and pin_equal and key_a == key_b and ref_a != ref_b
Reason: grep of the SHA hits both keys; the leftover is the named ref omitted from the key
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
