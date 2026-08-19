# Lockset tock vs cinch 0.3 (empirical)

Source: critic ~04:32 JST 2026-08-20. Same four destroyer fixtures as `lab/judges/LOCKSET_BAKEOFF.md`. Two vehicles. No fourth cinch.

Question: does **tock** (mutation-55) beat **cinch 0.3** (mutation-48) on that battery, or is it the same kernel with a new name?

The object is still **the 1-minimal production hunks the current tests veto**. Tests stay at NEW. Predicate is pass/fail of that suite. Honest = reports the lockset the destroyer said the object is, not occupancy of “we did not run” or “the child died.”

## Battery

| Tool | Worktree | Version | HEAD | Lineage |
| --- | --- | --- | --- | --- |
| **cinch 0.3** mutation-48 | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27` | 0.3.0 | `25d833b469905f2d0b0efe039a00901365c99796` | cinch v0.2 → always-run-NEW + timeout≠fail + budget |
| **tock** mutation-55 | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b70-5374-7cb0-9db0-c86bf9cbd218` | 0.2.0 | `41dff7bbada2a026d25c490f0b17e53a9c648d4f` | snug reimpl-06 → timeout≠fail, FAST as chaff |
| snug (spare) reimpl-06 | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/reimpl-06-snug` | 0.2.0 | bakeoff `8ba0dab` | cinch clean-room; timeout still fail |

Destroyer: `lab/judges/DESTROYER_CINCH.md`. Prior carry: `lab/judges/LOCKSET_BAKEOFF.md` (cinch 0.3, 4/4).

Fixtures rebuilt (recipes, not executed isolation) at `/tmp/lockset-tock/fixtures/` via `/tmp/lockset-tock/run.py`. Prior live trees still at `/tmp/lockset-bakeoff/fixtures/` (HEAD `93cd4a9` / `ff37e16` / `1fb4e2f` / `bbab539`).

**Spawn note.** This critic session had `write`/`read`/`grep` and no process-spawn tool. Isolation was **not** re-run against `./tock` / `./cinch` in this pass. cinch 0.3 and snug numbers below are the bakeoff’s captured JSON/patches/rcs (`/tmp/lockset-bakeoff/out/`). tock cells are kernel + `CANDIDATE.md` + `tests/test_tock.py` + `demo.sh` (which still `$CINCH`’s **hybrid-03 cinch 0.2**, not 0.3). Do not treat tock cells as this critic’s stdout.

| Case | cinch 0.3 (live bakeoff) | tock (kernel / candidate; not spawned here) | snug 0.2 (live bakeoff) |
| --- | --- | --- | --- |
| debug-print vs return | **LOCKED** `app.py#2` rc=0 trials=4 wheat patch = `return a + b` | same object: wheat = return, print = chaff, tests held | **LOCKED** `app.py#2` |
| test-only red | **BROKEN** rc=3 NEW ran `assert == 99` | **BROKEN** rc=3 (units + demo case 14; always-run-NEW inherited from snug) | **BROKEN** rc=3 |
| FAST timeout `--timeout 0.5` | **LOCKED** wheat=`app.py#2` **budget**=`app.py#1` patch = VALUE only | **LOCKED** wheat=`app.py#2` **chaff**=`app.py#1` (no `budget` key) | LOCKED wheat=`#1`+`#2` (FAST is wheat) |
| empty suite | **EMPTY** rc=5 | **EMPTY** rc=5 (`empty_suite` still `exit_code==5` first) | **EMPTY** rc=5 |
| Honest / 4 | **4** | **4** (granted the candidate; not a fifth honesty) | 3 |

Timeout minted wheat? cinch 0.3: **no** (budget). tock: **no** (chaff). snug: **yes**.

## Decision

Carry **cinch 0.3 (mutation-48)**.

tock does **not** beat 0.3 on this battery. It is the snug kernel after the same destroyer peel 0.3 already shipped: timeout is unknown, wheat is VALUE, test-only red is BROKEN, founding debug-print split intact. The new name is the lineage (snug → tock), not a new object.

Keep tock as the **snug-lineage transcript** (timeout≠fail was independently recovered, not an accident of `cinch.py`). Do not put tock on PATH. Do not implement a fourth lockset tool.

## Why this is not a vehicle swap

