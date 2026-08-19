# mutation-22 — pin

## Primitive

A code locus is a **pin**: mint a self-contained fingerprint once, store the token, resolve it onto a later tree **without** re-supplying `path:line`. v0.3 keeps that object and stops the token from lying: leftover stubs are not identity, uniqueness is uniqueness in *both* snapshots, a missing `--to` is an error, a clipped token fails closed, and a foreign repo is refused unless `--any-repo`.

## Why this might not exist

Ancestor pin (mutation-14) flipped slip's "re-supply locator + SHA every time." Destroyer then showed the pin still pretended to be more than it was:

1. A module extraction that leaves a re-export at the old path scores `shifted 1.000` on the stub. The file-split story only held if the old path was *gone*.
2. Two identical dest copies both scored 1.000; walk-order / basename hid one.
3. Files over 1 MB were silently omitted from the snapshot (`MAX_FILE_BYTES`).
4. NFD `cafe\u0301.py` and NFC `caf\u00e9.py` were different paths. APFS is not git.
5. `--to this-ref-does-not-exist` listed as `deleted` / exit 0.
6. Truncated `pin1.…` porcelain-resolved as `unresolved` / exit 0. `show` already failed closed.
7. A helper pin minted in repo A landed `moved 1.000` on repo B.

The missing verb is still the token. The mutation is: **the token is allowed to refuse.**

## How to run

From the worktree root:

```bash
chmod +x ./pin
./pin --help
./pin --selftest
./demo.sh
./pin mint --repo /path --from <old-sha> path:line
./pin resolve --repo /path --to HEAD pin1.…
./pin resolve --repo /path --to HEAD --file review.pins
./pin show pin1.…
```

Exit 0 on success. `resolve` exits 2 if you hand it a `path:line`. Missing `--from`/`--to` refs exit 2 (`unknown ref`). Corrupt / truncated tokens exit 1 with no result row. Origin mismatch exits 1 unless `--any-repo`. `--strict` also fails on `ambiguous`. Confirmed deletions are still answers.

## The assumption that was flipped

Ancestor killed: "the user re-supplies `path:line` every time."

This mutation kills the seven follow-on lies that made that token look more durable than it was.

### Bought

- Leftover stub at the old path loses to the extracted body (`src/calc/ops.py`), including `add()`.
- Identical dest copies emit `ambiguous` and list both addresses. Never 1.000 twice.
- 1.2 MB godfile mints and resolves (limit 48 MB, mint-target fallback if a snapshot skip still happens).
- NFD locators bind NFC git paths.
- Missing `--to` is `unknown ref`, not `deleted`.
- Clipped tokens fail like `show`.
- Root-commit origin in the token; foreign repo refused.
- After the first dogfood pass: when several exact copies exist and one wins, the note names what was skipped (`leftover stub`, `basename bait`, voidtrace `import {` clones).

### Lost

- A pin from repo A will not land on repo B without `--any-repo`, even when the helper text is identical. That was the pitch's footgun; it is also a loss of "paste onto whatever tree."
- Two honest copies cannot be ranked by basename anymore. You get `ambiguous` and have to look.
- Token v2 carries `o` (origin). Slightly longer. v1 tokens still decode, without an origin check.

## Empirical transcript

### Working software (v0.3), before the note improvement

Selftest + ugly fixture + destroyer regressions + kizu / voidtrace / tenaoshi. Leftover stub already landed in `ops.py` at 0.998, not the wrapper. Identical helpers were `ambiguous`. Godfile 1 200 042 bytes minted. NFD `café` minted. Missing `--to` exited 2. Half-token exited 1 with `corrupt pin`. Foreign repo refused.

```
$ PIN=$(./pin mint --repo $UGLY --from $V1 src/calc.py:14)
$ ./pin resolve --repo $UGLY --to $V2 --porcelain "$PIN"
moved	-	src/calc.py:14	src/math/ops.py:8	1.000	path or surrounding file changed

$ ./pin resolve --repo $STUB --to $STUB_V2 --porcelain "$STUBPIN"
moved	-	src/calc.py:5	src/calc/ops.py:5	0.998	path or surrounding file changed
# dest is ops.py, not the leftover wrapper, not src/legacy/calc.py
```

The 0.998 (not 1.000) is the point: dest has three exact `def helper_keep():` lines, so uniqueness is a lie. Neighbors + stem-split (`src/calc.py` → `src/calc/`) pick the body.

### After the improvement

The leftover landing was correct but mute. Voidtrace identity stayed on `evaluate.ts:1` while `import {` clones (`cli.test.ts`, `cli.ts`, `catalog.ts`, …) sat in dest. The first skip-note patch named them, and the naive demo grep for `cli.test.ts` on the whole row failed — the pin had not moved; the note had gotten honest.

