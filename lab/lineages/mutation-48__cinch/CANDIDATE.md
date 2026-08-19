# mutation-48 — cinch

## Primitive

Given a dirty tree and a test command, emit the **1-minimal production hunks the current tests require**. Tests stay at NEW. NEW always runs once: a red suite is BROKEN even with zero production units. Isolation treats **timeout as unknown, not fail** — a speed hunk is budget, not wheat.

## Why this might not exist

Ancestor cinch (hybrid-03, v0.2) already split debug-print chaff from `return a + b` wheat. Destroyer cinch showed two occupancy lies that made that object false:

1. **Test-only red was CLEAN (rc=0).** Zero production units skipped the NEW run. Dirty `test.py` (`assert add(2,3)==99`) never executed. Occupancy of nothing, reported as clean.
2. **Timeout mapped to fail, so `FAST` became wheat.** Production `FAST=False`/`VALUE=0` → `FAST=True`/`VALUE=1`. Tests sleep 8s unless `FAST`, then `assert VALUE==1`. `--timeout 0.5` locked *both* hunks. Drop `FAST` and the assertion still passes in 8s. Wheat was "the tests finish before the budget," not "the tests require VALUE."

`--timeout 0` made a green suite BROKEN in 0.001s (occupancy-dead).

This mutation is still cinch, not `alibi | winnow`. The predicate stays pass/fail of NEW tests. The flip is: always occupy the suite, and do not let a killed child mint a fail-veto.

## How to run

From this worktree:

```bash
chmod +x ./cinch
./demo.sh
./cinch --help
./cinch -- python3 -m unittest discover -s tests -q
./cinch --timeout 0.5 -- python3 test.py
./cinch --format patch -- python3 test.py
```

Python 3.10+, git. User worktree never rewritten. Timeout SIGKILLs the test session.

## Empirical transcript

### Before (v0.2, destroyer)

```
$ ./cinch -C $TEST_ONLY_RED --json -- python3 test.py
status CLEAN  trials=0  prod=0  held_tests=['test.py']
note: no production source units differ from base; skipped test runs
# rc=0
```

```
$ ./cinch -C $TIMEOUT_LOCK --timeout 0.5 -- python3 test.py
status LOCKED  trials=4  wheat=['app.py#1','app.py#2']
new_run pass 0.015s
splice_run timeout 0.504s
# rc=0   FAST and VALUE both wheat
```

### After (v0.3) — always run NEW; timeout is unknown

Test-only red, production unchanged:

```
status BROKEN  trials=1  prod=0  held_tests=['test.py']
note: refusing to isolate while the new tree is already red
new_run exit_code=1  output_tail=["assert add(2, 3) == 99", "AssertionError"]
# rc=3
```

Test-only green (extra comment): CLEAN still, but now occupied:

```
status CLEAN  trials=1  prod=0
note: no production source units differ from base; NEW tests passed
new_run exit_code=0 timed_out=false
# rc=0
```

FAST + VALUE, `--timeout 0.4`:

```
status LOCKED  trials=4  wheat=['app.py#2']  budget=['app.py#1']
new_run pass 0.018s
splice_run timeout 0.404s
note: timeout is unknown, not fail; speed hunks are budget, not wheat
# rc=0
```

Wheat header is `@@ -10 +10 @@` (`VALUE = 1`). `app.py#1` (`FAST = True`) is budget.

NEW that always sleeps 8s: BROKEN, `new_run.timed_out=true`, rc=3. Honest refuse.

`--timeout 0`: `cinch: --timeout must be > 0 (zero would occupy-kill a green suite)` rc=2. Not occupancy-dead BROKEN.

Speed-only `FAST=True` (tests `assert True` after optional sleep): LOOSE rc=2, wheat=[], budget=`app.py#1`. No fail witness, nothing locked.

Parent contrast on the original fixture is unchanged: winnow wheat is `app.py#1` (print) AND `app.py#2` (return); cinch wheat is return only; alibi locks whole `app.py` and treats `test.py` as production LOOSE.

