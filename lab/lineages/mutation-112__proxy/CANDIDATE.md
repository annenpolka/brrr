# mutation-112 — proxy

## Primitive

Follow the **expected name** to its bound value before classifying `EXPECTED-BOUND vs ACTUAL-BOUND`. One failing assertion is one pair, not two inverted PM / E +/- pairs.

## Why this might not exist

vow (mutation-68) inferred two oaths from a failing assertion. Unary source did not chain `home = os.environ['HOME']` → `expected = home` → `assert got == expected`. A pytest dump of that shape emitted two pairs: an inverted pytest PM (`left` taken as expected) and a correct E +/- (or a `-vv` pair whose expected was the identifier `home`). JSON with `len(pairs)!=1` had no top-level `pair`. The object was "two oaths"; the dump emitted two *pairs*.

troth (mutation-89) closed host-role `--apply`. It did not follow the name.

Discarded: lees `--par`. Discarded: visa-of-the-file. Discarded: making HOST a hard axis. Discarded: treating `# ran on` as an oath. Discarded: TAINTing sitbone titles.

## How to run

From this worktree root:

```bash
./demo.sh
./proxy --help
./proxy --self-test
python3 -m unittest discover -s tests -q
./proxy fixtures/name_follow.py
./proxy fixtures/name_follow_literal.py
./proxy --from-fail < fixtures/name_follow_fail_diff.txt
./proxy --from-fail < fixtures/name_follow_fail_vv.txt
./proxy --from-fail < fixtures/pytest_fail.txt
./proxy --from-fail < fixtures/xctest_fail.txt
./proxy fixtures/comment_only.py
./proxy fixtures/host_getenv.py
./proxy --scan -C /path/to/repo --porcelain
```

## Empirical transcript

### v0.1 — name follow is the object

Follow `expected → home → <bound>` in source. pytest PM `assert left == right` takes left as actual. rustc `left:` is actual. Inverted PM + E +/- collapse to one pair.

```
$ ./proxy --json fixtures/name_follow.py
status OPEN  require {}
window assert  expected=os.environ["HOME"]  proxy=expected→home→os.environ["HOME"]

$ ./proxy --json fixtures/name_follow_literal.py
status BOUND  require HOME=/Users/annenpolka

$ ./proxy --from-fail < fixtures/name_follow_fail_diff.txt
proxy  pair  pytest  EXPECTED-BOUND vs ACTUAL-OPEN
  expected /Users/annenpolka
  actual   /tmp/x
# n=1  (vow: two inverted pairs)

$ ./proxy --from-fail < fixtures/name_follow_fail_vv.txt
# same one pair: `and expected = home` follows to /Users/annenpolka
```

A dump that also pasted the assignments still split:

```
$ ./proxy --from-fail < fixtures/name_follow_fail_src.txt
# v0.1 n=2  (no top-level pair)
#   pytest-pm  expected=os.environ['HOME']  actual=/tmp/x
#   pytest     expected=/Users/annenpolka   actual=/tmp/x
```

Gold pair unchanged. sitbone 0 BOUND / 4 FIXTURE. kizu 0 BOUND / 2 SPEC / 13 OPEN.

### v0.2 — getenv expression + sibling path is the same name

The followed expected `os.environ['HOME']` is not an identifier, so v0.1 would not join it to the E +/- path. After: a sibling pair with the same actual and a literal expected *is* the bound value of that name. One pair, with the proxy chain.

```
$ ./proxy --from-fail < fixtures/name_follow_fail_src.txt
proxy  pair  pytest  EXPECTED-BOUND vs ACTUAL-OPEN
  expected /Users/annenpolka
  actual   /tmp/x
  proxy    os.environ['HOME']→/Users/annenpolka
# n=1
```

`./proxy --self-test` 81/81. Unittest 42/42. `./demo.sh` passed=76 failed=0.

Gold pytest `EXPECTED-BOUND vs ACTUAL-BOUND` alice vs runner, n=1. Gold XCTest `EXPECTED-OPEN vs ACTUAL-BOUND`. Cargo `left:` is actual. HOST getenv OPEN + soft. `# ran on` silent. sitbone FIXTURE not TAINTED.

## Dogfood targets

- `fixtures/` — name-follow source + dumps, comment vs env-assert, alice/CI snaps, sitbone-shaped title, kizu quoting, pytest/cargo/jest/go/junit/xctest dumps, HOST getenv
- DESTROYER_VOW home-alias fixtures (`name_follow*.py`, `name_follow_fail*.txt`)
- This host's live `$HOME`/`$USER` written into `demo-tmp/live.snap` (MATCH)
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu}` `--scan` (read-only)

## Surprises

- Following the name in *source* and flipping pytest PM polarity (`left` is actual) are the same object: the expected slot is a name until it is bound. E +/- then stops being a second inverted pair and becomes a duplicate of the followed one.
- `home = os.environ['HOME']` as the terminal value is OPEN, not BOUND. There is no literal machine. The follow is still visible on the window (`proxy=expected→home→os.environ['HOME']`).
- rustc gold had alice on the left because vow agreed with the fixture, not with rustc. Flipping `left:` to actual makes cargo match pytest's oracle/actual split.

## Failures

- A dump with no assignment and no literal on the expected side (`assert '/tmp/x' == expected`) is one pair `EXPECTED-OPEN vs ACTUAL-OPEN`. The name did not bind because the dump did not name a value.
- HOST is still soft. A HOSTNAME assert that failed on this box does not name `host ACTUAL`.
- Swift Testing dumps are still unary-expected. Wrap-across-newline XCTest is still one-line.
- `skills` / voidtrace / tenaoshi were not scanned this generation (sitbone/kizu were the gold).

## Suggested mutations

- `--apply` from host role ∪ OPEN expected (troth's object; not this one).
- Swift Testing dump as a pair: parse `Expectation failed: (actual) == expected`.
- Wrap-across-newline is one XCTAssert.
- Follow `want`/`golden` across files (the name defined in a helper).

## Kill / keep

**Keep.** The object is new: the expected *name* is a proxy for its bound value, and a fail dump is one pair after the follow. Gold XCTest `/tmp` vs Alice, gold pytest alice vs runner, sitbone 0 BOUND / 4 FIXTURE, kizu comments silent + quoting SPEC, own-line `# ran on` silent, HOST soft — all still hold. Not lees `--par`, not visa's whole file, not troth's apply set.
