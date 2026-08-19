# hybrid-03 — cinch

## Primitive

Given a dirty tree and a test command, emit the **1-minimal production hunks the current tests require**. Tests stay at NEW (they are the lock, never wheat). The predicate is pass/fail, not a command fingerprint.

## Why this might not exist

alibi asks whether *the production diff as a whole* has an alibi (LOCKED/LOOSE), optionally per file. winnow asks which uncommitted hunks reproduce a command's *current behavior*. Piping them is the conventional hybrid and the wrong object.

The wheat of a test failure is not "hunks that change the test output." A new test file, a `print("debug")`, and a header comment all change output. The object is the **lockset**: the production hunks the new tests actually veto. Coverage says a line executed. alibi says the file is necessary. winnow says the hunk changed stdout. cinch says: *drop this hunk and the tests go red; drop that one and they stay green.*

Discarded as concatenation: `winnow --fingerprint exit` (still wheat-includes new tests), `alibi --per-path` then manually split hunks (file grain, leave-one-out not 1-minimal).

## How to run

From the worktree root:

```bash
chmod +x ./cinch
./demo.sh
./cinch --help
./cinch -- python3 -m unittest discover -s tests -q
./cinch --format patch -- pytest
./cinch --list
./cinch --base origin/main -- pytest
```

Python 3.10+, git. The user worktree is never rewritten.

## Empirical transcript

### v1 (`db76e4f`) — demo PASS, lockset ≠ fingerprint

`./demo.sh` exit 0. Cases: debug-print chaff, joint files, LOOSE, CLEAN, BROKEN, intra-file hunk split, new-symbol wheat, ugly paths, docs-only CLEAN, 1-minimal redundant hunks, pycache, user tree untouched.

Parent contrast on the same dirty tree (debug print + return fix + new tests + README):

```
winnow wheat: app.py#1 (print("debug")) AND app.py#2 (return a + b)
cinch  wheat: app.py#2 only
alibi  per-path: app.py LOCKED (whole file); test.py classified as production LOOSE
```

winnow's object is the fingerprint. The print changes stdout, so it is wheat. cinch's object is veto-power. Tests still pass without the print.

### Dogfood that v1 got wrong

tenaoshi clone, dirty `justfile` + `AGENTS.md`. Default `detect_cmd` falls through to `unittest discover -q`. Python 3.14:

```
Ran 0 tests in 0.000s
NO TESTS RAN
exit 5
```

v1 called that **BROKEN** and refused to isolate. The justfile hunk is real production; the suite is not red; there are no tests. alibi v1 hit the same exit-5 on itself.

Self vs HEAD: **CLEAN**. Comment at top of `cinch.py`: **LOOSE**, chaff `cinch.py#1`, tests held.

kizu clone, header comment + trailing `pub fn cinch_probe_marker()` in `src/app.rs`, noise in `src/config.rs` + README:

```
prod   3 production unit(s)
  production  modify src/app.rs  #1 @@ -0,0 +1 @@
  production  modify src/app.rs  #2 @@ -6128,0 +6130,2 @@ mod tests {
  production  modify src/config.rs  #1 @@ -368,0 +369 @@
  ignored     README.md
```

voidtrace: dirty `.ts` is production; `package.json` and README ignored. sitbone: `Package.swift` production; README ignored. skills: docs-only, production empty.

alibi copy (real tests). Header comment + `.toml` added to `SOURCE_EXTENSIONS` + new `test_toml_is_production` + README:

```
status LOCKED  trials 4
held   tests/test_alibi.py
ignored README.md
wheat  alibi.py#2  @@ -115,0 +117 @@ SOURCE_EXTENSIONS = {   locked by: test_toml_is_production
chaff  alibi.py#1  @@ -0,0 +1 @@     (header comment)
```

`--format patch` emitted only the `.toml` line. First attempt appended the test *after* `if __name__` so it never collected — that was operator error, not a cinch miss. Inserted into `PathHeuristics`, the lockset was exact.

### v2 — EMPTY ≠ BROKEN

`empty_suite()`: unittest/pytest exit 5, or `NO TESTS RAN` / `collected 0 items`. Status `EMPTY`, exit 5, do not isolate, tell the user to pass `--cmd`.

tenaoshi same dirty justfile after v2:

```
status EMPTY  exit 5
chaff  justfile#1
ignored AGENTS.md
note: test command collected no tests … not BROKEN — pass --cmd
```

`./demo.sh` still 0, now including case 13 (empty discover on a dirty `app.py`).

## Dogfood targets

- `tests/test_cinch.py` + `./demo.sh` (13 cases, parent winnow/alibi contrast)
- This repo vs `HEAD` (CLEAN / comment-only LOOSE)
- alibi worktree copy: `.toml` lockset vs header-comment chaff
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone,tenaoshi,voidtrace,skills}` clones (originals never mutated)

## Surprises

- winnow on the hybrid's own proof fixture did **not** mark `test.py` as wheat (comment-only, location-stripped fingerprint). It *did* keep the debug-print hunk. The contrast is stdout, not the test file.
- alibi `--per-path` still treats `test.py` as production (its regex wants `test_*.py`). cinch holds `test.py`. Two parents, two file-role bugs; we inherited alibi's source-extension heuristic and then had to add `^tests?\.py$`.
- `Package.swift` is production because the extension is `.swift`. Honest, a bit loud.
- First alibi dogfood was LOOSE with a "new test" that Python nested under `if __name__`. Isolation was correct; the suite never asked for `.toml`.

## Failures

- v1 tenaoshi: empty unittest → BROKEN. Fixed: EMPTY.
- CLEAN still skips the NEW run when there is no production unit. A test-only red suite looks CLEAN. (BROKEN requires a production unit in the fixture.)
- Did not run `cargo test` / `swift test` / `vitest` splices on kizu/sitbone/voidtrace: those suites are minutes × N hunks. `--list` classification only.
- Commands that consult the git index see a lie: we materialize a temp tree, never the index.
- Hunk apply is UTF-8 text; mixed hunks on a binary path fall back to whole-file.

## Suggested mutations

- Always run NEW, even with zero production units, so a test-only red suite is BROKEN not CLEAN.
- `--cmd` recipes from `justfile` / `Makefile` without taking `just test` as a silent default (tenaoshi e2e is not a unit suite).
- `--commit-wheat` / `--stash-chaff`: keep only the lockset.
- Coverage hint to pick a test subset before isolation.
- `--src` / `--ignore` globs (Package.swift, demo.sh, justfile).
- Body preview on `--list` / JSON so `@@ -0,0 +1 @@` shows the added line.
- Invert: largest production subset the tests do *not* lock (split an untested refactor out of a tested fix).

## Kill / keep

**Keep.** The object changed. Demo case 1 is a tree on which winnow wheat is two hunks and cinch wheat is one; alibi locks the whole file. alibi-copy dogfood produced a one-line `.toml` patch locked by a named test, with the header comment as chaff. v2 came from a real tenaoshi EMPTY, not a feature list. Kill only if a later generation proves that "run alibi --per-path then winnow the LOCKED files" recovers the lockset — it does not, because winnow's predicate is still the fingerprint.
