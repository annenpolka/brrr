# hybrid-14 — neap

## Primitive

Overlay a unified diff in memory onto `--base` and emit the **exclusive-A path-condition stacks that would die** — stacks true on HEAD (or `-C repo`) and false after the overlay. Not the stacks the patch births. Not `git apply && wane`. The worktree is never written.

## Why this might not exist

`liken` (mutation-61) overlays and answers graft's invert: *which `+` lines share this `given`?* That is overlay-**births**. `wane` (mutation-58) answers exclusive-A deaths of **two git trees**. Reviewers of an unapplied patch still ask wane's question about a file that only exists on `--base`: *what would die if I applied this?* They either apply (and lie to the worktree) or reconstruct deaths by scrolling.

`git apply && wane` is the concatenation. It writes. It is not an overlay. `wane` on HEAD alone cannot name `FocusRiverView` after the island; the file is gone.

Not leftover-name hunting. Not a third `ambit`/`amid` clone. Not `liken | wane`.

## How to run

```bash
chmod +x ./neap ./demo.sh
./neap --selftest
./demo.sh
./neap --base :wt --diff fixtures/island.diff
git -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone diff 14b1d6e HEAD \
  | ./neap -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --base 14b1d6e --limit 6
git -C /Users/annenpolka/ghq/github.com/annenpolka/kizu diff 3b3e0a9^ 3b3e0a9 \
  | ./neap -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --base 3b3e0a9^
```

Python 3.9+, stdlib. stdin = unified diff. Exit 0 deaths, 1 none, 2 usage.

## Empirical transcript

### Before the improvement (this first commit)

Fixture island (`fixtures/island.diff` deletes `river.py`, adds three `unique_mod_*` files):

```
$ ./neap --base :wt --diff fixtures/island.diff
  A   exclusive_a  if flow_score > 0.2
  A   exclusive_a  elif flow_score < -0.2
neap=2  deaths=2  born=3  moves=0
```

`fixtures/mod0.py` is never created. `keep.py`'s `if keep_flag` lives on the worktree and is not a death. Overlay-deaths ≠ overlay-births ≠ HEAD-only.

`fixtures/newif.diff` (adds `if bytes.len() > 100`) default covering is empty (no deleted file). JSON still reports `deaths=1`: the old exact stack of `let p` (without the new `given ¬(len > 100)`) is counted as exclusive-A of a surviving file. That is a wrap, not a death. `--also-changed` would name it.

`fixtures/move.diff` (rename `git.py` → `parse_moved.py`): covering empty, `moves=1`. Destination never written.

kizu `3b3e0a9^` vs `3b3e0a9`:

```
# 4 only-B, 2 changed
neap  (exclusive-A path-conditions that would die)
  (empty — nothing died)
neap=0  deaths=0  born=0  moves=102
```

Silent. Porcelain unchanged. The split is a move.

sitbone island `14b1d6e` vs HEAD — wane names `if app.flowScore>0.2` on FocusRiverView. neap v1:

```
# 2 only-A, 60 only-B, 10 changed
  A   exclusive_a  if let w = window
           holders A: Sources/SitboneUI/FocusRiverView.swift
           pin  Sources/SitboneUI/FocusRiverView.swift:209
neap=1  deaths=19  born=268  moves=0
```

FocusRiverView is the deleted file (good). The named stack is `func show()`'s `if let w = window`, not `if app.flowScore > 0.2`. The flowScore arms live in Swift `var barColor` / `var dotColor` computed properties; the brace engine never walks a `var … {` body, so those stacks are invisible. Sitbone porcelain empty. Camera births are counts, not covering members.

`./demo.sh` exits 0.

### After the improvement (this commit)

Forced by sitbone island leftover, not polish.

1. **Swift computed `var` is a fn-shaped body.** `var barColor: Color { if app.flowScore > 0.2 { … } }` was a plain statement. The brace engine never walked the body, so the island's money-shot stack did not exist. Stored `var x = …` stays a statement (`=` before `{`). Accessors `get`/`set`/`willSet`/`didSet` walk too. Kind is `fn` so the property name is not leftover-name identity.

