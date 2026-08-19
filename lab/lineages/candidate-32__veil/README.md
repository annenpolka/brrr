# veil

A Unix command nobody invented: **did the tests actually look at this production change, or did they mock it away?**

Coverage says a line executed. `alibi` asks whether the suite goes red without the production tree. `veil` asks a different review question, statically:

> For each changed production name, is there a test that live-calls it, a test that only ever sees a mock of it, or no test that cites it at all?

```
LIVE    tests call / import the name without mocking it
VEIL    the only test relationship is a mock of the name or its module
BARE    no test cites it and no test mocks it
```

The object is a **cover-type**. The verb is the join of a production diff to the test suite's mocks and citations.

## Install / run

Python 3.10+, git, stdlib only.

```bash
chmod +x ./veil
./veil --help
./veil --self-test
./demo.sh
```

## Three examples

### 1. Review the dirty tree against HEAD

```bash
./veil
./veil --explain
./veil --check          # exit 1 if any VEIL or BARE
```

A comment-only edit is `CLEAN` (no production names changed). A new `retry_budget` helper that no test names is `BARE`. A test that `@patch('shop.checkout')` after you just rewrote `checkout` is `VEIL`.

### 2. Review a commit range (a PR)

```bash
./veil --from origin/main --to HEAD
./veil --from HEAD~3 --to HEAD --porcelain
./veil --from HEAD~3 --to HEAD --json | jq '.names[] | select(.status=="VEIL")'
```

`--porcelain` is a stable TSV: `STATUS  QUALNAME  FILE  TEST  VIA`.

Unexported helpers that no test cites are hidden (they drowned the report). `--all-names` brings them back. Unexported names that are **VEIL** still show: a mock of a hidden helper is the whole point.

### 3. The ugly fixture (spaces, unicode, nested git, JS module mock)

```bash
./demo.sh
# or:
./veil --self-test
```

Self-test builds a tiny repo where `add` is LIVE, `checkout` is VEIL (`@patch('shop.checkout')`), `retry_budget` is BARE, and `vi.mock('./loader.js')` veils `loadTemplate` while `compose` stays LIVE.

## Output

| status   | meaning                                      | `--check` |
| -------- | -------------------------------------------- | --------- |
| `CLEAN`  | no changed production names                  | 0         |
| `COVERED`| every changed name has a live test           | 0         |
| `THEATER`| some name is only mocked, none are bare      | 1         |
| `EXPOSED`| some name is uncited                         | 1         |
| `OPEN`   | both VEIL and BARE are present               | 1         |

Production means source files (`.py`, `.ts`, `.rs`, `.swift`, …). Tests, fixtures, goldens, and docs are not production. Nested `.git` directories are ignored.

## Not this

- Not leftover names of deleted symbols (`wraith` / `haunt`)
- Not inverse printf (`unfmt`)
- Not wait-for / process graphs (`hitch` / `spoor`)
- Not “run the tests on the old tree” (`alibi`) — veil does not run tests
- Not hunk-to-test impact analysis — the mock is first-class
