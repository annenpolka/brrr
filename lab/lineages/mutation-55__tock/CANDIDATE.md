# mutation-55 — tock

## Primitive

Given a dirty tree and a test command, emit the **1-minimal production hunks the current tests require**. Tests stay at NEW. A splice timeout is **unknown**, not fail: a timed-out trial is an error, not “this hunk is guilty,” and must not mint wheat.

Mutation of `snug` (reimpl-06 / cinch clean-room). snug already always runs NEW (test-only red is BROKEN). tock keeps that, then flips DESTROYER_CINCH §5.

## Why this might not exist

cinch and snug map `TimeoutExpired` to fail (exit 124). A production hunk that only makes the suite *finish before `--timeout`* becomes wheat, even though the assertions would pass without it. That is winnow’s fingerprint object wearing a lockset badge: the budget changed, so the hunk is “guilty.”

The lockset is “drop this hunk and an assertion dies.” A killed child is not an assertion.

## How to run

```bash
chmod +x ./tock
./demo.sh
./tock --help
./tock -- python3 -m unittest discover -s tests -q
./tock --timeout 0.5 -- python3 test.py
./tock --format patch -- pytest
./tock --list
```

Python 3.10+, git. The user worktree is never rewritten.

## Empirical transcript

### Before the improvement (`7afdc23`) — timeout is still fail

Port of snug 0.2. `./demo.sh` exit 0 (14 cinch/snug cases + units). Always-run-NEW, test-only red BROKEN, debug-print vs return lockset matches cinch.

DESTROYER_CINCH FAST fixture (not yet in that demo): `FAST=False`/`VALUE=0` → `FAST=True`/`VALUE=1`. Tests sleep 1.5s unless `FAST`, then `assert VALUE==1`. `--timeout 0.4`:

```
snug  status=LOCKED  trials=4  wheat=['app.py#1','app.py#2']  chaff=[]
SPLICE timeout 0.41s
```

Both hunks are wheat. Drop `FAST` and the assertion still passes in 1.5s. Timeout mapped to fail, so the speed hunk is “guilty.”

### After the improvement (v0.2)

Timeout is a third outcome: not pass, not fail, no fail witness. Isolation keeps hunks that an **assertion** vetoed. Hunks whose only “veto” was a killed child are chaff. If nothing has a fail witness, status is `TIMEOUT` (exit 6), wheat=[].

Same FAST fixture:

```
tock  base=HEAD  status=LOCKED  trials=4
NEW    pass         0.01s
SPLICE timeout      0.41s

wheat (1 units / 1 files):
  modify app.py  #2 @@ -10 +10 @@ FAST = False
chaff (1 units / 1 files):
  modify app.py  #1 @@ -1 +1 @@
note: base production timed out; timeout is unknown, not a test failure
note: timed-out splice trials were not treated as failures; a timeout is not a fingerprint change and must not mint wheat
```

Parent contrast on the same tree, same `--timeout 0.4`:

```
tock  wheat ['app.py#2']           chaff ['app.py#1']
snug  wheat ['app.py#1','app.py#2'] chaff []
cinch wheat ['app.py#1','app.py#2'] chaff []
```

Only-FAST (tests sleep unless `FAST`, no VALUE change):

```
tock  status=TIMEOUT  exit=6  wheat=[]  splice timed_out=true
snug  status=LOCKED   exit=0  wheat=['app.py#1']
```

NEW timeout (suite sleeps even with WIP production) is still **BROKEN** (exit 3): the new tree never went green. Isolation is unaskable. Different from splice timeout.

`./demo.sh` exit 0, 17 cases (14 inherited + FAST lockset + only-FAST TIMEOUT + NEW-timeout BROKEN). No leftover `time.sleep` processes.

Debug-print vs return, test-only red BROKEN, EMPTY, LOOSE, joint, redundant 1-minimal: unchanged.

## Dogfood targets

- `tests/test_tock.py` + `./demo.sh` (17 cases)
- DESTROYER_CINCH FAST+VALUE timeout lock
- snug/cinch proof fixture (debug print vs return)
- only-FAST (timeout with no assertion lock)
- NEW-timeout vs splice-timeout

## Surprises

- git `-U0` still labels the VALUE hunk header with `FAST = False` (the first assignment). The hunk index is the identity; the header is git’s context hint.
- ddmin on two hunks still runs 4 trials. The flip is the *witness rule*, not a new search. Strip FAST after the fact: it was in the 1-minimal *passing* set only because VALUE-only timed out.
- only-FAST cannot be LOOSE: we did not observe a pass on base (the child was killed). TIMEOUT is the honest refuse. Reporting LOCKED FAST would be the destroyer miss; reporting LOOSE would claim a pass we never saw.
- Process-group kill on timeout (`start_new_session` + `killpg`) is load-bearing. Without it, 1.5s sleeps would leak across trials.

## Failures

- `--timeout 0` still makes NEW `TimeoutExpired` immediately → BROKEN. A green suite with a zero budget is occupancy-dead, same as cinch.
- VALUE-only is named wheat from the FAST-only assertion fail, not from a passing VALUE-only trial (that trial times out). The claim is necessity, not observed sufficiency-under-budget.
- Commands that consult the git index still see a sandbox without `.git`.
- Hunk apply is UTF-8 text; mixed hunks on a binary path fall back to whole-file.
- `generated/` / `vendor/` still not skipped (DESTROYER_CINCH §3, not this mutation).
- Exit 5 is still unittest/pytest-empty *or* a runner that uses 5 for “failed.”

## Suggested mutations

- `--commit-wheat` / `--stash-chaff`: keep only the lockset.
- Coverage hint to pick a test subset before isolation.
- `--src` / `--ignore` globs.
- Invert: largest production subset the tests do *not* lock.
- If a timeout occurs, optionally retry that one trial with `--timeout` × N before TIMEOUT (still never mint wheat from the kill).

## Kill / keep

**Keep.** The object survived the destroyer’s load-bearing timeout case: cinch/snug wheat is two hunks (FAST+VALUE); tock wheat is VALUE; FAST is chaff. only-FAST is TIMEOUT with empty wheat, not a speed lock. Test-only red remains BROKEN (snug’s first improvement). Kill only if a later generation shows that treating timeout as pass (LOOSE the FAST hunk by assuming the sleep would finish) is the real lockset — it is not; that would invent a pass the tool never saw.
