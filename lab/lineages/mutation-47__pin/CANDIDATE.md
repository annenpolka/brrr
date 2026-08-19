# mutation-47 — pin

## Primitive

A code locus is a **pin**: mint a self-contained fingerprint once, store the token, resolve it onto a later tree **without** re-supplying `path:line`. v0.5 keeps the v0.4 refuses (origin body is identity, leftover stubs are not) and flips the stem-split-only vote: **when origin is a stub, prefer the extracted body over same-basename copies even if the new path does not share the old stem.**

## Why this might not exist

Ancestor pin v0.4 (mutation-34) stopped extract-and-keep from scoring `moved` onto `src/calc/ops.py`. Destroyer then showed leftover-stub landing still needs `is_stem_split`:

1. Leftover wrapper at `src/calc.py`, body at `src/math/ops.py`, clone at `src/legacy/calc.py` → `ambiguous`. Neighbors are equal. Stem-split was the only vote; origin is a stub so body-hold does not fire.
2. Preferring same-basename when origin is gone would hide a real `calc.py` rename. The missing vote is *stub origin + unique extract*, not “basename always loses.”

The missing verb is still the token. The mutation is: **a leftover is a pointer, not a tie with bait.**

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

v0.4 killed: "a stem-split copy is a move even when the minted path still has the body."

This mutation kills the follow-on lie: "without `oldstem/…` there is no extract, only `ambiguous` copies."

### Bought

- Leftover + renamed package (`src/math/ops.py`) lands on the body, not `src/legacy/calc.py`.
- Extract-and-keep still `same 1.000` at origin, including a copy at `src/math/ops.py`.
- Leftover that kept the add() docstring still loses.
- Identical dest copies with no leftover still emit `ambiguous`. Godfile / NFD / missing `--to` / clipped tokens / foreign repo: as v0.4.

### Lost

- A review pin on a function you then copy into a package **and leave in place** will not follow the copy. Mint the extract if that is the bookmark.
- Two honest extracts and no leftover import stay `ambiguous`. You wanted ranking; the token says it cannot see which copy is the move.

## Empirical transcript

### Working software (v0.5), before the improvement

`./pin selftest` → `selftest: ok`. `./demo.sh` all checks passed (leftover stub, extract-and-keep, leftover + `src/math/ops.py`, kizu / voidtrace / tenaoshi).

```
$ PIN=$(./pin mint --repo $MATH --from $V1 src/calc.py:4)
$ ./pin resolve --repo $MATH --to $V2 --porcelain "$PIN"
moved	-	src/calc.py:4	src/math/ops.py:4	0.910	path or surrounding file changed; skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1

$ ./pin resolve --repo $KEEPM --to $KEEPM_V2 --porcelain "$KEEPMPIN"
same	-	src/calc.py:4	src/calc.py:4	1.000	skipped basename bait src/legacy/calc.py:1; extracted copy src/math/ops.py:4
```

Ancestor v0.4 on the math leftover fixture landed `ambiguous … src/legacy/calc.py:1,src/math/ops.py:4`. Extract-and-keep stayed identity (that refuse is kept).

kizu godfile split is unchanged (old path is gone):

```
$ ./pin resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
```

### Failures that drove the first improvement

Non-basename was the first vote. Extract to `src/math/calc.py` (kept the old basename) still tied with `src/legacy/calc.py`:

```
ambiguous	-	src/calc.py:4	src/legacy/calc.py:1,src/math/calc.py:3	0.952	2 copies: src/legacy/calc.py:1; src/math/calc.py:3
```

The leftover already named the landing (`from src.math.calc import helper_keep as impl`). That pointer was unused. Two non-basename extracts plus bait was the same hole.

Extract-and-keep was not the hole: origin still holds the body, so import-following must not run.

### After the improvement

The leftover function body is searched for dest-path spellings (`src.math.calc`, `math.calc`). A unique named extract wins, including same-basename landings. Bare `calc` is not a form — it would match both `math.calc` and `legacy.calc`.

```
$ ./pin resolve --repo $SAMEB --to $SAMEB_V2 --porcelain "$SAMEBPIN"
moved	-	src/calc.py:4	src/math/calc.py:4	0.952	path or surrounding file changed; skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1
```

`./demo.sh` still exits 0. New guards: `18r` renamed leftover, `18m` extract-and-keep to `src/math/ops.py`, `18s` leftover import vs same-basename bait. Voidtrace `import {` clones stay skipped paths, not leftover stubs or extracted copies.

## Dogfood targets

- Leftover wrapper + renamed extract `src/math/ops.py` + basename bait `src/legacy/calc.py`.
- Extract-and-keep to `src/calc/ops.py` and to `src/math/ops.py`. Origin untouched.
- Leftover that names `src.math.calc` while bait is `src/legacy/calc.py`.
- Leftover that kept the add() docstring. Noisy origin with comments past ctx=3.
- Synthetic ugly repo, 1.2 MB godfile, NFD `café.py`, missing `--to`, truncated tokens, foreign helper.
- kizu `src/app.rs` split at `b4e6a5d`; voidtrace `evaluate.ts:1`; tenaoshi `KinsokuEngine.swift:12`.

## Surprises

- Scoring already preferred basename (`src/legacy/calc.py` path_score 0.52 vs `src/math/ops.py` 0.10). Using path_score as the tie-break would have *picked the bait*. The vote had to be “basename is bait when origin is a stub,” not “higher path affinity.”
- `_pick_exact` never saw those scores anyway: equal neighbor windows and no stem-split returned `None` → `ambiguous`. The hole was the picker, not the scorer (same class as v0.4).
- Naming every non-origin exact copy `extracted copy` lied on voidtrace: `import {` clones are not extracts. Origin-won copies need the body window before that label. Identity clones stay skipped paths.
- Leftover import is a stronger vote than non-basename, but it must not run when origin holds the body. Otherwise extract-and-keep that mentions the new module in a comment would follow the clone.

## Failures

- `}`-only and blank lines still refuse to mint (`too trivial`).
- Whole-tree dest index on every resolve.
- Relative leftover `from .calc import` does not name `src/math/calc.py`. No dotted stem, still `ambiguous` if both copies share the basename.
- v1 pins (no origin) still resolve onto any repo.
- Origin is still sorted root SHAs (orphan / shallow / graft look foreign).
- Token length ~160–450 chars.

## Suggested mutations

- Relative / `from .ops import` leftovers must still name the extract.
- Origin as a stable repo id, not the set of root SHAs (orphan / shallow / graft).
- `--to-dir` inside a git repo must inherit origin; missing origin / v1 fail closed unless `--any-repo`.
- Mint-target fallback on dest, or refuse to mint `SKIP_DIRS` paths. Huge dest omit with a sibling is still `deleted`.

## Kill / keep

**Keep.** The object is still the token. Unique kizu pins still land the godfile split. Leftover stubs still lose, including renamed packages. Extract-and-keep is still identity. Kill only if a later mutation proves bookmarks *want* to follow every clone — that is a different verb (follow-the-clone), not this pin.
