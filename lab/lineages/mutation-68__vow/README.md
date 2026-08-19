# vow

A failing assertion implies **two** oaths. Pair the expected-literal machine with the actual-side machine. The object is `EXPECTED-BOUND vs ACTUAL-BOUND` (or OPEN), not lees residue.

oath (mutation-44) named only the expected side. Comments containing HOME or a username are still not oaths. `assertEqual` / `XCTAssertEqual` / `#expect` second arguments, snapshot goldens, and pytest `expected=` still are.

## Install / run

Python 3.9+, stdlib only.

```bash
chmod +x ./vow
./vow --help
./demo.sh
./vow --self-test
```

## Three examples

### 1. Expected-bound vs actual-bound is two machines, not a substitution

```bash
./vow --from-fail < fixtures/pytest_fail.txt
# vow  pair  pytest  EXPECTED-BOUND vs ACTUAL-BOUND
#   expected /Users/alice/proj
#   actual   /home/runner/work/proj
#   host     NEITHER  this host is neither recorded machine
#   expected BOUND
#     require  HOME=/Users/alice
#     require  platform=Darwin
#     apply    [ "$(uname -s)" = Darwin ] && [ "${HOME}" = /Users/alice ]
#   actual   BOUND
#     require  HOME=/home/runner
#     require  CI=github-actions
#     apply    [ "$(uname -s)" = Linux ] && [ "${HOME}" = /home/runner ] && [ -n "${GITHUB_ACTIONS:-}" ]
```

lees `--par` would print `alice → runner` and an empty residue. vow keeps both unary skip/apply predicates.

The pair also names **this host's role**: `EXPECTED` (you are the oracle machine), `ACTUAL` (you produced the fail), `NEITHER`, or `BOTH`. OPEN sides are not identities, so a portable `/tmp` expected does not claim every host.

`--side actual --emit shell` prints the actual machine's apply predicate.

### 2. Actual is Alice, expected is a temp path

```bash
./vow --from-fail < fixtures/xctest_fail.txt
# vow  pair  xctest  EXPECTED-OPEN vs ACTUAL-BOUND
#   expected /tmp/x
#   actual   /Users/alice/Library
#   expected OPEN    apply true
#   actual   BOUND   HOME=/Users/alice  platform=Darwin

./vow --from-fail < fixtures/pytest_vv_tmp.txt
# same pair from pytest -vv  where got = / and expected =

./vow --from-fail < fixtures/junit_tmp.txt
# same pair from junit expected:<…> but was:<…>
```

oath `--from-fail` visad the expected `/tmp/x` and stayed silent about Alice. vow names the actual.

### 3. A comment is still not an oath. Sitbone stays FIXTURE.

```bash
./vow fixtures/comment_only.py
# vow  …  OPEN
#   silent   comment  USER=alice  ran on alice
#   apply    true

./vow fixtures/env_assert.py
# vow  …  BOUND  require USER=alice
#   silent   comment  USER=alice   ← seen, not required

./vow --from-fail < fixtures/comment_in_fail.txt
# # ran on alice in the dump does not bind
# pair  EXPECTED-OPEN vs ACTUAL-OPEN

./vow fixtures/title.swift
# FIXTURE  USER=annenpolka is identity-as-data, not a skip
```

`--scan -C sitbone` stays 0 BOUND / 4 FIXTURE. kizu comments about John Doe stay silent; quoting asserts are SPEC.

## Why this is not oath, not lees

oath asked "what machine does the expected literal demand?" and `--from-fail` threw the actual away. lees subtracted two transcripts and named the leftover. visa scanned the whole file. stain/admit walk production worlds.

vow's window is the failing assertion: two assertion-literal oaths, paired.
