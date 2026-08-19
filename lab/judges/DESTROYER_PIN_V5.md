# DESTROYER — pin v0.5

Adversarial pass on origin-body identity + leftover-as-pointer. No rewrites: the failures are conceptual, not one-line bugs.

- **pin** (mutation-47, v0.5) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b62-b665-75a1-a5b6-d92ea07fa7a5`
- Prior: `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab/judges/DESTROYER_STUMP_PIN.md`
- Transcripts: `/tmp/destroy-pin-v5/attack.py`, `/tmp/destroy-pin-v5/transcript-round2.txt`
- Fixtures: `/tmp/destroy-pin-v5/fixtures/`
- `./pin selftest` → `selftest: ok`. `./pin --selftest` is not a flag (`unrecognized arguments: --selftest`, rc=2).
- `./demo.sh` → `All demo checks passed.` (18 leftover stub, 18k extract-and-keep, 18r leftover+`src/math/ops.py`, 18m renamed extract-and-keep, 18s leftover import vs same-basename bait, kizu / voidtrace / tenaoshi).

Verdict: **mutate, do not kill.** The DESTROYER_STUMP_PIN leftover-stub / extract-and-keep pair is actually closed on the fixtures they wrote. The new holes are where v0.5 overcorrected: leftover is not a pointer, and origin-body identity is not identity of the file.

---

## Previous DESTROYER bugs — verified fixed (v0.5 claims)

Re-ran the v0.4 holes plus `./demo.sh`. Porcelain from `/tmp/destroy-pin-v5/fixtures/`.

| old bug | now |
| --- | --- |
| extract-and-keep `moved … src/calc/ops.py` (stump-pin §1) | `same	-	src/calc.py:4	src/calc.py:4	1.000	skipped extracted copy src/calc/ops.py:4; basename bait src/legacy/calc.py:1` |
| extract-and-keep to renamed package | `same	-	src/calc.py:4	src/calc.py:4	1.000	skipped basename bait src/legacy/calc.py:1; extracted copy src/math/ops.py:4` |
| leftover + `src/math/ops.py` `ambiguous` with basename bait (stump-pin §2) | `moved	-	src/calc.py:4	src/math/ops.py:4	0.910	… leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1` |
| leftover import vs `src/math/calc.py` / `src/legacy/calc.py` | demo 18s `moved … src/math/calc.py:4 0.952` |
| leftover that kept add() docstring | demo 18d `moved … src/calc/ops.py:1` |
| comments past ctx=3 | demo 18n `same … src/calc.py:1 0.680 skipped extracted copy` |
| origin comment names the extract | `same	-	src/calc.py:4	src/calc.py:4	1.000	skipped … extracted copy src/math/ops.py:4` (import-following does not run when the body is held) |

kizu `src/app.rs:529@b4e6a5d` still lands `src/app/layout.rs:17`. Voidtrace `evaluate.ts:1` stays identity; tenaoshi line 12 is `same 1.000`. Missing `--to`, truncated tokens, NFD café, 1.2 MB mint, foreign `--repo` refuse: as advertised.

The leftover **wrapper** no longer scores `shifted 1.000`. Extract-and-keep is no longer reported as a move, and origin is no longer called basename bait. Those two refuses hold.

---

## pin

Primitive restated: mint a self-contained fingerprint once; the token is allowed to refuse. Origin still holding the implementation is identity. If origin is a stub, a leftover re-export is a **pointer** at the extract, including when the extract is not `oldstem/…` and even when it kept the old basename.

`_pick_exact` vote order after origin-body-hold fails (`pin` ~1140–1177):

1. unique strong neighbor window
2. **unique stem-split** (`src/calc.py` → `src/calc/…`)
3. leftover blob contains a dest-path spelling (`form in blob`)
4. **unique non-basename** copy, if origin is a stub
5. else `ambiguous`

(2) and (4) fire without a pointer. (3) is unanchored substring of the enclosing function, not an import of this name. That is not the same object as “leftover is a pointer.”

`origin_holds_body` requires **every** minted implementation neighbor to sit in the enclosing dest function (`body_ns >= 1.0 - TIE_EPS`). Comments that push the body past `--context` still hold (18n). A one-line body edit does not.

### 1. Stem-split still beats a unique leftover pointer (conceptual, lethal to “leftover is a pointer”)

v0.5 added leftover-import as the vote that stem-split cannot cast. It did not reorder. Unique `oldstem/…` still returns first.

Leftover **names** `src.math.ops`. Abandoned clone at `src/calc/ops.py`. Body also at `src/math/ops.py`. Basename bait `src/legacy/calc.py`.

```
$ PIN=$(./pin mint --repo $SS --from $V1 src/calc.py:4)
$ ./pin resolve --repo $SS --to HEAD --porcelain "$PIN"
moved	-	src/calc.py:4	src/calc/ops.py:4	0.998	path or surrounding file changed; skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1; extracted copy src/math/ops.py:4
```

Human format rounds that to `moved 1.00`. The leftover’s import is sitting on disk. The note calls the named extract `extracted copy` and lands on the stem-split clone the wrapper does not import.

The pointer exists. Stem-split does not read it.

### 2. Unique non-basename decoy; the real extract is “basename bait” (conceptual, lethal)

CANDIDATE: “basename is bait when origin is a stub,” because path_score would have picked `src/legacy/calc.py`. When leftover is a relative import, leftover_names hits 0, and unique non-basename is the vote. Basename copies are ineligible, including the extract that kept the old name.

Leftover: `from .ops import helper_keep as impl` (no dotted stem). Real extract: `src/pkg/calc.py`. Decoy: `src/utils/helpers.py`. Bait: `src/legacy/calc.py`.

```
$ ./pin resolve --repo $REL --to HEAD --porcelain "$PIN"
moved	-	src/calc.py:4	src/utils/helpers.py:1	0.910	path or surrounding file changed; skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1; basename bait src/pkg/calc.py:4
```

`src/pkg/calc.py` is the module extraction. The note calls it basename bait. The landing is a helpers clone that the leftover does not mention.

Same shape with tests:

```
moved	-	src/calc.py:4	tests/helpers.py:1	0.904	… basename bait src/pkg/calc.py:4
```

Relative leftover is not a refuse. It is a coin flip toward whichever exact copy does **not** share the basename. `from .math.ops import` still works (the dotted stem is in the blob) — the hole is the fallback, not “relative is hard.”

### 3. Module-level re-export is invisible (conceptual)

The common Python shim is not an inline import:

```
from src.math.calc import helper_keep as _impl

