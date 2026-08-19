# mutation-34 — pin

## Primitive

A code locus is a **pin**: mint a self-contained fingerprint once, store the token, resolve it onto a later tree **without** re-supplying `path:line`. v0.4 keeps the v0.3 refuses and flips the leftover-stub overcorrection: **if the origin path still holds the implementation body, that is not a move.** Stem-split is a tie-break against leftover stubs, not against the original body copied into `src/oldstem/…`.

## Why this might not exist

Ancestor pin v0.3 (mutation-22) stopped leftover wrappers from scoring `shifted 1.000`. Destroyer then showed the file-split story now fires when the old path is *not* gone:

1. Extract-and-keep: v2 **copies** `helper_keep` to `src/calc/ops.py` and leaves `src/calc.py` byte-identical. Resolve reports `moved … ops.py` and names the identity `basename bait`.
2. Preferring same-path when `ns >= 0.5` before stem-split would hide (1) and re-open a leftover that kept a docstring neighbor.

The missing verb is still the token. The mutation is: **the origin is the locus until its body is gone.**

## How to run

From the worktree root:

```bash
chmod +x ./pin
./pin --help
./pin --selftest
./demo.sh
./pin mint --repo /path --from <old-sha> path:line
./pin resolve --repo /path --to HEAD pin1.…
./pin show pin1.…
```

Exit 0 on success. `resolve` exits 2 if you hand it a `path:line`. Missing `--from`/`--to` refs exit 2. Corrupt / truncated tokens exit 1 with no result row. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `ambiguous`. Confirmed deletions are still answers.

## The assumption that was flipped

v0.3 killed: "a leftover re-export at the old path is identity."

This mutation kills the follow-on lie: "a stem-split copy is a move even when the minted path still has the body."

### Bought

- Extract-and-keep stays `same 1.000` at origin. The stem-split is an `extracted copy`, not a landing. Origin is not basename bait.
- Leftover stubs still lose to `src/calc/ops.py`, including `add()`.
- Identical dest copies emit `ambiguous`. Godfile / NFD / missing `--to` / clipped tokens / foreign repo: as v0.3.

### Lost

- A review pin on a function you then copy into a package **and leave in place** will not follow the copy. You wanted the extract; the token says the locus did not move. Mint the extract if that is the bookmark.

## Empirical transcript

### Working software (v0.4), before the improvement

`./pin selftest` → `selftest: ok`. `./demo.sh` all checks passed (leftover stub, extract-and-keep, kizu / voidtrace / tenaoshi).

```
$ PIN=$(./pin mint --repo $KEEP --from $V1 src/calc.py:4)
$ ./pin resolve --repo $KEEP --to $V2 --porcelain "$PIN"
same	-	src/calc.py:4	src/calc.py:4	1.000	skipped extracted copy src/calc/ops.py:4; basename bait src/legacy/calc.py:1

$ ./pin resolve --repo $STUB --to $STUB_V2 --porcelain "$STUBPIN"
moved	-	src/calc.py:5	src/calc/ops.py:5	0.998	path or surrounding file changed; skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1
```

Ancestor v0.3 on the keep fixture landed `moved … src/calc/ops.py:4` and called origin `basename bait`.

kizu godfile split is unchanged (old path is gone):

```
$ ./pin resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
```

### Failures that drove the first improvement

Body hold used the neighbor *ctx window*. Insert three comments between `def helper_keep():` and `return "stable helper"` at origin, copy the original to `src/calc/ops.py`: origin still has the body, resolve reports `moved … ops.py` and names origin `leftover stub`.

A leftover that kept the add() docstring still followed the extract (body_ns=0 at origin) — that is the case a `ns >= 0.5` swap would have gotten wrong. It was not the hole.

### After the improvement

Body-hold searches the **enclosing function**, not `--context` lines. Comments are not a leftover stub. A leftover that kept only the docstring still loses (implementation `return a + b` is gone).

```
$ ./pin resolve --repo $NOISY --to $NOISY_V2 --porcelain "$NOISYPIN"
same	-	src/calc.py:1	src/calc.py:1	0.680	skipped extracted copy src/calc/ops.py:1
# v0.4-ctx-window was: moved … ops.py:1  skipped leftover stub src/calc.py:1

$ ./pin resolve --repo $DOC --to $DOC_V2 --porcelain "$DOCPIN"   # add() leftover kept the docstring
moved	-	src/calc.py:1	src/calc/ops.py:1	0.998	skipped leftover stub src/calc.py:5
```

The 0.680 (not 1.000) is the comments: path+text are identity, neighbors in the ctx window are not. A 1.000 here would pretend the function did not grow.

`./demo.sh` still exits 0. New guards: `18d` docstring leftover, `18n` noisy origin.

## Dogfood targets

- Extract-and-keep git repo: origin untouched, copy at `src/calc/ops.py`, basename bait `src/legacy/calc.py`.
- Leftover stub + stem-split (v0.3 regression). Leftover that kept the add() docstring.
- Noisy extract-and-keep: origin still has `return "stable helper"` below three comments.
- Synthetic ugly repo, 1.2 MB godfile, NFD `café.py`, missing `--to`, truncated tokens, foreign helper.
- kizu `src/app.rs` split at `b4e6a5d`; voidtrace `evaluate.ts:1`; tenaoshi `KinsokuEngine.swift:12`.

## Surprises

- Scoring already gave origin 1.000 vs copies 0.999 (`same_path and ns >= 0.5`). `_pick_exact` never saw those scores: unique stem-split won first. The overcorrection was the picker, not the scorer.
- `ns` counts docstrings. That is why `ns >= 0.5` cannot be the body test: leftover add() that kept `"""Return the sum of a and b."""` scores 0.5 at origin and 1.0 at the extract.
- The ctx window is the leftover-stub *ranker*. Body-hold is a different question (is the implementation still in this function). Mixing them made comments look like a re-export.
- Noisy origin scores `same 0.680`, not 1.000: the locus did not move, the neighbors did. Voidtrace `import {` clones are still skipped paths, not leftover stubs.

## Failures

- `}`-only and blank lines still refuse to mint (`too trivial`).
- Whole-tree dest index on every resolve.
- Leftover wrapper + extract to a *renamed* package (`src/math/ops.py`) still ties with basename bait (`ambiguous`). Stem-split was the only vote; origin is a stub so body-hold does not fire.
- v1 pins (no origin) still resolve onto any repo.
- Token length ~160–450 chars.

## Suggested mutations

- File-split to a renamed package must not tie with basename bait (destroyer pin §2).
- Origin as a stable repo id, not the set of root SHAs (orphan / shallow / graft).
- `--to-dir` inside a git repo must inherit origin; missing origin / v1 fail closed unless `--any-repo`.
- Mint-target fallback on dest, or refuse to mint `SKIP_DIRS` paths. Huge dest omit with a sibling is still `deleted`.

## Kill / keep

**Keep.** The object is still the token. Unique kizu pins still land the godfile split. Leftover stubs still lose. The new refuse is the honest one: a copy is not a move while the body sits at origin. Kill only if a later mutation proves bookmarks *want* to follow the extract even when the original remains — that is a different verb (follow-the-clone), not this pin.
