# HDD Ledger

Iteration: 1

## Preserve

- A cache can report FRESH on an unchanged source identity after only the lockfile changed
- The stored artifact can still name the old lock bytes

## Established

- Host fixture: first BUILT key 673767793f4a artifact built-with:serde = 1.0.0; after_lock_bump FRESH same key; lock_changed True

## Rejected

- A patched fingerprint() that prints Hashing bytes is not required evidence
- Specific /tmp/tmpz5j7c0y1 paths are Dreamer-generated

## Constraints

- No cargo-inspect, no real crate cache
- Observable evidence is the owned fixture prints plus whether named lock strings appear in the key inputs

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Ask which byte strings entered the identity and whether the live lockfile is one of them

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name the byte strings that formed a freshness identity and say whether the live lockfile is among them
Nearest existing operation: print the fixture key twice and diff the lockfile by hand
Observable delta: one query that labels lockfile-in-identity vs lockfile-omitted instead of two printed keys
Reason: FRESH looks like success; the miss is the omitted lock bytes
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no cargo. Continue only from the owned cache_lock.py prints.

## Pending

(none)
