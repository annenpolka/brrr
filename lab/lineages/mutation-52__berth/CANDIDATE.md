# mutation-52 — berth

## Primitive

`berth --follow` occupies a **file identity**. A rename is one roost, not a path death plus a birth. Query the old name or the new name; occupancy stays TRUE and holders still split.

Default exact `exists` follows. `--no-follow` is ancestor roost (path occupancy). `--boolean` is ancestor `held`.

## Why this might not exist

`git log --follow` only walks *changes*, backward, from a name that exists at HEAD. `held exists PATH` and `roost exists PATH` treat the path as the identity, so `git mv old new` is FALSE after the old name and TRUE after the new one. `grep` already splits TOKEN_B when the holder set changes; `exists` cannot, because the holder *is* the path. glyph emits `held --follow exists old` as a question and does not walk. till follows *function* names for tests. Nobody occupies **the file that moved**.

Discarded as too conventional: wrapping `git log --follow --name-only`, pairing `exists old` with `exists new` in a script.

## How to run

```bash
./berth --help
./demo.sh 0
./demo.sh
./berth -C /path/to/repo exists 'old name.txt'
./berth -C /path/to/repo --no-follow exists 'old name.txt'
./berth -C /path/to/repo --full exists docs/deep-research-ai-agent-hooks.md
./berth -C /path/to/repo --full exists deep-research-ai-agent-hooks.md
./berth -C /path/to/repo grep preact-zero-mock
./berth -C /path/to/repo --full grep FocusRiverView
```

Python 3.9+, stdlib only, `git`. Exit 0 iff the predicate holds at the last sample.

## Empirical transcript

### Before the improvement (this first commit)

Synthetic fixture: `--no-follow` keeps ancestor path death (`old name.txt` TF, `new name.txt` FT). `--follow` on either name is one identity (`old name.txt → new name.txt`), `boolean=1` `eras=2` kinds `birth/move`, always held. A copy (`alpha.txt` → `beta.txt`) is not a follow. Oscillate delete+revive is path occupancy TFTF and identity occupancy TF (reincarnation is a different file). 3-hop `old.txt → new name.txt → 最終.md` is the same roost from any name.

Real repos — sitbone/skills ancestor gold still holds. kizu `--full --follow` stitches the one recorded rename, then **lies**:

```
$ ./berth --full exists docs/deep-research-ai-agent-hooks.md
identity: deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
FALSE  57 commits
TRUE   13 commits  holders: deep-research-ai-agent-hooks.md
TRUE  174 commits  holders: docs/deep-research-ai-agent-hooks.md
       + docs/deep-research-ai-agent-hooks.md
       - deep-research-ai-agent-hooks.md
       ghost: definition left; name still berths in documentation
now=TRUE  true=187/244  boolean=2  holder_splits=1
hint: now=TRUE only as a documentation mention (docs/…); definition deep-research-ai-agent-hooks.md is gone
```

The same command on the dead name is the same roost (`true=187`). `--no-follow` on the old path is the ancestor lie: TRUE 13 then FALSE 174, `now=FALSE`.

The ghost is wrong. The file moved into `docs/`. `is_doc_holder` treats the dest as documentation and the old basename as a lost definition. That heuristic is for `grep preact-zero-mock` (SKILL.md gone, README remains). An identity rename is a **move**.

sitbone `--full grep FocusRiverView` still `boolean=3` kinds `birth/spread/shrink`. skills `grep preact-zero-mock` still README-only ghost. Those must not change.

`./demo.sh 0` — 76 assertions, exit 0.

### After the improvement

Forced by that kizu transcript, not polish. An identity move is a **move**. Ghost stays the grep lie (skills `preact-zero-mock`). First-parent origin now follows the identity, so dest occupancy that starts at merge `ca0577a` names the old-name birth `321a830`, not the `R100` commit `4e37f16`.

