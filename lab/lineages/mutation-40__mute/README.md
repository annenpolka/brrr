# mute

Emit the **production hunks in a PR range that no NEW test locks**.

This is not hasp inverted as a flag. hasp's product is the 1-minimal production *new tests require*. **mute** is the complementary object: production the PR changed that those new tests never look at.

An updated old assertion is not a new test. A debug print is mute (pass/fail, not a fingerprint). A production-only PR with no new tests is MUTE (the entire production range). A tests-only PR is empty mute.

## Install / run

Python 3.10+, git. No third-party packages.

```bash
chmod +x ./mute
./mute --help
./demo.sh
./mute origin/main...HEAD
./mute --format patch main...HEAD > mute.patch
./mute --list main...HEAD
```

The user worktree is never rewritten. Each trial is a temp tree: new tests @ NEW, production reconstructed from a hunk subset of the range.

`A...B` is merge-base (the PR). `A..B` is two-dot. `mute main` is `main...worktree`.

## Three examples

### 1. New test locks `add()`, not the debug print

`add()` is the real fix. A `print("debug")` landed next to it. `extra()` was refactored and the *old* test updated. Only `test_add` is new.

```bash
./mute main...HEAD; echo $?
```

```
mute   range=main...HEAD  status=MUTE  reason=partial
new tests (the lock; only these run):
  tests/test_app.py::TestApp.test_add
background tests (in range, not the lock, not run):
  tests/test_app.py::TestApp.test_extra
mute (3 units / 1 files)  — the product:
  modify app.py  #1  + print("debug")
  modify app.py  #3  + return 1
  modify app.py  #4  + DEBUG = True
locked (1 units / 1 files)  — new tests require:
  modify app.py  #2  + return a + b
```

Exit **1**: there is unlocked production. hasp on the same range exits 0 with wheat=`add()`. cinch holds the whole suite, so `extra()` is locked too.

### 2. Production-only PR is MUTE

The PR updates production (and maybe an old assertion). Nothing named `test_*` is born.

```bash
./mute main...HEAD; echo $?
# status MUTE  reason=no-new-tests  exit 1
# mute = entire production range
# locked = (empty)
```

### 3. Tests-only PR is empty mute

```bash
./mute main...HEAD; echo $?
# status CLEAN  exit 0
# mute = (empty)
# production_units = 0
```

`--format patch` of an empty mute is empty. Exit 0 means every production hunk is locked (or there is none).

## Statuses and exit codes

| status        | meaning                                              | exit |
| ------------- | ---------------------------------------------------- | ---- |
| `LOCKED`      | production exists; new tests lock all of it          | 0    |
| `CLEAN`       | no production units in the range                     | 0    |
| `MUTE`        | unlocked production (the product is non-empty)       | 1    |
| `BROKEN`      | new tests already fail on the new tree               | 2    |
| `UNBUILDABLE` | no production subset makes the new tests load        | 2    |
| `EMPTY`       | new-test command collected no tests                  | 2    |
| `FOREIGN`     | new tests exist but none are Python-runnable         | 2    |

`MUTE` reasons: `no-new-tests` (production-only), `loose` (new tests already true on old production), `partial` (some hunks locked, some not).

New tests are named functions born in the range. Golden files and `__init__.py` are fixtures, not the lock. Isolation runs only those new Python names — never the historical suite.

Extensionless shebang scripts (`./mute`, `./hasp`) are production. Tests that import `mute.py` do not lock the wrapper; the wrapper is mute.
