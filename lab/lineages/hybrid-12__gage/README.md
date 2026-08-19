# gage

Clearance of the lockset: **LOCKED-and-BOUND vs LOCKED-and-OPEN**.

`alibi` asks whether current tests veto old production (LOCKED / LOOSE). `stain` asks whether production leaked a machine. A test that locks a path but is OPEN (no HOME/USER/platform) is a different verdict from a test that locks a bound world. `gage` names that joint.

Default CI: empty stdout and exit 0 when no lock assumes a machine. OPEN locks are a clearance. BOUND locks are a stained alibi.

Tests are the lockset. Worlds are their visa. Production is spliced whole — this is not a fourth cinch.

## Install / run

Python 3.10+, git, stdlib only. v0.2.

```bash
chmod +x ./gage
./gage --help
./gage --self-test
./demo.sh
```

## Three examples

### 1. LOCKED-and-OPEN — clearance, empty, exit 0

New tests lock `is_browser("Brave Browser")`. No machine. `print("debug")` next to a real `return a + b` is the same verdict: the lock is OPEN.

```bash
./gage -C fixtures/debug-print
# (no stdout)
# exit 0

./gage -C fixtures/debug-print --report
# LOCKED  OPEN  …  verdict LOCKED-and-OPEN
```

alibi would print LOCKED. stain would print nothing (no HOME). gage's default is stain-shaped: empty, because the lockset is cleared of machines.

### 2. LOCKED-and-BOUND — stained alibi, exit 1

A test that vetoes old production *and* assumes this host's HOME:

```bash
./gage -C fixtures/bound-lock
# gage  machines=1  bound-locks=1  miss=0
#   LOCKED  BOUND  MATCH  HOME=/Users/you USER=you platform=Darwin  parent=CLEAN
#     who  who("/Users/you")  app.py:4
# exit 1
```

CI does not care that the laptop holds the visa. MATCH is still a stain of the lock.

### 3. SKIP-and-BOUND is not a lock (ugly)

Alice's HOME in an emitted world-test skipifs on this host. stain fails (production leaked a machine). alibi sees a green splice (skip = pass). gage names occupancy SKIP. Default stays empty: a skip did not veto. `--due` recovers the stained tests that never occupied the lock.

```bash
./gage -C fixtures/ugly          # empty, exit 0
./gage -C fixtures/ugly --due    # exit 1
./gage -C fixtures/ugly --report
# SKIP  BOUND  MISS  parent=CLEAN  load_profile("/Users/alice")
# UNRUN OPEN         isBrowser("Brave Browser")
```

| code | meaning |
| --- | --- |
| 0 | lockset cleared (no LOCKED-and-BOUND) |
| 1 | a lock assumes a machine (or `--due` saw SKIP-and-BOUND) |
| 2 | usage / not a git repo |
| 3 | a world-test already fails on the new tree |
