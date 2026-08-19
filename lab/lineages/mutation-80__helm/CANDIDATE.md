# mutation-80 — helm

## Primitive

A leftover re-export is an **import relative to the leftover file**. Mint a self-contained helm token once; resolve it onto a later tree without re-supplying `path:line`. `from .ops import add` in `src/calc.py` names dest `src/math/ops.py`. `from src.math import calc` at module level follows. `io.fs` ⊂ `audio.fs` stays ambiguous. Origin is keel's key: remotes + tip witnesses, not root SHAs.

## Why this might not exist

Keel (mutation-60) kept pin v0.5 leftover matching and flipped origin. Shunt (mutation-66) parsed leftover grammar, then followed it — but relative leftover still resolved as a **Python sibling only**. `from .ops import` in `src/calc.py` became `src.ops` (`src/ops.py`). The extract at `src/math/ops.py` missed. Unique-non-basename was already deleted, so the pin went `ambiguous` rather than following the leftover's own name.

DESTROYER_PIN_V5 and keel's suggested mutation named the hole:

1. `from .ops import` after extract to `src/math/ops.py` must `moved` to the extract.
2. `from .calc import` must name `src/math/calc.py`, not stay `ambiguous`.
3. Module-level `from src.math import calc` follows (shunt).
4. `io.fs` ⊂ `audio.fs` must not land `src/io/fs.py` (shunt).

The missing verb is still the token. The mutation is: **leftover is relative to the leftover file, not an unanchored substring and not basename bait.**

## How to run

From the worktree root:

```bash
chmod +x ./helm
./helm --help
./helm selftest
./demo.sh
./helm mint --repo /path --from <old-sha> path:line
./helm resolve --repo /path --to HEAD helm1.…
./helm show helm1.…
./helm id --repo /path
```

Exit 0 on success. `resolve` exits 2 if you hand it a `path:line`. Missing `--from`/`--to` refs exit 2. Corrupt / truncated tokens exit 1 with no result row. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `ambiguous`. Confirmed deletions are still answers.

## The assumption that was flipped

Shunt leftover matching was: parse import grammar, resolve relative specs as **package-sibling modules**, match dest on exact module identity.

This mutation keeps the grammar and kills sibling-only resolution. A relative leftover names dest modules by the **tail spelled relative to the leftover file** (`ops` from `from .ops import` in `src/calc.py` → unique dest ending in `.ops`). Short tails (`fs`, len < 3) are dropped so `io.fs` ⊂ `audio.fs` cannot unique-land bait. Basename is not bait. Origin is remotes + witnesses (inherited from keel).

### Bought

- `from .ops import` in leftover `src/calc.py` lands unique extract `src/math/ops.py`.
- `from .calc import` unique extract `src/math/calc.py` lands (leftover skipped as self).
- `require('./ops')` in leftover `src/calc.js` lands `src/math/ops.js`.
- Relative leftover + helpers decoy still refuses (no dest named `ops`).
- Module-level `from src.math import calc` and `from src.math.calc import helper_keep as _impl` follow.
- Comment `audio.fs` + relative `.fs` stays `ambiguous` (`src/io/fs.py` and `src/radio/fs.py`).
- Extract-and-keep still `same 1.000` at origin, including a copy at `src/math/ops.py`.
- Leftover + `src/math/ops.py` still `moved`. Stem-split clone cannot beat a unique named extract.
- Depth-1 `file://` clone of the same project resolves; orphan extra root is the same helm; foreign repo fail-closes.
- Unique kizu pins still land the godfile split.

### Lost

- A leftover `from .ops import` with two dests named `ops` (`src/math/ops.py` and `src/calc/ops.py`) is `ambiguous` rather than guessing. Leftover did not say which.
- Relative `.fs` (tail shorter than 3) will not unique-land `radio/fs.py` when `io/fs.py` also exists.
- A leftover with no parseable import of this name, plus several exact copies, is `ambiguous`.

## Empirical transcript

### Working software (v0.7), gold holds

`./helm selftest` → `selftest: ok`. `./demo.sh` all checks passed.

```
$ PIN=$(./helm mint --repo $RELOPS --from $V1 src/calc.py:4)
$ ./helm resolve --repo $RELOPS --to HEAD --porcelain "$PIN"
moved	-	src/calc.py:4	src/math/ops.py:4	0.910	skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1

$ PIN=$(./helm mint --repo $KEEP --from $V1 src/calc.py:4)
$ ./helm resolve --repo $KEEP --to HEAD --porcelain "$PIN"
same	-	src/calc.py:4	src/calc.py:4	1.000	skipped extracted copy src/calc/ops.py:4; basename bait src/legacy/calc.py:1
```

kizu godfile split is unchanged (old path is gone):

```
$ ./helm resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000
```

