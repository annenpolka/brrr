# mutation-39 — dreg

## Primitive

Emit the SUPERSEDED occupancy of a patch stream as an applyable patch (the dregs). Occupancy is not only a report.

## Why this might not exist

sate (candidate-34) classifies how a tree occupies each hunk: APPLIED / PENDING / MIXED / DUPLEX / SUPERSEDED. lodge (hybrid-08) occupies mixed git+review streams with the same vocabulary and fuses equal cores into `via=both`. Both stop at the report.

The daily next step is always *give me the hunks that HEAD no longer occupies so I can see what died*. Concatenating `sate --json` with `git format-patch` is two tools and the wrong object (the commit, not the unoccupied cores). GitHub outdated is line-identity. `git apply --check` remains a boolean lie this tool does not wrap.

Flip: occupy, then stdout of `--pick SUPERSEDED` (default) **is** a unified diff of those cores. `--pick PENDING` is the leftover apply. Sandwich: against C, SUPERSEDED of `C^..C` is empty; against a later rewrite, the old cores come out as a patch.

## How to run

From the worktree root:

```bash
chmod +x ./dreg ./demo.sh
./dreg --help
./dreg --selftest
./demo.sh
./dreg --git HEAD --against HEAD
./dreg --git 88362116 -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --against HEAD
./dreg --log 8 -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --stat
./dreg --git HEAD --against HEAD^ --pick PENDING
```

Python 3.10+, stdlib, git. Exit 0 empty pick, 1 emitted a patch, 2 `--report` split, 3 error. `--quiet` is patch-only on stdout; the occupancy legend is stderr.

## Empirical transcript

### v0.1 (occupy + emit cores)

`./dreg --selftest` 12 passed. Occupancy kernel copied from sate v2 including the prefix rule (pure addition is APPLIED, not DUPLEX). Emit reconstructed the picked hunks as a unified diff with the fate in the `@@` trailer.

kizu `88362116` (release: v0.6.0) vs HEAD:

```
* SUPERSEDED  Cargo.toml  #1  neither
  PENDING     Cargo.lock  #1  core-minus
@@ -1 +1 @@ SUPERSEDED 88362116
-version = "0.5.1"
+version = "0.6.0"
```

Gold content was right (dead 0.6.0 core, not live 0.7.0; Cargo.lock not in the SUPERSEDED pick). `git apply` of that patch onto `88362116^` **failed**: zero-context hunks need `git apply --unidiff-zero`. The `@@ -1` locus was the hunk start (`[package]`), not the version line.

voidtrace/tenaoshi/sitbone/kizu: SUPERSEDED of `C` vs `C` empty (exit 0). voidtrace HEAD has 2 true DUPLEX modify copies (`exact-both`, not prefix-addition). Prefix rule held.

### v0.2 (one improvement, forced by the gold apply)

Two dogfood findings, one emit fix:

1. **Core coordinates.** Walk original tagged lines; `@@` starts at the first minus/plus, not at the hunk header. The version bump is `@@ -3 +3`, not `@@ -1 +1`.
2. **One original context line.** Default SUPERSEDED emit keeps one adjacent context line from the original hunk (`@@ -2,3 +2,3` with `name = "kizu"` / `edition = "2024"`). Vanilla `git apply` onto the preimage succeeds. `--core` is the 0-context form.

After v0.2: `./dreg --selftest` **13 passed**. `./demo.sh` **48 passed, 0 failed**. kizu v0.6.0 dreg applies onto a tree holding `Cargo.toml` from `88362116^` and lands `version = "0.6.0"`. Against HEAD it stays SUPERSEDED (does not splice 0.7.0).

`--stat` exit is patch-mode (0 empty / 1 has dregs), not sate's occupancy-split of the whole log.

## Dogfood targets

- `./dreg --selftest` (13): exact fates, prefix-addition not DUPLEX, sandwich empty dregs, rewrite cores come out, leftover apply, core `@@` at first change, Japanese path with spaces.
- `./demo.sh` fixtures: sandwich, leftover apply, version ratchet, `--log --stat`, stdin, four-fate pick.
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — gold `88362116` Cargo.toml SUPERSEDED (now 0.7.0); `--log 8` six dregs; PENDING leftover is Cargo.lock.
- sitbone / voidtrace / tenaoshi — sandwich SUPERSEDED of HEAD vs HEAD empty. voidtrace DUPLEX=2 is `exact-both` copies in `evaluate.ts` / `scenario-domain.ts`, not sate v1 addition-prefix.

## Surprises

- The occupancy sandwich for *dregs* is stronger than sate's: SUPERSEDED of C vs C is empty even when the commit is DUPLEX (voidtrace). DUPLEX is occupancy of both images, not of neither.
- kizu Cargo.lock of v0.6.0 is PENDING via `core-minus` because `version = "0.5.1"` still lives on *other* packages. `--pick PENDING` emits that hunk. `git apply --check` against HEAD fails. Occupancy of a generic line is not leftover apply. dreg does not wrap the boolean.
- `--log` dregs include whole files that were created then rewritten (`src/hook/tests.rs` +583, sitbone `FocusTransitionReasonTests.swift` +207). That is occupancy: the after-image of the create no longer occupies HEAD. Not `git log --diff-filter=A`.
- Fate in the `@@` trailer (`@@ -2,3 +2,3 @@ SUPERSEDED 88362116`) survives piping and is ignored by `git apply`. Provenance without becoming format-patch.

## Failures

- Binary patches SKIP/BINARY; nothing to emit.
- Combined merge diffs are not parsed; `--log` is `--no-merges`.
- Generic change lines (`version = "0.5.1"` in a lockfile) can PENDING a hunk whose @@ window no longer matches. The leftover patch is occupancy, not a promised apply.
- 0-context `--core` still needs `git apply --unidiff-zero` (or `patch -p1`). Default margin=1 is the applyable form.
- `--log` concatenation is one stream of independent era-hunks. Applying the whole stream against HEAD will fail. Each dreg applies onto *its* preimage.

## Suggested mutations

- MIXED as a split: emit only the plus/minus lines the tree still lacks (finish-the-apply dreg).
- Retarget PENDING exact-before hunks at `near_line` in the live tree.
- Pair `--log` creates that later appear as deletes (the file moved; lodge's path map).
- `--pick APPLIED` of `C^..C` vs C as the "what still holds" dual of SUPERSEDED.

## Kill / keep

**Keep.** The object changed. sate's `--log` v0.6.0 line is a report (`SUPERSEDED=1`). dreg's stdout on that commit is the Cargo.toml version core, applyable onto the preimage, empty against C, and not `git format-patch 88362116`. Prefix rule did not regress: voidtrace/tenaoshi sandwich SUPERSEDED at HEAD is empty; voidtrace DUPLEX is real copies.

Kill only if a later generation proves that `sate --json --only SUPERSEDED` plus reconstructing hunks from `git show` is the same object — it is not, because occupancy already dropped the PENDING lockfile hunk and the live 0.7.0 image, and the emit recomputes @@ from the change-core rather than from the original window.

## What the flipped assumption bought and lost

**Bought**

- `dreg --log 8` is the interaction: the dregs as a patch, not a table.
- Sandwich for SUPERSEDED: empty against C, old cores against a rewrite.
- `--pick PENDING` leftover apply is the same verb.
- Fate trailer in the hunk; one vocabulary; no format-patch envelope.

**Lost**

- lodge's mixed review stream / `via=both` (pipe the patch in; suggestions are a later ingest).
- A promised `git apply` against HEAD of SUPERSEDED cores (the world moved on; that is the point).
- sate's `--suggest` JSONL (same object, not this mutation's flip).