2. **A wrap is not a death.** Inserting a total-exit `if` used to kill the old exact stack of the lines below (`deaths=1` on `newif.diff`). A stack on A still lives if it is a prefix of a B stack.

Same sitbone command:

```
A   exclusive_a  given ¬(app.flowScore > 0.2) | if app.flowScore < -0.2
                 holders A: Sources/SitboneUI/FocusRiverView.swift
                 pin  Sources/SitboneUI/FocusRiverView.swift:190
A   exclusive_a  if app.flowScore > 0.2
                 pin  Sources/SitboneUI/FocusRiverView.swift:121
A   exclusive_a  elif app.flowScore < -0.2
                 pin  Sources/SitboneUI/FocusRiverView.swift:123
A   exclusive_a  given ¬(app.flowScore > 0.2) | given ¬(app.flowScore < -0.2)
                 pin  Sources/SitboneUI/FocusRiverView.swift:191
neap=4  deaths=24  born=293  moves=1
```

`if let w = window` dropped. `if app.flowScore > 0.2` at L121 matches wane's pin. The extra `given ¬(>0.2) | if < -0.2` is `dotColor`'s second sequential `if` (not `else if`) — a real exclusive-A, invisible to v1. `guard totalTime > 0` is now `moves=1` (copied onto SiteObserver in the same overlay). Camera births stay a count.

`fixtures/newif.diff`: `deaths=0`, `born=2`. The old `given a/` stack is a prefix of the new `given a/ | given ¬(len > 100)`. kizu still silent (`moves=102`). Porcelain still empty. `./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `fixtures/island.diff` | flow_score dies; unique_mod births silent; no write |
| `fixtures/keep.py` | HEAD-only stack is not an overlay-death |
| `fixtures/newif.diff` | default covering empty; wrap is `deaths=0` after v0.2 |
| `fixtures/river.swift` | computed `var barColor` exposes `if app.flowScore > 0.2` |
| `fixtures/move.diff` | rename silent |
| `fixtures/copyguard.diff` | copied `if flow_score > 0.2` is AB |
| `fixtures/strip.diff` | surviving-file death is `--also-changed` |
| kizu `3b3e0a9^..3b3e0a9` | silent (move) |
| sitbone `14b1d6e` vs HEAD | deleted-file leftover; FocusRiverView; not camera births |

Read-only on the real repos. Overlay never writes them.

## Surprises

- The valuable invert of liken is not "group the `+` lines." It is "the `given` that exists on `--base` and would be gone after this overlay." Overlay of the whole file, not the hunk window, is still the primitive; the query is deaths.
- A 100% rename with no hunks is still an overlay: pre and post are the same blob at two paths. Stack identity is AB.
- Sitbone's money-shot stack sits in a computed `var`, not a `func`. graft/liken's fn-shaped brace walk cannot see it. Walking `var name: T {` as fn-like is enough; we did not become a third whenline.
- `guard totalTime > 0` copied into a *new* file of the same overlay is a move (`moves=1`). Overlay-scoped copy detection does not need a full-tree parse.

## Failures

1. **Trailing-closure ifs** (SwiftUI `ForEach { if … }`) still sit inside a plain statement. Island flowScore did not need them.
2. **Match-arm / `if let` pairing** inherited from liken.
3. **Combined / binary diffs** are unplaced (exit 2 if that is all), not guessed.
4. **Cover order** prefers deeper name-like arms, so `dotColor`'s sequential `if < -0.2` lists above the true-arm. The true-arm is present.

## Suggested mutations

- Cluster sibling arms (`if flowScore>0.2` / `elif` / given-else / sequential `if`) as one obituary.
- Pipe overlay-deaths into `tenure --rev` of the pre-image pin.
- Walk trailing-closure bodies when the overlay actually deletes an if inside one.

## Kill / keep

**Keep**, if the invert stays deaths of an *unapplied* overlay. Kill if a later generation reduces it to `git apply && wane`, or to liken's `+` groups with a filter.
