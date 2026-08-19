# mutation-40 — mute

## Primitive

Production hunks in a **PR range** that **no NEW test locks**.

## Why this might not exist

hasp emits the 1-minimal production NEW tests require. Reviewers also need the complement: the production the PR changed that those new tests never look at — the debug print beside a fix, the refactor only old tests pin, the whole production-only PR.

cinch's invert would be "largest production the *current suite* does not lock" and still holds old tests. `alibi --per-path` then winnow is file grain and a fingerprint predicate (debug prints become wheat). Leftover-name hunting is a different object. mute is the MUTE subset of a LOCKED PR, plus the honest "entire production" when the range births no test.

## How to run

From the worktree root:

```bash
chmod +x ./mute
./demo.sh
./mute --help
./mute origin/main...HEAD
./mute --format patch main...HEAD
./mute --list --json main...HEAD
```

Python 3.10+, git. The user worktree is never rewritten. `A...B` is merge-base.

Exit 0 if mute is empty, 1 if any unlocked production, 2 on error.

## Empirical transcript

### v1 — demo PASS, object ≠ hasp

`./demo.sh` exit 0. Money shot (case 1): committed PR, clean worktree. `test_add` is new; `test_extra` was updated; debug print + `extra()` + `DEBUG` flipped.

```
mute locked: app.py#2  return a + b
mute mute:   app.py#1  print("debug")
             app.py#3  return 1     (extra)
             app.py#4  DEBUG = True
hasp wheat:  app.py#2  return a + b
hasp chaff:  app.py#1,#3,#4
cinch wheat: app.py#2 AND app.py#3   (old test_extra at NEW keeps extra())
exit 1
```

Required fixtures:

| case | result |
| --- | --- |
| new test locks add(), not debug print | MUTE reason=partial, exit 1, patch has print not `return a + b` |
| production-only PR (updated old assertion, no new name) | MUTE reason=no-new-tests, mute = entire production, exit 1 |
| tests-only PR | CLEAN, mute empty, exit 0 |
| every production hunk locked | LOCKED, mute empty, exit 0 |
| FOREIGN Swift names | listed, not exec'd, mute empty, exit 2 |

`--format patch` is the mute set. User tree never rewritten.

### v1 dogfood

Self vs HEAD (dirty mute sources, 13 new tests): **MUTE** in 4 trials. locked: `mute.py#1`. mute: `demo.sh#1`. **Bug:** wrapper `./mute` classified as ignored (`path_role` wants an extension). Tests import `mute.py`; the wrapper is untested — but it is production, not docs.

cinch `db76e4f...d7195b5`: **MUTE** in 12 trials. New tests: `EmptySuite.test_exit_5_is_empty`, `test_assertion_failure_is_not_empty`. locked: `EMPTY_SUITE_RE` and `def empty_suite`. mute: VERSION bump, format_human EMPTY copy, the *call site* `if empty_suite(new_run):` in `run_cinch`, EMPTY exit code, demo.sh case 13. The new tests lock the helper, not the wiring. Same split hasp reported as wheat/chaff; mute *is* that chaff.

hasp `0242ff6...6c09747`: **MUTE**. locked: `hasp.py`. mute: `demo.sh`. Wrapper `hasp` ignored (same extensionless miss).

tenaoshi dirty `--list`: **255 production, 131 named Swift tests** (`composesCrossBatchUnitsInOriginalOrder`, `generatedCasesLoad`, `oneCall`, …). Isolate: **FOREIGN** exit 2. Harness file is a fixture. Did not launch `swift test` × 255 hunks.

voidtrace `origin/main...HEAD`: **182 production, 51 named `it()` tests**, 241 background, 14 golden JSON/pkl fixtures (not the lock). Isolate: **FOREIGN** exit 2.

kizu / sitbone `origin/main...HEAD`: 0 production, 0 new tests — honest **CLEAN** exit 0.

### v2 — shebang wrappers are production, and mute

Forced by that dogfood, not a feature list:

**Extensionless `#!` files are production.** `./mute`, `./hasp`, `./tool` are no longer ignored. Isolation still pass/fail: tests that import `mute.py` do not lock the wrapper, so the wrapper is mute.

Re-runs:

- **Self isolate:** 3 production units. locked `mute.py#1`. mute `demo.sh#1` **and** `mute#1`. Wrapper left ignored? False.
- **hasp v1 range:** mute now includes `hasp#1` (the wrapper) plus `demo.sh`. locked still `hasp.py`.
- **hasp v2 `6c09747...9dfc5b1`:** new tests `LanguageNames.test_swift_testing_and_xctest` / `test_js_it_names` / `test_init_and_golden_are_not_runnable`. locked: `SWIFT_TEST_RE` and `swift_test_ids` (90 lines of extractors). mute: VERSION, format_human, FOREIGN status wiring, demo case 14, `--list` printers. The tests lock the names, not the FOREIGN refusal.
- **`./demo.sh`:** still 0, now 9 cases including shebang wrapper.

## Dogfood targets

- `tests/test_mute.py` + `./demo.sh` (15 unit tests, 9 demo cases, hasp/cinch contrast)
- This dirty worktree vs HEAD (wrapper ignored → wrapper mute)
- cinch `db76e4f...d7195b5`
- hasp `0242ff6...6c09747` and `6c09747...9dfc5b1`
- `/Users/annenpolka/ghq/github.com/annenpolka/{tenaoshi,kizu,sitbone,voidtrace}` `--list` + isolate (FOREIGN / CLEAN)

## Surprises

- cinch's EMPTY-suite *call site* is mute against the tests that commit added. A reviewer would ask for a test that sees status EMPTY. mute is that question as a patch.
- hasp v2's FOREIGN wiring is mute against the tests that commit added. Those tests lock `@Test func` extractors. The status code and `--list` printers are unlocked production.
- Self-dogfood mute set was `demo.sh` plus the wrapper, not "everything that is not mute.py". README/CANDIDATE stay ignored (not source). That is the object, not leftover-name.

## Failures

- Isolation still Python-only. FOREIGN is the honest refusal, not a Swift runner. `--cmd 'swift test'` would run the *whole* suite and collapse back to cinch's object.
- Commands that consult the git index see a lie: we materialize a temp tree, never the index.
- Hunk apply is UTF-8 text; mixed hunks on a binary path fall back to whole-file.
- `it("…")` names are the string, so a reworded assertion looks like a new test even when the body is old.
- kizu/sitbone vs `origin/main` were clean — no mute to report. Dirty-tree dogfood lived in tenaoshi/voidtrace/`--list`.

## Suggested mutations

- Per-new-test mute sets (leave-one-out of the new tests).
- Narrow `--cmd` for cargo/swift/vitest (`swift test --filter`, `vitest -t`) so FOREIGN can isolate.
- `--stash-mute` / `--commit-locked`: split the untested refactor out of the tested fix.
- Largest contiguous mute region a reviewer could peel into a second PR.
- `--keep` defaults that still hold `Package.swift` / `justfile` as production when they should be ignored.

## Kill / keep

**Keep.** The object changed. Demo case 1 is a committed PR on which hasp wheat is one hunk and mute is three; cinch wheat includes `extra()` because the old test is the lock. cinch-range dogfood produced a two-hunk `empty_suite` lockset with VERSION/demo.sh/call-site as mute. v2 came from this tool's own wrapper being ignored, not from concatenating `--lang sh`. Kill only if a later generation proves that `hasp --format patch` then `git diff | subtract` recovers the mute set — it does not, because mute's exit is the presence of unlocked production, and a production-only PR has no hasp wheat to subtract from.
