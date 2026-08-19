# Lockset bakeoff (empirical)

Source: critic `01a01b7a-4151-7541-829c-e67d4f6a186a`. Same four destroyer fixtures, three binaries, no fourth cinch.

The object is still **the 1-minimal production hunks the current tests veto**. Tests stay at NEW. Predicate is pass/fail of that suite, not a command fingerprint. This is not `alibi | winnow`.

## Battery

| Tool | Worktree | Version | HEAD |
| --- | --- | --- | --- |
| cinch 0.2 ancestor | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-03-cinch` | 0.2.0 | `d7195b5` |
| cinch 0.3 mutation-48 | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27` | 0.3.0 | `25d833b` |
| snug reimpl-06 | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/reimpl-06-snug` | 0.2.0 | `8ba0dab` |

Destroyer that named the occupancy lies: `lab/judges/DESTROYER_CINCH.md`.

Fixtures rebuilt from that destroyer’s recipes (and the demo money shot) at `/tmp/lockset-bakeoff/fixtures/`. Raw JSON / patches / rcs: `/tmp/lockset-bakeoff/out/`. Same trees for every binary (`-C` only).

| Case | cinch 0.2 | cinch 0.3 | snug 0.2 |
| --- | --- | --- | --- |
| debug-print vs return | **LOCKED** `app.py#2` | **LOCKED** `app.py#2` | **LOCKED** `app.py#2` |
| test-only red | CLEAN rc=0, trials=0, NEW skipped | **BROKEN** rc=3, NEW ran | **BROKEN** rc=3, NEW ran |
| FAST timeout `--timeout 0.5` | LOCKED wheat=`#1`+`#2` (FAST is wheat) | **LOCKED** wheat=`#2`, budget=`#1` | LOCKED wheat=`#1`+`#2` (FAST is wheat) |
| empty suite | **EMPTY** rc=5 | **EMPTY** rc=5 | **EMPTY** rc=5 |
| Honest / 4 | 2 | **4** | 3 |

Honest = reports the lockset the destroyer said the object is, not occupancy of “we did not run” or “the child died.”

## Decision

Carry **cinch 0.3 (mutation-48)**.

- The founding split is not in dispute. All three drop `print("debug")` and keep `return a + b`. The primitive survived a clean-room rebuild.
- cinch 0.2 still reports a **red suite as CLEAN** when production is empty. Occupancy of nothing, exit 0.
- snug closed that lie (always run NEW) and still **mints FAST as wheat** because timeout maps to fail. Same destroyer hole as cinch 0.2. Independent reimpl is proof the object is real, not a reason to ship two kernels.
- Only cinch 0.3 treats timeout as unknown. Wheat is VALUE. FAST is budget. The patch is the lockset.

Do not implement a fourth cinch. Do not keep 0.2 as a product. Keep snug as the reimpl transcript (the lockset is not an accident of one file). Mutate 0.3 toward the remaining destroyer list (exit-5 ≠ empty, `generated/`/`vendor/`, nested git, `--max-trials` all-required). Those holes are **shared**; they do not pick a vehicle.

---

## Fixtures (identical trees)

### 1. debug-print vs return — HEAD `93cd4a95371a`

Demo money shot the destroyer said survived. HEAD `add` returns `0`. WIP: `print("debug")` + `return a + b` + comment in `test.py` + dirty README.

```
$ git -C /tmp/lockset-bakeoff/fixtures/debug-print status --short
 M README.md
 M app.py
 M test.py
```

Command: `--json -- python3 test.py` and `--format patch -- python3 test.py`.

### 2. test-only red — HEAD `ff37e16dfdec`

Destroyer §1 / `attack.py` `fx_test_only_red`. Production unchanged (`return a + b`). Dirty `test.py`: `assert add(2, 3) == 99`.

```
$ git -C /tmp/lockset-bakeoff/fixtures/test-only-red status --short
 M test.py
```

Command: `--json -- python3 test.py`.

### 3. FAST timeout — HEAD `1fb4e2ff55fa`

Destroyer §5 / `attack.py` `fx_timeout_as_lock`. HEAD `FAST = False` / `VALUE = 0`. WIP `FAST = True` / `VALUE = 1`. Test sleeps 8s unless `FAST`, then `assert VALUE == 1`. Two hunks.

