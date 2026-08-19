# alibi

Transplant **current tests** onto **another revision's production sources**. If the tests fail, the production diff is **LOCKED** — it has an alibi. If they still pass, the production diff is **LOOSE**: nothing in the suite actually vetoes the old code.

This is not coverage. A line can execute and still assert nothing. `alibi` asks the question TDD implies and CI almost never runs: *would these tests go red without that production change?*

## Install / run

Python 3.10+, git, no third-party packages.

```bash
./alibi --help
./alibi                  # splice HEAD production under the worktree's tests
./alibi origin/main      # splice main's production under current tests
./alibi HEAD --json
```

Default test command is auto-detected (`unittest`, `pytest`, `cargo test`, `vitest`/`jest`, `swift test`). Override with `--cmd`.

## Three examples

### 1. Uncommitted feature vs HEAD

You just implemented `add` and wrote a test. Does the test actually depend on the new code?

```bash
./alibi HEAD --cmd 'python3 -m unittest discover -q'
```

```
alibi  base=HEAD (a1b2c3d4e5f6)  new=worktree  status=LOCKED
cmd    python3 -m unittest discover -q
prod   1 path(s) differ from base (non-test)
         adder.py
NEW    pass         0.04s
SPLICE fail(1)      0.04s   (tests@new, production@base)

tests veto base production — the production diff is witnessed
witnesses:
  test_sum
```

A comment-only edit of `adder.py` with the same tests yields `LOOSE`.

### 2. Pull request vs main

Keep current tests (including new ones). Replace every non-test file with `origin/main`. Expect red.

```bash
./alibi origin/main --cmd 'cargo test --offline --quiet'
```

`CLEAN` means production already matches main (test-only PR). `BROKEN` means the suite is already red on the PR tree — fix that first. `UNBUILDABLE` means the new tests cannot even load against main's API.

### 3. Inspect the splice without running

```bash
./alibi HEAD --list
./alibi HEAD --list --json | jq '.production_changed'
```

`--keep REGEX` treats extra paths as tests (they stay at the new revision). `--per-path` leave-one-out attributes LOCKED/LOOSE to each changed production file (N extra test runs).

Production means *source* (`.py`, `.rs`, `.ts`, `.swift`, …). Markdown, lockfiles, and gitignore stay at the new tree and do not create a fake LOOSE/LOCKED. Fixture/golden/snapshot directories count as tests.

## Statuses and exit codes

| status        | meaning                                              | exit |
| ------------- | ---------------------------------------------------- | ---- |
| `LOCKED`      | tests fail on base production                        | 0    |
| `CLEAN`       | no production file differs from base                 | 0    |
| `LOOSE`       | tests still pass on base production                  | 2    |
| `BROKEN`      | tests already fail on the new tree                   | 3    |
| `UNBUILDABLE` | spliced tree cannot load/compile the tests           | 4    |

Compose: `./alibi origin/main --json; echo $?`
