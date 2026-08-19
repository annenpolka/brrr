# writ

Splice **current tests** onto **old production**, then oath the splice failure as two sides: **LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-BOUND**.

alibi stops at LOCKED. gage visaes the *test file* (unary world). troth oaths a dump you already have. cinch peels 1-minimal hunks. writ's object is the join: the lock's failing assertion is a pair, and `--apply` is host-role on that pair. Skip is not a lock. Comments are not oaths. Not a fourth cinch.

## Install / run

Python 3.10+, git, stdlib only.

```bash
chmod +x ./writ
./writ --help
./demo.sh
./writ --self-test
python3 -m unittest discover -s tests -q
```

## Three examples

### 1. Old production leaked this host; new tests lock `/tmp`

New tests assert `who() == "/tmp/x"`. HEAD still returns `$HOME`.

```bash
./writ HEAD --cmd 'python3 -m unittest discover -q'
# writ  status=LOCKED
# lock   LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-BOUND
#   expected /tmp/x  OPEN
#   actual   /Users/you  BOUND  MATCH
#   host     ACTUAL  this host produced the fail
#   legal    OPEN ACTUAL
#   apply    APPLY  OPEN expected still applies (portable golden)
#            ACTUAL-BOUND skip/fixture is legal
# exit 1
```

alibi says LOCKED. gage says LOCKED-and-OPEN (the test assumes `/tmp`). troth never splices. writ names the *actual* of the splice fail.

```bash
./writ HEAD --apply     # exit 0 — portable golden still applies here
./writ HEAD --fixture   # [ "$(uname -s)" = Darwin ] && [ "${HOME}" = /Users/you ]
```

### 2. New tests demand Alice; old production is `/tmp`

```bash
./writ HEAD
# lock   LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-OPEN
#   expected /Users/alice/proj  BOUND  MISS
#   actual   /tmp/x  OPEN
#   host     NEITHER
#   legal    (none)
#   apply    SKIP
# exit 1
```

`--apply` exits 1: Alice's golden is not legal on this host. `--fixture` prints `false`. This is a fake alibi — the tests only lock a laptop.

### 3. A skip is not a lock. A comment is not an oath. Numbers are not hunks.

```bash
# skipUnless Alice — suite is green here because it skipped
./writ HEAD            # status=SKIP  exit 0
./writ HEAD --due      # same report, exit 1 (hid a machine skip)

# # ran on alice above assertEqual(add(2,3), 5)
./writ HEAD
# lock   LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-OPEN
# comments are not oaths

# debug-print + return a+b vs HEAD return 0
./writ HEAD --json | jq '.lock, .wheat, .hunks'
# "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-OPEN"
# []
# []
```

cinch would keep `return a + b` and drop `print("debug")`. writ splices whole production and oaths `5` vs `0`. No wheat.

## Statuses and exit codes

| status        | meaning                                              | exit |
| ------------- | ---------------------------------------------------- | ---- |
| `LOCKED` both OPEN | portable lock; neither side named a machine     | 0    |
| `LOCKED` with BOUND | EXPECTED-BOUND and/or ACTUAL-BOUND             | 1    |
| `CLEAN`       | no production source differs from base               | 0    |
| `SKIP`        | machine skip fired; skip is not a lock               | 0 (`--due` 1) |
| `LOOSE`       | tests still pass on base production                  | 2    |
| `BROKEN`      | tests already fail on the new tree                   | 3    |
| `UNBUILDABLE` | spliced tree cannot load/compile                     | 4    |
| `EMPTY`       | no tests ran                                         | 5    |
| `TIMEOUT`     | splice timed out — not a fail oath                   | 6    |

`--apply` is the legal set `OPEN expected ∪ ACTUAL-BOUND-if-this-host` (exit 0 APPLY / 1 SKIP). `--side both` is not a flag: AND of actual MISS into OPEN expected is vow's hole.

`--clearance` prints nothing when no BOUND side.

Compose: `./writ origin/main --json; echo $?`
