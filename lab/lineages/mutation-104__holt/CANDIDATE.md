# mutation-104 — holt

## Primitive

`holt exists PATH` occupies a **file identity** resolved from **all reachable R records**. Occupancy defaults to every reachable commit (`--first-parent` is opt-in). Query the old name or the new name; occupancy stays TRUE. If PATH exists at the walk tip, that occupant is the identity — a leftover name is a new roost, not the twin that moved.

`--no-follow` is ancestor path occupancy. `--boolean` is ancestor `held`. Copies (`C`) are ignored.

## Why this might not exist

berth sold “query the old name or the new name; occupancy stays TRUE.” DESTROYER_BERTH showed that is **false on the default first-parent walk**: kizu `exists deep-research-ai-agent-hooks.md` is never-held (merge `ca0577a` added dest as A, no R on mainline). Default `exists PATH` at a living leftover name occupies the *other* file (first-existence seed). Two files swapping names: wrong roost.

rove already resolved identity from all-reachable R for `grep -- PATH`. berth's `exists` still used the walk's own name-status. Nobody made first-parent `exists` of a dead name the dest roost, and nobody seeded from the tip occupant.

Discarded as too conventional: wrapping `git log --follow`, leftover-name search (find mentions of the old path), a fourth cinch.

## How to run

```bash
./holt --help
./demo.sh 0
./demo.sh
./holt -C /path/to/repo exists 'old name.txt'
./holt -C /path/to/repo --no-follow exists 'old name.txt'
./holt -C /path/to/repo exists docs/deep-research-ai-agent-hooks.md
./holt -C /path/to/repo exists deep-research-ai-agent-hooks.md
./holt -C /path/to/repo --first-parent exists deep-research-ai-agent-hooks.md
./holt -C /path/to/repo grep FocusRiverView
./holt -C /path/to/repo grep preact-zero-mock
```

Python 3.9+, stdlib only, `git`. Exit 0 iff the predicate holds at the last sample.

## Empirical transcript

### Before the improvement (this first commit)

Synthetic: `--no-follow` keeps path death. Default `exists` on either name of a spaces rename is one identity. Copy is not a follow. Oscillate delete+revive is TF under follow (reincarnation is a different file) and TFTF under `--no-follow`. 3-hop CJK is one roost from any name.

Leftover recreate (`git mv old.txt new.txt` then recreate `old.txt`): `exists old.txt` is a new roost (`identity=old.txt`, FT true=1). `exists new.txt` is `old.txt → new.txt`. Serialized swap: `exists a.txt` identity is `b.txt → a.txt` (occupant BBB); `exists b.txt` is `a.txt → tmp.txt → b.txt` (occupant AAA). Non-ff merge: `--first-parent exists old.txt` is FT, origin is the topic birth, holders `dest.txt`.

kizu **default** (no `--full`) from either name:

```
$ ./holt exists docs/deep-research-ai-agent-hooks.md
identity: deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
FALSE  57 commits
TRUE   13 commits  holders: deep-research-ai-agent-hooks.md
TRUE  174 commits  holders: docs/deep-research-ai-agent-hooks.md
now=TRUE  true=187/244  boolean=2  holder_splits=1
# kinds birth/move. Same command on the dead name is the same roost.
```