def helper_keep():
    return _impl()
```

`leftover_names_extract` joins `enclosing_function_lines` of the origin exact line. The function body is `return _impl()`. Extract `src/math/calc.py`, bait `src/legacy/calc.py`:

```
ambiguous	-	src/calc.py:4	src/legacy/calc.py:1,src/math/calc.py:4	0.952	2 copies: src/legacy/calc.py:1; src/math/calc.py:4
```

Demo 18s passed because the fixture inlined `from src.math.calc import helper_keep as impl` **inside** the function. The leftover pointer lives at module scope. v0.5 does not read it. Unique non-basename cannot break two same-basename copies, so this is `ambiguous` — the v0.4 hole, reopened for the usual shim.

### 4. `from src.math import calc` is not `math.calc` (conceptual)

Split import is the other usual form. Blob `from src.math import calc` / `return calc.helper_keep()`. Forms for `src/math/calc.py` are `src.math.calc`, `math.calc`, `math/calc`. None of those strings are contiguous in the leftover.

```
ambiguous	-	src/calc.py:4	src/legacy/calc.py:1,src/math/calc.py:4	0.952
```

Contrast: `from src.math import ops` **does** land `src/math/ops.py`, because that extract is the unique non-basename copy — the pointer still did not fire; vote (4) saved it. Same-basename extract has no such vote. `importlib.import_module("src.math.ops")` happens to contain `src.math.ops` and lands. The matcher is spelling, not import grammar.

### 5. Pin on the body line cannot see the leftover (conceptual)

Leftover names `src.math.ops`. Pin the **def** (demo shape): `moved … src/math/ops.py`. Pin the **return** that was the implementation (`src/calc.py:5`, text `return "stable helper"`):

```
$ ./pin show "$RETPIN"
  minted: src/calc.py:5
  text:       return "stable helper"
  before:
    - def add(a, b):
    -     return a + b
    - def helper_keep():

