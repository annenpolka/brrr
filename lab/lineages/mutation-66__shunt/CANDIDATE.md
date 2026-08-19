# mutation-66 — shunt

## Primitive

A leftover re-export is an **import pointer** of this name. Mint a self-contained fingerprint once; resolve it onto a later tree without re-supplying `path:line`. v0.6 keeps the v0.4/v0.5 gold (origin body is identity; leftover + `src/math/ops.py` is a move) and flips v0.5 leftover matching: not substring-of-function, not stem-split-first, not basename-is-bait.

## Why this might not exist

Ancestor pin v0.5 (mutation-47) stopped leftover stubs from tying with basename bait when the leftover *inlined* `from src.math.ops import helper_keep`. DESTROYER_PIN_V5 showed leftover still was not a pointer:

1. Unique `oldstem/…` still voted first. Leftover named `src.math.ops`; an abandoned `src/calc/ops.py` clone won.
2. Relative leftover `from .ops import` missed; unique-non-basename landed `src/utils/helpers.py` and called the real extract `src/pkg/calc.py` **basename bait**.
3. Module-level `from src.math.calc import helper_keep as _impl` was invisible (pointer lived outside the enclosing function) → `ambiguous`.
4. `from src.math import calc` had no contiguous `math.calc` spelling → `ambiguous`.
5. Last-two substring `io.fs` ⊂ `audio.fs` landed `src/io/fs.py` when the extract was `src/radio/fs.py`.

The missing verb is still the token. The mutation is: **parse leftover grammar, then follow it.**

## How to run

From the worktree root:

```bash
chmod +x ./shunt
./shunt --help
./shunt selftest
./demo.sh
./shunt mint --repo /path --from <old-sha> path:line
./shunt resolve --repo /path --to HEAD shunt1.…
./shunt show shunt1.…
```

Exit 0 on success. `resolve` exits 2 if you hand it a `path:line`. Missing `--from`/`--to` refs exit 2. Corrupt / truncated tokens exit 1 with no result row. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `ambiguous`. Confirmed deletions are still answers.

## The assumption that was flipped

v0.5 leftover matching was: `form in enclosing-function-blob` + stem-split first + unique-non-basename (basename is bait).

This mutation kills that triple. Leftover is the import **of this name** in the leftover *file*. Stem-split cannot beat a unique named extract. Unique-non-basename is not a vote.

### Bought

- Leftover that names `src.math.ops` lands there even when `src/calc/ops.py` still exists.
- Relative leftover + unique helpers decoy does **not** land the decoy or call `src/pkg/calc.py` basename bait (refuses `ambiguous`).
- Module-level `from src.math.calc import … as _impl` and `from src.math import calc` follow the pointer.
- Comment `audio.fs` does not land `src/io/fs.py`.
- Extract-and-keep still `same 1.000` at origin, including a copy at `src/math/ops.py`.
- Leftover + `src/math/ops.py` still `moved`. Leftover that kept the add() docstring still loses.
- Identical dest copies with no leftover still emit `ambiguous`. Godfile / NFD / missing `--to` / clipped tokens / foreign repo: as v0.4/v0.5.

### Lost

- A leftover with no parseable import of this name, plus several exact copies, is `ambiguous` rather than “pick the unique non-basename.” That was follow-the-clone, not a pointer.
- Relative `.ops` that does not resolve to a dest file will not guess `src/pkg/calc.py`. Refuse is the vote.

## Empirical transcript

### Working software (v0.6), gold still holds

`./shunt selftest` → `selftest: ok`. `./demo.sh` all checks passed.

```
$ PIN=$(./shunt mint --repo $KEEP --from $V1 src/calc.py:4)
$ ./shunt resolve --repo $KEEP --to $V2 --porcelain "$PIN"
same	-	src/calc.py:4	src/calc.py:4	1.000	skipped extracted copy src/calc/ops.py:4; basename bait src/legacy/calc.py:1

$ PIN=$(./shunt mint --repo $MATH --from $V1 src/calc.py:4)
$ ./shunt resolve --repo $MATH --to $V2 --porcelain "$PIN"
moved	-	src/calc.py:4	src/math/ops.py:4	0.910	path or surrounding file changed; skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1
```

### Failures that drove the first improvement (DESTROYER_PIN_V5)

Ancestor v0.5 on stem-over-pointer:

```
moved	-	src/calc.py:4	src/calc/ops.py:4	0.998	skipped leftover stub; basename bait; extracted copy src/math/ops.py:4
```

The leftover imported `src.math.ops`. Stem-split voted first.

Ancestor v0.5 on relative leftover + helpers decoy:

