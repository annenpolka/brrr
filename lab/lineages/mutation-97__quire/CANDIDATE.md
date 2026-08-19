# mutation-97 — quire

## Primitive

Emit **one tree-image** covering for COMMUTE across files (unanimous fate or labelled MIXED), so `quire --emit | git apply` is the apply of the *tree fold*, not of N file rows joined. JAM still refuses. STACK fold stays `-beta` `+beta3` with file context. Locus slack is load-bearing. ECHO is a locus, not image-identity.

## Why this might not exist

hank `--emit`s the composed covering of suggestion strands as one unified diff. Occupancy stays a verb. Hole: two nits on `app.py` and `util.py` are **DISJOINT** (hidden) plus two PARALLEL singletons. `hank --emit` concatenates the file coverings; without `-C` that is two 1-line strand fences. Occupying each file and joining rows is not a tree-image.

spar `--emit` is still N GitHub fences. braid occupies one composed after-image *per path*. GitHub "Add to batch" is untyped. `git apply` of two STACK fences against the origin looks for `beta2` and misses; `git apply` of a missing-path sibling can land the file that was present and fail the one that was not.

Discarded: piping `hank | git apply` of whatever files covered; occupying each strand and joining rows as emit; a fourth cinch.

## How to run

```bash
chmod +x ./quire ./demo.sh
./quire --help
./quire --selftest
./demo.sh
./quire --emit -C fixtures/trees/two-file fixtures/two-file.jsonl | git apply
./quire --emit -C fixtures/trees/stack fixtures/stack.jsonl
./quire --emit fixtures/jam.jsonl
./quire --emit -C fixtures/trees/cli-orig fixtures/cli-pr7.json
gh api repos/cli/cli/pulls/7/comments | ./quire --emit -C /path/to/cli | git apply
```

Python 3.9+, stdlib. Exit 0 occupy-ok / emit-ok / empty, 1 SPLIT, 2 JAMMED, 3 error.

## Empirical transcript

### v0.1 — cross-file COMMUTE is one tree-image patch

`./quire --selftest` → **31 passed**. `./demo.sh` → **90 passed, 0 failed**.

Gold two-file against `alpha/beta` × `gamma/delta`:

```
$ ./quire -C fixtures/trees/two-file fixtures/two-file.jsonl
quire  n=2  files=2  compose=PARALLEL  occupy=PENDING  image=tree
  COMMUTE  app.py × util.py  #alice@1  #bob@1  disjoint files
  PARALLEL app.py,util.py  #alice,#bob  tree-image; compose in any order
# rc=0
```

hank on the same stream: `pairs []` (DISJOINT hidden), two PARALLEL singletons, no tree.

```
$ ./quire --emit -C fixtures/trees/two-file fixtures/two-file.jsonl
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
# git apply → ALPHA/beta and GAMMA/delta
```

One patch, both paths. A-only tree (`ALPHA/beta` × `gamma/delta`) is `occupy=MIXED` (`app.py=APPLIED`, `util.py=PENDING`), not two occupy rows joined as the object. JAM on `app.py` plus a commuting nit on `util.py`: `quire: JAMMED; not emitting` rc=2, empty stdout.

STACK fold against hank's `fixtures/trees/stack`: `-beta` `+beta3` with `alpha`/`gamma` context; no `beta2`. cli/cli PR #7: one file, two mixed hunks; line 354 leftover `return nil, err` survives (locus slack). Dup-sites: same `return 0→return 1` on line 1 and line 10 is COMMUTE (two loci), not apply-once ECHO.

Forced the emit hole below.

### v0.2 — a partial tree is not a tree-image

Forced by the v0.1 two-file run, not a feature list.

v0.1 without `-C` still emitted two 1-line strand fences (`-alpha`/`+ALPHA` and `-gamma`/`+GAMMA`), `occupy=SUPERSEDED` of missing files, rc=0. That concatenation is not applyable against `alpha/beta` × `gamma/delta` (vanilla `git apply` wants context). A tree missing `util.py` still emitted `app.py` (which would apply) plus a fake `util.py` hunk — occupying each file and joining the row that worked.

v0.2 `--emit` of a multi-file COMMUTE is all-or-nothing against `-C`:

```
$ ./quire --emit fixtures/two-file.jsonl
quire: app.py: no tree-image (need -C to cover COMMUTE across files)
quire: util.py: no tree-image (need -C to cover COMMUTE across files)
# rc=3  empty stdout

$ ./quire --emit -C trees/only-app.py fixtures/two-file.jsonl
quire: util.py: no tree-image (need -C to cover COMMUTE across files)
# rc=3  empty stdout  (app.py is not emitted alone)
```

MIXED occupy (both files present, one already applied) still emits the origin covering of the tree; `git apply` fails atomically; `util.py` stays `gamma`. Honest, same class as hank a-only.

`./quire --selftest` → **33 passed**. `./demo.sh` → **97 passed, 0 failed**.

## Dogfood targets

- hank worktree (WORKTREE.txt): `fixtures/commute.jsonl`, `stack.jsonl`, `jam.jsonl` + trees
- braid worktree (WORKTREE.txt): `fixtures/echo-dup-sites.jsonl` + `trees/dup-sites`
- DESTROYER_PLAIT: overlap-same-after JAM, md-commute-noquote, stack-cycle, echo-dup-sites (ECHO is locus)
- cli/cli PR #7 harvest + `fixtures/trees/cli-orig/command/pr.go`
- New: `fixtures/two-file.jsonl` / `two-file-jam.jsonl` + `trees/two-file`, `trees/two-file-a-only`

## Surprises

- hank with `-C` already concatenated two file diffs that `git apply` lands. The hole was the algebra (DISJOINT, two singletons) and the emit without a tree / with a missing path — joining the files that covered. The tree-image is the refuse, not a prettier `diff --git` count.
- Across files, partial apply is **MIXED**, not SUPERSEDED of a union. Within one file, alice-only of a commuting pair is SUPERSEDED of the covering (the gap is one region). Independent paths can land separately; labelling that SUPERSEDED would lie about `app.py` already holding `ALPHA`.
- `git apply` of a two-file origin covering against an a-only tree fails on `app.py` and leaves `util.py` untouched (atomic enough here). The lie to avoid is emitting only `util.py` because splice of `app.py` failed.
- Locus slack is still load-bearing on cli/cli #333030758: file-wide after-search would stain line 354.

## Failures

- `--remarks` on cli-pr7 is still MIXED (PARALLEL + THREAD). Remarks are not after-images; emit of the suggestion covering stays.
- SERIES covering remains the one-line fold; without `-C` vanilla `git apply` still wants `--unidiff-zero`. Pad is emit-only when the tree is present.
- subset fold after-image includes a trailing blank line; `git apply` warns `new blank line at EOF` and still applies.
- NFC-equivalent path keys: ingest NFC-normalizes, so the destroyer's APFS inode pair is not re-opened here as two files. A tree that stores the other normalization would still miss.

## Suggested mutations

- Multi-file STACK (suggestion A creates the path B edits).
- `--apply` write the tree-image into `-C` instead of piping.
- MIXED compose (SERIES on one path, PARALLEL on another) as an explicit schedule, not only a label.

## Kill / keep

**Keep.** The object changed: stdout is the tree-image of the fold. Demo two-file COMMUTE is one applyable patch. Demo a-only is MIXED of that image. JAM still refuses. Without `-C`, two strand fences are not emitted. DESTROYER_PLAIT's ECHO-as-image and empty-before SPLIT are not reproduced. STACK fold is still `-beta` `+beta3` with file context.

Kill only if concatenating hank's per-file emit plus `git apply` recovers the missing-path refuse — it does not, because hank emits `app.py` when `util.py` is absent.

## What the flipped assumption bought and lost

**Bought**

- `gh api …/comments | quire --emit -C HEAD | git apply` is the interaction across files: compose, occupy the tree, apply one patch.
- Cross-file COMMUTE is visible (not hidden DISJOINT).
- Partial apply of one path is MIXED of the tree-image.
- A missing path refuses the whole emit.
- JAM/SPLIT still fail closed without a fake patch.
- Locus-aware ECHO and STACK fold survive.

**Lost**

- hank's "every file that covered is in the patch" (partial tree emit). That was joining rows.
- plait's apply-schedule witness table. The fold is the witness.
- spar's per-strand emit (N fences).
