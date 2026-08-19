# reimpl-10 — cleat

## Primitive

A leftover re-export is an **import relative to the leftover file**. Mint a self-contained cleat token once; resolve it onto a later tree without re-supplying `path:line`. `from .ops import add` in `src/calc.py` names dest `src/math/ops.py`. `from src.math import calc` at module level follows. `io.fs` ⊂ `audio.fs` stays ambiguous.

## Why this might not exist

DESTROYER_PIN_V5 showed leftover was not a pointer: unique `oldstem/…` voted first, unique-non-basename treated basename extracts as bait, module-level and split imports were invisible, and `io.fs` ⊂ `audio.fs` unique-landed the wrong file. Shunt parsed leftover grammar then followed it, but relative leftover was still a Python sibling (`from .ops import` in `src/calc.py` → `src.ops`). Helm claimed leftover is relative to the leftover file. This is a clean-room rebuild of that object, from the destroyer holes, without reading helm/shunt/pin sources.

The missing verb is still the token. The mutation is: **leftover is relative to the leftover file, not an unanchored substring and not basename bait.**

## How to run

From the worktree root:

```bash
chmod +x ./cleat
./cleat --help
./cleat selftest
./demo.sh
./cleat mint --repo /path --from <old-sha> path:line
./cleat resolve --repo /path --to HEAD cleat1.…
./cleat show cleat1.…
./cleat id --repo /path
```

Exit 0 on success. `resolve` exits 2 if you hand it a `path:line`. Missing `--from`/`--to` refs exit 2. Corrupt / truncated tokens exit 1 with no result row. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `ambiguous`. Confirmed deletions are still answers.

## The assumption that was flipped

v0.5 leftover matching was: `form in enclosing-function-blob` + stem-split first + unique-non-basename (basename is bait). Relative leftover as a package sibling (`src.ops`) still misses `src/math/ops.py`.

This rebuild kills substring search and sibling-only resolution. A relative leftover names dest modules by the **tail spelled relative to the leftover file** (`ops` from `from .ops import` in `src/calc.py` → unique dest ending in `.ops`, with leading-dot suffix identity). Short tails (`fs`, len < 3) drop so `io.fs` ⊂ `audio.fs` cannot unique-land bait. Unique-non-basename is not a vote. Origin is remotes + tip witnesses, not root SHAs.

### Bought

- `from .ops import` in leftover `src/calc.py` lands unique extract `src/math/ops.py`.
- `from .calc import` unique extract, and extract + thin bait, land `src/math/calc.py`.
- Relative leftover + helpers decoy refuses (no dest named `ops`).
- Module-level `from src.math.calc import helper_keep as _impl` and `from src.math import calc` follow.
- Comment `audio.fs` + relative `.fs` stays `ambiguous`.
- Extract-and-keep still `same 1.000` at origin, including a copy at `src/math/ops.py`.
- Leftover + `src/math/ops.py` still `moved`. Stem-split clone cannot beat a unique named extract.
- Body-line pin still follows leftover at the minted path. Unused `from src.math.ops import add` does not steal `helper_keep`. Docstring path is not a pointer. `ops` does not match `ops_v2`.
- Depth-1 `file://` clone of the same project resolves; orphan extra root is the same cleat; foreign repo fail-closes.
- Unique kizu pins still land the godfile split. Voidtrace `import {` stays identity.

### Lost

- A leftover `from .ops import` with two dests named `ops` is `ambiguous` rather than guessing.
- Relative `.fs` (tail shorter than 3) will not unique-land `radio/fs.py` when `io/fs.py` also exists.
- A leftover with no parseable import of this name, plus several exact copies, is `ambiguous`.
- v1 tokens (no origin) fail closed on a git dest unless `--any-repo`.

## Empirical transcript

### Working software, gold holds

`./cleat selftest` → `selftest: ok`. `./demo.sh` all checks passed.

```
$ PIN=$(./cleat mint --repo $RELOPS --from $V1 src/calc.py:4)
$ ./cleat resolve --repo $RELOPS --to HEAD --porcelain "$PIN"
moved	-	src/calc.py:4	src/math/ops.py:4	1.000	path or surrounding file changed; skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1

$ PIN=$(./cleat mint --repo $KEEP --from $V1 src/calc.py:4)
$ ./cleat resolve --repo $KEEP --to HEAD --porcelain "$PIN"
same	-	src/calc.py:4	src/calc.py:4	1.000	skipped extracted copy src/calc/ops.py:4; basename bait src/legacy/calc.py:1
```

kizu godfile split (old path is gone):

```
$ ./cleat resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
```

Relative leftover → extract is the object. It survived a clean-room rebuild from DESTROYER_PIN_V5 without reading helm.

### Failures that drove the first improvement

First demo run labeled `src/legacy/calc.py` as `skipped extracted copy` on extract-and-keep, because the bait still had `return "stable helper"`. DESTROYER gold wants `basename bait` for same-basename copies:

