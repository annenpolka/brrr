# hasp

Emit the **1-minimal production hunks that NEW tests in a PR range lock** against old production.

This is not cinch. cinch holds the *whole current suite* at NEW and 1-minimizes a dirty tree. An updated old test will keep production it now requires. **hasp** takes a *range* (`main...HEAD`, two git trees, not a dirty worktree) and uses only tests that *appear* in that range as the lock. Production that only old tests require is chaff. A range with production and no new tests is **MUTE**.

## Install / run

Python 3.10+, git. No third-party packages.

```bash
chmod +x ./hasp
./hasp --help
./demo.sh
./hasp origin/main...HEAD
./hasp --format patch main...HEAD > locked.patch
./hasp --list main...HEAD
```

The user worktree is never rewritten. Each trial is a temp tree: new tests @ NEW, production reconstructed from a hunk subset of the range.

## Three examples

### 1. A committed PR, clean worktree

`add()` is the real fix. `extra()` was refactored and the *old* test updated. A debug flag flipped. Only `test_add` is new.

```bash
./hasp main...HEAD
```

```
hasp   range=main...HEAD  status=LOCKED  trials=6
new tests (the lock; only these run):
  tests/test_app.py::TestApp.test_add
background tests (in range, not the lock, not run):
  tests/test_app.py::TestApp.test_extra
wheat (1 units / 1 files):
  modify app.py  #1 @@ -2 +2 @@     + return a + b
chaff (2 units / 1 files):
  modify app.py  #2 @@ -15 +15 @@    + return 1
  modify app.py  #3 @@ -26 +26 @@    + DEBUG = True
```

`./hasp` with no range on the same clean branch is **CLEAN**: HEAD vs worktree is empty. The object is the range.

cinch `--base main` on the same tree keeps `extra()` because `test_extra` at NEW requires it. alibi reports the whole production diff LOCKED.

### 2. MUTE: production with no new tests

The PR updates `extra()` and the existing test. Nothing named `test_*` is born.

```bash
./hasp main...HEAD; echo $?
# status MUTE  exit 6
# new tests: (empty)
# background: TestApp.test_extra
```

cinch LOCKED. hasp refuses to treat an updated old test as an alibi.

### 3. Paths / patch for composition

```bash
./hasp --format paths origin/main...HEAD
# app.py
./hasp --format patch origin/main...HEAD > locked.patch
./hasp --list --json main...HEAD | jq '.new_tests'
```

The patch is the production the new tests actually veto, not the PR.

## Statuses and exit codes

| status        | meaning                                                        | exit |
| ------------- | -------------------------------------------------------------- | ---- |
| `LOCKED`      | 1-minimal production subset the new tests require              | 0    |
| `CLEAN`       | no production unit differs in the range                        | 0    |
| `LOOSE`       | new tests still pass on old production                         | 2    |
| `BROKEN`      | new tests already fail on the new tree                         | 3    |
| `UNBUILDABLE` | no production subset makes the new tests load                  | 4    |
| `EMPTY`       | new-test command collected no tests                            | 5    |
| `MUTE`        | production changed; no new tests in the range                  | 6    |
| `FOREIGN`     | new tests exist but none are Python-runnable                   | 7    |

`A...B` is merge-base (the PR). `A..B` is two-dot. `hasp main` is `main...worktree`.

New tests are named functions born in the range (Python `test_*`, Swift `@Test`/`func test*`, JS/TS `it()`/`test()`, Rust `fn test_*`, Go `func Test*`). Golden files and `__init__.py` are fixtures, not the lock. Non-Python names are listed; isolation without `--cmd` is FOREIGN.