```
$ git -C /tmp/lockset-bakeoff/fixtures/timeout-lock status --short
 M app.py
```

Command: `--json --timeout 0.5 -- python3 test.py` and `--format patch --timeout 0.5 -- python3 test.py`.

### 4. empty suite — HEAD `bbab53987eb3`

Destroyer §1 / `attack.py` `fx_empty_suite`. Dirty `app.py` (`return 0` → `return a + b`). `tests/` exists, no test files. Default detect: `unittest discover -s tests`.

```
$ git -C /tmp/lockset-bakeoff/fixtures/empty-suite status --short
 M app.py
```

Command: `--json` (no `--cmd`).

---

## 1. Debug-print vs return — all three keep the return

Same JSON shape. Same 4 trials. Same wheat/chaff ids. Same wheat-only patch.

```
$ ./cinch -C $DEBUG --json -- python3 test.py     # 0.2 and 0.3
$ ./snug  -C $DEBUG --json -- python3 test.py
# all three:
status LOCKED  trials=4  prod=2
wheat=['app.py#2']  header="@@ -4 +4 @@ def add(a, b):"
chaff=['app.py#1']  header="@@ -2 +2 @@ def add(a, b):"
held_tests=['test.py']  ignored=['README.md']
# rc=0  elapsed≈0.21s (snug 0.258s)
```

Human (0.3; 0.2 and snug print the same wheat/chaff):

```
cinch  base=HEAD (93cd4a95371a)  status=LOCKED  trials=4
held tests (always NEW, never wheat):
  test.py
ignored (not production source):
  README.md
wheat (1 units / 1 files):
  modify app.py  #2 @@ -4 +4 @@ def add(a, b):
chaff (1 units / 1 files):
  modify app.py  #1 @@ -2 +2 @@ def add(a, b):
```

`--format patch` from all three:

```
--- a/app.py
+++ b/app.py
@@ -1,4 +1,4 @@
 def add(a, b):
     x = 0
 
-    return 0
+    return a + b
```

No `print("debug")` in any wheat patch. This is the object. A bakeoff that disagreed here would have killed the lineage. It did not.

---

## 2. Test-only red — 0.2 is occupancy-dead CLEAN

```
$ ./cinch -C $TEST_ONLY_RED --json -- python3 test.py   # 0.2.0
{
  "status": "CLEAN",
  "trials": 0,
  "production_units": 0,
  "held_tests": ["test.py"],
  "notes": ["no production source units differ from base; skipped test runs"],
  "new_run": null
}
# rc=0  elapsed=0.093s
```

Human:

```
cinch  base=HEAD (ff37e16dfdec)  status=CLEAN  trials=0
note: no production source units differ from base; skipped test runs
```

The suite is `assert add(2, 3) == 99`. It never ran. Destroyer called this occupancy of nothing, reported as clean. Still true of the ancestor.

```
$ ./cinch -C $TEST_ONLY_RED --json -- python3 test.py   # 0.3.0
{
  "status": "BROKEN",
  "trials": 1,
  "production_units": 0,
  "held_tests": ["test.py"],
  "notes": ["refusing to isolate while the new tree is already red"],
  "new_run": {
    "exit_code": 1,
    "timed_out": false,
    "output_tail": ["assert add(2, 3) == 99", "AssertionError"]
  }
}
# rc=3  elapsed=0.128s
```

snug 0.2.0 matches 0.3 on this fixture (BROKEN, trials=1, NEW `exit_code=1`, rc=3, elapsed=0.134s). The reimpl’s listed improvement is real. It is not enough.

---

## 3. FAST timeout — only 0.3 keeps the lockset

Drop `FAST` and the assertion still passes in 8s. Timeout is a budget, not a fail witness. Wheat must be VALUE only.

```
$ ./cinch -C $TIMEOUT_LOCK --timeout 0.5 -- python3 test.py   # 0.2.0
cinch  base=HEAD (1fb4e2ff55fa)  status=LOCKED  trials=4
NEW    pass         0.02s
SPLICE timeout      0.51s
wheat (2 units / 1 files):
  modify app.py  #1 @@ -1 +1 @@
  modify app.py  #2 @@ -3 +3 @@ FAST = False
# rc=0  elapsed=1.155s
```

