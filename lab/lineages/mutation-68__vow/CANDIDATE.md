# mutation-68 — vow

## Primitive

Infer a vow from the **actual side** of a failing assertion and **pair** it with the expected-literal oath: two oaths (`EXPECTED-BOUND` vs `ACTUAL-BOUND` vs `OPEN`), not lees residue. Comments are not oaths.

## Why this might not exist

oath (mutation-44) flipped visa's whole-file scan to assertion literals. It still `--from-fail`ed only the *expected* side. A red XCTest that printed `("/Users/alice/Library") is not equal to ("/tmp/x")` became an empty OPEN tmp oath. The actual machine that produced the fail was discarded.

lees (candidate-31) named the leftover as a substitution: `PATH /Users/alice → /home/runner`, empty residue, verdict MACHINE. That is one bool-shaped story. The daily loop is two skip/apply predicates: "the golden demands Alice" and "this run was the runner". Nobody emits both as objects.

Discarded: becoming stain/admit (production worlds × visa). Discarded: treating `# ran on alice` as an oath. Discarded: wrapping `uname` or emitting a Dockerfile.

## How to run

From this worktree root:

```bash
./demo.sh
./vow --help
./vow --self-test
python3 -m unittest discover -s tests -q
./vow fixtures/comment_only.py
./vow fixtures/env_assert.py
./vow --from-fail < fixtures/pytest_fail.txt
./vow --from-fail < fixtures/xctest_fail.txt
./vow --from-fail --side actual --emit shell < fixtures/pytest_fail.txt
./vow --scan -C /path/to/repo --porcelain
```

## Empirical transcript

### v0.1 (`ea3988c`) — the pair is the object

`./vow --self-test` 60/60. Unittest 30/30. `./demo.sh` passed=50 failed=0.

```
$ ./vow --from-fail < fixtures/pytest_fail.txt
vow  pair  pytest  EXPECTED-BOUND vs ACTUAL-BOUND
  expected /Users/alice/proj
  actual   /home/runner/work/proj
  expected BOUND
    require  HOME=/Users/alice
    require  platform=Darwin
    apply    [ "$(uname -s)" = Darwin ] && [ "${HOME}" = /Users/alice ]
  actual   BOUND
    require  HOME=/home/runner
    require  CI=github-actions
    apply    [ "$(uname -s)" = Linux ] && [ "${HOME}" = /home/runner ] && …

$ ./vow --from-fail < fixtures/xctest_fail.txt
vow  pair  xctest  EXPECTED-OPEN vs ACTUAL-BOUND
  expected /tmp/x
  actual   /Users/alice/Library
  expected OPEN     apply true
  actual   BOUND    HOME=/Users/alice platform=Darwin
```

oath on the same XCTest dump visad `/tmp/x` (or, with inverted polarity, only Alice as expected). vow uses Apple's actual-first order and keeps both sides.

pytest `-vv` `where got =` / `and expected =` and junit `expected:<tmp> but was:<alice>` produce the same `EXPECTED-OPEN vs ACTUAL-BOUND`. `# ran on alice` in `comment_in_fail.txt` stays `EXPECTED-OPEN vs ACTUAL-OPEN`.

Unary gold (oath window, unchanged):

```
# ran on alice          → OPEN, silent comment USER=alice
assert os.environ['USER'] == 'alice'  → BOUND require USER=alice
title.swift             → FIXTURE USER=annenpolka, require empty
payload.rs              → SPEC (John Doe /home/user quoting)
```

Dogfood `--scan` (this host, 2026-08-20):

| repo    | BOUND | OPEN | SPEC | UNSAT | FIXTURE | note |
| ------- | ----- | ---- | ---- | ----- | ------- | ---- |
| sitbone | **0** | 21   | 0    | 0     | 4       | title fixture, not TAINTED |
| kizu    | 0     | 13   | 2    | 0     | 0       | comments silent; quoting SPEC |

