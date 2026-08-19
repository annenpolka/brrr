# weir

Occupancy of a **merge-of-merges is a recursive join of parent occupancy**, not a parent-tree join and not a boolean sample on the merge SHA.

`ford` joins parent *trees*. A merge-parent that is itself a merge then contributes its snapshot (`TRUE` at kizu `0ea3916`) into the next merge (`21ae074`), so `T⊓T` looks like preserve and first-parent TRUE starts at PR #2. Occupancy of the introducing weir never flowed.

`weir`: a merge-parent that is itself a merge contributes its **occupancy lattice**, not its tree. Refuse to call birth at a merge whose parents already held TRUE. Later same-origin weirs compress as `inherited` (kizu PR #3–#6 after `21ae074`). `--follow` is berth, not this object. `--boolean` that would downcast UNKNOWN/SHALLOW/EMPTY is a refuse; T/F downcast is a labelled lie.

| flag | lattice | TRUE at a merge when |
| --- | --- | --- |
| default (`--all`) | meet `⊓` | **every** parent *occupancy* is TRUE (the merge *preserves*) |
| `--any` | join `⊔` | **any** parent occupancy is TRUE (the merge *introduces* via a side) |

Order: `FALSE ⊑ SHALLOW ⊑ UNKNOWN ⊑ EMPTY ⊑ TRUE`. `weir lattice` prints the tables.

## Install / run

```bash
chmod +x ./weir
./weir --help
./weir lattice
./demo.sh
```

Python 3.9+, stdlib only, `git`. Exit `0` last sample TRUE, `1` FALSE, `3` UNKNOWN/SHALLOW/EMPTY, `2` error. TSV on a pipe, human on a tty, `--json` for asserts.

## Examples

**1. A merge-of-merges is not T⊓T preserve. The inner merge contributes occupancy.**

```bash
weir exists src/app.py            # M2: occupancy(M1)=FALSE ⊓ TRUE = FALSE
weir --any exists src/app.py      # FALSE ⊔ TRUE = TRUE, origin still the topic birth
weir --tree exists src/app.py     # held: TRUE birth at the merge
```

```
FALSE     1 commit   M2
       weir  FALSE ⊓ TRUE = FALSE  (recursive: merge-parent contributes occupancy, not tree)
       parent M1=FALSE  occupancy  FALSE ⊓ TRUE = FALSE  (tree=TRUE)
              parent B=FALSE  tree
              parent D=TRUE   tree
       parent E=TRUE   tree
       tree=TRUE  snapshot has it; occupancy is the recursive join, not a birth
       origin: D
       refuse birth: a parent already held TRUE
```

**2. `--now` on a repo with no commits sees a dirty README.**

```bash
weir --now -C empty-dirty exists README.md
```

```
TRUE      1 sample   WORKTREE
now=TRUE  walk=filesystem
```

**3. `--follow` is berth. `--boolean` that downcasts UNKNOWN is a refuse.**

```bash
weir --follow exists CLAUDE.md
# weir: error: --follow is berth, not this object

weir --boolean --timeout 0.2 exec -- sleep 8
# weir: --boolean would downcast UNKNOWN to FALSE; that is a labelled lie. refuse.
```
