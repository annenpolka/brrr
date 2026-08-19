# hank

braid composes review-suggestion strands and occupies the **single** composed after-image. Occupancy is a fate (`PENDING` / `APPLIED` / `SUPERSEDED`). It is not a patch.

spar `--emit` of a COMMUTE pair is **N suggestion fences**. GitHub "Commit suggestion" is one click per fence. `git apply` of those fences is not the STACK fold (`beta2` is not in the origin file).

**hank `--emit`s the composed covering as one unified diff.** `hank --emit | git apply` is the apply of the *fold*, not of N fences. Occupancy stays a verb (stderr). JAM/SPLIT refuse occupy and refuse emit.

| compose | occupy | emit |
| --- | --- | --- |
| **PARALLEL** (COMMUTE) | one fate of the file covering | one hunk of that covering |
| **SERIES** (STACK) | one fate of origin→final | one hunk of that fold (`-beta` `+beta3`, not two rounds) |
| **ECHO** | one fate of the locus | one hunk (apply once) |
| **SPLIT** | rc=1, no occupy | not emitting |
| **JAMMED** | rc=2, no occupy | not emitting |

Not occupying each strand and joining rows. Not plait's apply-schedule table.

## Install / run

Python 3.9+, stdlib. `git` only for `--against REF` or to apply the emit.

```bash
chmod +x ./hank ./demo.sh
./hank --help
./hank --selftest
./demo.sh
```

Exit: `0` occupy-ok / emit-ok / empty, `1` SPLIT, `2` JAMMED, `3` error. `--report-only` forces `0`. `--json` / `--tsv` compose+occupy. `--emit` is the covering on stdout.

COMMUTE with a hole needs `-C` so the covering can fill unclaimed lines from the tree. SERIES folds without a tree; apply still needs the file.

## Examples

### 1. Two nits commute — one covering, one apply

```bash
./hank --emit -C fixtures/trees/commute fixtures/commute.jsonl | git apply
```

```
@@ -1,3 +1,3 @@
-alpha
+ALPHA
 beta
-gamma
+GAMMA
```

One file, mixed context (the unclaimed `beta` stays). Occupancy of a tree where only alice landed is still `SUPERSEDED` of that covering.

### 2. Overlap is a jam — refuse emit

```bash
./hank --emit fixtures/jam.jsonl
# rc=2  hank: JAMMED; not emitting
```

Same-span two afters are SPLIT, rc=1, also no emit. Replacement, not hunk-union.

### 3. Two review rounds — emit the fold

```bash
./hank --emit -C fixtures/trees/stack fixtures/stack.jsonl
# @@ -1,3 +1,3 @@
#  alpha
# -beta
# +beta3
#  gamma
```

The intermediate `beta2` is not in the patch. `git apply` of the fold is `beta→beta3` in one step. Two GitHub fences would look for `beta2` in the origin file and miss.

Compose: `gh api repos/cli/cli/pulls/7/comments | ./hank --emit -C /path/to/cli | git apply`