```
$ ./pin resolve --repo $STUB --to $STUB_V2 --porcelain "$STUBPIN"
moved	-	src/calc.py:5	src/calc/ops.py:5	0.998	path or surrounding file changed; skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1

$ ./pin resolve --repo $STUB --to $STUB_V2 --porcelain "$ADDPIN"   # src/calc.py:1 add()
moved	-	src/calc.py:1	src/calc/ops.py:1	0.998	path or surrounding file changed; skipped leftover stub src/calc.py:5

$ ./pin resolve --to-dir $IDENT_TO --porcelain "$IDPIN"
ambiguous	-	src/calc.py:1	a/ops.py:1,z/calc.py:1	0.946	2 copies: a/ops.py:1; z/calc.py:1

$ ./pin mint --from-dir $HUGE src/godfile.py:1   # 1_200_042 bytes
$ ./pin resolve --to-dir $HUGE --porcelain "$GOD"
same	-	src/godfile.py:1	src/godfile.py:1	1.000

$ python3 -c '… mint NFD src/cafe\u0301.py:1 …'
$ ./pin show "$CAFEPIN"
  minted: src/café.py:1
  text:   def cafe_fn():

$ ./pin resolve --repo $UGLY --to this-ref-does-not-exist --porcelain "$PIN"
# rc=2 stderr: pin: unknown ref: this-ref-does-not-exist
# stdout empty — not `deleted`

$ ./pin resolve --repo $UGLY --to $V2 --porcelain "${PIN:0:24}"
# rc=1 stderr: pin resolve: corrupt pin: Error -5 while decompressing data: incomplete or truncated stream
# stdout empty

$ ./pin resolve --repo $UNREL --to HEAD --porcelain "$PIN"
# rc=1 stderr: pin belongs to a different repository (git:06b35edd3c8ca290 vs git:40e967456f4e512c)

$ ./pin resolve --repo $UNREL --to HEAD --any-repo --porcelain "$PIN"
moved	-	src/calc.py:14	pkg/util.py:1	1.000
```

kizu, still no path:line on resolve:

```
$ ./pin resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000

$ ./pin resolve --repo kizu --to HEAD --porcelain "$LAND"
moved	-	src/app.rs:543	src/app/navigation.rs:22	1.000

$ ./pin resolve --repo kizu --to HEAD --porcelain "$FP"
edited	-	src/app.rs:602	src/app/layout.rs:35	0.868	line text drifted

$ ./pin resolve --repo voidtrace --to HEAD --porcelain "$VP"
same	-	packages/kernel/src/evaluate.ts:1	packages/kernel/src/evaluate.ts:1	1.000	skipped …/cli.test.ts:1; apps/cli/src/cli.ts:1; …
```

`./demo.sh` exits 0.

## Dogfood targets

- Synthetic ugly git repo: split+rename, signature drift, deletion, unicode `src/日本語.py`, `src/weird:colon.py`, `notes/file with spaces.txt`, NFC `src/café.py`, extensionless `Makefile`, nested git under `vendor/nested`.
- Destroyer fixtures in `./demo.sh`: leftover stub + `src/calc/ops.py` + `src/legacy/calc.py`; identical `a/ops.py` + `z/calc.py`; 1.2 MB `godfile.py`; missing `--to` / `--from`; truncated token; unrelated repo with the same helper.
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `src/app.rs` split at `b4e6a5d`; four pins plus a named pinfile.
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — HEAD identity on `evaluate.ts:1` must not jump to other `import {` files.
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — `KinsokuEngine.swift:12` `transform` from `a41089c` → HEAD, score 1.000.

## Surprises

- The leftover stub is not a scorer bug, it is an identity rule. `path == dest_path` plus `unique_tok <= 2` *is* "this is the same function." Once uniqueness means `df == 1` in dest *and* neighbors vote, the stub falls out without a special case for re-exports.
- Stem-split (`src/calc.py` → `src/calc/ops.py`) has to beat basename (`src/legacy/calc.py`) or the file-split story loses to the first `calc.py` git finds.
- Voidtrace `import {` is the honest twin of leftover stub: many exact copies, one of them *is* identity. Same-path + neighbor window = 1.000; the note now lists the clones instead of pretending they were never candidates.
- Origin as root commits is small (16 hex) and enough to stop the helper-keep/unrel 1.000. Unique kizu pins already refused voidtrace; the failure was the *common* helper.

## Failures

- `}`-only and blank lines still refuse to mint (`too trivial`).
- Whole-tree dest index on every resolve. 1.2 MB / 3 lines is cheap; linux.git is not.
- `--any-repo` still lands a common helper at 1.000 on a stranger. That is the override, not the default.
- Two copies whose neighbors *also* match and neither is a stem-split are `ambiguous` even when a human would pick "the one in `src/`."
- v1 pins (no origin) still resolve onto any repo. Old tokens cannot grow a fingerprint.
- Token length ~160–450 chars. Origin adds a few.

## Suggested mutations

- Attach a note/expectation to the pin (`--note`) so the token carries the review comment. PRIOR_ART's original wording, still open.
- `pin watch`: rewrite a pinfile onto HEAD as the tree moves.
- Mint-from-one-file as the default for godfiles: index dest only for the pin's unique tokens, stream the rest.
- Hunk-level pin: mint each `@@` of a failing `git am`.

## Kill / keep

**Keep.** The object is still the token; kizu's godfile split still lands from a stored pin with no origin SHA. The destroyer cases are now part of `./demo.sh` and they fail closed. Kill only if a later mutation proves the pinfile-as-registry is the primitive and the self-contained token is just an encoding — and even then, leftover-stub / ambiguous / origin have to travel with it.
