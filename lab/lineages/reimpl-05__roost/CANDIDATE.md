# reimpl-05 — roost

## Primitive

`roost` emits occupancy eras that also split when the **witness set** changes. Same TRUE, different files (or lines) holding it → a new era. Occupancy + who is holding.

Reimplementation of `perch` under a new name, from observed CLI behavior only (README, `demo.sh`, `--help`, and live runs — not the `perch` source). `--boolean` is ancestor `held`. Default `roost` is tenure.

## Why this might not exist

`git log -S` finds commits that *changed* a string. `git bisect` finds one cut. `held` finds intervals where a predicate is true — and then treats every TRUE sample as the same era, even when the name moved from `keep.txt` to `other.txt`, or a plugin died and only README still says the word.

There is no Unix verb whose value is **who is currently holding a still-true fact**. Blame is line identity. Log is change events. Occupancy without a holder is how `grep preact-zero-mock` says TRUE sixteen commits after the plugin was deleted.

Rebuilding from the outside tests whether holder-split occupancy is a real primitive or an accident of one implementation.

## How to run

```bash
./roost --help
./demo.sh
./roost -C /path/to/repo grep TOKEN_B
./roost -C /path/to/repo --boolean grep TOKEN_B
./roost -C /path/to/repo --grain loci grep TOKEN_B
./roost -C /path/to/repo --full grep FocusRiverView
./roost -C /path/to/repo grep preact-zero-mock
```

Python 3.9+, stdlib only, `git`. Exit 0 iff the predicate holds at the last sample.

## Empirical transcript

### Before the improvement (this first commit)

Synthetic fixture matched observed `perch`: `oscillate.txt` eras `TFTF`; TOKEN_A reincarnated `keep.txt` → `other.txt`; TOKEN_B never flipped occupancy (`boolean=1`) but split `alpha.txt` → `alpha.txt,beta.txt` → `beta.txt` (`eras=3`, kinds `birth/spread/shrink`). `--grain lines` split the t3 line-number shift (4 eras); `--grain loci` did not. `--boolean` recovered one TRUE era. `--now` saw an uncommitted resurrection (`end.kind=worktree`). Dead pathspec and case-fold hints fired.

Real repos — gold checks against live `perch` answers (original source never opened):

```
$ git -C sitbone log --oneline -- Sources/SitboneUI/FocusRiverView.swift
# (empty)  — the footgun

$ ./roost -C sitbone --full grep FocusRiverView
FALSE  11 commits  a2512fe..74363dc  2026-03-31
TRUE    1 commit   14b1d6e  2026-03-31
       holders: Sources/SitboneUI/FocusRiverView.swift
TRUE    5 commits  ef9452f..74d42a1  2026-03-31 → 2026-04-01
       holders: Sources/SitboneUI/FocusRiverView.swift, Sources/SitboneUI/NotchOverlay.swift
       + Sources/SitboneUI/NotchOverlay.swift
TRUE    5 commits  50e5311..1fefafb  2026-04-01
       holders: Sources/SitboneUI/FocusRiverView.swift
       - Sources/SitboneUI/NotchOverlay.swift
FALSE  78 commits  70ec7df..094769d  2026-04-01 → 2026-04-17
now=FALSE  true=11/100  eras=5  boolean=3  holder_splits=2
# kinds of TRUE eras: birth, spread, shrink — remaining holder is code, not a ghost

$ ./roost -C skills grep preact-zero-mock
FALSE   2 commits
TRUE   21 commits  holders: preact-zero-mock/SKILL.md
TRUE   10 commits  holders: README.md, preact-zero-mock/SKILL.md
       + README.md
TRUE   16 commits  holders: README.md
       - preact-zero-mock/SKILL.md
       ghost: definition left; name still roosts in documentation
now=TRUE  true=47/49  eras=4  boolean=2  holder_splits=2
hint: now=TRUE only as a documentation mention (README.md); definition preact-zero-mock/SKILL.md is gone
```

`held` / `--boolean` collapses skills to FALSE 2 / TRUE 47. The last sixteen commits are occupancy without a definition. v1 names that **ghost**.

```
$ ./roost -C kizu exists CLAUDE.md
# exists CLAUDE.md  (kizu, 24 of 244 commits, first-parent)
FALSE   1 commit   cbaf29a  2026-04-15
TRUE   23 commits  0ea3916..9349dc5  2026-04-15 → 2026-05-04
       0ea3916  Merge pull request #1 from annenpolka/chore/bootstrap-ci-and-claude-md
now=TRUE  true=23/24
```

