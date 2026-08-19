# cinch

Emit the **1-minimal production hunks the current tests require**.

Tests stay at NEW. They are the lock, never the wheat. Search only production. The predicate is pass/fail, not a command fingerprint.

This is not `alibi | winnow`. alibi reports whether the *whole* production diff is LOCKED (file grain at best). winnow 1-minimizes *every* uncommitted hunk against stdout. A new test file, a debug print, and a traceback line shift all change winnow's wheat. **cinch** asks: *which production hunks do these tests actually veto?*

## Install / run

Python 3.10+, git. No third-party packages.

```bash
chmod +x ./cinch
./cinch --help
./demo.sh
./cinch -- python3 -m unittest discover -s tests -q
./cinch --format patch -- pytest tests/test_foo.py
```

The user worktree is never rewritten. Each trial is a temp tree: tests@NEW, production reconstructed from a hunk subset.

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

### 2. Paths / patch for composition

```bash
./cinch --format paths -- pytest
# app.py
./cinch --format patch -- pytest > locked.patch
```

The patch is the production lockset, not the dirty tree.

### 3. Classify without running

```bash
./cinch --list
./cinch --base origin/main --list --json
```

Docs, lockfiles, and test paths are not production. A dirty `AGENTS.md` is ignored.

## Statuses and exit codes

| status        | meaning                                              | exit |
| ------------- | ---------------------------------------------------- | ---- |
| `LOCKED`      | 1-minimal production subset the tests require        | 0    |
| `CLEAN`       | no production unit differs from base                 | 0    |
| `LOOSE`       | tests still pass with every production hunk reverted | 2    |
| `BROKEN`      | tests already fail on the new tree                   | 3    |
| `UNBUILDABLE` | splice fails and no subset makes tests pass          | 4    |
| `EMPTY`       | test command collected no tests (not a red suite)    | 5    |

`--granularity file` coarsens to paths. `--keep REGEX` treats extra paths as tests (held, not searched).