JSON wheat `['app.py#1','app.py#2']`. Patch is **both** lines:

```
--- a/app.py
+++ b/app.py
@@ -1,3 +1,3 @@
-FAST = False
+FAST = True
 
-VALUE = 0
+VALUE = 1
```

snug is the same lie with a different banner (`[snug: timed out after 0.5s]`, elapsed=1.196s). `interesting()` is `not result.ok`; timeout sets `ok=False`; FAST vetoes.

```
$ ./cinch -C $TIMEOUT_LOCK --timeout 0.5 -- python3 test.py   # 0.3.0
cinch  base=HEAD (1fb4e2ff55fa)  status=LOCKED  trials=4
NEW    pass         0.02s
SPLICE timeout      0.51s
wheat (1 units / 1 files):
  modify app.py  #2 @@ -3 +3 @@ FAST = False
budget (1 units / 1 files) — timeout is unknown, not fail:
  modify app.py  #1 @@ -1 +1 @@
note: splice timed out; timeout is unknown, not a fail veto
note: timeout is unknown, not fail; speed hunks are budget, not wheat
# rc=0  elapsed=1.158s
```

JSON: `wheat=['app.py#2']` `budget=['app.py#1']`. Patch is VALUE only; FAST stays at BASE:

```
--- a/app.py
+++ b/app.py
@@ -1,3 +1,3 @@
 FAST = False
 
-VALUE = 0
+VALUE = 1
```

That is the destroyer mutation. snug did not take it. A fourth cinch would only re-derive this peel.

Wall time is the same order (~1.16s) because the splice still waits out 0.5s. Honesty is not cheaper. It is a different predicate.

---

## 4. Empty suite — EMPTY is unanimous

Default detect on `tests/` with no test files:

```
$ ./cinch -C $EMPTY_SUITE --json     # all three
status EMPTY  trials=1  prod=1  wheat=[]  chaff=['app.py#1']
cmd=["…/python3.14","-m","unittest","discover","-s","tests","-q"]
new_run exit_code=5  output_tail=["Ran 0 tests in 0.000s","NO TESTS RAN"]
# rc=5  elapsed≈0.14s
```

Human (0.3; others match):

```
cinch  base=HEAD (bbab53987eb3)  status=EMPTY  trials=1
test command collected no tests — not a red suite; pass --cmd
chaff (1 units / 1 files):
  modify app.py  #1 @@ -2 +2 @@ def add(a, b):
```

v2’s EMPTY ≠ BROKEN holds on all three. Exit 5 is still the magic number the destroyer flagged (pytest-empty and `sys.exit(5)` collide). Shared hole. Not a vehicle discriminator.

---

## What this is not

- Not a winnow bakeoff. winnow on the debug-print tree still keeps the print (stdout). All three lockset tools drop it.
- Not a hasp bakeoff. hasp is the *range* lockset (MUTE when no new names). Complementary object; DESTROYER_CINCH already contrasted it.
- Not a fourth implementation. The mutation that closed both occupancy lies already exists.

## Remaining shared holes (do not pick a vehicle)

From DESTROYER_CINCH, still open in 0.3 and therefore in the others:

- Exit 5 without the empty banner is EMPTY.
- `generated/` / `vendor/` test paths still lock.
- Nested untracked git is outer production.
- `--max-trials` on an all-required set dies instead of saying “every hunk is required.”

Mutate **cinch 0.3** on those. Do not spawn another `*-ch` name to rediscover timeout≠fail.

## Kill / keep

| tool | do | because |
| --- | --- | --- |
| **cinch 0.3** | **vehicle** | 4/4. Always occupies NEW. Timeout is unknown. Wheat patch is VALUE. Founding split intact. |
| snug 0.2 | keep as reimpl proof, not PATH | Same lockset on debug-print; same BROKEN on test-only red; still timeout-as-fail. |
| cinch 0.2 | ancestor only | Founding split. Occupancy-dead CLEAN. FAST wheat. Superseded. |
