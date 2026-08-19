# tock

Emit the **1-minimal production hunks the current tests require**.

Tests stay at NEW. They are the lock, never the wheat. Search only production. The predicate is pass/fail of the suite, not a command fingerprint.

`tock` is a mutation of `snug` (reimpl-06): same lockset object, same always-run-NEW rule (test-only red is BROKEN). After the first improvement, a **splice timeout is unknown**, not fail — a speed hunk must not become wheat.

## Install / run

Python 3.10+, git. No third-party packages.

```bash
chmod +x ./tock
./tock --help
./demo.sh
./tock -- python3 -m unittest discover -s tests -q
./tock --format patch -- pytest tests/test_foo.py
./tock --timeout 0.5 -- python3 test.py
```

The user worktree is never rewritten. Each trial is a temp tree: tests@NEW, production reconstructed from a hunk subset.

## Three examples

### 1. Mixed WIP: fix + debug print + new tests + README

```bash
./tock -- python3 test.py
```

```
tock  base=HEAD (a1b2c3d4e5f6)  status=LOCKED  trials=4
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

### 2. FAST hunk under a tight `--timeout`

Production flips `FAST=False`→`True` and `VALUE=0`→`1`. Tests sleep unless `FAST`, then `assert VALUE==1`.

cinch/snug map timeout→fail, so **both** hunks are wheat: the tests finishing before the budget is treated as a veto. tock treats a timed-out splice as an error, not guilt. Wheat is `VALUE` only. `FAST` is chaff.

```bash
./tock --timeout 0.5 -- python3 test.py
```

### 3. Paths / patch for composition

```bash
./tock --format paths -- pytest
# app.py
./tock --format patch -- pytest > locked.patch
```

## Statuses and exit codes

| status        | meaning                                              | exit |
| ------------- | ---------------------------------------------------- | ---- |
| `LOCKED`      | 1-minimal production subset the tests require        | 0    |
| `CLEAN`       | no production unit differs from base (and tests pass)| 0    |
| `LOOSE`       | tests still pass with every production hunk reverted | 2    |
| `BROKEN`      | tests already fail (or time out) on the new tree     | 3    |
| `UNBUILDABLE` | splice fails and no subset makes tests pass          | 4    |
| `EMPTY`       | test command collected no tests (not a red suite)    | 5    |
| `TIMEOUT`     | a splice trial timed out; timeout must not mint wheat| 6    |
