# mutation-87 — hank

## Primitive

`--emit` the composed covering of review-suggestion strands as one unified diff, so `hank --emit | git apply` is the apply of the *fold*, not of N GitHub suggestion fences. Occupancy stays a verb.

## Why this might not exist

braid composes then occupies the single after-image, and stops: there is no stdout object. spar `--emit` of a COMMUTE pair is wholesale before→after **per strand** (N fences). GitHub "Commit suggestion" is one click per fence; "Add to batch" is untyped. `git apply` of two STACK fences against the origin file looks for `beta2` and misses.

The reviewer question after "they commute" / "occupy the union" is: give me the patch of *that* result. Concatenating fences is not the covering. Occupying each strand and joining rows is not emit.

Discarded: piping `braid | spar`; occupying each strand; growing plait's `line`/`time`/`topo`/`same-tree` table; a fourth cinch.

## How to run

```bash
chmod +x ./hank ./demo.sh
./hank --help
./hank --selftest
./demo.sh
./hank --emit -C fixtures/trees/commute fixtures/commute.jsonl | git apply
./hank --emit -C fixtures/trees/stack fixtures/stack.jsonl
./hank --emit fixtures/jam.jsonl
./hank --emit -C fixtures/trees/cli-orig fixtures/cli-pr7.json
gh api repos/cli/cli/pulls/7/comments | ./hank --emit -C /path/to/cli
```

Python 3.9+, stdlib. Exit 0 occupy-ok / emit-ok / empty, 1 SPLIT, 2 JAMMED, 3 error.

## Empirical transcript

### v0.1 — wholesale covering emit

`./hank --selftest` → **28 passed**. `./demo.sh` → **57 passed** with `--unidiff-zero` on STACK/cli. Forced the STACK/cli apply hole below.

Gold commute covering against `alpha/beta/gamma`:

```
$ ./hank --emit -C fixtures/trees/commute fixtures/commute.jsonl
hank  compose=PARALLEL  occupy=PENDING  emit=1  files=1
diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,3 +1,3 @@
-alpha
-beta
-gamma
+ALPHA
+beta
+GAMMA
```

One `@@`. `git apply` of that patch yields `ALPHA/beta/GAMMA`. Two GitHub fences would have been two hunks.

Same stream, no `-C`: `hank: app.py: no covering (need -C to fill COMMUTE gaps)` rc=3. Concatenation of nits is not a covering and is not emitted.

Gold jam: `hank: JAMMED; not emitting` rc=2, empty stdout.

STACK fold `beta→beta3` (inverted `created_at`):

```
@@ -2,1 +2,1 @@
-beta
+beta3
```

The patch does not mention `beta2`. Occupancy of `stack-mid` (`beta2` live) is still SUPERSEDED of the fold.

`git apply` of that 1-line zero-context hunk **fails**. `git apply --unidiff-zero` yields `alpha/beta3/gamma`. Same hole on cli/cli PR #7: covering is the 54-line span @347–400, one hunk, vanilla `git apply` fails, `--unidiff-zero` lands both `return nil` nits. File-wide after-search would have stained line 354 (`return nil, err` already there); the covering keeps locus slack.

A-only tree still emits the origin covering (`-alpha`); apply fails. Occupancy SUPERSEDED. Honest.

### v0.2 — mixed file after-image so vanilla `git apply` is the fold

Forced by the v0.1 commute/stack/cli run, not a feature list.

Wholesale zero-context hunks: STACK 1-line fold and the cli/cli 54-line covering both need `git apply --unidiff-zero`. Mixed opcodes *inside* that 54-line covering still fail vanilla `git apply` / `patch` even when the old side equals the file window (`old==window` empirically). `diff -u` of the file after splicing the covering after-image applies cleanly as two mixed hunks @344 and @397.

v0.2 `--emit` (default; `--wholesale` is v0.1) splices the covering onto `-C` and prints that file-level unified diff:

