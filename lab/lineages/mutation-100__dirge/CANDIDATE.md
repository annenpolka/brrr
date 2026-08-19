# mutation-100 — dirge

## Primitive

Overlay a unified diff in memory onto `--base` and emit the **exclusive-A path-condition forks that would die**, with sibling arms (`if` / `elif` / given-else / sequential `if`) clustered as **one obituary**. Stacks true on HEAD (or `-C repo`) and false after the overlay. Not the stacks the patch births. Not `git apply && wane`. The worktree is never written.

## Why this might not exist

`neap` (hybrid-14) already answers overlay-deaths. Its leftover is the covering: sitbone island prints four exclusive-A rows that are one color-threshold decision (`if flowScore>0.2`, `elif < -0.2`, sequential `if` in `dotColor`, given-else). Reviewers count N obituaries for one fork.

`wane` has the same hole on two trees. Concatenation (`neap | awk` grouping labels) does not know that `given ¬(P) | if Q` is the sequential arm of `if P`. Not leftover-name hunting. Not a third `ambit`/`amid` clone. Not overlay-births.

## How to run

```bash
chmod +x ./dirge ./demo.sh
./dirge --selftest
./demo.sh
./dirge --base :wt --diff fixtures/island.diff
git -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone diff 14b1d6e HEAD \
  | ./dirge -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --base 14b1d6e --limit 6
git -C /Users/annenpolka/ghq/github.com/annenpolka/kizu diff 3b3e0a9^ 3b3e0a9 \
  | ./dirge -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --base 3b3e0a9^
```

Python 3.9+, stdlib. stdin = unified diff. Exit 0 deaths, 1 none, 2 usage.

## Empirical transcript

### Before the improvement (this first commit)

Fixture island (`fixtures/island.diff` deletes `river.py`, adds three `unique_mod_*` files):

```
$ ./dirge --base :wt --diff fixtures/island.diff
  A   exclusive_a  if flow_score > 0.2
           1 file  depth=1  arms=2  if/elif
             · if flow_score > 0.2
             · elif flow_score < -0.2
           pin  fixtures/river.py:3
dirge=1  deaths=2  born=3  moves=0  arms=2
```

neap printed two covering rows. Clustered obituary ≠ N sibling rows. `fixtures/mod0.py` is never created. `keep.py`'s `if keep_flag` lives on the worktree and is not a death.

`fixtures/seq.diff` (barColor `if/elif` + dotColor sequential `if`): `dirge=1  arms=4`. `fixtures/twochain.diff`: `dirge=2` (independent chains stay separate). `fixtures/newif.diff`: covering empty, `deaths=0`. `fixtures/move.diff`: silent, `moves>0`.

kizu `3b3e0a9^` vs `3b3e0a9`:

```
dirge  (exclusive-A forks that would die; sibling arms clustered)
  (empty — nothing died)
dirge=0  deaths=0  born=0  moves=102  arms=0
```

Silent. Porcelain unchanged. The split is a move.

sitbone island `14b1d6e` vs HEAD:

```
  A   exclusive_a  given ¬(app.flowScore > 0.2) | if app.flowScore < -0.2
           1 file  depth=2  arms=4  given-else/if/elif
             · given ¬(app.flowScore > 0.2) | if app.flowScore < -0.2
             · if app.flowScore > 0.2
             · given ¬(app.flowScore > 0.2) | given ¬(app.flowScore < -0.2)
             · elif app.flowScore < -0.2
           holders A: Sources/SitboneUI/FocusRiverView.swift
           pin  Sources/SitboneUI/FocusRiverView.swift:190
  A   exclusive_a  if let w = window
           arms=2
           pin  Sources/SitboneUI/FocusRiverView.swift:209
dirge=2  deaths=24  born=293  moves=1  arms=6
```

Four flowScore siblings are one obituary (`dirge=2`, not `neap=4`). Leftover on the same deleted file names the `if let w = window` fork (also clustered). The flowScore **headline** is the sequential `dotColor` arm at L190, not wane's true-arm `if app.flowScore > 0.2` at L121. Cover rank prefers deeper stacks; that is the leftover.