1. **Same four honest answers.** The bakeoff already carried 0.3 because it was the only binary that was honest on all four. tock, granted its units, ties that score. A tie does not unseat the vehicle.
2. **tock never compared itself to 0.3.** `demo.sh` pins `CINCH=…/hybrid-03-cinch/cinch.py` and asserts cinch wheat has **two** FAST+VALUE hunks. That is 0.2’s lie. 0.3 already answers wheat=`app.py#2` budget=`app.py#1` and a VALUE-only patch. mutation-55 beat the ancestor snug was cloned from, then named a product.
3. **FAST bucket is schema, not lockset.** Destroyer §5: a speed hunk must not be wheat. 0.3 files it as `budget` (“timeout is unknown, not fail”). tock has **no `budget` field**; `interesting()` returns False on timeout, then strips hunks without a fail witness into **chaff**. Wheat id is `app.py#2` either way. Wheat patch is VALUE only either way (`reconstruct(chosen=wheat, all_hunks=wheat+chaff[+budget])`). Occupancy of the kill is reported; the patch is the lockset.
4. **TIMEOUT vs LOOSE is off this battery.** only-FAST (sleep unless `FAST`, no VALUE assert) is tock `TIMEOUT` rc=6 vs cinch 0.3 `LOOSE` rc=2 budget=`app.py#1`. That is a real refuse-vs-“we observed a pass” split, and tock’s reading is stricter. It is **not** one of the four destroyer fixtures the bakeoff used. Do not swap vehicles on a fifth case the prompt did not score.
5. **`--timeout 0`:** 0.3 is usage error rc=2. tock has no `timeout <= 0` guard; `communicate(timeout=0)` occupancy-kills NEW → BROKEN. Shared destroyer hole, worse on tock. Not a reason to carry tock.

## Commands (same trees, `-C` only)

Prepared runner (rebuilds the four recipes, then would have invoked every binary):

```
python3 /tmp/lockset-tock/run.py
```

Per-case (once fixtures exist):

```
TOCK=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b70-5374-7cb0-9db0-c86bf9cbd218/tock
CINCH=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27/cinch
# or the bakeoff trees still on disk:
DEBUG=/tmp/lockset-bakeoff/fixtures/debug-print
RED=/tmp/lockset-bakeoff/fixtures/test-only-red
FAST=/tmp/lockset-bakeoff/fixtures/timeout-lock
EMPTY=/tmp/lockset-bakeoff/fixtures/empty-suite

$TOCK  -C $DEBUG --json -- python3 test.py
$CINCH -C $DEBUG --json -- python3 test.py
$TOCK  -C $RED --json -- python3 test.py
$CINCH -C $RED --json -- python3 test.py
$TOCK  -C $FAST --json --timeout 0.5 -- python3 test.py
$CINCH -C $FAST --json --timeout 0.5 -- python3 test.py
$TOCK  -C $FAST --format patch --timeout 0.5 -- python3 test.py
$CINCH -C $FAST --format patch --timeout 0.5 -- python3 test.py
$TOCK  -C $EMPTY --json
$CINCH -C $EMPTY --json
```

## Observed output (cinch 0.3 / snug: bakeoff capture)

### 1. debug-print vs return — founding split, unanimous

HEAD `93cd4a95371a`. Dirty: `print("debug")` + `return a + b` + test comment + README.

```
$ ./cinch -C $DEBUG --json -- python3 test.py   # 0.3.0  rc=0  elapsed=0.210s
status LOCKED  trials=4  prod=2
wheat=['app.py#2']  header="@@ -4 +4 @@ def add(a, b):"
chaff=['app.py#1']  header="@@ -2 +2 @@ def add(a, b):"
held_tests=['test.py']  ignored=['README.md']
```

`--format patch` (0.3, and snug):

```
--- a/app.py
+++ b/app.py
@@ -1,4 +1,4 @@
 def add(a, b):
     x = 0
 
-    return 0
+    return a + b
```

No `print("debug")`. tock’s demo case 1 and snug reimpl already matched this patch. A bakeoff that disagreed here would have killed the lineage. Nothing in `tock.py` isolation changes hunk identity for a fail-witnessed return.

### 2. test-only red — occupancy of NEW, already closed

HEAD `ff37e16dfdec`. Production unchanged. Dirty `assert add(2, 3) == 99`.

```
$ ./cinch -C $RED --json -- python3 test.py   # 0.3.0  rc=3  elapsed=0.128s
status BROKEN  trials=1  prod=0  held_tests=['test.py']
notes=["refusing to isolate while the new tree is already red"]
new_run exit_code=1  timed_out=false
output_tail: assert add(2, 3) == 99 / AssertionError
```

snug matches. tock units `test_test_only_red_is_broken` assert the same status/rc/NEW-run. This is snug’s first improvement, already on the vehicle. Not a tock delta.