```
$ ./hank --emit -C fixtures/trees/stack fixtures/stack.jsonl
@@ -1,3 +1,3 @@
 alpha
-beta
+beta3
 gamma
# git apply → alpha/beta3/gamma   (no --unidiff-zero)

$ ./hank --emit -C fixtures/trees/cli-orig fixtures/cli-pr7.json
diff --git a/command/pr.go b/command/pr.go
@@ -344,7 +344,7 @@
@@ -397,7 +397,7 @@
# one file, two mixed hunks of the covering; git apply lands both return-nil nits
# line 354 leftover `return nil, err` survives (locus slack)
```

COMMUTE stays one hunk (` beta` as context). STACK still has no `beta2`. Distant COMMUTE sites (cli, dup-sites) may be two `@@` of **one** `diff --git` — git's mixed context of the fold, not two strand fences.

`./hank --selftest` → **28 passed**. `./demo.sh` → **60 passed, 0 failed**.

## Dogfood targets

- braid gold `fixtures/commute.jsonl` / `jam.jsonl` / `stack.jsonl` / `echo-dup-sites.jsonl` / `shift.jsonl` / `stack-subset.jsonl` (copied from hybrid-12 worktree)
- DESTROYER_PLAIT: overlap-same-after JAM, md-commute-noquote, stack-cycle
- cli/cli PR #7 harvest + `fixtures/trees/cli-orig/command/pr.go`
- sitbone/kizu: no ` ```suggestion ` fences; skipped

## Surprises

- `git apply` (no `--unidiff-zero`) wants at least one context line for a mid-file hunk. Wholesale covering of a whole tiny file applies; wholesale covering of a 1-line STACK fold or a 54-line cli span does not. Occupancy was never this object.
- Mixed opcodes *inside* the 54-line covering still fail `git apply` / `patch` even when `old==window`. The applyable object is `diff -u` of the file after splicing the covering, not a one-hunk covering dump.
- COMMUTE emit without `-C` must die, not emit `alpha|gamma → ALPHA|GAMMA`. That concatenation is not applyable against `alpha/beta/gamma`.
- A-only still emits the origin covering, not a patch from `ALPHA`. Emit is of the fold, not of whatever HEAD happens to hold.

## Failures

- v0.1 wholesale emit is not `hank --emit | git apply` for STACK or cli/cli without `--unidiff-zero`.
- SERIES covering remains the one-line fold; without `-C` the emit has no neighbors and vanilla `git apply` still wants `--unidiff-zero`.
- `--remarks` still MIXED (PARALLEL + THREAD); remarks are not after-images.
- subset fold after-image includes a trailing blank line (`""` in the insert after); `git apply` warns `new blank line at EOF` and still applies.

## Suggested mutations

- Multi-file COMMUTE as one tree-image emit.
- NFC-equivalent path keys.
- `--apply` write the covering into `-C` instead of piping.

## Kill / keep

**Keep.** The object changed: stdout is the covering of the fold. Demo commute is one mixed hunk that applies. Demo STACK is `-beta` `+beta3` with file context, not two rounds. JAM still refuses to emit. DESTROYER_PLAIT's ECHO-as-image and empty-before SPLIT are not reproduced.

Kill only if concatenating `spar --emit` fences plus `git apply --unidiff-zero` recovers the STACK fold — it does not, because the second fence looks for `beta2` in the origin file.

## What the flipped assumption bought and lost

**Bought**

- `gh api …/comments | hank --emit -C HEAD | git apply` is the interaction: compose, occupy, apply the covering.
- Partial apply still SUPERSEDED of the composed image; emit of that covering will not apply there.
- STACK emit is the series fold; leftover `beta2` is not a fence in the patch.
- JAM/SPLIT still fail closed without a fake patch.

**Lost**

- plait's apply-schedule witness table. The fold is the witness.
- spar's per-strand emit (N fences). That is the hole this mutation closes.
- Wholesale hunks are uglier than `git show`. v0.2 closed that for apply; distant COMMUTE sites are two mixed hunks of one file, not two strand fences.
