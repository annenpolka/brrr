# DESTROYER leakorder 3

Date: 2026-09-02 16:39 JST
RUN_ID: specimen-hdd-20260902-1112
Job: `job-0439`
Worker: `destroyer-leakorder-3`

Target (archive, after isolate / class-attr mutate; DESTROYER_2 KEEP):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder`

CLI sha256 `d711f95c4a8ff27e55b75fc93cae58ea4e1ee1ff4e837df68e594466afaa767d` (20896 bytes, 638 lines). Matches `MUTATE.md` and DESTROYER_leakorder_2. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-leakorder-isolate/leakorder/leakorder` and `leakorder.py` are byte-identical (`cmp` rc=0). Branch `specimen-hdd/candidate-leakorder-isolate`. Isolate commit `3fc09c071650729ecd97cabf809e7b028f0d0053`. HEAD `e405a75` only records that hash in `MUTATE.md`. Parent `main` is `432f954`; `git ls-tree HEAD leakorder` empty. Host Python 3.14.5. unittest 24/24 OK twice (2.069s / 2.165s). `./demo.sh` ×2 this pass byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 1404 bytes). No `deepcopy` / `import copy` / `leaked=` in the CLI source. `cmp` archive vs sibling `ordleak` rc=1. No merge onto `main`. Not merged with sibling `ordleak`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-order` / specimens 009, 012, 060): for named callables, report the binding whose *start* depended only on order, leftover-after labeled leftover, and the order that exposes a status split. Kind: competing-reimplementation of the same harvest as `ordleak`. First Selection kept **ordleak**, not this CLI.

First destroyer (`DESTROYER_leakorder.md`) **MUTATE**. Second (`DESTROYER_leakorder_2.md`) **KEEP**. First KEEP/MUTATE is not protection. Job kill_condition: Honor KILL if leftover-after is still the leak dialect / same-process deepcopy / `leaked_names none` next to `sufficient_exposing_order` ≠ `none`. This pass also Honor-KILL if THIN_WRAPPER of two order greps, or if the object is the same primitive as Honor-KEEP `ordleak_3` (start-of-victim) with extra print and **no leftover-after join**.

`MUTATE.md` claimed isolate + class attrs + start-of-victim + leftover labeled leftover. Host-executed, not trusted. DESTROYER_2 leftovers re-hit, not faked.

**Those Honor-KILL conditions did not fire.** Decision: **KEEP**. Not FIX. Not a required MUTATE of the object. Not KILL. No fossil.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder
ORD=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak
S009=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-009/files/test_order.py
S012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files/test_order.py
S060=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-060/files/test_class_leak.py
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/fixtures
SCRATCH=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_leakorder3_scratch
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not merge this binary into `ordleak`. Sibling `ordleak` (Honor-KEEP after DESTROYER_ordleak_3) is start-of-victim + `into`/`via` + copy-import-tree. This CLI asks the same harvest question with a leftover-after column. Later jury picks one PATH install.

---

## Honor KILL (did not fire)

| condition | host result |
| --- | --- |
| leftover-after still the *leak* dialect (`leaked=` on order lines) | **no.** Order lines have `leftover=` and no `leaked=`. CLI source has 0 `leaked=` tokens. Hunt across this pass's leakorder `*.out` order lines: **0** `leaked=` hits. |
| same-process deepcopy of `vars(mod)` | **no.** No `copy`/`deepcopy`. CLI always `render(..., isolated=True)` → one `subprocess.run` worker per order. pid probe: `a 32408` / `b 32408` then `b 32409` / `a 32409`. `unique_pids=['32408','32409']` subprocess_isolation=YES. Helper `n=11` / `n=10`, never `n=21`. |
| `leaked_names none` next to `sufficient_exposing_order` ≠ `none` | **no.** Hunt across this pass's leakorder `*.out`: **0 hits**. Splits with no snapshotted writer are `unknown` (env, fs-with-cleanup, contextvars, `sys.modules`, `os.chdir`, `object()` identity). |
| THIN_WRAPPER of two order greps / start snapshots the caller already labeled | **no.** Caller gives FILE. Discovery + structured snapshot names `acc` / `Box.bucket` / `_acc` / `holder.acc` / `bag.__defaults__[0]` / closure `acc` / `f.cache_info.currsize` / `box` / `box.n`. `run_orders.py` already prints `acc_after ['a']` for a known name; it does not name `Box.bucket`. |
| same primitive as KEEP `ordleak_3` with extra print, **no leftover-after join** | **no.** leftover-after diverges from start-of-victim (restore / cleanup / leftover-only). Not a reprint of `leaked acc into test_b [] ['a'] via test_a`. |

`leftover={'acc': ['a']}` on a green order is leftover-after **labeled leftover**, which DESTROYER_1 item 3 allowed. That is not the leak column. Hidden leak (both PASS) names `acc` because start of `test_b` differs; `sufficient_exposing_order none`. That is start-of-victim, the harvest question, plus leftover-after on both green orders.

---

## Leftover-after join vs Honor-KEEP `ordleak_3` (Honor KILL 5)

Same harvest, two surfaces. Host, same files, sibling not merged:

```text
# leakorder S009
order test_a,test_b  test_a=PASS test_b=FAIL ['a']  leftover={'acc': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leftover={'acc': ['a']}
leaked_names  acc
sufficient_exposing_order  test_a,test_b
rc=1

# ordleak S009 test_a test_b
exposing_order  test_a test_b
leaked  acc  into  test_b  []  ['a']  via  test_a
rc=1
```

specimen-060: leakorder `leftover={'Box.bucket': ['a']}` / `leaked_names Box.bucket`; ordleak `leaked Box.bucket into test_b [] ['a'] via test_a`. `_acc`: both name `_acc` (DESTROYER_2's "underscore names" distinct-surface vs *then*-ordleak is gone after ordleak mutate-3). FILE-only argv + discovery remain a surface; they are not the leftover-after join.

The leftover-after join is host-true when leftover and start-of-victim **disagree**:

```text
# restore.py — victim finally-clears acc
# leakorder
order test_a,test_b  test_a=PASS test_b=FAIL []  leftover={}
order test_b,test_a  test_b=PASS test_a=PASS  leftover={'acc': ['a']}
leaked_names  acc
sufficient_exposing_order  test_a,test_b
# ordleak still
leaked  acc  into  test_b  []  ['a']  via  test_a
```

Exposing-order leftover-after is `{}` (restored). `leaked_names` is still `acc` (start of `test_b` differed). ordleak's `into`/`via` row does not print that restore. That is leftover-after labeled leftover, not extra print of start-of-victim.

```text
# cleanup_pass.py — test_b clears, both PASS
leftover=['{}', "{'acc': ['a']}"]  leaked_names=acc  sufficient=none  rc=1

# leftover_only.py — both append, both PASS
leftover=["{'acc': ['a', 'b']}", "{'acc': ['b', 'a']}"]  leaked_names=acc  sufficient=none  rc=1

# same_twice.py — --order test_a twice
leftover=["{'acc': ['a']}", "{'acc': ['a']}"]  leaked_names=none  sufficient=none  rc=0
```

`same_twice` is leftover-after without a start-of-victim leak. `leaked_names none` here is honest: starts of `test_a` were both `[]`.

KILL as competing reimpl would have been honor if leftover were always the same dict as `leaked_names` / reconstructable from `into`/`via` with no leftover-after work. It is not. Do not keep both as competing PATH installs. Do not merge the binaries.

---

## What DESTROYER_2 still holds (host-executed this pass)

### specimen-060 `Box.bucket`

```text
order test_a,test_b  test_a=PASS test_b=FAIL ['a']  leftover={'Box.bucket': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leftover={'Box.bucket': ['a']}
leaked_names  Box.bucket
sufficient_exposing_order  test_a,test_b
rc=1
```

DESTROYER_1 on this same file: `leaked_names none`, `leftover={}`, rc=0. Still closed. Space-in-name names `acc` on a copy of 009, rc=1.

### specimen-009 / 012 module global `acc`

specimen-012 remains byte-identical to 009 (`cmp` rc=0). Both name `acc` / `test_a,test_b` / leftover `{'acc': ['a']}`. Unseen this cut is 060 + helper + restore, not 012.

### Isolation is a process pair

Helper `from helper import bucket`: reverse PASSes; leftover `{'bucket': ['a']}`; `leaked_names bucket`; sufficient `test_a,test_b`; rc=1.

Helper `import helper` counter: `n=11` / `n=10`, **never `n=21`**. Both orders FAIL; `sufficient_exposing_order none`; `leaked_names helper.n`; leftover-after of the reverse order is `{'helper.n': 11}` (test_b +=10 then test_a +=1). FAIL detail `n=10` is start-of-that-call, leftover is after the whole order.

Env split: `leaked_names unknown`, leftover `{}`, sufficient `test_a,test_b`, rc=1. Not `none`.

### Start-of-victim, not leftover-after, for `leaked_names`

| probe | leftover | leaked_names | sufficient | rc |
| --- | --- | --- | --- | ---: |
| hidden leak, both PASS | `{'acc': ['a']}` both | `acc` | `none` | 1 |
| `nan` + `object()` import identity | `{}` | `none` | `none` | 0 |
| `time.time_ns()` stamp | `{}` | `none` | `none` | 0 |
| always-fail `test_b` + real `acc` | `{'acc': ['a']}` | `acc` | `none` | 1 |
| empty file | (no order rows) | `none` | `none` | 0 |
| `unseen_bucket.py` without `--order` | `{'bucket': {'w'}}` | `bucket` | `test_write,test_empty` | 1 |

`sufficient` is unique fail-vs-pass, not first non-PASS. Empty file does not invent `test_a,test_b`.

### Class attrs and the other FILE hiding places

Named, not `none`: `_acc`, `holder.acc`, `bag.__defaults__[0]`, closure `acc`, `box.n` under custom `__eq__`, `TestOrder.bucket` with `--order Class.method`, `f.cache_info.currsize`, FILE-level slots instance as `box`.

Unseen splits are `unknown`, not `none`: env, contextvars, `sys.modules`, `os.chdir`, `object()` identity swap, filesystem marker **with** cleanup that preserves the split.

`async def` / generator = ERROR, not PASS. `SystemExit(3)` = `test_a=ERROR SystemExit: 3`, CLI rc≠3. Missing file / no args: rc=2. NUL source: `leakorder: SyntaxError` rc=1.

---

## Remaining holes (documented; not Honor KILL)

DESTROYER_2 leftovers, re-hit this pass. They are not leftover-after-as-leak, not same-process deepcopy, not `none` next to a split, not missing leftover-after join.

1. **Filesystem marker next to FILE still smears.** Workers `cwd` to FILE's directory. No sibling copy (ordleak copies `.py` into a temp tree). Marker without cleanup: both orders FAIL, `leaked_names none`, `sufficient none`, rc=0, file left on disk (`MARKER_SMEAR exists=True`). Marker with unlink-in-victim: split survives and is `unknown`. Env is isolated; a FILE-dir write is not. Dual-FAIL smear looks like a clean pair here; that is this CLI's ceiling, not ordleak's `<unseen>` rc=1. Do not copy ordleak's temp-tree to look less like leftover-after.

2. **Relative `from .helper import bucket` still fails** (`leakorder: ImportError: attempted relative import with no known parent package`). Absolute `import helper` is the dogfood.

3. **Unittest `class TestOrder` is not discovered.** Default run: no order rows, `leaked_names none`, `sufficient none`, rc=0. `--order TestOrder.test_a,TestOrder.test_b` names `TestOrder.bucket`. DESTROYER_1 asked to discover or require names honestly; default still misses class methods.

4. **Three-test default is the full list and its reverse**, not every pair. `test_a`/`test_b`/`test_c` named `acc` and `test_a,test_b,test_c`. `--order test_a,test_c` still required for the subset pair.

5. **`__repr__` that raises aborts the worker** (`leakorder: RuntimeError: boom`, rc=1, no report). Structured snapshot still ends in `repr`.

6. **Dual-ERROR (async / generator / SystemExit) is rc=0.** Both orders have ERROR, `sufficient none`, `leaked_names none`. MUTATE.md said rc=0 only for the clean pair; dual-ERROR is not a unique split and not a named leak. Honesty leftover, not `none` next to a split.

7. **FILE-level slots name `box`, not `box.n`.** leftover `{'box': {'n': 1}}`. Honor-KEEP ordleak names both `box` and `box.n`. Completeness of the object model, not a missing leftover-after join.

8. **Same harvest question as Honor-KEEP `ordleak`.** Distinct surface: FILE-only argv, leftover-after column, discovery. `_` names are no longer distinct (ordleak_3 names `_acc`). First Selection already kept `ordleak`. Do not keep both as competing PATH installs. Do not merge the binaries. Jury picks one.

9. **No timeout of a runaway *test* beyond the 20s worker bound.** Infinite loops become `leakorder: timeout running order`.

Do not mutate further to escape a KILL that does not apply. Do not copy ordleak's temp-tree isolation just to look less like leftover-after. Do not send this back to R1. Do not become ordleak.

---

## Primitive

Reality-stripped operation: discover `test_*` (or take `--order`), spawn one subprocess per order with FILE's directory on `sys.path`, snapshot FILE globals / class attrs / function attrs / defaults / closures / sibling local modules as structured values, diff **start-of-victim** across orders for keys that a callable wrote, print leftover-after as `leftover=`, print unique fail-vs-pass as `sufficient_exposing_order`, print `unknown` when a split has no snapshotted writer. rc=1 when a leak is named or a split is unnamed; rc=0 when there is no named leak and no unique exposing split (including dual-FAIL smear and dual-ERROR).

Nearest ordinary workflow: specimen `run_orders.py` / two pytest nodeid lines, plus looking at `acc` / `Box.bucket`. Observable capability lost if leakorder vanishes: the **name** of the order-dependent start binding plus a leftover-after column that can be empty on the exposing order while start-of-victim still names the writer, as one FILE query. Sibling `ordleak` already names start-of-victim + `Box.bucket` + `via` + copy-import-tree. This CLI is a second embodiment of that harvest with leftover-after labeled leftover, not `run_orders.py` with extra print, and not extra print of `ordleak`'s `into`/`via` row.

That is why this is KEEP, not KILL: DESTROYER_1 required (1)+(2)+(4) or a later destroyer should KILL as leftover-after / same-process deepcopy / `none` next to a split. DESTROYER_2 landed those. This pass Honor-KILL added THIN_WRAPPER and competing-reimpl-without-leftover-after-join. Neither landed. Dreamer ancestry is not protection. First MUTATE is not protection. First KEEP is not protection. The kill condition still does not hold.

That is why this is not MUTATE: remaining holes are DESTROYER_2's advertised ceiling (FILE-dir smear, relative import, default discovery, three-test reverse, `repr` abort, 20s timeout) plus dual-ERROR rc=0 and slots naming `box` not `box.n`. Copying ordleak's import tree would be becoming the kept sibling. Do not.

Hardcoded ceiling:

- leftover-after remains a labeled `leftover=` column (green `test_a` still mutates; restore can empty it on the exposing order)
- FILE-dir writes smear across children; dual-FAIL smear is rc=0 `leaked_names none`
- default discovery is top-level `test_*`, not `Class.method`
- default orders are discovered list + reverse, not every pair
- relative import without a package is an error
- `repr` of a snapshotted value can abort the worker
- dual-ERROR is rc=0
- 20s order timeout; repr cap 240 / leftover cap 500
- competing start-of-victim CLI next to first-selection `ordleak`; leftover-after is the distinct join, not a PATH license for both

---

KEEP
