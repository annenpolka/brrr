# mutation-101 — sear

## Primitive

`--follow` the visa *slot* across dest-file identity (git R records), then still require same-commit lockset clearance. A dest-only rename is not a birth. Copy is not a follow. Skip is not a lock. SPREAD is not a mint. Rename of a visa-bearing test still brands the **birth** commit, not the rename.

## Why this might not exist

`brand` is lockset clearance at visa-birth: LOCKED-and-BOUND-at-birth. `mint`'s hole, inherited: dest-file path is in the slot key, so `git mv src/profile.py src/user.py` of a BOUND world looks like ABSENT→BOUND. Concatenation `brand && git log --follow` still names dest recency. `git log --follow` walks the blob (copy is follow). berth/ditto already said dest identity is **R records**.

The missing verb is: **this lock, whose visa was minted in that commit, whose dest file later moved — still that birth, not the rename.**

Not a fourth cinch (cinch 0.3 stays the lockset vehicle — sear splices whole production onto dest identity). Not a third ambit. Not leftover-name.

## How to run

```bash
chmod +x ./sear
./sear --self-test
./demo.sh
./sear -C <repo>
./sear -C <repo> --report
./sear -C <repo> --due
./sear -C <repo> --walk --max 20
./sear -C <repo> --no-follow <sha>
./sear --check origin/main..HEAD
```

Python 3.10+, git, stdlib. Exit 0 when no LOCKED-and-BOUND-at-birth. Exit 1 on a brand (or `--due` SKIP-at-birth). Exit 3 if the suite is already red on the child. `-C` must be a worktree root. `--follow` is default.

## Empirical transcript

### v0.1 (`ab5014f`) — follow dest identity; sitbone/kizu brands=0

`./sear --self-test` ok. `./demo.sh` → **passed=80 failed=0**.

| fixture | brand-now | sear --follow | sear --no-follow |
| --- | --- | --- | --- |
| pin Alice + tests lock same commit | **BRAND** | **BRAND** | **BRAND** |
| pin Alice, tests still `/tmp` | empty / MINT | empty / MINT | empty / MINT |
| skipUnless Alice | empty / `--due` 1 | same | same |
| lock Alice two commits after the pin | empty | empty | empty |
| SPREAD Alice into Swift | empty | empty | empty |
| GitHub titles / Brave / `/home/user` | empty | empty | empty |
| `git mv` visa-bearing `tests/test_profile.py` after a brand | (brand walk still birth) | rename empty; **walk brands the birth SHA** | rename empty |
| `git mv src/profile.py src/user.py` after a brand | path-keyed hole | rename empty; walk brands the birth | **false BRAND** ABSENT→BOUND (import-fail counted as LOCKED) |
| `cp` BOUND dest to a new path | — | empty (copy is not R) | empty |

sitbone first-parent walk: **brands=0**, empty stdout, no Brave. kizu first-parent walk: **brands=0**, no AbsoluteLinkError. Mint's gold — sear did not invent a visa.

Stop condition holds: rename of a visa-bearing test still brands the birth commit, not the rename.

### v0.2 — splice follows dest; unique dead-slot when R is missing

Forced by v0.1: `--no-follow` dest rename was a false brand because overlay unlinked `src/user.py` and import-fail counted as LOCKED. Occupancy now always follows dest identity. `--no-follow` only path-keys slot pairing.

Same-commit pin + `git mv` + lock was D+A (content changed with the path), so R records missed. Unique (fn, params) whose parent dest died and whose child dest was born is the same slot. Copy still is not a follow (parent dest lives).

`./demo.sh` → **passed=87 failed=0**. sitbone/kizu still 0.

| fixture | v0.1 | v0.2 --follow | v0.2 --no-follow |
| --- | --- | --- | --- |
| dest rename after a brand | false BRAND (import-fail) | empty; walk brands birth | **MINT** ABSENT→BOUND-unlocked (lock=LOOSE) |
| same-commit pin+mv+lock | untested / ABSENT→BOUND | **BRAND SPEC→BOUND** (`was` `/tmp` at `src/profile.py`) | **BRAND ABSENT→BOUND** (kind is the hole; lock is real) |

```
./sear -C $SAME <pin-mv-lock>
# sear  brands=1  worlds=1  commit=666f5e5  parent=a71c6aa
#   pin Alice, mv dest, and lock it
#   BRAND  LOCKED-and-BOUND-at-birth  SPEC→BOUND  HOME=/Users/alice …
#     who  who("/Users/alice")  src/user.py
#     was  SPEC  who  who("/tmp/cache")  src/profile.py
#     lock  tests/test_profile.py
```

## Dogfood targets

- Synthetic histories in `--self-test` / `./demo.sh` (joint brand, mint-only, skip-at-birth, OPEN lock, SPREAD, GitHub titles, live HOME MATCH, abs symlink, test rename, dest rename, copy, same-commit pin+mv+lock)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` first-parent (brands=0)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` first-parent (brands=0; AGENTS.md absolute symlink)

## Surprises

- `--no-follow` dest rename after a brand was a **false brand** in v0.1, not a false mint. Child tests import `src.user`; overlay without dest identity unlinked that path; splice import-fail was LOCKED. The visa was already at the parent. Occupancy lied. v0.2 splice follows dest; the lock is LOOSE; default empty.
- A pin that also `git mv`s the dest is often D+A. R records are not enough. Unique dead-slot (fn, params) recovers SPEC→BOUND. Two births of the same sig stay unmatched; copy is not a follow.
- Copy of a BOUND file is not R, so it is not a follow and not a birth. ditto's lesson, inherited on purpose.
- Walk after test rename still lists `lock tests/test_profile.py` — the name at birth. That is the object: the commit, not the current dest name.

## Failures

- Swift `loadHome` / Brave: UNRUN (Python suite only). Visa still visible as a non-birth.
- JS/RS worlds UNRUN.
- Unique dead-slot follow is 1:1. A split of `who` into two dest files will not pair.
- Walk still names the lock file as it was at birth, not HEAD dest.

## Suggested mutations

- Follow lock-test dest identity in the report (`lock tests/test_who.py was tests/test_profile.py`) while keeping the birth SHA.
- Join with held: eras of BOUND-and-LOCKED, not only onset.
- Occupancy of Swift/JS world-tests so an UNRUN Brave lock could become LOCKED-and-OPEN at an OPEN birth (still not a brand).

## Kill / keep

**Keep.** Follow is a different object than brand-now: dest rename of a locked visa is empty, and the walk still names the birth. Same-commit pin+mv+lock is SPEC→BOUND, which concatenation `brand | git log --follow` cannot say (copy follows the blob; D+A of a pin+rename is not R). Kill only if a later generation proves `git log --follow` plus brand names dest-file slot identity — it does not, because copy follows the blob and a rename of a visa-bearing test is not a birth.