### Failures that drove the first improvement (after dogfood)

`from .calc import` in leftover `src/calc.py` with extract `src/math/calc.py` **and** bait `src/legacy/calc.py` stayed `ambiguous`. Leftover-relative tail `calc` named both dests. Unique extract without bait already landed.

```
ambiguous	-	src/calc.py:4	src/legacy/calc.py:1,src/math/calc.py:4	0.952	2 copies: …
```

DESTROYER_PIN_V5 fixture `relamb` is this shape. The leftover named `calc` relative to the leftover file; the extract kept `add()`; the bait is a thin helper_keep clone.

A first richness vote (unique leftover-named dest with more defs) closed relamb, then stole voidtrace identity:

```
moved	packages/kernel/src/evaluate.ts:1	packages/kernel/src/trace-replay.ts:1	0.596
```

`evaluate.ts:1` is `import {`. The file also has `from "./trace-replay.ts"`. Origin had two `import {` lines so `origin_exact` returned None; leftover richness ranked sibling imports of a real module.

### After the first improvement

Among leftover-named dests, unique dest that still implements more of the module (strictly more defs, and the minted body) is the extract — **only when the leftover is a def re-export of this locus**. Thin same-basename bait loses. Two full copies stay `ambiguous`. `origin_exact` prefers the minted line when the origin file has several exact copies, so file-level `import {` identity holds.

```
$ ./helm resolve --repo $RELC2 --to HEAD --porcelain "$RELC2PIN"
moved	-	src/calc.py:4	src/math/calc.py:4	0.952	skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1

$ ./helm resolve --repo voidtrace --to HEAD --porcelain "$VP"
same	-	packages/kernel/src/evaluate.ts:1	packages/kernel/src/evaluate.ts:1	1.000
```

`io.fs` ⊂ `audio.fs` is unchanged (`ambiguous`). Relative `.ops` unique extract is unchanged.

## Dogfood targets

- DESTROYER_PIN_V5 fixtures: rel_ok (`from .math.ops import` → `src/math/ops.py`), iofs (must not land `src/io/fs.py`), rel_decoy, modlevel, splitimp, stem_over_ptr.
- Leftover `from .ops import` + extract `src/math/ops.py` + basename bait `src/legacy/calc.py`.
- Leftover `from .calc import` unique extract, and extract + bait.
- Extract-and-keep to `src/calc/ops.py` and to `src/math/ops.py`. Origin untouched.
- Synthetic ugly repo, 1.2 MB godfile, NFD `café.py`, missing `--to`, truncated tokens, foreign helper, `file://` depth-1 clone, orphan extra root.
- kizu `src/app.rs` split at `b4e6a5d`; voidtrace `evaluate.ts:1`; tenaoshi `KinsokuEngine.swift:12`; sitbone `PresenceArbiter.swift:75`.

## Surprises

- Shunt already resolved `.ops` from `src/calc.py` to `src.ops`. The dest `src.math.ops` does not equal `src.ops` and does not end with `.src.ops`. The leftover *did* name `ops` relative to its file; the package prefix was leftover's old home, not the extract's.
- Dropping tails shorter than 3 (`fs`) is what keeps `from .fs import` + comment `audio.fs` from unique-landing `src/io/fs.py`. Suffix identity on `fs` would have hit both `radio/fs` and `io/fs` — refuse is correct; substring landing is not.
- `git clone --depth 1 /local/path` is still not shallow. The destroyer's shallow hole is `file://`.
- Voidtrace `evaluate.ts:1` is `import {` and also `from "./trace-replay.ts"`. Ranking leftover-named dests by def count without requiring a leftover *def* follows sibling imports of a real module. `origin_exact` also has to prefer the minted line when the origin file repeats `import {`.

## Failures

- `}`-only and blank lines still refuse to mint (`too trivial`).
- Whole-tree dest index on every resolve.
- Relative leftover that names two dests with the same relative tail and the same def count still refuses.
- v1 tokens (no origin) still resolve onto any repo.
- Token length ~160–450 chars plus a short helm origin.

## Suggested mutations

- Pin on the body line when origin_exact is gone still follows leftover at the minted path (partially: leftover_pointer no longer requires origin_exact).
- `--to-dir` inside a git repo inherits origin (done here, from keel). Missing origin / v1 fail closed unless `--any-repo`.
- Mint-target fallback on dest, or refuse to mint `SKIP_DIRS` paths.

## Kill / keep

**Keep.** The object is still the token. Unique kizu pins still land the godfile split. Leftover stubs still lose, including renamed packages and leftover-relative extracts. Extract-and-keep is still identity. Origin is the project, not the DAG's roots. Kill only if a later mutation proves bookmarks *want* to follow every clone — that is a different verb (follow-the-clone), not this helm.