v1 gap: first-parent occupancy starts at a merge. The file was born on the topic branch at `e1098c8`. perch/`held` had the same blind spot: they hint `--full` only when the predicate *never* held on first-parent, not when it held starting at a merge.

`./demo.sh` — 57 assertions, exit 0, including sitbone FocusRiverView holder splits and skills preact-zero-mock README-only tenure.

### After the improvement

Same sitbone/skills commands still match perch exactly (origin only attaches when a first-parent TRUE era *starts at a merge*). Forced by kizu `CLAUDE.md`, not polish.

```
$ ./roost -C kizu exists CLAUDE.md
# exists CLAUDE.md  (kizu, 24 of 244 commits, first-parent)
FALSE   1 commit   cbaf29a  2026-04-15
TRUE   23 commits  0ea3916..9349dc5  2026-04-15 → 2026-05-04
       0ea3916  Merge pull request #1 from annenpolka/chore/bootstrap-ci-and-claude-md
       9349dc5  release: v0.7.0
       origin: e1098c8  chore: bootstrap CLAUDE.md, CI, and t-wada TDD conventions  (1 commit before this merge)
       holders: CLAUDE.md
now=TRUE  true=23/24
```

The occupancy git actually shipped, not the merge that made it visible on mainline. sitbone FocusRiverView (never on first-parent) and skills preact-zero-mock (birth is not a merge) are unchanged: still `boolean=3` / holder splits on NotchOverlay, still README-only ghost for the last 16 commits.

`./demo.sh` — 58 assertions, exit 0.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView island `git log -- path` cannot see; NotchOverlay gained then lost the name while the file lived
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — `preact-zero-mock` ghost occupancy (last 16 commits README-only); `circuit-breaker` boolean death
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — first-parent compression; merge-birth of `CLAUDE.md`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — phrase + case footguns kept from held
- synthetic fixture: TOKEN_B copy/move with no FALSE gap; TOKEN_A reincarnation; line-number shift vs loci grain; `--now`; nested git; empty repo

## Surprises

- The interesting split is not TOKEN_A (FALSE already cuts it). It is TOKEN_B / preact-zero-mock: occupancy never dies and the holder does.
- Dropping a *code* holder is not a ghost. FocusRiverView losing NotchOverlay is shrink; the type still roosts in its file. Ghost is: remaining holders are documentation, a non-doc holder left.
- `is_doc_holder` must treat `SKILL.md` as a definition (code), not markdown-as-docs, or the skills ghost never fires.
- `--grain lines` splits when someone inserts a header above a match. `--grain loci` (path + line text) ignores that. Default grain is files.
- kizu first-parent `24 of 244` is the walk, not a bug — but the TRUE era's start commit is a merge, which is a different lie than `git log -- PATH`.

## Failures

- v1 named ghost occupancy (the perch v2 lesson) but still named the merge as CLAUDE.md's birth on first-parent. v2 names `e1098c8`.
- `exists` of an exact path cannot split on holders (the holder *is* the path). Rename is still a death.
- Full-history eras are ordered by `git log --reverse`, not a merge-diamond lattice.
- `exec` holders are stdout lines. A noisy command fragments eras. Silent predicates (`test -f`) stay boolean.
- Glob catalog walks (`*SKILL.md`) emit one era per addition.

## Suggested mutations

- `--follow` so a rename is one roost, not a path death plus a birth.
- Ignore-docs / `--code` grain so kizu `line_number` does not fragment on ADR accretion.
- Cache probes in `.git/roost-cache/` keyed by `(sha, predicate, grain)`.

## Flipped assumption: bought and lost

Ancestor `held` assumed **TRUE is TRUE**. One occupancy interval, witnesses as a footnote. `perch` flipped that. Rebuilding from the outside kept the flip.

**Bought**

- Copy and move without a FALSE gap become visible (TOKEN_B; FocusRiverView ↔ NotchOverlay).
- `grep` that stays true after a deletion is no longer a 47-commit blob. The last tenure is named, and if it is documentation-only, it is a ghost.
- `--boolean` is an explicit downcast to held.

**Lost**

- Eras are no longer a pure boolean occupancy. TFTF diagrams lie; `boolean=2 holder_splits=2` is the real shape.
- Growing modules fragment (glob `*SKILL.md`).
- Ghost is a heuristic over remaining holders, not a proof the definition is dead (`exists` already answers that).

## Kill / keep

**Keep.** Rebuilt from the outside, it reproduced perch's sitbone holder splits and skills README-only tenure exactly, including the ghost. The first improvement was forced by kizu: first-parent occupancy starts at a merge, so v1 (like perch) named the merge and hid `e1098c8`. The primitive survived a clean-room reimplementation and then beat its ancestor on that merge-birth case.