`--first-parent` from the **dead name** is the dest roost (rove's stitch, now on exists):

```
$ ./holt --first-parent exists deep-research-ai-agent-hooks.md
identity: deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
FALSE   3 commits
TRUE   21 commits
       origin: 321a830  as deep-research-ai-agent-hooks.md
       holders: docs/deep-research-ai-agent-hooks.md
now=TRUE  true=21/24
```

Same command on dest matches. berth's default on the dead name was never-held + hint `--full`.

sitbone default `exists FocusRiverView.swift` finds the 11-commit island (no `--full`). `--first-parent` is never-held and hints to drop the flag. `--full grep FocusRiverView` gold is now the default: `boolean=3` kinds `birth/spread/shrink`. skills `grep preact-zero-mock` is still README-only ghost. C056 `src/init.rs` does not follow `install.rs`. `src/git.rs` does not follow `parse.rs`.

Then `--now` of an uncommitted dest **lied**:

```
$ git mv 'old name.txt' 'new name.txt'     # uncommitted
$ ./holt --now exists 'new name.txt'
FALSE  never=1     # live dest, no commit seed
$ ./holt --now exists 'old name.txt'
holders: old name.txt then WORKTREE new name.txt    # dead name sees dest
```

Committed merge: query dest works, query old name works (either-name). Dirty tree: query old name works, query dest does not. “Either name” is not a symmetry under `--now`. A dirty leftover at the old name followed outgoing R to dest and ignored the occupant.

### After the improvement

Forced by that `--now dest` transcript, not polish. The walk tip under `--now` is the worktree. A live dest of dirty R seeds historical identity from the source; a leftover at the old name is a new roost.

```
$ git mv 'old name.txt' 'new name.txt'
$ ./holt --now exists 'new name.txt'
identity: old name.txt → new name.txt
TRUE  1 commit   holders: old name.txt
TRUE  WORKTREE   holders: new name.txt
now=TRUE  true=1/1

$ ./holt --now exists 'old name.txt'
# same roost (dead name follows outgoing dirty R)

$ echo DIRTY-REINCARNATE > 'old name.txt'
$ ./holt --now exists 'old name.txt'
identity: old name.txt
FALSE 1 commit
TRUE  WORKTREE  holders: old name.txt
now=TRUE  true=0/1     # leftover is this path, not the twin

$ ./holt --now exists 'new name.txt'
identity: old name.txt → new name.txt
TRUE historically, WORKTREE dest     # the file that moved
```

`./demo.sh 0` — 112 assertions, exit 0.

## Dogfood targets

- synthetic fixture: spaces rename; 3-hop CJK; copy vs rename; oscillate; leftover recreate; serialized swap; non-ff merge-birth; `--now`; nested git; empty repo
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — R100 `deep-research-ai-agent-hooks.md → docs/…` (`true=187` default from either name; `--first-parent` true=21 from either name, origin `321a830`); CLAUDE.md origin `e1098c8`; C056 leftover blob; `git.rs` split refused
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView island on the default walk; `--first-parent` never-held
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — preact-zero-mock README-only ghost; circuit-breaker path death

## Surprises

- Default occupancy walk is all reachable, so sitbone's island is visible without `--full`. berth taught `--full` as the rare flag; holt inverts it.
- `--first-parent exists` of a dead name still stitches dest because identity is a separate all-reachable R walk (rove already did this for grep).
- Leftover recreate is the distinguisher from berth: first-existence seed followed the twin; tip-occupant seed stays.

## Failures

- v1 `--now exists DEST` of an uncommitted `git mv` was never-held; dirty leftover followed the twin. v2: dest seeds from dirty source; leftover is a new roost.
- Full-history eras are still `git log --reverse` order, not a merge diamond (`TFTFT` on the non-ff fixture).
- Same-commit name swap is M/M; no R to follow.
- `--follow` with `--limit` still windows occupancy; identity is all-reachable R so a rename outside the occupancy window still stitches.

## Suggested mutations

- Occupancy on the merge lattice, not `git log --reverse`.
- Rename/rename split: say split (or refuse) when two dests share a birth.
- NFC/NFD: print stored bytes or refuse the other spelling.
- `git mv` + rewrite below similarity is D+A; name the missing R without lowering `-M`.

## Flipped assumption: bought and lost

Ancestor berth assumed **identity is walked on the same spec as occupancy** and **seed is first existence of the query path**. First-parent never saw the R; a leftover name occupied the twin.

**Bought**

- Either-name TRUE on the default walk (kizu 187) and on `--first-parent` (kizu 21) from a dead name `git log --follow` will not continue as occupancy.
- A leftover name is this path's identity. A serialized swap occupies the occupant at the query path.
- `--now exists DEST` of an uncommitted `git mv` is the dest roost; a dirty leftover is not the twin.
- `--no-follow` keeps TFTF path occupancy. Copy stays copy. C056 leftover blob stays a unique dest birth.

**Lost**

- Default occupancy is no longer first-parent. Callers who wanted mainline-only must pass `--first-parent`.
- Default `exists PATH` at a leftover name is the leftover, not the file that moved. Callers who wanted “the original file that used to have this name” must query the dest.

## Kill / keep

**Keep.** The first real-repo rename (`kizu` R100 into `docs/`) is one 187-commit identity from either name on the default walk, and one 21-commit dest roost from either name on `--first-parent`. berth's default dead-name was never-held. A leftover name is no longer the wrong roost. `--now exists DEST` of an uncommitted `git mv` is the same roost as the old name. Ghost remains correct for skills `preact-zero-mock`. Tenure's split remains refused. C056 leftover blob stays a unique dest birth.
