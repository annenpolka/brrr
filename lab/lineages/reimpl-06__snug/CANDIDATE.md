# reimpl-06 — snug

## Primitive

Given a dirty tree and a test command, emit the **1-minimal production hunks the current tests require**. Tests stay at NEW (they are the lock, never wheat). The predicate is pass/fail, not a command fingerprint.

Rebuilt from observed CLI / README / CANDIDATE / current tests of `cinch` (hybrid-03). The original Python file was never opened.

## Why this might not exist

alibi asks whether *the production diff as a whole* has an alibi (LOCKED/LOOSE), optionally per file. winnow asks which uncommitted hunks reproduce a command's *current behavior*. Piping them is the conventional hybrid and the wrong object.

The wheat of a test failure is not "hunks that change the test output." A new test file, a `print("debug")`, and a header comment all change output. The object is the **lockset**: the production hunks the new tests actually veto.

Rebuilding from the outside tests whether the primitive is real or an accident of one implementation. The gold check is the debug-print vs return fixture: two hunks in `app.py`, one test file, a dirty README. winnow keeps both hunks. cinch and snug keep only the return.

## How to run

```bash
chmod +x ./snug
./demo.sh
./snug --help
./snug -- python3 -m unittest discover -s tests -q
./snug --format patch -- pytest
./snug --list
./snug --base origin/main -- pytest
```

Python 3.10+, git. The user worktree is never rewritten.

## Empirical transcript

### Before the improvement (`27c8a9c`) — lockset matches cinch

`./demo.sh` exit 0 (13 cinch cases + unit tests).

Same dirty tree (debug print + return fix + new tests + README):

```
winnow wheat: app.py#1 (print("debug")) AND app.py#2 (return a + b)
cinch  wheat: app.py#2 only
snug   wheat: app.py#2 only
alibi  per-path: app.py LOCKED (whole file); test.py classified as production LOOSE
```

`--format patch` from both cinch and snug is the return line only:

```
--- a/app.py
+++ b/app.py
@@ -1,4 +1,4 @@
 def add(a, b):
     x = 0

-    return 0
+    return a + b
```

Trials=4, status=LOCKED, tests held, README ignored. Text reports match except the program name.

Cinch's listed failure reproduced: a **test-only red** suite (dirty `test.py` asserting `== 99`, production clean) is **CLEAN**, trials=0, `new_run` null. Both tools skip NEW when `production_units==0`.

### After the improvement (v0.2)

Always run NEW, even with zero production units.

Same test-only red fixture:

```
snug  status=BROKEN  exit=3  trials=1  held=test.py  wheat=[]
cinch status=CLEAN   exit=0  trials=0  (skipped test runs)
```

Test-only *green* (extra comment) stays CLEAN. Docs-only dirty stays CLEAN. Empty discover stays EMPTY. Debug-print lockset unchanged.

`./demo.sh` exit 0, now 14 cases including the cinch miss.

## Dogfood targets

- `tests/test_snug.py` + `./demo.sh` (14 cases, winnow / alibi / cinch contrast)
- The hybrid's own proof fixture (debug print vs return)
- Synthetic: joint files, LOOSE comment, CLEAN, BROKEN, intra-file hunk split, new-symbol wheat, ugly paths, docs-only, 1-minimal redundant hunks, pycache, EMPTY, test-only red

## Surprises

- winnow on the proof fixture does **not** mark `test.py` as wheat (comment-only, location-stripped fingerprint). It *does* keep the debug-print hunk. The contrast is stdout, not the test file.
- alibi `--per-path` still treats `test.py` as production. snug holds `test.py`. Two parents, two file-role bugs; we inherited the same test-path / source-extension heuristic observed via `--list` on a large dirty tree.
- `Package.swift` is production because the extension is `.swift`. `GNUmakefile` is other; `makefile` is production. `.mts` / `.cts` are other; `.ts` is production.
- detect_cmd: `Cargo.toml` and `Package.swift` beat pytest.ini; `justfile` / `Makefile` / `go.mod` do not. `package.json` scripts.test with vitest/jest get npx; any other test script becomes `npm test --silent`.
- splice of a new imported symbol is unbuildable; isolation still proceeds (LOCKED wheat = the add). That note is real: NEW is a copy of WIP, splice is a reconstruct from HEAD.

## Failures

- `--list` JSON unit order is path-sorted; text groups production / test / ignored. Harmless.
- Did not run `cargo test` / `swift test` / `vitest` splices on kizu/sitbone/voidtrace.
- Commands that consult the git index see a lie: we materialize a temp tree, never the index.
- Hunk apply is UTF-8 text; mixed hunks on a binary path fall back to whole-file.
- CLEAN after v0.2 still means "no production units and NEW passed." A docs-only tree with a failing default `unittest discover` would now be EMPTY/BROKEN depending on the detector — honest, a bit louder than cinch.

## Suggested mutations

- `--commit-wheat` / `--stash-chaff`: keep only the lockset.
- Coverage hint to pick a test subset before isolation.
- `--src` / `--ignore` globs (Package.swift, demo.sh, justfile).
- Body preview on `--list` / JSON so `@@ -0,0 +1 @@` shows the added line.
- Invert: largest production subset the tests do *not* lock (split an untested refactor out of a tested fix).
- `--cmd` recipes from `justfile` / `Makefile` without taking `just test` as a silent default.

## Kill / keep

**Keep.** The object survived a clean-room rebuild: demo case 1 is a tree on which winnow wheat is two hunks and snug/cinch wheat is one; alibi locks the whole file. The first improvement was forced by cinch's own listed failure (test-only red looks CLEAN). Kill only if a later generation proves that "run alibi --per-path then winnow the LOCKED files" recovers the lockset — it does not, because winnow's predicate is still the fingerprint.