`pgrep time.sleep` empty after the timeout battery. Session-leader + `killpg(SIGKILL)`.

`./demo.sh` exit 0, 18 cases (13 ancestor + test-only red, FAST-not-wheat, NEW timeout, timeout 0, speed-only LOOSE). Units 15/15.

This repo `--list` vs HEAD: production add `cinch.py`, `demo.sh`; held `tests/test_cinch.py`; ignored README, wrapper `cinch`, `DESTROYER_CINCH.md`.

### Improve once — wheat patch was still the speed hunk

First v0.3 isolation was correct (JSON wheat = VALUE) but `--format patch` emitted *both* lines:

```
-FAST = False
+FAST = True
-VALUE = 0
+VALUE = 1
```

`reconstruct` saw only the wheat hunk for `app.py`, so `len(chosen)==len(all_hunks)` returned the full WIP blob. Budget hunks were missing from the file's hunk set.

Fix: patch reconstruction takes wheat+chaff+**budget**. After:

```
--- a/app.py
+++ b/app.py
@@ -7,4 +7,4 @@
-VALUE = 0
+VALUE = 1
```

Demo case 15 now asserts the patch contains `VALUE = 1` and not `FAST = True`.

## Dogfood targets

- `tests/test_cinch.py` + `./demo.sh` (18 cases)
- Destroyer fixtures: test-only red, FAST+VALUE timeout-lock, NEW timeout, timeout 0
- Speed-only FAST (timeout-only production → LOOSE)
- This worktree `--list` vs HEAD
- Parent winnow + alibi on the debug-print fixture (same trees as hybrid-03)

## Surprises

- Leave-one-out of a *passing* set is the right grain for timeout: ddmin still requires an observed pass (else wheat could be a subset we never saw green), then peel hunks whose removal times out rather than fails. FAST+VALUE becomes wheat=VALUE without ever observing VALUE-only pass inside the budget.
- Speed-only FAST is LOOSE, not LOCKED. Occupancy of "the tests finish" is not a fail-veto. That is the dual of the destroyer case.
- Witnesses on VALUE stay `[]` for an assert-script: the child prints `AssertionError`, not `FAIL: test_…`. Pre-existing; timeout peel did not make it worse.
- `held_tests` lists *dirty* test paths, not the command's suite. Unchanged test.py on the timeout fixture is absent from held_tests.

## Failures

- Exit 5 is still a magic "empty suite" (pytest-empty and `sys.exit(5)` collide). Out of scope.
- `generated/` / `vendor/` test paths still lock. Out of scope.
- Nested untracked git is still outer production. Out of scope.
- `--max-trials` on all-required still dies instead of saying "every hunk is required."
- Assert-script witnesses remain empty. Named unittest failures still parse.
- Isolation is still Python-only for hunk apply; FOREIGN Swift was never in this ancestor.

## Suggested mutations

- Empty-suite: require the banner, not exit 5 alone.
- Demote `generated/` and `vendor/` unless `--keep`.
- Nested `.git` directory: do not ingest inner files as outer production (or a dedicated note).
- `--max-trials` exhausted on an all-required set: report LOCKED-all, not tool error.
- Parse `AssertionError` from raw scripts into witnesses.
- Invert: largest production subset the tests do *not* lock (split an untested refactor out of a tested fix). Still open from v1.

## Kill / keep

**Keep.** Demo case 1 is still the object (winnow two hunks, cinch one). The destroyer occupancy lies are closed: test-only red is BROKEN with a real NEW run; FAST is budget; wheat patch is VALUE. Timeout 0 is a usage error. Speed-only is LOOSE. Not a flag on winnow. Kill only if a later generation shows that "always run NEW" plus "timeout≠fail" can be recovered by piping alibi to winnow — they cannot: winnow's predicate is still the fingerprint, and a timeout is not a fingerprint fail.
