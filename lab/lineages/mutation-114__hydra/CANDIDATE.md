# mutation-114 — hydra

## Primitive

Occupancy of a merge is the n-parent lattice (how many parents held TRUE), not a folded meet, and the join inputs are parent occupancy when a parent is itself a merge.

## Why this might not exist

ford joins parent *trees*. weir peels that into recursive occupancy so kizu `21ae074` is `FALSE ⊓ TRUE`, not T⊓T preserve. DESTROYER_FORD then showed the remaining hole is **arity**, not recursion: octopus **1-of-3 and 2-of-3 are the same meet** (`FALSE` as soon as any parent is FALSE), the same `--any` join, the same exit, the same `never_held`. Origin is the first TRUE parent; the other introducing sides are dropped. Majority does not exist, and adding it quietly would be a different object.

The missing verb: at an n-parent commit, occupancy **is** k-of-n. Display the count. List every TRUE parent. Keep weir's recursive occupancy so first-parent TRUE does not start at a merge whose parents already held. `--boolean` stays a labelled lie, or a refuse when it would downcast UNKNOWN/SHALLOW/EMPTY.

## How to run

```bash
chmod +x ./hydra
./hydra --help
./hydra lattice
./demo.sh
./hydra --now -C /tmp/empty-dirty exists README.md
./hydra -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./hydra --any -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./hydra --boolean -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./hydra --full -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone exists Sources/SitboneUI/FocusRiverView.swift
./hydra -C /Users/annenpolka/ghq/github.com/annenpolka/skills grep preact-zero-mock
```

Python 3.9+, stdlib only, git. TSV on a pipe, human on a tty, `--json` for asserts. Exit 0 iff last sample is TRUE, 1 if FALSE, 3 if UNKNOWN/SHALLOW/EMPTY, 2 error.

## Lattice

Chain: `FALSE ⊑ SHALLOW ⊑ UNKNOWN ⊑ EMPTY ⊑ TRUE`.

Occupancy at a merge is **k-of-n** (TRUE parent occupancies). Meet `⊓` (`--all`) and join `⊔` (`--any`) remain labelled folds of that count — `now=` still uses them — but 1-of-3 and 2-of-3 are different hydras even when both folds are FALSE / both folds are TRUE. Majority is not this object.

Join inputs are parent **occupancy** when the parent is a merge (weir), parent **tree** otherwise. kizu `21ae074` is occupancy `1-of-2` and trees `2-of-2`. That is the tree-join lie as arity.

## Empirical transcript

### Before the improvement

v1 already had k-of-n, all TRUE origins, recursive occupancy, refuse-birth, `--boolean` refuse on UNKNOWN. Octopus 1-of-3 ≠ 2-of-3 (`held=1-of-3` vs `held=2-of-3`; origins 1 vs 2). kizu `0ea3916` was `1-of-2` with refuse birth; `21ae074` was occupancy `1-of-2` / trees `2-of-2` with refuse birth.

Forced by kizu, not polish: k-of-n lived on every merge probe, including T⊓T preserve. Compress then refused to join a non-merge TRUE (`0-of-0`) with a preserve merge (`2-of-2`). `annotate_continuations` saw `refused_birth` on those T⊓T runs and renamed them hydra. First-parent TRUE **split**:

```
TRUE      1 commit   d9b9645          continue after hydra 21ae074
TRUE      4 commits  37fd207..9c6e090 hydra  2-of-2   (PR #7–#10, T⊓T)
TRUE      1 commit   bed252a
TRUE      4 commits  55153fd..1519134 hydra  2-of-2
…
now=TRUE  held=2-of-2  true=17/24  eras=13  hydras=6
```

The 17-commit continue weir earned was gone. `held=2-of-2` on the summary was the last preserve merge, not occupancy of HEAD. Same class of lie as printing T⊓T as a crossing.

### After the improvement

k-of-n is the identity of a *crossing* (parents disagree, recursive occupancy≠tree, or tree≠join). Preserve (`k=n`, occupancy TRUE) compresses. `refused_birth` does not promote a run into a hydra unless it already is one. `held=` on the summary is occupancy of the last era, so a non-merge HEAD does not inherit a crossing's k-of-n.

```
$ ./hydra -C kizu exists CLAUDE.md
FALSE     1 commit    cbaf29a
FALSE     1 commit    0ea3916
       hydra  1-of-2  FALSE ⊓ TRUE = FALSE  (does not preserve)
       origin: e1098c8
       refuse birth: a parent already held TRUE
FALSE     1 commit    21ae074
       hydra  1-of-2  FALSE ⊓ TRUE = FALSE  (recursive)
       trees 2-of-2  occupancy 1-of-2  (ford would fold the trees)
       refuse birth: a parent already held TRUE
FALSE     4 commits   ca0577a..ad6de10
       inherited hydra 1-of-2 21ae074
TRUE     17 commits   d9b9645..9349dc5
       continue after hydra 21ae074; not birth
       origin: e1098c8
now=TRUE  true=17/24  eras=5  hydras=6  walk=first-parent  join=all  tree_now=TRUE
```

