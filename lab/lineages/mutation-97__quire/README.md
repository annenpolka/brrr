# quire

hank `--emit`s the composed covering of review-suggestion strands as one unified diff (`hank --emit | git apply` is the fold). Occupancy stays a verb. Hole: two files that commute are **DISJOINT** plus two PARALLEL singletons. Occupying each file covering and concatenating diffs is joining rows. Without `-C`, that emit is two strand fences, not a tree.

**quire emits one tree-image covering for COMMUTE across files** (unanimous fate or labelled MIXED). JAM still refuses. STACK fold stays `-beta` `+beta3` with file context. Locus slack is load-bearing. ECHO is a locus, not image-identity.

Not occupying each strand and joining rows. Not a fourth cinch.

| compose | occupy | emit |
| --- | --- | --- |
| **PARALLEL** (COMMUTE, including disjoint files) | one fate of the tree-image, or **MIXED** if files disagree | one patch of every claimed path |
| **SERIES** (STACK) | one fate of origin→final | one hunk of that fold (`-beta` `+beta3`, not two rounds) |
| **ECHO** | one fate of the locus | one hunk (apply once) |
| **SPLIT** | rc=1, no occupy | not emitting |
| **JAMMED** | rc=2, no occupy | not emitting (a jam on one file refuses the tree) |

## Install / run

Python 3.9+, stdlib. `git` only for `--against REF` or to apply the emit.

```bash
chmod +x ./quire ./demo.sh
./quire --help
./quire --selftest
./demo.sh
```

Exit: `0` occupy-ok / emit-ok / empty, `1` SPLIT, `2` JAMMED, `3` error. `--report-only` forces `0`. `--json` / `--tsv` compose+occupy. `--emit` is the tree-image on stdout; occupancy stays on stderr.

Same-file COMMUTE with a hole needs `-C` so the covering can fill unclaimed lines. Multi-file COMMUTE is a tree-image: `-C` is the canvas. Without a tree, or with a claimed path missing from it, emit is empty (rc=3) — two strand fences are not the image.

## Examples

### 1. Two files commute — one tree-image, one apply

```bash
./quire --emit -C fixtures/trees/two-file fixtures/two-file.jsonl | git apply
```

```
quire  compose=PARALLEL  occupy=PENDING  emit=2  files=2  image=tree
diff --git a/app.py b/app.py
@@ -1,2 +1,2 @@
-alpha
+ALPHA
 beta
diff --git a/util.py b/util.py
@@ -1,2 +1,2 @@
-gamma
+GAMMA
 delta
```

One patch, both paths. Occupancy of a tree where only alice landed is **MIXED** of that image, not APPLIED+PENDING of two rows. `quire --emit fixtures/two-file.jsonl` (no `-C`) is rc=3, empty stdout.

### 2. Overlap is a jam — refuse the tree

```bash
./quire --emit fixtures/jam.jsonl
# rc=2  quire: JAMMED; not emitting
./quire --emit -C fixtures/trees/two-file fixtures/two-file-jam.jsonl
# rc=2  jam on app.py refuses util.py too
```

Same-span two afters are SPLIT, rc=1, also no emit. Replacement, not hunk-union.

### 3. Two review rounds — emit the fold, not two fences

```bash
./quire --emit -C fixtures/trees/stack fixtures/stack.jsonl
# @@ -1,3 +1,3 @@
#  alpha
# -beta
# +beta3
#  gamma
```

The intermediate `beta2` is not in the patch. `git apply` of the fold is `beta→beta3` in one step.

Compose: `gh api repos/cli/cli/pulls/7/comments | ./quire --emit -C /path/to/cli | git apply`