`./demo.sh` exits 0.

### After the improvement (this commit)

Forced by sitbone island leftover, not polish.

**The obituary names the root true-arm.** Cover rank still prefers deeper named members when *choosing which fork* to emit. The headline and pin of a cluster now prefer `if P` over `given ¬(P) | if Q`. Sitbone's money-shot is wane's pin, not `dotColor`'s sequential arm.

Same sitbone command:

```
  A   exclusive_a  if app.flowScore > 0.2
           1 file  depth=2  arms=4  if/elif/given-else
             · if app.flowScore > 0.2
             · elif app.flowScore < -0.2
             · given ¬(app.flowScore > 0.2) | if app.flowScore < -0.2
             · given ¬(app.flowScore > 0.2) | given ¬(app.flowScore < -0.2)
           holders A: Sources/SitboneUI/FocusRiverView.swift
           pin  Sources/SitboneUI/FocusRiverView.swift:121
  A   exclusive_a  if let w = window
           arms=2
           pin  Sources/SitboneUI/FocusRiverView.swift:209
dirge=2  deaths=24  born=293  moves=1  arms=6
```

`dirge=2` ≠ neap's 4 sibling rows. Pin L121 matches wane. The second obituary is a *different* deleted-file fork (`show()`'s `if let w = window`), not a fifth flowScore arm — leftover spent on a distinct decision once siblings share a slot.

Island still `dirge=1 arms=2`. kizu still silent (`moves=102`). Porcelain still empty. `./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `fixtures/island.diff` | if+elif = 1 obituary; unique_mod births silent; no write |
| `fixtures/seq.diff` | elif + sequential if + given-else = 1 obituary |
| `fixtures/twochain.diff` | two independent if-chains stay 2 obituaries |
| `fixtures/keep.py` | HEAD-only stack is not an overlay-death |
| `fixtures/newif.diff` | wrap is `deaths=0` |
| `fixtures/move.diff` | rename silent |
| kizu `3b3e0a9^..3b3e0a9` | silent (move) |
| sitbone `14b1d6e` vs HEAD | FocusRiverView flowScore as one clustered obituary; pin L121 |

Read-only on the real repos. Overlay never writes them.

## Surprises

- Clustering is not "all ifs in a deleted file." Two independent if-chains (`if a/elif b` then `if c/elif d`) stay two obituaries. The sequential `given ¬(P) | if Q` is the arm that actually needs the invert: it does not share an AST `chain` with `else if`.
- Once siblings share a slot, leftover on the same deleted file names a second *fork* (`if let w = window`). neap spent that slot on another flowScore row. That is the object of `--limit`, not a leak of surviving-file ticks.
- The valuable name of a cluster is the root `if P`, even when a deeper sequential arm ranks higher as a covering member. Pin identity detaches from cover rank.

## Failures

1. **Trailing-closure ifs** (SwiftUI `ForEach { if … }`) still sit inside a plain statement. Inherited from neap.
2. **Match-arm / `if let` pairing** inherited from liken. Window's `if let` is its own fork, honestly.
3. **Combined / binary diffs** are unplaced (exit 2 if that is all), not guessed.
4. **`fn` of a computed `var barColor: Color` is `Color`.** barColor and dotColor therefore share a fn name; clustering does not rely on it (complement + nearest-if). Two Color properties with unrelated predicates would still be separate unless they complement.

## Suggested mutations

- Pipe overlay-obituaries into `tenure --rev` of the pre-image pin (one walk per fork, not per arm).
- Walk trailing-closure bodies when the overlay actually deletes an if inside one.
- `--flat` to explode an obituary back into neap rows for scripts that want arms.

## Kill / keep

**Keep**, if the invert stays clustered overlay-deaths of an *unapplied* patch. Kill if a later generation reduces it to `neap | awk`, to `git apply && wane`, or to leftover-name hunting.