$ ./pin resolve --repo $SLIM --to HEAD --porcelain "$RETPIN"
ambiguous	-	src/calc.py:5	src/legacy/calc.py:2,src/math/ops.py:2	0.739	2 copies: src/legacy/calc.py:2; src/math/ops.py:2
```

Origin leftover no longer has that line (`return impl()`), so `origin_exact` is None, `origin_is_stub` is false, leftover_names does not run, unique non-basename does not run. Neighbors of the two remaining copies are the same two-line function. The leftover still names the extract. Two pins from the same function, minted on adjacent lines, disagree: signature follows, body refuses.

A fatter extract that kept `add()` neighbors still binds the return pin (first attack, `moved … src/math/ops.py:5 0.803`) via neighbor score, not the pointer. The leftover vote is def-line-shaped.

### 6. Substring forms — unique pointer is not unique to the matcher (conceptual)

`module_forms("src/math/ops_v2.py")` includes `math.ops_v2`. `module_forms("src/math/ops.py")` includes `math.ops`. `"math.ops" in "src.math.ops_v2"` is True.

Leftover uniquely imports `src.math.ops_v2`. Bodies at `ops_v2.py`, `ops.py`, and `legacy/calc.py`:

```
ambiguous	-	src/calc.py:4	src/legacy/calc.py:1,src/math/ops.py:1,src/math/ops_v2.py:1	0.952	3 copies: …
```

A human pointer with one destination. `form in blob` hits two extracts plus cannot drop the basename copy, then unique-non-basename sees two non-basenames and returns None. Versioned modules (`ops` / `ops_v2`, `fs` / `fs2`) make leftover_names refuse the unique import.

### 7. Last-two `io.fs` ⊂ `audio.fs` picks the **wrong** file (conceptual)

Not only refuse. Last-two-components is short enough to false-unique.

Leftover: comment `migrated off audio.fs` plus `from .fs import`. Extract: `src/radio/fs.py`. Bait: `src/io/fs.py`.

```
moved	-	src/calc.py:1	src/io/fs.py:1	0.910	… leftover stub src/calc.py:1; extracted copy src/radio/fs.py:1
```

`io.fs in "audio.fs"` is True. `radio.fs` is not in the blob. leftover_names returns one hit: the bait. The real extract is labeled `extracted copy`. Relative import produced no competing form (`fs` is len 2, skipped). This is a successful wrong landing, not `ambiguous`.

### 8. Docstring path poisons the pointer (conceptual)

Same-basename extract, leftover inlines the real import **and** documents the old path:

```
def helper_keep():
    """Deprecated. Old copy: src/legacy/calc.py"""
    from src.math.calc import helper_keep as impl
    return impl()
