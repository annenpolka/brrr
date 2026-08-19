# ford

Occupancy of a **merge is a join of parent statuses**, not a boolean sample on the merge SHA.

`held` / `roost` / `stead` probe the merge tree. A file that arrived on a topic branch becomes a **birth at the merge** on first-parent (`kizu` `CLAUDE.md` at `0ea3916`, hiding `e1098c8`). `stead --full` then compresses connected components of those booleans — still not a lattice of the two parents.

`ford` keeps stead's five statuses (**TRUE / FALSE / UNKNOWN / SHALLOW / EMPTY**; a failed probe is not FALSE) and actually joins the parents:

| flag | lattice | TRUE at a merge when |
| --- | --- | --- |
| default (`--all`) | meet `⊓` | **every** parent is TRUE (the merge *preserves*) |
| `--any` | join `⊔` | **any** parent is TRUE (the merge *introduces* via a side) |

A merge whose parents disagree is printed as a **ford** (the crossing), not compressed into a boolean birth. A later TRUE run is `preserve`/`continue` after that ford, not a birth at the next merge. `--tree` samples the merge SHA like held. `--boolean` is lossy held recovery. `--list` is `git log --reverse` order. Depth-1 clones print **SHALLOW** and do not claim birth. `--now` on a commit-less dirty tree answers the filesystem.

Order: `FALSE ⊑ SHALLOW ⊑ UNKNOWN ⊑ EMPTY ⊑ TRUE`. `ford lattice` prints the tables.

## Install / run

```bash
chmod +x ./ford
./ford --help
./ford lattice
./demo.sh
```

Python 3.9+, stdlib only, `git`. Exit `0` last sample TRUE, `1` FALSE, `3` UNKNOWN/SHALLOW/EMPTY, `2` error. TSV on a pipe, human on a tty, `--json` for asserts.

## Examples

**1. A merge whose parents disagree is not a boolean birth.**

```bash
ford exists src/app.py            # diamond HEAD is a merge: FALSE ⊓ TRUE = FALSE
ford --any exists src/app.py      # FALSE ⊔ TRUE = TRUE, origin = topic
ford --tree exists src/app.py     # held: TRUE birth at the merge
```

```
FALSE     1 commit   3042f3b
       M merge topic
       ford  FALSE ⊓ TRUE = FALSE  (does not preserve)
       parent 0286af3=FALSE  B main no occupancy
       parent 1455a54=TRUE   D still holds on topic
       tree=TRUE  snapshot has it; occupancy is the parent join, not a birth
       origin: 1455a54  D still holds on topic  (TRUE parent)
now=FALSE  tree_now=TRUE  fords=1  join=all
```

**2. `--now` on a repo with no commits sees a dirty README.**

```bash
ford --now -C empty-dirty exists README.md
```

```
TRUE      1 sample   WORKTREE
now=TRUE  walk=filesystem
```

**3. Depth-1 kizu is SHALLOW, not birth. Timeout is UNKNOWN, not FALSE.**

```bash
ford -C kizu-shallow exists CLAUDE.md
# SHALLOW   1 commit   9349dc5     (not 0ea3916, not e1098c8)

ford --timeout 0.25 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi'
# TRUE / UNKNOWN / TRUE     witnesses: (timeout)
```