```
$ ./berth --full exists docs/deep-research-ai-agent-hooks.md
identity: deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
FALSE  57 commits
TRUE   13 commits  holders: deep-research-ai-agent-hooks.md
TRUE  174 commits  holders: docs/deep-research-ai-agent-hooks.md
       + docs/deep-research-ai-agent-hooks.md
       - deep-research-ai-agent-hooks.md
now=TRUE  true=187/244  boolean=2  holder_splits=1
# kinds: birth, move. No ghost. The file still exists; it changed path.

$ ./berth exists docs/deep-research-ai-agent-hooks.md
FALSE   3 / TRUE 21
       origin: 321a830  feat(ui,watcher): …  (55 commits before this merge)
                as deep-research-ai-agent-hooks.md
       holders: docs/deep-research-ai-agent-hooks.md
```

Same command on the dead name is still the same `--full` roost. skills `grep preact-zero-mock` is still a README-only ghost. sitbone FocusRiverView shrink (code remains) is still not a ghost. kizu `exists CLAUDE.md` origin is still `e1098c8` (no rename).

`./demo.sh 0` — 79 assertions, exit 0.

## Dogfood targets

- synthetic fixture: spaces rename; 3-hop CJK; copy vs rename; oscillate reincarnation vs identity; TOKEN_B; `--now`; nested git; empty repo
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `R100 deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md` (`true=187` follow vs `true=13` path death); CLAUDE.md merge-birth origin
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView island + NotchOverlay holder splits (ancestor gold)
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — preact-zero-mock README-only ghost; circuit-breaker path death

## Surprises

- `git log --follow` from the *old* name stops at the rename commit. berth from the old name continues as the dest for 174 more commits.
- First-parent never sees the old name (the merge adds dest as A). `--follow` on the dead name still hints `--full`. `--follow` on dest origin-names `321a830 as deep-research-ai-agent-hooks.md` — the birth, not the rename and not the merge.
- Delete then recreate `oscillate.txt` is *not* a follow. Identity dies at the first D.
- A copy is not a rename. TOKEN_B `grep` still splits; `exists --follow alpha.txt` does not pick up `beta.txt`.

## Failures

- v1 classified a rename into `docs/` as ghost and origin-named the R commit. v2: move, origin `321a830 as <old path>`.
- `--follow` is exists-only. `grep -- path` still does not follow the pathspec.
- Full-history eras are still `git log --reverse` order, not a merge diamond.
- `--follow` with `--limit` can miss a rename outside the window.
- Default exact `exists` follows. Oscillate reincarnation needs `--no-follow` to see TFTF.

## Suggested mutations

- `grep --follow -- PATH` so a path-limited grep survives `git mv`.
- `--follow` of a split (kizu `git.rs` → `parse.rs`) is tenure's object, not this one.
- Cache name-status per `(spec, first-parent)`.
- `--now` of a dead identity that the worktree recreated under the query path is a new identity; path occupancy still wants `--no-follow`.

## Flipped assumption: bought and lost

Ancestor roost assumed **the path is the identity**. Suggested mutation: `--follow` so a rename is one roost.

**Bought**

- `git mv` is occupancy + a holder move, from either name, including a dead name `git log --follow` will not continue.
- `--no-follow` keeps TFTF path occupancy (oscillate reincarnation; circuit-breaker death).
- Copy stays copy.

**Lost**

- Default exact `exists` is no longer path occupancy. Oscillate reincarnation is one TRUE island under `--no-follow` and a single death under `--follow`.
- Default exact `exists` is identity occupancy. Callers who wanted path reincarnation must pass `--no-follow`.

## Kill / keep

**Keep.** The first real-repo rename (`kizu` R100 into `docs/`) is one 187-commit identity from either name, which neither `git log --follow` nor roost `exists` will say. v1 lied that the dest was a documentation ghost; v2 was forced by that run. Ghost remains correct for skills `grep preact-zero-mock`.