sitbone `WindowTitleParserTests` USER empty, status FIXTURE. kizu `init/tests.rs` HOME empty, status SPEC.

### v0.2 — this host's role in the pair

v0.1 named two machines and stopped. `--apply` still talked only to the expected side. A dump whose actual is *this* `$HOME` and expected is `/tmp/x` did not say "you produced the fail".

After: every `--from-fail` pair names `host` `EXPECTED` | `ACTUAL` | `NEITHER` | `BOTH`. OPEN/SPEC/FIXTURE always MATCH, so they are not identities — only a BOUND side that holds can name the host.

```
$ ./vow --from-fail < fixtures/pytest_fail.txt
vow  pair  pytest  EXPECTED-BOUND vs ACTUAL-BOUND
  host     NEITHER  this host is neither recorded machine   # not alice, not runner

$ printf 'E   - /tmp/x\nE   + %s/proj\n' "$HOME" | ./vow --from-fail
vow  pair  pytest  EXPECTED-OPEN vs ACTUAL-BOUND
  host     ACTUAL  this host produced the fail
```

`--apply` stays expected-side (a portable `/tmp` golden still applies everywhere). The role is the new object, not a third exit code.

Also: an XCTest dump line is no longer reused as `source` (`XCTAssertEqual failed: … is not equal to`).

`./demo.sh` → passed=54 failed=0. Unittest 32/32. Self-test 64/64.

## Dogfood targets

- `fixtures/` — comment vs env-assert, alice/CI snaps, sitbone-shaped title, kizu quoting payload, pytest/cargo/jest/go/junit/xctest dumps, pytest `-vv` tmp-vs-alice, junit XML, `# ran on` inside a fail dump
- This host's live `$HOME`/`$USER` written into `demo-tmp/live.snap` (MATCH)
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu}` `--scan` (read-only)

## Surprises

- XCTest polarity is the whole flip. Apple prints `("actual") is not equal to ("expected")`. oath treated the first value as the oracle and "found" Alice on a dump whose expected was `/tmp/x`. vow's pair is `EXPECTED-OPEN vs ACTUAL-BOUND`.
- pytest `-vv` `assert '/Users/alice' == '/tmp/x'` fires an unlabeled AssertionError *before* `where got` / `and expected`. Without replacing that swapped pair, the labeled window never wins.
- `assert os.environ['USER'] == 'alice'` in a dump is a source hint, not a second pair whose "actual" is the expression `os.environ['USER']`. The actual is `runner` from the E +/- line.
- sitbone needed no new fixture rule. The assertion window already keeps `annenpolka` as identity-as-data. vow's new object lives only on `--from-fail`.

## Failures

- `--apply` on a pair still applies the *expected* side (oracle polarity). Host role is named, not an exit code — a portable expected must not skip just because you are NEITHER.
- HOST (hostname) is still soft and not part of `--apply`.
- Assertion strings that wrap across a third-argument message are parsed as call-args (usually fine); Swift `#expect` with `<>` generic noise is not.
- `skills` / voidtrace / tenaoshi were not scanned this generation (sitbone/kizu were the gold).

## Suggested mutations

- `--apply` from host role without breaking OPEN expected (a portable golden that failed on Alice should still apply here).
- `--held`-style: when did an assertion newly acquire an actual-bound machine.
- Join with alibi: splice tests onto old production, then vow the failure (LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-BOUND).
- Resolve `expected = home; assert got == expected` by following the name.

## Kill / keep

**Keep.** The object is new: two unary skip/apply machines from one failing assertion, not a substitution and not an expected-only oath. v0.2 names which of those machines this host is (`ACTUAL` when the dump's actual is `$HOME`). sitbone stays FIXTURE (not TAINTED). kizu comments about John Doe stay silent; quoting asserts are SPEC. A dump whose actual is `/Users/alice/...` and expected is `/tmp/x` pairs `EXPECTED-OPEN vs ACTUAL-BOUND`. `# ran on` does not bind. Not lees `--par`, not visa's whole file, not stain/admit.