```
FAIL: legacy bait unnamed: same	-	src/calc.py:4	src/calc.py:4	1.000	skipped extracted copy src/calc/ops.py:4; skipped extracted copy src/legacy/calc.py:1
```

Voidtrace identity also named every `import {` clone an extracted copy (DESTROYER: identity clones are skipped paths).

### After the first improvement

Same-basename dests are bait before any extract label. Origin-won copies are `extracted copy` only when they still implement this locus (def of `fn`) or are a stem-split of the minted path.

```
$ ./cleat resolve --repo $KEEP --to HEAD --porcelain "$KEEPPIN"
same	-	src/calc.py:4	src/calc.py:4	1.000	skipped extracted copy src/calc/ops.py:4; basename bait src/legacy/calc.py:1

$ ./cleat resolve --repo voidtrace --to HEAD --porcelain "$VP"
same	-	packages/kernel/src/evaluate.ts:1	packages/kernel/src/evaluate.ts:1	1.000
```

DESTROYER leftover fixtures after the improvement:

```
stem_over_ptr  moved  src/math/ops.py:4     leftover pointer beats abandoned src/calc/ops.py
rel_decoy      ambiguous                    no dest named ops; helpers not landed
rel_ops        moved  src/math/ops.py:4     from .ops import → extract
relamb         moved  src/math/calc.py:4    from .calc import + bait; richer extract wins
modlevel       moved  src/math/calc.py:4    module-level from src.math.calc import
splitimp       moved  src/math/calc.py:4    from src.math import calc
iofs           ambiguous                    io.fs ⊂ audio.fs does not land src/io/fs.py
```

## Dogfood targets

- DESTROYER_PIN_V5 fixtures: stem_over_ptr, rel_decoy, rel_ops, relamb, modlevel, splitimp, iofs, keep, keepmath, math leftover, body pin, ops vs ops_v2, unused import, docstring poison.
- Leftover wrapper + renamed extract `src/math/ops.py` + basename bait `src/legacy/calc.py`.
- Extract-and-keep to `src/calc/ops.py` and to `src/math/ops.py`. Origin untouched.
- Synthetic ugly repo, 1.2 MB godfile, NFD `café.py`, missing `--to`, truncated tokens, foreign helper, `file://` depth-1 clone, orphan extra root.
- kizu `src/app.rs` split at `b4e6a5d`; voidtrace `evaluate.ts:1`; tenaoshi `KinsokuEngine.swift:12`.

## Surprises

- Relative `.ops` from `src/calc.py` is the tail `ops`, not sibling module `src.ops`. `src.math.ops` endswith `.ops`; the leftover's old package prefix is not the extract's.
- Dropping tails shorter than 3 (`fs`) is what keeps `from .fs import` + comment `audio.fs` from unique-landing `src/io/fs.py`. Suffix identity on `fs` would have hit both `radio/fs` and `io/fs` — refuse is correct; substring landing is not.
- Unique-non-basename was doing leftover+`src/math/ops.py` work whenever leftover_names missed. Parsing the import makes that vote unnecessary; deleting it closed the helpers decoy without reopening extract-and-keep.
- `io.fs in "audio.fs"` is True. Module identity with a leading-dot suffix (`endswith("." + form)`) is not: `src.audio.fs.endswith(".io.fs")` is False.
- A leftover pointer has to read the *file*, not the enclosing function, or the usual Python shim is invisible.
- Witnesses (mint `--from` + HEAD) match a `file://` depth-1 clone that has lost V1. Root SHAs would have called it foreign.

## Failures

- `}`-only and blank lines still refuse to mint (`too trivial`).
- Whole-tree dest index on every resolve.
- Relative leftover that names two dests with the same relative tail and the same def count still refuses.
- Token length ~160–450 chars typically; 1.2 MB godfile token was 1778.
- tenaoshi `transform` still labels other `func transform` files as extracted copies (they implement a same-named def).
- `--any-repo` remains an explicit override. It is not used to paper over origin.

## Suggested mutations

- Pin on the body line when origin_exact is gone still follows leftover at the minted path (done here; needs more demo heat on slim extracts).
- `--to-dir` inside a git repo inherits origin (done). Missing origin / v1 fail closed unless `--any-repo` (done, stricter than pin v0.5).
- Mint-target fallback on dest, or refuse to mint `SKIP_DIRS` paths.
- Extracted-copy label should require the minted *body*, not only a same-named def (tenaoshi adapters).

## Kill / keep

**Keep.** The object is still the token. Unique kizu pins still land the godfile split. Leftover stubs still lose, including renamed packages and leftover-relative extracts. Extract-and-keep is still identity. The primitive (relative leftover → extract) survived a clean-room rebuild from DESTROYER_PIN_V5 without reading helm. Kill only if a later mutation proves bookmarks *want* to follow every clone — that is a different verb (follow-the-clone), not this cleat.
