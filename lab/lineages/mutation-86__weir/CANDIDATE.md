# mutation-86 — weir

## Primitive

A merge-parent that is itself a merge contributes its occupancy lattice, not its tree.

## Why this might not exist

ford joins parent *trees*. kizu `CLAUDE.md` at `0ea3916` is `FALSE ⊓ TRUE` (a ford, not a birth). The next first-parent merge `21ae074` (PR #2) has parent trees `TRUE ⊓ TRUE`, so ford names a 22-commit TRUE *preserve* starting there. Occupancy of `0ea3916` never flowed. Anyone who reads era starts as births still thinks the file was born at PR #2 — same class of lie, one merge later, now recursive.

The missing verb: at a merge-of-merges, occupancy **is** the join of parent *occupancy*. `--follow` is berth, not this object. `--boolean` that downcasts UNKNOWN is a labelled lie or a refuse.

## How to run

```bash
chmod +x ./weir
./weir --help
./weir lattice
./demo.sh
./weir -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./weir --any -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./weir --boolean -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./weir --follow exists CLAUDE.md   # refused: berth
```

Python 3.9+, stdlib only, git. Exit 0 iff last sample is TRUE, 1 if FALSE, 3 if UNKNOWN/SHALLOW/EMPTY, 2 error.

## Empirical transcript

### Before the improvement

v1 already had recursive occupancy join, nested parent lattice, refuse-birth, `--follow` → berth, `--boolean` refuse on UNKNOWN. `./demo.sh` — 113 assertions, exit 0.

Synthetic merge-of-merges: M1 is `FALSE ⊓ TRUE` (tree TRUE). M2's merge-parent is M1: ford would print `TRUE ⊓ TRUE` preserve. weir prints `FALSE ⊓ TRUE` with `parent M1=FALSE occupancy … (tree=TRUE)`, `reason=recursive`, refuse birth. TRUE starts at the next non-merge, `kind=continue`, origin the topic.

kizu first-parent `--all` refuses birth at `0ea3916` (ford gold) and then **does not** call `21ae074` preserve. `21ae074` is the real merge-of-merges: parent `0ea3916` contributes occupancy `FALSE ⊓ TRUE = FALSE`, not tree TRUE.

Forced by kizu, not polish: every later first-parent merge until the first non-merge reprints the whole nested lattice (PR #3 nested inside PR #4 nested inside …). TRUE `continue` points at `ad6de10` (the last cascade), not at `21ae074`. Six weirs, six hints, unreadable.

```
$ ./weir -C kizu exists CLAUDE.md
FALSE     1 commit    cbaf29a
FALSE     1 commit    0ea3916
       weir  FALSE ⊓ TRUE = FALSE  (does not preserve)
       parent cbaf29a=FALSE  tree
       parent e1098c8=TRUE   tree
       tree=TRUE  occupancy is the recursive join, not a birth
       origin: e1098c8
       refuse birth: a parent already held TRUE
FALSE     1 commit    21ae074
       weir  FALSE ⊓ TRUE = FALSE  (recursive: merge-parent contributes occupancy, not tree)
       parent 0ea3916=FALSE  occupancy  FALSE ⊓ TRUE = FALSE  (tree=TRUE)
              parent cbaf29a=FALSE  tree
              parent e1098c8=TRUE   tree
       parent 429e4ac=TRUE   tree
       origin: e1098c8
       refuse birth: a parent already held TRUE
FALSE     1 commit    ca0577a   # and 0aab861, 0b41dc6, ad6de10 — nested lattice reprints
TRUE     17 commits   d9b9645..9349dc5
       continue after weir ad6de10; not birth
       origin: e1098c8
now=TRUE  true=17/24  weirs=6  walk=first-parent  join=all  tree_now=TRUE
```

ford gold `TRUE spanning 21ae074` is the tree-join lie weir exists to name.

### After the improvement

Forced by kizu, not polish. After the first recursive weir, later same-origin weirs are `inherited` — occupancy still the recursive join, not a new crossing. TRUE `continue` points at `21ae074`. Two hints (introducing + recursive), not six.

```
$ ./weir -C kizu exists CLAUDE.md
FALSE     1 commit    cbaf29a
FALSE     1 commit    0ea3916
       weir  FALSE ⊓ TRUE = FALSE  (does not preserve)
       parent cbaf29a=FALSE  tree
       parent e1098c8=TRUE   tree
       tree=TRUE  occupancy is the recursive join, not a birth
       origin: e1098c8
       refuse birth: a parent already held TRUE
FALSE     1 commit    21ae074
       weir  FALSE ⊓ TRUE = FALSE  (recursive: merge-parent contributes occupancy, not tree)
       parent 0ea3916=FALSE  occupancy  FALSE ⊓ TRUE = FALSE  (tree=TRUE)
              parent cbaf29a=FALSE  tree
              parent e1098c8=TRUE   tree
       parent 429e4ac=TRUE   tree
       origin: e1098c8
       refuse birth: a parent already held TRUE
FALSE     4 commits   ca0577a..ad6de10
       inherited weir 21ae074; occupancy still the recursive join, not a new crossing
       origin: e1098c8
TRUE     17 commits   d9b9645..9349dc5
       continue after weir 21ae074; not birth
       origin: e1098c8
now=TRUE  true=17/24  eras=5  weirs=6  walk=first-parent  join=all  tree_now=TRUE
```

`--any` still a TRUE weir at `0ea3916`, not a 23-commit birth. `--boolean` is a labelled lie recovering held's birth at the merge. Depth-1 is SHALLOW. `./demo.sh` — 117 assertions, exit 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| synthetic diamond | non-recursive: same as ford; weir not birth |
| synthetic merge-of-merges | M2 occupancy FALSE, parent M1 source=occupancy, reason=recursive |
| merge-added file | F⊓F with tree=TRUE |
| preserve merge | T⊓T occupancy compresses |
| timeout parent | meet(T,U)=U; `--boolean` refused |
| `--follow` | refused: berth |
| kizu `exists CLAUDE.md` | refuse birth at `0ea3916`; recursive weir at `21ae074`; origin `e1098c8` |
| sitbone `FocusRiverView.swift` | first-parent never; `--full` island 11 |
| skills `grep preact-zero-mock` | still TRUE at HEAD |

## Surprises

- Recursive meet at `21ae074` is `FALSE ⊓ TRUE = FALSE` even though both parent *trees* have `CLAUDE.md`. ford's preserve was the tree-join.
- The FALSE occupancy then cascades through every first-parent merge until a non-merge samples the tree (`d9b9645`). That is honest and unreadable until inherited weirs compress.
- `--any` at `0ea3916` is still a TRUE weir (introduced via `e1098c8`); later T⊔T occupancy preserves.

## Failures

1. **`--tree` / `--boolean` reintroduce the merge-birth lie** by design. `--boolean` is a labelled lie when all samples are T/F; UNKNOWN is a refuse.
2. **Rename is still path death.** `--follow` is berth, not this object.
3. **Octopus is folded meet/join.** Nested display is two-parent shaped.
4. **First-parent TRUE still starts at the first non-merge** (`d9b9645`), not at topic `e1098c8` (off the walk) and not at `21ae074` (occupancy FALSE).

## Suggested mutations

- Pipe `weir --json` into roost to split holders on a still-TRUE recursive join.
- Cache `(sha, predicate) → occupancy` so extra ancestor probes are free.
- `--unfold` to reprint inherited weirs as the v1 nested lattice.

## Flipped assumption: bought and lost

ford assumed **join inputs have to be parent trees, not parent occupancy**, or `0ea3916`'s FALSE would flow into PR #2 forever.

**Bought**

- A merge-of-merges is a printed recursive join, not a T⊓T preserve.
- kizu `21ae074` is a weir; origin is still `e1098c8`; refuse birth.
- `--follow` cannot pretend to be file identity. `--boolean` cannot silently turn UNKNOWN into FALSE.

**Lost**

- First-parent TRUE no longer *spans* `21ae074`. Occupancy there is FALSE; the snapshot is TRUE (`tree=`).
- Cascade of FALSE weirs on a merge-heavy first-parent until a non-merge.

## Kill / keep

**Keep.** The occupancy verb was already real. This mutation is the recursive join ford named and refused. The v1→v2 change was forced by kizu: recursive join at `21ae074` still left five later merges reprinting the nested lattice. Inherited weirs are the same occupancy, not a new crossing. Not polish.