```

```
ambiguous	-	src/calc.py:4	src/legacy/calc.py:1,src/math/calc.py:4	0.952
```

Without the docstring, demo 18s lands `src/math/calc.py`. The pointer is unique. A path spelling anywhere in the function blob, including a deprecation URL, ties it with bait.

### 9. Unused import + unique-non-basename follows the unused module (conceptual)

Leftover **returns** `src.legacy.calc.helper_keep`. It also has `from src.math.ops import add` (copy-paste / neighboring name). Both copies have `def helper_keep():`.

leftover_names hits 2 → None. Unique non-basename then picks `src/math/ops.py` because `legacy/calc.py` shares the basename:

```
moved	-	src/calc.py:4	src/math/ops.py:4	0.910	… leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1
```

The leftover’s actual re-export is the file the note calls basename bait. “Any dest-path spelling in the function” is not “the import of this function,” and the basename-is-bait fallback then steers.

### 10. Rust `::` leftover, same-basename extract still `ambiguous` (conceptual)

```
pub fn helper_keep() -> &'static str {
    crate::math::calc::helper_keep()
}
```

Extract `src/math/calc.rs`, bait `src/legacy/calc.rs`. Forms are `math.calc` / `math/calc`, not `math::calc`.

```
ambiguous	-	src/calc.rs:1	src/legacy/calc.rs:1,src/math/calc.rs:1	0.952
```

kizu dogfood is a gone-path split (`src/app.rs` → `src/app/layout.rs`), which stem-split still wins. A Rust `pub use` leftover that kept the old basename is the 18s fixture in a language v0.5’s pointer does not speak. `require('./math/ops')` happens to contain `math/ops` and lands; `require('./ops')` with a helpers.js decoy is `ambiguous` (three copies) — JS relative is the same fallback hole as Python `.ops`.

### 11. Function-scoped body-hold: same-file impl is a leftover stub (conceptual)

Origin still has the implementation, in a sibling function. A clone also exists:

```
# src/calc.py (dest)
def helper_keep():
    return helper_keep_impl()

def helper_keep_impl():
    return "stable helper"

# src/math/ops.py
def helper_keep():
    return "stable helper"
```

```
moved	-	src/calc.py:4	src/math/ops.py:1	0.910	path or surrounding file changed; skipped leftover stub src/calc.py:1
```

`origin_holds_body` searches the enclosing function of the exact def, not the file. The body in `helper_keep_impl` does not count. Origin is a stub. Unique non-basename takes the clone. The file that still has `return "stable helper"` is named leftover stub.

Without the clone, `len(exacts)==1` would keep the wrapper. Extract-and-keep to another function in the **same** file is identity of the signature; add a copy and it becomes a move. Body-hold was scoped to kill docstring leftovers (18d). It cannot see a same-file remaining body.

### 12. `origin_holds_body` is 100%: a local edit is a leftover; the stale clone wins (conceptual, lethal to “origin body is identity”)

Mint:

```
def helper_keep():
    flag = True
    return "stable helper"
```

Dest origin still has the function, with a one-line edit (`flag = False`). Clone at `src/math/ops.py` still has `flag = True`.

```
$ ./pin show "$PIN"
  minted: src/calc.py:1
  after:
    -     flag = True
    -     return "stable helper"

