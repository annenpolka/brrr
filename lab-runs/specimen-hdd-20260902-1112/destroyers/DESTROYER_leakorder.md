# DESTROYER leakorder

Date: 2026-09-02 12:29 JST

Target (harvested competing reimpl): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder`

sha256 `6710f7f5e1a4c959c2491d35804ace5504759ec703638da66f1f00f51c13581a` (4127 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/leakorder-leakorder/leakorder/leakorder.py` is byte-identical. `tests/` is empty.

Origin claim (`CANDIDATE.md`): CLI over a Python file of `test_*` callables. Reports leaked module names and the order sufficient to expose them. Specimens `[specimen-009, specimen-012]`. Kind: competing-reimplementation of the same harvest as `ordleak`.

Happy path is real. Specimen-009 `test_a` then `test_b` fails with leftover `{'acc': ['a']}`; reverse passes; the report names `acc` and `sufficient_exposing_order test_a,test_b`. That is not enough. Isolation is a same-process fiction with a fixed module name `leakorder_mod`, "leaked" is a within-order leftover (pre/post of each callable), and `leaked_names none` is emitted while a status split is sitting on the next line.

Adversarial transfer this file exists to run: specimen-060 class-attribute leak. Mutated sibling `ordleak` names `Box.bucket`. This CLI does not.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder
S009=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-009/files/test_order.py
S012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files/test_order.py
S060=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-060/files/test_class_leak.py
UNSEEN=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/fixtures/unseen_bucket.py
ORD=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak
```

No merge onto `main`. This object is not a PATH install.

---

## What still works

The owned module-list pair, and any other pair of 0-argument top-level functions that share a module-level `list` / `set` / `dict` / similar deepcopy-and-`==` value.

```bash
python3 "$CLI" "$S009"
```

```text
file  .../specimen-009/files/test_order.py
order test_a,test_b  test_a=PASS test_b=FAIL  leaked=acc  leftover={'acc': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leaked=acc  leftover={'acc': ['a']}
leaked_names  acc
sufficient_exposing_order  test_a,test_b
order_axis  fail=['test_a,test_b'] pass=['test_b,test_a']
rc=0
```

Set-bucket rename (`unseen_bucket.py` `test_write` / `test_empty`) names `bucket` **if** `--order` is passed. Two leaked FILE globals both appear (`acc,other`). Unicode names (`箱`, `test_α`) work. Dataclass **instance** `state = S([])` at module level names `state`. `threading.Lock` survives via `repr` (`unlocked` → `locked`). Hidden leak without a failing assert (`test_a` mutates, `test_b` is `pass`) still names `acc` and honestly says `sufficient_exposing_order none`. Import-time `time.time_ns()` is **not** reported as a leak (within-order leftover; unlike sibling `ordleak`). Relative path, space in filename, symlink: rc=0.

Missing path / directory / `/dev/null`: `leakorder: file not found` rc=2. No args: argparse usage rc=2.

That is the whole useful delta. Attacks below break the isolation claim around it, or show the primitive cannot see the usual Python hiding places for order-dependent state.

---

## Implementation

### 1. specimen-060: class attribute is `leaked_names none` next to a real exposing order

Owned adversarial packet. `Box.bucket` appends in `test_a`; `test_b` asserts empty. Order still splits PASS/FAIL. Snapshot walks `vars(mod)` and skips `callable` values. Classes are callable. `Box` is dropped. `snapshot(load_fresh(S060))` is `{}`.

```bash
python3 "$CLI" "$S060"
```

```text
order test_a,test_b  test_a=PASS test_b=FAIL  leaked=none  leftover={}
order test_b,test_a  test_b=PASS test_a=PASS  leaked=none  leftover={}
leaked_names  none
sufficient_exposing_order  test_a,test_b
order_axis  fail=['test_a,test_b'] pass=['test_b,test_a']
rc=0
```

Honesty, same file, mutated sibling:

```bash
python3 "$ORD" "$S060" test_a test_b
# exposing_order  test_a test_b
# leaked  Box.bucket  into  test_b  []  ['a']  via  test_a
# rc=1
```

A module-level **instance** `box = Box(); box.bucket = []` *is* seen (`leaked=box`), because the instance is not callable. The miss is specifically the class attribute — the shape specimen-060 was built to hold.

Same FAIL `['a']` (computed internally, then discarded from the report; see §8). The join the harvest promised is missing. `leaked_names none` is unsupported certainty: it reads as "no binding differed", not "we refused to look at the name that differed".

### 2. The other usual hiding places are the same lie

| where the state actually lives | status split | leaked_names |
| --- | --- | --- |
| `class Box: bucket = []` (specimen-060) | yes | `none` |
| `_acc = []` | yes | `none` |
| `holder.acc = []` | yes | `none` |
| mutable default `def bag(xs=[]):` | yes | `none` |
| closure cell from `make()` | yes | `none` |
| `@lru_cache` `currsize` | yes | `none` |
| `import helper; helper.bucket` | both orders FAIL | `none` |
| `os.environ` / side file | both orders FAIL | `none` |
| custom `__eq__` always true on `box.n` | yes | `none` |

`is_binding` is `not name.startswith("_")` and `not callable` and `not ModuleType`. Functions, classes, modules, and `_` names are invisible. A status split with unnamed leak is the current product.

### 3. "Each order is a fresh load" is false for anything not this FILE's dict

`load_fresh` uses the **same** module name `"leakorder_mod"` every time and does not put FILE's directory on `sys.path`. Both orders run in **one process**. `sys.modules` keeps imported helpers. `os.environ` and the filesystem survive into the second order.

Sibling import without `PYTHONPATH` does not even load:

```text
ModuleNotFoundError: No module named 'helper'
```

Traceback through `leakorder:19 load_fresh`, no `leakorder:` prefix, rc=1. Relative `from .helper import bucket`: `attempted relative import with no known parent package`. `python3 "$CLI" FILE` puts the **CLI's** directory on `sys.path[0]` (`.../lineages/candidate-leakorder`), not FILE's directory and not cwd. Confirmed by a probe that wrote `sys.path[:4]` to a side file while cwd was FILE's directory.

With `PYTHONPATH` set to the file's directory:

```python
# helper.py
n = 0
# test_a: helper.n += 1
# test_b: helper.n += 10; raise AssertionError("n=" + str(helper.n))
```

```text
order test_a,test_b  test_a=PASS test_b=FAIL  leaked=none  leftover={}
order test_b,test_a  test_b=FAIL test_a=PASS  leaked=none  leftover={}
sufficient_exposing_order  test_a,test_b
order_axis  fail=['test_a,test_b', 'test_b,test_a'] pass=['none']
rc=0
```

Internal records (same process `render` uses): first order `test_b` FAIL `n=11`; second order `test_b` FAIL `n=21`. The order axis the tool exists to name is gone. `helper` is a `ModuleType` skip, so the FILE-global snapshot never sees `n`.

`from helper import bucket` **is** a FILE global (in-spec leftover). Same process, same helper:

```text
order test_a,test_b  ... leaked=bucket  leftover={'bucket': ['a']}
order test_b,test_a  test_b=FAIL ... leftover={'bucket': ['a', 'a']}
order_axis  fail=[..., ...] pass=['none']
```

`test_b` fails in **both** orders. The leftover row on the reverse order is `['a', 'a']` — bytes from **order 1's `test_a`**, still sitting in `sys.modules['helper']`. `sufficient_exposing_order` still prints the first record, which did not uniquely expose anything.

`os.environ["LEAKORDER_MARK"]` and a marker file do the same: first order writes, second order's "first" test already sees it, statuses agree FAIL, `leaked_names none`. Marker file still on disk after rc=0. Env smear stays inside the CLI process (parent subprocess env was clean); the fs write does not.

### 4. `leaked` is leftover-after, not start-of-victim across orders

On specimen-009 the passing order is:

```text
order test_b,test_a  test_b=PASS test_a=PASS  leaked=acc  leftover={'acc': ['a']}
```

`test_a` mutates even when the suite is green. Two identical passing orders (`--order test_b,test_a` twice) still report `leaked=acc` and `sufficient_exposing_order none`. That is honest leftover accounting and a false "leak" relative to the harvest question (what differed **because order changed**).

Sibling `ordleak` diffs start-of-victim across orders. This CLI diffs pre/post **within** an order and unions the names. Same harvest, two meanings of "leaked". `DESTROYER_ordleak` already said pick one and do not grow a second leftover dialect.

`sufficient()` returns the first record with any non-`PASS`, including `MISSING` and `ERROR`. It is not "the order that exposes a status split".

Always-fail `test_b` (`assert False` first) plus a real `acc` mutation:

```text
order_axis  fail=['test_a,test_b', 'test_b,test_a'] pass=['none']
sufficient_exposing_order  test_a,test_b
leaked_names  acc
```

No passing order exists. The column still names an exposing order.

Empty file / comments-only / missing `test_b` / unittest `class TestOrder` methods:

```text
order test_a,test_b  test_a=MISSING test_b=MISSING  leaked=none  leftover={}
sufficient_exposing_order  test_a,test_b
```

Nothing ran. The tool still claims that order is sufficient to expose a leak.

Default orders are hardcoded `test_a,test_b` and reverse. The lineage's own `unseen_bucket.py` without `--order`:

```text
order test_a,test_b  test_a=MISSING test_b=MISSING  leaked=none
sufficient_exposing_order  test_a,test_b
```

The rename fixture only works if the caller already knows the names. Three-test files ignore `test_c` unless `--order` names it; default run reports leftover `acc` and `sufficient_exposing_order none` while `test_a` then `test_c` is the exposing pair.

### 5. Snapshot inequality is not a write

`float("nan")` at module level, tests are `pass`:

```text
leaked=nan  leftover={'nan': nan}
leaked_names  nan
sufficient_exposing_order  none
```

`nan != nan`. No test mutated `nan`.

`sentinel = object()`: deepcopy succeeds; `==` is identity; two snapshots are two objects:

```text
leaked=sentinel  leftover={'sentinel': <object object at 0x...>}
```

Custom `__eq__` that always returns true **hides** a real `box.n` mutation (`leaked_names none`) while `sufficient_exposing_order test_a,test_b` still fires. Opposite of `nan`.

### 6. `SystemExit` is the CLI's exit; `GeneratorExit` is an uncaught traceback

`invoke` is not a function. `run_one` catches `AssertionError` and `Exception` only.

```bash
# test_a: raise SystemExit(3)
python3 "$CLI" t.py
# rc=3, stdout 0 bytes, stderr 0 bytes, no report
```

```bash
# test_a: raise GeneratorExit()
# rc=1, traceback through leakorder:49 fn(), no leakorder: prefix
```

A test that calls `sys.exit` is indistinguishable from the tool succeeding at status 3. SyntaxError, NUL-byte source, and `import helper` dump raw importlib traces. `import traceback` is unused. Infinite loops hang with no timeout (observed 2s kill, 0 bytes).

`async def test_a` is `PASS` with `RuntimeWarning: coroutine 'test_a' was never awaited` — test did not run, `leaked_names none`. A generator `test_a` (`yield`) is the same silent PASS. Misleading exit zero.

Unittest / pytest `TestOrder.test_a` is `MISSING`. `--order TestOrder.test_a,TestOrder.test_b` is the same. No `Class()` instantiation.

### 7. Isolation identity noise on instances

Each load uses module name `leakorder_mod`. A module-level instance leftover is:

```text
leftover={'box': <leakorder_mod.Box object at 0x105ade580>}
```

The bucket contents are not in the leftover repr. Addresses differ across orders because they are different objects from different loads, not because the value differed at start of victim. Dataclass `__repr__` happens to show `S(acc=['a'])`; a plain class does not.

### 8. The report is not a record; exit 0 does not mean clean

FAIL/ERROR detail is computed then thrown away:

```python
bits = " ".join(f"{n}={s}" for n, s, _ in rec["results"])
```

Internal specimen-009 `test_b` is `FAIL ['a']`. Printed line is `test_b=FAIL`. Helper `n=11` vs `n=21` never appears. `run_orders.py` already prints the assertion detail this CLI drops.

`leftover={...}` is `repr` of a Python dict. A 200k-char append dumps 400370 bytes of stdout with no cap. Tabs/newlines in assertion messages do not split rows **because they are discarded**; leftover `repr` is still not TSV.

Leak present, leak absent, MISSING-as-exposing-order, and `leaked none` next to a status split are all rc=0. Fine as a printer; hostile as a pipe predicate. Mutated `ordleak` exits 1 when a leak is named.

`--order ""` prints `order     leaked=none` and `order_axis pass=['']`. `--order test_a,test_a` is a green "order" with leftover `['a', 'a']`.

### 9. Claimed unseen specimen is a byte copy

```bash
cmp "$S009" "$S012"   # IDENTICAL
```

specimen-012 is the same `acc = []` / `test_a` / `test_b` file. Transfer was not run. The set-bucket pair in `fixtures/unseen_bucket.py` is a real rename and does work **with `--order`**. Default names miss it (§4). That is not what `CANDIDATE.md` cited. `fixtures/specimen009.py` is the same program with extra blank lines; not a second specimen.

Empty `tests/`. No dogfood of class attributes, helpers, `_` names, or rc.

---

## Primitive

Reality-stripped operation: `spec_from_file_location("leakorder_mod", FILE)` twice in one process, call two 0-arg callables (default names hardcoded), `deepcopy` leftover `vars(mod)` skipping callables / modules / `_` names, print names whose pre/post differed **within** an order, print the first non-all-PASS order as `sufficient_exposing_order`.

Nearest ordinary workflow: the specimen already ships `files/run_orders.py`, which runs both orders and prints PASS/FAIL plus `acc_after`. `python3 FILE` in two sequences, or two pytest nodeid lines, plus looking at `acc`, is the same observation. Observable capability lost if leakorder vanishes: the **name** of the mutated module global as one leftover dict, plus a first-failing-order label. That join is real on a module-level list shared by two top-level functions. It is not a test runner, not a fixture tracer, not a class-attribute tracer, not a permutation scanner.

That is why this is not KILL: the *question* (which name leaked between these two tests, and which order is enough) is a debugging object pytest will not emit. The current embodiment is a specimen-009 leftover printer that pretends classes are not state, that two loads are isolated worlds, and that `none` means "looked and found nothing".

The ceiling is already written down, and it is too small for the claim:

- "leaked module names" + `callable` skip → class attributes, function attributes, mutable defaults, closures, `_` names are `leaked_names none` while the status split is real (specimen-060)
- leftover-after + green `test_a` mutation → `leaked=acc` on an all-pass order
- one process + fixed module name → imported aliases, env, and fs smear the second order; `sufficient_exposing_order` still names the first record
- `sufficient` = first non-PASS, including `MISSING` on an empty file
- advertised `test_*` callables; default `test_a,test_b` only
- specimen-012 is not unseen
- mutated sibling `ordleak` already names `Box.bucket` and exits 1

Same-harvest sibling `ordleak` already disagrees on the object. It diffs start-of-victim across orders. This CLI diffs leftover-after. On specimen-009 both name `acc` and `test_a,test_b`. On specimen-060 only `ordleak` names the binding. Two groundings, two meanings of "leaked", one name in the harvest. Pick one. Do not merge them.

---

## Mutation (what must change)

Keep the object: for named callables, report the binding whose value depended only on order, and the order that exposes a status (or assertion-reason) split.

Do not keep a same-process deepcopy of `vars(mod)` that only replays specimen-009 and prints `none` on specimen-060.

1. **See class attributes, or refuse.** Snapshot class attributes, function attributes, mutable defaults, and closure cells on FILE, or print `leaked_names <unseen>` / `unknown` when a status split has no snapshotted binding. `leaked_names none` is illegal next to `sufficient_exposing_order` ≠ `none`. Specimen-060 must name `Box.bucket` (or an honest unseen row). `_acc` must not claim `none`.
2. **Isolate orders for real.** One subprocess per order, or an explicit reset of imported-module dicts plus env plus cwd. FILE's directory (and package parent) on `sys.path`. After that, `from helper import bucket` must show `[]` vs `['a']` into `test_b` via `test_a`, and the reverse order must PASS. If the second order still sees `n=21`, the fresh-load sentence is still a lie.
3. **Leak is order-dependent start, or leftover is labeled leftover.** Do not emit `leaked=acc` on an all-pass order unless the column is renamed `mutated` / `leftover_names`. Do not emit `leaked` for `nan` or `object()` identity. Compare structured values, not type-pointer `==` across loads. Custom `__eq__` that hides `box.n` cannot be `none` next to a split.
4. **`sufficient_exposing_order` is a status split, not first non-PASS.** Empty file / `MISSING` / always-fail-in-both-orders → `none`. If both orders fail, do not name the first argv order as sufficient.
5. **Discover or require names honestly.** Default `test_a,test_b` on a file whose callables are `test_write`/`test_empty` must not invent an exposing order. Implement `Class.method` by instantiating `Class()` and calling the method, or drop class tests from the claim. `async def` / generators are ERROR, not PASS.
6. **Catch `BaseException`.** `SystemExit` and `GeneratorExit` are test ERROR rows, not the CLI's rc and not a traceback. Prefix load errors `leakorder:`. Bound the run. Cap `repr` length. Print FAIL detail (the `['a']` already computed). rc=1 when a leak is named or a split is unnamed; rc=0 only for the clean pair.
7. **One meaning vs `ordleak`.** If this lineage keeps leftover-after, it is not the harvest object and a later destroyer should KILL it in favor of mutated `ordleak`. If it mutates toward start-of-victim + class attributes, it is a second `ordleak` and should not remain a competing CLI under the same name.
8. **Dogfood that is not a copy of specimen-009.** specimen-012 is byte-identical. Next unseen must be specimen-060 (class attribute), a helper-module pair, or an env/fs pair — and the tool must either name the leak or refuse with a non-`none` row. Empty `tests/` is not a suite.

If the mutation cannot do (1)+(2)+(4), the object is still `run_orders.py` with extra print, and a later destroyer should KILL. Do not merge.

---

MUTATE
