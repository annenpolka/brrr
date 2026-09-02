# DESTROYER leakorder 2

Date: 2026-09-02 15:45 JST
RUN_ID: specimen-hdd-20260902-1112
Job: `job-0379`
Worker: `destroyer-leakorder-2`

Target (archive, after isolate / class-attr mutate):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder`

CLI sha256 `d711f95c4a8ff27e55b75fc93cae58ea4e1ee1ff4e837df68e594466afaa767d` (20896 bytes, 638 lines). Matches `MUTATE.md`. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-leakorder-isolate/leakorder/leakorder` and `leakorder.py` are byte-identical (`cmp` rc=0). Branch `specimen-hdd/candidate-leakorder-isolate`. Isolate commit `3fc09c071650729ecd97cabf809e7b028f0d0053`. HEAD `e405a75` only records that hash in `MUTATE.md`. Parent `main` is `432f954`; `git ls-tree HEAD leakorder` empty. Host Python 3.14.5. unittest 24/24 OK (2.078s). `./demo.sh` ×2 this pass byte-identical; archived `demo-1.log` / `demo-2.log` already identical. No `deepcopy` / `import copy` in the CLI. No merge onto `main`. Not merged with sibling `ordleak`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-order` / specimens 009, 012, 060): for named callables, report the binding whose *start* depended only on order, leftover-after labeled leftover, and the order that exposes a status split. Kind: competing-reimplementation of the same harvest as `ordleak`. First Selection kept **ordleak**, not this CLI.

First destroyer (`DESTROYER_leakorder.md`) **MUTATE**. Required (1) class attributes (or refuse `none` next to a split), (2) isolate orders for real, (4) `sufficient_exposing_order` is a unique fail-vs-pass split. Kill later if leftover-after stayed the leak dialect, if isolation stayed a same-process deepcopy of `vars(mod)`, or if `leaked_names none` sat next to `sufficient_exposing_order` ≠ `none`. Job kill_condition: Honor KILL if still leftover-after / same-process deepcopy / `leaked_names none` next to sufficient.

`MUTATE.md` claimed isolate + class attrs + start-of-victim. Host-executed, not trusted.

**Those Honor-KILL conditions did not fire.** Decision: **KEEP**. Not FIX. Not a required MUTATE of the object. Not KILL. No fossil.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder
ORD=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak
S009=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-009/files/test_order.py
S012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files/test_order.py
S060=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-060/files/test_class_leak.py
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/fixtures
SCRATCH=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_leakorder2_scratch
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not merge this binary into `ordleak`. Sibling `ordleak` is start-of-victim; this CLI now asks the same harvest question with a leftover column. Later jury picks one.

---

## Honor KILL (did not fire)

| condition | host result |
| --- | --- |
| still leftover-after as the *leak* dialect | **no.** Order lines have `leftover=` and no `leaked=`. `leaked_names` is start-of-victim + writer. Hunt: 0 `leaked=` tokens on `order` lines in this pass's outs. |
| same-process deepcopy | **no.** No `copy`/`deepcopy`. CLI always `render(..., isolated=True)` → one `subprocess.run` worker per order. FAIL details `pid=6758` vs `pid=6759`. leftover `seen` `[6763, 6763]` vs `[6764, 6764]`. |
| `leaked_names none` next to `sufficient_exposing_order` ≠ `none` | **no.** Hunt across this pass's `*.out`: **0 hits**. Splits with no snapshotted writer are `unknown` (env, fs-with-cleanup, contextvars, `sys.modules`, builtins, `os.chdir`, `object()` identity). |

`leftover={'acc': ['a']}` on a green order is leftover-after **labeled leftover**, which DESTROYER_1 item 3 allowed. That is not the leak column. Hidden leak (both PASS) names `acc` because start of `test_b` differs; `sufficient_exposing_order none`. That is start-of-victim, the harvest question.

---

## What the mutation still holds (host-executed)

### specimen-060 `Box.bucket` (owned packet, not the fixture copy)

```bash
python3 "$CLI" "$S060"; echo rc=$?
```

```text
file  .../specimens/specimen-060/files/test_class_leak.py
order test_a,test_b  test_a=PASS test_b=FAIL ['a']  leftover={'Box.bucket': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leftover={'Box.bucket': ['a']}
leaked_names  Box.bucket
sufficient_exposing_order  test_a,test_b
order_axis  fail=['test_a,test_b'] pass=['test_b,test_a']
rc=1
```

DESTROYER_1 on this same file: `leaked_names none`, `leftover={}`, rc=0. Closed. Space-in-name and symlink to the same packet also name `Box.bucket`, rc=1.

Honesty, same file, sibling (not merged, not this victim):

```bash
python3 "$ORD" "$S060" test_a test_b
# exposing_order  test_a test_b
# leaked  Box.bucket  into  test_b  []  ['a']  via  test_a
# rc=1
```

### specimen-009 / 012 module global `acc`

```text
order test_a,test_b  test_a=PASS test_b=FAIL ['a']  leftover={'acc': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leftover={'acc': ['a']}
leaked_names  acc
sufficient_exposing_order  test_a,test_b
rc=1
```

No `leaked=acc` on the passing order line. specimen-012 is still byte-identical to 009; it is not unseen. Unseen this cut is 060 + helper.

### Isolation is a process pair, not two `load_fresh` calls in one world

Helper `from helper import bucket`: reverse PASSes; leftover `{'bucket': ['a']}`; `leaked_names bucket`; sufficient `test_a,test_b`; rc=1.

Helper `import helper` counter: `n=11` / `n=10`, **never `n=21`**. Both orders FAIL (always-assert); `sufficient_exposing_order none`; `leaked_names helper.n`. DESTROYER_1 smear is closed.

Env split (`os.environ["LEAKORDER_MARK"]`): `leaked_names unknown`, sufficient `test_a,test_b`, rc=1. Not `none`.

### Start-of-victim, not leftover-after, for `leaked_names`

| probe | leaked_names | sufficient | rc |
| --- | --- | --- | ---: |
| hidden leak, both PASS | `acc` | `none` | 1 |
| `nan` + `object()` import identity, tests `pass` | `none` | `none` | 0 |
| `time.time_ns()` stamp, tests `pass` | `none` | `none` | 0 |
| always-fail `test_b` + real `acc` | `acc` | `none` | 1 |
| empty file | `none` | `none` | 0 |
| `unseen_bucket.py` without `--order` | `bucket` | `test_write,test_empty` | 1 |

`sufficient` is unique fail-vs-pass, not first non-PASS. Empty file does not invent `test_a,test_b`.

### Class attrs and the other FILE hiding places

Named, not `none`: `_acc`, `holder.acc`, `bag.__defaults__[0]`, closure `acc`, `box.n` under custom `__eq__`, inherited `Base.bucket`, `TestOrder.bucket` with `--order Class.method`, `bag.xs` on a callable instance, `f.cache_info.currsize`, `box.n` SimpleNamespace, slots instance as `box`, `buf` bytearray, `q.queue`.

Unseen splits are `unknown`, not `none`: env, contextvars, `sys.modules`, builtins monkeypatch, `os.chdir`, `object()` identity swap, filesystem marker **with** cleanup that preserves the split.

`async def` / generator = ERROR, not PASS. `SystemExit(3)` = `test_a=ERROR SystemExit: 3`, CLI rc≠3. Missing file / directory / `/dev/null`: `leakorder: file not found` rc=2. No args: argparse rc=2. NUL source: `leakorder: SyntaxError` rc=1.

---

## Remaining holes (documented; not Honor KILL)

These are MUTATE.md leftovers, re-hit, not faked. They are not leftover-after-as-leak, not same-process deepcopy, not `none` next to a split.

1. **Filesystem marker next to FILE still smears.** Workers `cwd` to FILE's directory. No sibling copy (ordleak copies `.py` into a temp tree). Marker without cleanup: both orders FAIL, `leaked_names none`, `sufficient none`, rc=0, file left on disk. Marker with unlink-in-victim: split survives and is `unknown`. Env is isolated; a FILE-dir write is not.

2. **Relative `from .helper import bucket` still fails** (`leakorder: ImportError: attempted relative import with no known parent package`). Absolute `import helper` is the dogfood.

3. **Unittest `class TestOrder` is not discovered.** Default run: no order rows, `leaked_names none`, `sufficient none`, rc=0. `--order TestOrder.test_a,TestOrder.test_b` names `TestOrder.bucket`. DESTROYER_1 asked to discover or require names honestly; default still misses class methods.

4. **Three-test default is the full list and its reverse**, not every pair. This pass's `test_a`/`test_b`/`test_c` still named `acc` and `test_a,test_b,test_c`. `--order` still required for a subset pair.

5. **`__repr__` that raises aborts the worker** (`leakorder: RuntimeError: boom`, rc=1, no report). Structured snapshot still ends in `repr`.

6. **Same harvest question as mutated `ordleak`.** Distinct surface: FILE-only argv, leftover column, discovery, `_` names. First Selection already kept `ordleak`. Do not keep both as competing PATH installs. Do not merge the binaries. Jury picks one.

7. **No timeout of a runaway *test* beyond the 20s worker bound.** Infinite loops become `leakorder: timeout running order`.

Do not mutate further to escape a KILL that does not apply. Do not copy ordleak's temp-tree isolation just to look less like leftover-after. Do not send this back to R1.

---

## Primitive

Reality-stripped operation: discover `test_*` (or take `--order`), spawn one subprocess per order with FILE's directory on `sys.path`, snapshot FILE globals / class attrs / function attrs / defaults / closures / sibling local modules as structured values, diff **start-of-victim** across orders for keys that a callable wrote, print leftover-after as `leftover=`, print unique fail-vs-pass as `sufficient_exposing_order`, print `unknown` when a split has no snapshotted writer. rc=1 when a leak is named or a split is unnamed; rc=0 only for the clean pair.

Nearest ordinary workflow: specimen `run_orders.py` / two pytest nodeid lines, plus looking at `acc` / `Box.bucket`. Observable capability lost if leakorder vanishes: the **name** of the order-dependent start binding (including class attributes and `_` names) plus a leftover column and a unique exposing order, as one FILE query. Sibling `ordleak` already names start-of-victim + `Box.bucket` + `via`. This CLI is a second embodiment of that join, not `run_orders.py` with extra print.

That is why this is KEEP, not KILL: DESTROYER_1 required (1)+(2)+(4) or a later destroyer should KILL as leftover-after / same-process deepcopy / `none` next to a split. All three landed, host-executed, including specimen-060 `Box.bucket`. Dreamer ancestry is not protection. First MUTATE is not protection. The kill condition still does not hold.

Hardcoded ceiling:

- leftover-after remains a labeled `leftover=` column (green `test_a` still mutates)
- FILE-dir writes smear across children
- default discovery is top-level `test_*`, not `Class.method`
- default orders are discovered list + reverse, not every pair
- relative import without a package is an error
- `repr` of a snapshotted value can abort the worker
- 20s order timeout; repr cap 240 / leftover cap 500
- competing start-of-victim CLI next to first-selection `ordleak`

---

KEEP