$ ./pin resolve --repo $PB --to HEAD --porcelain "$PIN"
moved	-	src/calc.py:1	src/math/ops.py:1	0.910	… leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1
```

Origin is labeled leftover stub. The pin follows the **unedited clone**. CANDIDATE’s lost clause was “a review pin on a function you then copy into a package **and leave in place** will not follow the copy. Mint the extract if that is the bookmark.” A local bugfix at origin plus an untouched extract is that case. body_ns at origin is 0.5; the check demands 1.0. Comments-only (18n) still holds. Any implementation drift does not. That is follow-the-clone, which they said is a different verb.

---

## Acknowledged, still true (not this mutation)

CANDIDATE already listed these. Re-confirmed so they are not mistaken for v0.5 fixes.

| hole | now |
| --- | --- |
| `from .calc import` + two same-basename copies | `ambiguous … src/legacy/calc.py:1,src/math/calc.py:4` |
| `vendor/` mint then resolve same tree | mint ok; `deleted	-	vendor/lib/x.py:1	-	0.000	no candidates` rc=0 |
| `--to-dir` of a foreign repo **subdir** | `--repo` refuses; `--to-dir $UNREL/pkg` → `moved … util.py:1 1.000`. Gitless copy the same. |
| forged v1 payload (no `o`) | `moved … pkg/util.py:1 1.000` on the unrelated repo |
| extra git root (orphan branch) | mint origin `git:732b83e4fa5f8764`; resolve `--to` the **same** commit after `git checkout --orphan` → rc=1 `git:732b83e4fa5f8764 vs git:732b83e4fa5f8764,a0eb80fc3fff68ab` |
| dest omit over `HARD_MAX_BYTES` with a sibling | mint 1.2 MB godfile; dest 48 000 062-byte same path + `other.py` → `pin: skipping huge file src/god.py (48000062 bytes)` then `deleted	-	src/god.py:1	-	0.000	no candidates` rc=0. Mint of a file already over 48 MB dies (`file exceeds 48000000 bytes`). |

Origin is still sorted root SHAs. `--to-dir` still sets origin only when `discover_repo(directory) == directory`. `origins_match(None, dest)` is still True.

---

## What survived

- Extract-and-keep (stem-split **and** `src/math/ops.py`) is `same 1.000` at origin. Origin is not called basename bait. A comment at origin that names the extract does not follow the clone.
- Leftover **inline** `from src.math.ops import helper_keep as impl` beats basename bait when there is no stem-split clone and the extract is the unique non-basename (demo 18r) or leftover_names uniquely hits (demo 18s).
- Leftover that kept a docstring still loses to `src/calc/ops.py`.
- Two leftover-named extracts: leftover import still picks `src/math/ops.py` over `src/pkg/helpers.py` (selftest `two_ext`, attack NEW 16).
- Identical dest copies with no leftover still emit `ambiguous`. `--strict` fails.
- Unique kizu pins still land the godfile split. Voidtrace `import {` clones stay skipped paths, not leftover stubs.
- Missing `--to`, truncated tokens, NFD locators, 1.2 MB mint, foreign git **root**: as v0.4.
- `./pin selftest` and `./demo.sh` still exit 0 after the attacks.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still the token. Unique kizu pins still land. Origin-body identity holds on the byte-identical extract-and-keep fixtures. Leftover stubs still lose on the inline-import fixtures they wrote. Kill only if a later mutation proves the leftover vote is “any second copy that does not share a basename” — that is follow-the-clone, not this pin.

| do not kill because | mutate toward |
| --- | --- |
| v0.4 extract-and-keep refuse is real. Demo 18r/18s leftover landings are real. Token still refuses locators, bad refs, clipped pins, foreign roots. | Leftover pointer is the import **of this name**, not `form in enclosing-function-blob`. Stem-split cannot beat a unique named extract. Unique non-basename cannot run when a same-basename copy still has the body, and cannot run on a relative leftover as if basename were always bait. Read module-level imports. `from src.math import calc` / `math::calc` / `require('./ops')` are leftover grammar, not missing votes. Pin on the body line must still see a leftover at the minted path. `origin_holds_body` is file-or-function and is not `== 1.0` (a local edit is not a stub; a sibling fn in the same file is not a missing body). Last-two-component substring (`io.fs` ⊂ `audio.fs`, `math.ops` ⊂ `math.ops_v2`) is not a pointer. Vendor dest omit / 48 MB dest omit / origin-as-roots / v1 / `--to-dir` subdir stay the previous mutation list. |

A one-line “run leftover_names before stem-split” would hide §1 and would not touch relative decoys, module-level shims, split imports, body-line pins, substring false uniques, or 100% body-hold. Not applied.

A one-line “unique non-basename always loses to same-basename” would hide §2/§9/§17 and would re-open leftover+`src/math/ops.py` vs `src/legacy/calc.py` whenever leftover_names misses (relative, module-level, Rust). The leftover-as-pointer vs basename-is-bait trade is the mutation, not a patch.