```
moved	-	src/calc.py:4	src/utils/helpers.py:1	0.910	… basename bait src/pkg/calc.py:4
```

### After the first improvement

Pointer before stem-split; unique-non-basename removed; leftover is import grammar over the leftover file.

```
$ ./shunt resolve --repo $SS --to HEAD --porcelain "$SSPIN"
moved	-	src/calc.py:4	src/math/ops.py:4	0.910	skipped leftover stub src/calc.py:1; extracted copy src/calc/ops.py:4; basename bait src/legacy/calc.py:1

$ ./shunt resolve --repo $REL --to HEAD --porcelain "$RELPIN"
ambiguous	-	src/calc.py:4	src/legacy/calc.py:1,src/pkg/calc.py:4,src/utils/helpers.py:1	0.952	3 copies: …
```

kizu godfile split is unchanged (old path is gone):

```
$ ./shunt resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
```

### After the second improvement (module-level / split import / io.fs)

Ancestor v0.5 on module-level shim and `from src.math import calc` both printed `ambiguous … src/legacy/calc.py:1,src/math/calc.py:4`. Comment `audio.fs` uniquely landed `src/io/fs.py`.

```
$ ./shunt resolve --repo $MOD --to HEAD --porcelain "$MODPIN"
moved	-	src/calc.py:4	src/math/calc.py:4	0.952	skipped leftover stub src/calc.py:4; basename bait src/legacy/calc.py:1

$ ./shunt resolve --repo $SPLIT --to HEAD --porcelain "$SPLITPIN"
moved	-	src/calc.py:4	src/math/calc.py:4	0.952	skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1

$ ./shunt resolve --repo $IOFS --to HEAD --porcelain "$IOFSPIN"
ambiguous	-	src/calc.py:1	src/io/fs.py:1,src/radio/fs.py:1	0.910	2 copies: src/io/fs.py:1; src/radio/fs.py:1
```

Selftest also: leftover `from src.math.ops_v2 import` lands `ops_v2.py` not `ops.py`; unused `from src.math.ops import add` does not steal `helper_keep`'s `from src.legacy.calc import`; docstring `src/legacy/calc.py` is not a pointer; body-line pin still sees leftover at the minted path; Rust `crate::math::calc::helper_keep()` lands `src/math/calc.rs`.

## Dogfood targets

- DESTROYER_PIN_V5 fixtures: stem_over_ptr, rel_decoy, modlevel, splitimp, iofs.
- Leftover wrapper + renamed extract `src/math/ops.py` + basename bait `src/legacy/calc.py`.
- Extract-and-keep to `src/calc/ops.py` and to `src/math/ops.py`. Origin untouched.
- Synthetic ugly repo, 1.2 MB godfile, NFD `café.py`, missing `--to`, truncated tokens, foreign helper.
- kizu `src/app.rs` split at `b4e6a5d`; voidtrace `evaluate.ts:1`; tenaoshi `KinsokuEngine.swift:12`.

## Surprises

- Unique-non-basename was doing the v0.5 gold `leftover + src/math/ops.py` work whenever leftover_names missed. Parsing the import makes that vote unnecessary; deleting it closed the helpers decoy without reopening 18r.
- `io.fs in "audio.fs"` is True. Module identity with a leading-dot suffix (`endswith("." + form)`) is not: `src.audio.fs.endswith(".io.fs")` is False.
- A leftover pointer has to read the *file*, not the enclosing function, or the usual Python shim (`from … import helper_keep as _impl` then `return _impl()`) is invisible.

## Failures

- `}`-only and blank lines still refuse to mint (`too trivial`).
- Whole-tree dest index on every resolve.
- Relative leftover that names a missing `.ops` still cannot choose among same-basename copies; it refuses.
- v1 tokens (no origin) still resolve onto any repo.
- Origin is still sorted root SHAs (orphan / shallow / graft look foreign).
- Token length ~160–450 chars.

## Suggested mutations

- Pin on the body line when origin_exact is gone still follows leftover at the minted path (partially: leftover_pointer no longer requires origin_exact; needs more demo heat).
- Origin as a stable repo id, not the set of root SHAs.
- `--to-dir` inside a git repo must inherit origin; missing origin / v1 fail closed unless `--any-repo`.
- Mint-target fallback on dest, or refuse to mint `SKIP_DIRS` paths.

## Kill / keep

**Keep.** The object is still the token. Unique kizu pins still land the godfile split. Leftover stubs still lose, including renamed packages, because leftover is now a pointer. Extract-and-keep is still identity. Kill only if a later mutation proves bookmarks *want* to follow every clone — that is a different verb (follow-the-clone), not this shunt.