Octopus (synthetic, 3-parent `git merge t1 t2`):

```
$ ./hydra -C octopus-1of3 exists src/app.py
       hydra  1-of-3  FALSE ⊓ TRUE ⊓ FALSE = FALSE  (n-parent lattice, not a folded meet)
       origin: T1  (TRUE parent; 1-of-3)
       refuse birth
now=FALSE  held=1-of-3

$ ./hydra -C octopus-2of3 exists src/app.py
       hydra  2-of-3  FALSE ⊓ TRUE ⊓ TRUE = FALSE
       origins: 2-of-3  T1; T2
       refuse birth
now=FALSE  held=2-of-3
```

`--any` still TRUE for both (join fold) and still `1-of-3 ≠ 2-of-3`. 3-of-3 (every parent already held) compresses; `hydras=0`. `--boolean` on kizu recovers held's birth at `0ea3916` and prints `boolean_lie`. Depth-1 is SHALLOW. `./demo.sh` — 149 assertions, exit 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| synthetic octopus 1-of-3 / 2-of-3 | folded meet is the same FALSE; hydra `held` and origins differ; refuse birth |
| synthetic octopus 3-of-3 | k=n preserve, not a hydra |
| synthetic diamond | 1-of-2, not birth; `--any` still 1-of-2; `--tree`/`--boolean` recover held's FT |
| synthetic merge-of-merges | M2 occupancy 1-of-2, trees 2-of-2, parent M1 source=occupancy, refuse birth |
| merge-added file | 0-of-2, tree=TRUE, reason=tree |
| timeout parent | meet(T,U)=U; `--boolean` refused |
| `--follow` | refused: berth |
| kizu `exists CLAUDE.md` | refuse birth at `0ea3916` and `21ae074`; occupancy 1-of-2 at PR #2; trees 2-of-2; origin `e1098c8`; TRUE starts at `d9b9645` |
| sitbone `FocusRiverView.swift` | first-parent never; `--full` island 11 |
| skills `grep preact-zero-mock` | still TRUE at HEAD |

## Surprises

- 2-of-3 has two introducing sides. Printing both origins is the arity; keeping `origin` (singular) as the deepest TRUE still lets continue footnotes name `e1098c8` on kizu.
- Recursive occupancy at `21ae074` is the same 1-of-2 *count* as `0ea3916`, distinguished by `trees 2-of-2` and `source=occupancy`. Arity without recursion would have called PR #2 a 2-of-2 preserve.
- Putting k-of-n on preserve merges looked honest and destroyed the TRUE continue. The count is a crossing identity, not a label for every merge.

## Failures

1. **`--tree` / `--boolean` reintroduce the merge-birth lie** by design. `--boolean` is a labelled lie when all samples are T/F; UNKNOWN is a refuse.
2. **Rename is still path death.** `--follow` is berth, not this object.
3. **`now=` is still the folded meet/join.** 1-of-3 and 2-of-3 both `now=FALSE` under `--all` and both `now=TRUE` under `--any`. The object that differs is `held`. Majority is still not occupancy.
4. **First-parent TRUE still starts at the first non-merge** (`d9b9645`), not at topic `e1098c8` (off the walk) and not at `21ae074` (occupancy FALSE).
5. **`never_held` at an octopus HEAD whose tree has the file** is still true on first-parent (TRUE never starts on the walk). `tree_now` and `held=k-of-n` are the exits. Occupancy-never is not path-never.

## Suggested mutations

- A `--majority` object: TRUE when k > n/2. Different occupancy. Do not fold it into hydra.
- Pipe `hydra --json` into roost to split holders per introducing origin on a 2-of-3.
- `--unfold` to reprint inherited hydras as the nested lattice.
- Refuse `never_held` when k>0 (a parent held): occupancy-never is not path-never.

## Flipped assumption: bought and lost

ford/weir assumed **n-parent occupancy is the inf/sup of parent statuses**.

**Bought**

- 1-of-3 ≠ 2-of-3. Origins list every TRUE parent.
- Recursive occupancy at kizu `21ae074` is 1-of-2, trees 2-of-2. Refuse birth. TRUE continue starts at `d9b9645`.
- Meet/join remain labelled folds. Majority is not smuggled in.

**Lost**

- `now=` no longer distinguishes octopus introductions; `held=` does.
- First-parent TRUE no longer spans `21ae074`. Occupancy there is FALSE; the snapshot is TRUE (`tree=`).

## Kill / keep

**Keep.** The occupancy verb was already real. This mutation is the n-parent lattice DESTROYER_FORD named after weir shipped the recursive peel. The v1→v2 change was forced by kizu: k-of-n on preserve merges re-split the 17-commit continue into T⊓T hydras. Crossing identity, not a sticker on every merge. Not polish.
