# hybrid-06 — hasp

## Primitive

Given a **PR range** (two revisions, not a dirty tree), emit the **1-minimal production hunks that NEW tests in that range lock** against old production.

## Why this might not exist

cinch already joins alibi+winnow: the whole current suite stays at NEW; production hunks of a dirty tree are 1-minimized by pass/fail. That is the wrong object for a pull request.

A PR is a range (`main...HEAD`), often with a clean worktree. cinch without `--base` is CLEAN on that tree. cinch *with* `--base main` still holds the **whole suite**, so an updated old test keeps production it now requires. alibi is binary LOCKED/LOOSE on the whole production diff.

The reviewer question is: *which production hunks do the tests this PR actually added veto?* An updated assertion is not a new test. A refactor that only old tests pin is not the PR's lockset. A production-only PR with no new test names is MUTE, not LOCKED.

Discarded as concatenation: `cinch --base main --only-new-tests` (the range is still a dirty-tree diff; old tests still run unless the command is rewritten). `alibi --per-path` then winnow (file grain, fingerprint predicate). Discovering *which tests were born in the range* is the object.

## How to run

From the worktree root:

```bash
chmod +x ./hasp
./demo.sh
./hasp --help
./hasp origin/main...HEAD
./hasp --format patch main...HEAD
./hasp --list --json main...HEAD
./hasp main
```

Python 3.10+, git. The user worktree is never rewritten. `A...B` is merge-base (the PR). `A..B` is two-dot. `hasp main` is `main...worktree`.

## Empirical transcript

### v1 (`6c09747`) — demo PASS, object ≠ cinch

`./demo.sh` exit 0 (13 cases). Money shots:

**Case 1.** Committed PR, clean worktree. `test_add` is new; `test_extra` was updated to match a refactor; DEBUG flipped.

```
hasp wheat:  app.py#1  return a + b
hasp chaff:  app.py#2  return 1     (extra)
             app.py#3  DEBUG = True
hasp new:    TestApp.test_add
hasp bg:     TestApp.test_extra
cinch wheat: app.py#1 AND app.py#2   (old test_extra at NEW keeps extra())
alibi:       LOCKED app.py           (whole file)
./hasp          on the same clean branch: CLEAN  (HEAD vs worktree is empty)
./hasp main...HEAD: LOCKED
```

**Case 2.** Same production + updated old test, no new `test_*` name.

```
hasp:  MUTE exit 6
cinch: LOCKED app.py#2 (extra)
```

Self vs `main` (`0242ff6...6c09747`): **LOCKED**. `hasp.py` wheat, `demo.sh` chaff. Wrapper `hasp` ignored (no extension). **Bug:** `tests/__init__.py::<module>` counted as a new test and was exec'd.

cinch `db76e4f...d7195b5` (EMPTY-suite commit): **LOCKED** in 12 trials. New tests: `EmptySuite.test_exit_5_is_empty`, `test_assertion_failure_is_not_empty`. Wheat: `EMPTY_SUITE_RE` and `def empty_suite`. Chaff: VERSION bump, format_human EMPTY copy, the *call site* in `run_cinch`, EMPTY exit code, demo.sh case 13. The new tests assert the helper, not the wiring. Honest.

alibi `fa08ea3...f433c1d`: **LOCKED** in 27 trials. 3 new tests, 22 background. Wheat: `FIXTURE_DIR_NAMES`, fixture dir check, `is_source_path`/`path_role`, `production_changed` filter. Chaff: detect_cmd `-s tests`, materialize plumbing, demo.sh.

tenaoshi dirty `--list`: **15 new tests, all `<module>`**, whole Swift files. voidtrace `origin/main...HEAD`: **14 new tests**, all golden JSON/pkl `::<module>`. JSON `cmd` leaked a deleted sandbox path. Witnesses duplicated `_hasp_tests_test_cinch_py.EmptySuite.*`.

### v2 — named tests, not `<module>`; fixtures are not the lock

Forced by that dogfood, not a feature list:

1. **Language-aware names.** Swift `@Test func`, XCTest `func test*`, JS/TS `it()`/`test()`, Rust `fn test_*`, Go `func Test*`. Python AST unchanged.
2. **Fixtures are not new tests.** `__init__.py`, `conftest.py`, golden JSON, pkl, harness files without names → `new_fixtures` (held, not run).
3. **FOREIGN.** If every new test is non-Python, do not exec Swift as Python. `--list` is the report. Exit 7.
4. **Stable `cmd`.** `["hasp-run", "path::Test.test_name", …]`. Witnesses drop the `_hasp_*` module prefix.

Re-runs:

- **Self `--list`:** 11 named tests, `tests/__init__.py` is a fixture, not a lock.
- **cinch range:** still LOCKED, wheat still the two `empty_suite` hunks. `cmd` is `hasp-run tests/test_cinch.py::EmptySuite.test_exit_5_is_empty …`. Witnesses `EmptySuite.test_*`.
- **tenaoshi dirty `--list`:** 15 `<module>` files → **131 named Swift tests** (`composesCrossBatchUnitsInOriginalOrder`, `generatedCasesLoad`, `oneCall`, …). Isolate: **FOREIGN** (`131 new test(s) are not Python (swift)`). Harness file is a fixture. Did not launch `swift test` × 255 hunks.
- **voidtrace `origin/main...HEAD`:** 14 fake goldens → **51 named `it()` tests** (`round-trips Forced Slash Direct Hit…`, `matches the independently authored Shield-then-Health Direct Hit…`). 14 goldens moved to fixtures. 0 `<module>`.
- **`./demo.sh`:** still 0, now 14 cases including FOREIGN Swift names.

kizu/sitbone/skills: 0 production, 0 new tests (honest CLEAN). Did not mutate those clones.

## Dogfood targets

- `tests/test_hasp.py` + `./demo.sh` (14 cases, cinch/alibi contrast)
- This repo vs `main` (0242ff6…HEAD)
- cinch `db76e4f...d7195b5`
- alibi `fa08ea3...f433c1d`
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone,tenaoshi,voidtrace,skills}` `--list`; tenaoshi isolate (FOREIGN)

## Surprises

- cinch's EMPTY-suite *call site* is chaff against the tests that commit added. The tests lock `empty_suite()`, not `run_cinch`. A reviewer would ask for a test that sees status EMPTY.
- `specs/` is a test directory in the inherited heuristic, so voidtrace pkl was "tests". v2 demotes them to fixtures; they stay at NEW, they are not the lock.
- tenaoshi uses Swift Testing (`@Test func composes…`), not XCTest `func test*`. The `@Test` regex was the whole improvement; `func test` alone would have missed almost every name.

## Failures

- Isolation still Python-only. FOREIGN is the honest refusal, not a Swift runner. `--cmd 'swift test'` would run the *whole* suite and collapse back to cinch's object.
- Extensionless `hasp` wrapper is ignored (not a source extension). Tests import `hasp.py`; the wrapper is untested. Fine.
- Commands that consult the git index see a lie: we materialize a temp tree, never the index.
- Hunk apply is UTF-8 text; mixed hunks on a binary path fall back to whole-file.
- `it("…")` names are the string, so a reworded assertion looks like a new test even when the body is old.

## Suggested mutations

- Per-new-test locksets (leave-one-out of the new tests).
- Narrow `--cmd` for cargo/swift/vitest (`swift test --filter`, `vitest -t`) so FOREIGN can isolate.
- `--commit-wheat` / `--stash-chaff`.
- Invert: production in the range that no new test locks (the MUTE subset of a LOCKED PR).
- Treat extensionless shebang scripts as production.

## Kill / keep

**Keep.** The object changed. Demo case 1 is a committed PR on which cinch wheat is two hunks and hasp wheat is one; case 2 is MUTE for hasp / LOCKED for cinch. cinch-range dogfood produced a two-hunk `empty_suite` patch locked by two named tests, with VERSION/demo.sh/call-site as chaff. v2 came from tenaoshi's 15 `<module>` files and voidtrace's golden JSON "tests", not from concatenating `--lang swift`. Kill only if a later generation proves that `cinch --base main` plus a hand-narrowed pytest nodeid recovers the lockset — it does not, because discovering which tests were *born in the range* is the object.
