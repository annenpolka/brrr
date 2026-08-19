# cinch

Emit the **1-minimal production hunks the current tests require**.

Tests stay at NEW. They are the lock, never the wheat. Search only production. The predicate is pass/fail, not a command fingerprint.

This is not `alibi | winnow`. alibi reports whether the *whole* production diff is LOCKED (file grain at best). winnow 1-minimizes *every* uncommitted hunk against stdout. A new test file, a debug print, and a traceback line shift all change winnow's wheat. **cinch** asks: *which production hunks do these tests actually veto?*

Mutation-48 (v0.3): **always run NEW once**. A test-only red suite is BROKEN, not CLEAN. Isolation treats **timeout as unknown, not fail** — a `FAST` speed hunk must not become wheat.

## Install / run

Python 3.10+, git. No third-party packages.

```bash
chmod +x ./cinch
./cinch --help
./demo.sh
./cinch -- python3 -m unittest discover -s tests -q
./cinch --format patch -- pytest tests/test_foo.py
```

The user worktree is never rewritten. Each trial is a temp tree: tests@NEW, production reconstructed from a hunk subset. The test process is a session leader; timeout SIGKILLs the group.

## Three examples

### 1. Mixed WIP: fix + debug print + new tests + README

```bash
./cinch -- python3 test.py
```

```
cinch  base=HEAD (a1b2c3d4e5f6)  status=LOCKED  trials=6
cmd    python3 test.py
held tests (always NEW, never wheat):
  test.py
ignored (not production source):
  README.md
wheat (1 units / 1 files):
  modify app.py  #2 @@ -4 +4 @@     return a + b
chaff (1 units / 1 files):
  modify app.py  #1 @@ -2 +2 @@     print("debug")
```

winnow on the same command keeps the debug print (stdout changed) and often `test.py`. alibi `--per-path` marks all of `app.py` LOCKED.

### 2. Test-only red is occupancy of the suite, not a free CLEAN

Dirty `test.py` (`assert add(2,3)==99`), production unchanged:

```bash
./cinch --json -- python3 test.py
# status BROKEN  trials=1  prod=0  held_tests=['test.py']  rc=3
```

v0.2 skipped the NEW run when production was empty and reported CLEAN. v0.3 always executes NEW tests once.

### 3. Timeout is unknown — a speed hunk is not wheat

`FAST=True` plus `VALUE=1`. Tests sleep 8s unless `FAST`, then `assert VALUE==1`. `--timeout 0.5`:

```
status LOCKED  wheat=['app.py#2']  budget=['app.py#1']
# FAST timed out when dropped; VALUE failed when dropped.
```

`--format paths` still prints only wheat (`app.py`). `--timeout 0` is a usage error (rc=2), not occupancy-dead BROKEN.

## Statuses and exit codes

| status        | meaning                                                                 | exit |
| ------------- | ----------------------------------------------------------------------- | ---- |
| `LOCKED`      | 1-minimal production subset with a fail veto                            | 0    |
| `CLEAN`       | no production unit differs from base; NEW tests ran and passed          | 0    |
| `LOOSE`       | tests still pass with every production hunk reverted (or timeout-only)  | 2    |
| `BROKEN`      | tests already fail *or time out* on the new tree                        | 3    |
| `UNBUILDABLE` | splice fails and no subset makes tests pass                             | 4    |
| `EMPTY`       | test command collected no tests (not a red suite)                       | 5    |

`--granularity file` coarsens to paths. `--keep REGEX` treats extra paths as tests (held, not searched).
