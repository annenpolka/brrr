# mutation-62 — scree

## Primitive

Given a dirty tree and a test command, emit the **largest production subset the current tests do not lock**. Tests stay at NEW. A hunk is unlocked only after an **observed pass** with it dropped. A timeout is unknown: never locked, never unlocked. An empty suite is EMPTY, not a giant unlocked set.

Invert of cinch 0.3 / tock: their object is the 1-minimal wheat the tests veto. scree's object is the slack — the chaff. Same occupancy rules, opposite emit.

## Why this might not exist

cinch/tock answer "what must I keep?" The complementary verb is "what can I shed?" A mixed WIP is a tested fix plus an untested refactor plus a debug print. Wheat is the commit. Slack is the other PR — or the delete.

Tock already *computes* chaff, then leads with wheat. Treating timeout as chaff (tock) or as budget-next-to-wheat (cinch 0.3) still frames the speed hunk as leftover of a lockset search. The invert makes **observed-unlocked** the thing you pipe: `--format paths` is `c.py`, not `a.py\nb.py`. `--format patch` is `print("debug")`, not `return a + b`.

A killed child is not an observed pass. v0.1 called that slack. That is the same occupancy lie as timeout-as-wheat, just signed the other way.

Not `alibi` (tests stay at NEW). Not winnow (predicate is pass/fail, not a fingerprint). Not a fourth cinch (the patch is the unused extra).

## How to run

```bash
chmod +x ./scree
./demo.sh
./scree --help
./scree -- python3 -m unittest discover -s tests -q
./scree --format patch -- python3 test.py
./scree --timeout 0.5 -- python3 test.py
./scree --list
```

Python 3.10+, git. The user worktree is never rewritten.

## Empirical transcript

### Before the improvement (`fbb6559`) — timeout is unlocked

v0.1. `./demo.sh` exit 0 (16 cases + units). Debug-print vs return: unlocked=`app.py#1` (`print("debug")`), locked=`app.py#2` (`return a + b`). Patch is the print, complement of cinch/tock wheat. Empty suite EMPTY with `unlocked=[]`. Test-only red BROKEN.

DESTROYER_CINCH FAST+VALUE, `--timeout 0.4`, sleep 1.5s unless FAST:

```
scree  base=HEAD  status=SLACK  trials=4
NEW    pass         0.02s
SPLICE timeout      0.40s

unlocked (1 units / 1 files) — tests do not lock:
  modify app.py  #1 @@ -1 +1 @@
locked (1 units / 1 files) — drop fails an assertion:
  modify app.py  #2 @@ -10 +10 @@ FAST = False
note: v0.1: timeout treated as unlocked (not locked ⇒ slack)
```

`--format patch`:

```
--- a/app.py
+++ b/app.py
-FAST = False
+FAST = True
```

We never observed a pass without FAST. The patch claims slack we did not see. Same occupancy hole as cinch 0.2's FAST-as-wheat, inverted.

### After the improvement (v0.2)

Timeout is a third bucket: unknown. Not locked (no fail witness). Not unlocked (no observed pass). FAST+VALUE:

```
scree  status=TIGHT  trials=4
unlocked (empty)
locked   app.py#2   # VALUE; header still says FAST = False
unknown  app.py#1   # FAST
# rc=1  --format patch is empty
```

only-FAST (tests `assert True` after optional sleep):

```
scree  status=TIMEOUT  exit=6  unlocked=[]  unknown=['app.py#1']
```

Parent contrast on the same FAST+VALUE tree, same `--timeout 0.4`:

```
scree unlocked []              locked [VALUE]  unknown [FAST]
tock  wheat    [VALUE]         chaff  [FAST]
cinch wheat    [VALUE]         budget [FAST]
```

tock's chaff *is* FAST — the invert of its wheat. scree refuses that bucket as slack. cinch 0.3 budget matches our unknown; cinch still emits VALUE as the object. scree emits nothing: there is no observed-unlocked production.

Debug-print vs return unchanged: unlocked is the print, locked is the return, patch has `print("debug")` and not `return a + b`.

`./demo.sh` exit 0, 17 cases + cinch/tock contrasts. No leftover `time.sleep` processes.

## Dogfood targets

- `tests/test_scree.py` + `./demo.sh`
- cinch/tock proof fixture (debug print vs return) — complements
- DESTROYER_CINCH FAST+VALUE timeout lock
- only-FAST (timeout with no assertion lock)
- NEW-timeout vs splice-timeout
- empty suite (not a giant unlocked set)
- test-only red (always occupy NEW)

## Surprises

- `--format paths` on the founding split is still `app.py` (one file, mixed hunks). The invert shows up in the patch and in JSON hunk ids, not in the path list. Joint+noise is where paths invert: cinch prints `a.py\nb.py`, scree prints `c.py`.
- git `-U0` labels the VALUE hunk header with `FAST = False` (first assignment). Identity is the hunk index.
- tock already computed FAST as chaff. The v0.1 lie was "chaff = unlocked." That identity fails the moment a drop times out. Slack needs a pass witness the way wheat needs a fail witness.
- LOOSE is the maximum slack (everything unlocked) and keeps exit 2. SLACK is the interesting mixed case (exit 0). TIGHT is "you asked for slack; there is none" (exit 1).

## Failures

- `--timeout 0` is a usage error (rc=2). A green suite with a zero budget is still occupancy-dead if we ran it.
- VALUE is locked from the FAST-only assertion fail, not from a passing VALUE-only trial (that trial times out). Necessity, not observed sufficiency-under-budget. Dual of tock's wheat claim.
- Commands that consult the git index still see a sandbox without `.git`.
- Hunk apply is UTF-8 text; mixed hunks on a binary path fall back to whole-file.
- `generated/` / `vendor/` still not skipped (DESTROYER_CINCH §3; skipping them is not this mutation).
- Exit 5 is still unittest/pytest-empty *or* a runner that uses 5 for "failed."
- Redundant FLAG|VALUE: largest unlocked has size 1, but which hunk is slack depends on ddmin order. Cardinality is the object, not a canonical leftover.

## Suggested mutations

- `--stash-unlocked` / `--commit-locked`: keep only what the tests veto.
- If a timeout occurs, optionally retry that one trial with `--timeout` × N before UNKNOWN (still never mint slack from the kill).
- Search for a *globally* largest unlocked set when several maximal sets exist (FLAG vs VALUE).
- `--src` / `--ignore` globs.
- Coverage hint to prefer dropping uncovered hunks first.

## Kill / keep

**Keep.** The invert is real on the founding fixture (patch is the print) and on joint+noise (`paths` = `c.py`). The v0.1 lie was load-bearing: timeout-as-unlocked mints FAST as slack, the destroyer's hole with the other sign. v0.2 closes it without becoming a fourth cinch — the object is still the unused extra; FAST is simply not in it. Kill only if a later generation shows that "complement of cinch wheat" is the whole product and the timeout bucket does not need its own verb.