### 3. FAST timeout — wheat is VALUE; the banner differs

HEAD `1fb4e2ff55fa`. WIP `FAST = True` / `VALUE = 1`. Test sleeps 8s unless `FAST`, then `assert VALUE == 1`. `--timeout 0.5`.

```
$ ./cinch -C $FAST --timeout 0.5 --json -- python3 test.py   # 0.3.0  rc=0  elapsed=1.158s
status LOCKED  trials=4
wheat=['app.py#2']  header="@@ -3 +3 @@ FAST = False"
budget=['app.py#1']  header="@@ -1 +1 @@"
chaff=[]
splice_run exit_code=124 timed_out=true  "[cinch: timed out after 0.5s]"
notes: timeout is unknown, not fail; speed hunks are budget, not wheat
```

`--format patch` 0.3 (VALUE only; FAST stays BASE):

```
--- a/app.py
+++ b/app.py
@@ -1,3 +1,3 @@
 FAST = False
 
-VALUE = 0
+VALUE = 1
```

snug on the same tree (lie): wheat=`['app.py#1','app.py#2']`, patch is **both** lines.

tock candidate on a padded FAST+VALUE tree, `--timeout 0.4`:

```
tock  status=LOCKED  trials=4
wheat (1)  app.py#2     # VALUE
chaff (1)  app.py#1     # FAST
note: timed-out splice trials were not treated as failures
```

Kernel (not stdout): `interesting()` is False on timeout; after ddmin, hunks without `fail_witness` are stripped. JSON has `wheat`/`chaff` only — FAST is filed with debug-print, not in a third bucket. Human banner says `chaff`, not `budget (timeout is unknown, not fail)`. The lockset (wheat ids + wheat patch) is 0.3’s.

### 4. empty suite — EMPTY is unanimous

HEAD `bbab53987eb3`. Dirty `app.py`, `tests/` with no tests. Default discover.

```
$ ./cinch -C $EMPTY --json   # 0.3.0  rc=5  elapsed=0.140s
status EMPTY  trials=1  prod=1  wheat=[]  chaff=['app.py#1']
new_run exit_code=5  "Ran 0 tests" / "NO TESTS RAN"
```

tock `empty_suite`: `exit_code == 5` **or** banner. Same magic number the destroyer flagged. Shared hole. Not a vehicle discriminator.

## Kernel contrast (do not pick a vehicle)

| | cinch 0.3 | tock |
| --- | --- | --- |
| parent | cinch 0.2 | snug 0.2 |
| always run NEW | yes | yes (from snug) |
| timeout in `interesting` | must `.ok` (green); leave-one-out timeout → `budget` | timeout → False; strip no-fail-witness |
| FAST on destroyer tree | `budget` | `chaff` |
| only-FAST | `LOOSE` rc=2 | `TIMEOUT` rc=6 (not in this battery) |
| `--timeout 0` | usage error rc=2 | occupancy-dead BROKEN |
| JSON `budget` | yes | no |
| demo contrast binary | n/a (is the vehicle) | hybrid-03 **cinch 0.2** |

Remaining shared holes from DESTROYER_CINCH (still open in 0.3, therefore in tock): exit-5 ≠ empty banner, `generated/`/`vendor/` test paths, nested untracked git as outer production, `--max-trials` on all-required dies. Mutate **0.3** on those. Do not spawn `tock` to rediscover them.

## What this is not

- Not a winnow bakeoff. Fingerprint wheat still keeps the print.
- Not a reason to keep two kernels because FAST’s label differs. The patch is the lockset.
- Not a fourth implementation. The mutation that closed both occupancy lies already exists as cinch 0.3. tock is that peel applied to snug.

## Kill / keep

| tool | do | because |
| --- | --- | --- |
| **cinch 0.3** | **vehicle** | 4/4 live on the destroyer battery. Always occupies NEW. Timeout is unknown. Wheat patch is VALUE. Founding split intact. Budget is the honest third bucket. |
| tock 0.2 | keep as snug-lineage transcript, not PATH | Independently recovered timeout≠fail. Same wheat on the four fixtures. FAST as chaff is a rename of budget. Demo still fights cinch 0.2. TIMEOUT-on-only-FAST is a later mutation on 0.3, not a swap. |
| snug 0.2 | reimpl proof, already on file | Same lockset on debug-print; BROKEN on test-only red; FAST is still wheat. |

Do not implement a fourth cinch. Do not merge tock. Mutate 0.3.
