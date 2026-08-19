# hydra

Occupancy of a merge is the **n-parent lattice** (how many parents held TRUE), not a folded meet and not a boolean sample on the merge SHA.

`ford` and `weir` fold an octopus into inf/sup. **1-of-3 and 2-of-3 are the same meet** (FALSE as soon as any parent is FALSE) and the same join (TRUE as soon as any parent is TRUE). Origin is the first TRUE parent; the other introducing sides are dropped. Majority is a different object — hydra does not add it.

`hydra`: occupancy is **k-of-n**, from parent *occupancy* (weir), not parent trees (ford). Recursive occupancy so first-parent TRUE does not start at a merge whose parents already held (kizu `21ae074` is occupancy `1-of-2`, trees `2-of-2` — ford's T⊓T preserve). Refuse birth at a merge. `--boolean` is a labelled lie, or a refuse if it would downcast UNKNOWN/SHALLOW/EMPTY. `--follow` is berth.

| flag | what it is | TRUE at a merge when |
| --- | --- | --- |
| default | k-of-n occupancy; meet `⊓` is a **labelled fold** | k = n (every parent occupancy TRUE) |
| `--any` | k-of-n occupancy; join `⊔` is a labelled fold | k ≥ 1 (any parent occupancy TRUE) |
| `--tree` | sample the merge SHA (held) | the snapshot has it |
| `--boolean` | labelled lie / refuse | held recovery, not a lattice downcast |

Order: `FALSE ⊑ SHALLOW ⊑ UNKNOWN ⊑ EMPTY ⊑ TRUE`. `hydra lattice` prints the tables and the arity note.

## Install / run

```bash
chmod +x ./hydra
./hydra --help
./hydra lattice
./demo.sh
```

Python 3.9+, stdlib only, `git`. Exit `0` last sample TRUE, `1` FALSE, `3` UNKNOWN/SHALLOW/EMPTY, `2` error. TSV on a pipe, human on a tty, `--json` for asserts.

## Examples

**1. Octopus 1-of-3 is not 2-of-3. The folded meet is the same FALSE; hydra is not.**

```bash
hydra exists src/app.py            # 1-of-3 vs 2-of-3; origins list every TRUE parent
hydra --any exists src/app.py      # labelled join fold; still 1-of-3 ≠ 2-of-3
hydra --tree exists src/app.py     # held: TRUE birth at the merge
```

```
FALSE     1 commit   M octopus t1 t2
       hydra  1-of-3  FALSE ⊓ TRUE ⊓ FALSE = FALSE  (n-parent lattice, not a folded meet)
       parent A=FALSE  tree
       parent T1=TRUE  tree
       parent T2=FALSE tree
       tree=TRUE  snapshot has it; occupancy is the n-parent lattice, not a birth
       origin: T1  (TRUE parent; 1-of-3)
       refuse birth: a parent already held TRUE
now=FALSE  held=1-of-3

FALSE     1 commit   M octopus t1 t2
       hydra  2-of-3  FALSE ⊓ TRUE ⊓ TRUE = FALSE  (n-parent lattice, not a folded meet)
       origins: 2-of-3  T1; T2
now=FALSE  held=2-of-3
```

**2. kizu `CLAUDE.md`: refuse birth at `0ea3916`; recursive occupancy at `21ae074` is 1-of-2, not T⊓T.**

```bash
hydra -C kizu exists CLAUDE.md
```

```
FALSE     1 commit    0ea3916
       hydra  1-of-2  FALSE ⊓ TRUE = FALSE
       refuse birth: a parent already held TRUE
       origin: e1098c8
FALSE     1 commit    21ae074
       hydra  1-of-2  FALSE ⊓ TRUE = FALSE  (recursive)
       trees 2-of-2  occupancy 1-of-2  (ford would fold the trees)
       refuse birth: a parent already held TRUE
TRUE     17 commits   d9b9645..9349dc5
       continue after hydra 21ae074; not birth
```

**3. `--boolean` that downcasts UNKNOWN is a refuse. T/F downcast is a labelled lie.**

```bash
hydra --follow exists CLAUDE.md
# hydra: error: --follow is berth, not this object

hydra --boolean --timeout 0.2 exec -- sleep 8
# hydra: --boolean would downcast UNKNOWN to FALSE; that is a labelled lie. refuse.
```
