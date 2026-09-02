# DESTROYER ordleak

Date: 2026-09-02

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak`

Worktree (byte-identical, sha256 `79552164dc8d0fc0eeed943d39fc5ad69eeb897a4ed7cdfba7b1c180e5a312e9`): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-ordleak-ordleak/ordleak/ordleak`

Same-harvest sibling (different CLI, not this file's victim): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/leakorder-leakorder/leakorder/leakorder.py`

Origin claim: for a named pair, one query names the module binding that differed when only order changed, and the order sufficient to expose it.

Happy path is real. Unit tests (6/6) pass. Specimen-009 `test_a` then `test_b` fails with leftover `['a']`; reverse passes; the report names `acc` and `exposing_order test_a test_b`. That is not enough. Isolation is a same-process fiction, "leaked" is start-snapshot inequality (including import-time noise and cross-load class identity), and `leaked none` is emitted while a status split is sitting on the next line.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak
S009=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-009/files/test_order.py
S012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files/test_order.py
```

---

## What still works

The owned fixture, and any other pair of 0-argument top-level functions that share a module-level `list` / `set` / `dict` / similar deepcopy-and-`==` value.

```bash
python3 "$CLI" "$S009" test_a test_b
```

```text
file	.../specimen-009/files/test_order.py
pair	test_a	test_b
order	test_a test_b
status	test_a	PASS
status	test_b	FAIL	['a']
order	test_b test_a
status	test_b	PASS
status	test_a	PASS
exposing_order	test_a test_b
leaked	acc	into	test_b	[]	['a']	via	test_a
rc=0
```

A renamed set-bucket pair (write, then assert empty) also names `bucket` and the exposing order. Delete and create of a module name are reported as `<absent>`. Two leaked bindings in one pair both appear. Unicode callable names work. Relative and absolute paths resolve. Missing file / directory / syntax error / null-byte source / duplicate names are clean `ordleak:` errors (rc 1 or 2). Hidden leak without a failing assert (`test_a` mutates, `test_c` is `pass`) still names `acc` — that row is the only join `run_orders.py` does not already print.

That is the whole useful delta. Attacks below break the isolation claim around it, or show the primitive cannot see the usual Python hiding places for order-dependent state.

---

## Implementation

### 1. "The two orders do not share state" is false for anything not a fresh module dict

README: "Each order is a fresh import of FILE. … The two orders do not share state." Both orders run in **one process**. `sys.modules.pop` drops only the uuid-named test module. Imported helpers, `os.environ`, and the filesystem survive into the second order.

Sibling import without `PYTHONPATH` does not even load (see §2). With `PYTHONPATH` set to the file's directory:

```python
# helper.py
bucket = []
```

```python
# test_mod.py
import helper
def test_a():
    helper.bucket.append("a")
def test_b():
    assert helper.bucket == [], helper.bucket
```

```text
order	test_a test_b
status	test_a	PASS
status	test_b	FAIL	['a']
order	test_b test_a
status	test_b	FAIL	['a']
status	test_a	PASS
exposing_order	none
leaked	none
rc=0
```

`test_b` fails in **both** orders. The order axis the tool exists to name is gone. `helper` is an `ismodule` skip, so the FILE-global snapshot never sees `bucket`.

`from helper import bucket` **is** a FILE global (in-spec). Same process, same helper:

```text
exposing_order	none
leaked	bucket	into	test_a	[]	['a']	via	test_b
```

`test_b` still fails in both orders (`['a']`). The leaked row attributes `['a']` at the start of `test_a` to `via test_b`. `test_b` does not append. The bytes came from **order 1's `test_a`**, still sitting in `sys.modules['helper']`. `via` is the other name in the pair, not the writer.

A counter on the helper makes the cross-order smear numeric:

```python
# helper.py
n = 0
# test_a: helper.n += 1
# test_b: raise AssertionError(f"n={helper.n}") after helper.n += 10
```

```text
status	test_b	FAIL	n=1     # first order
status	test_b	FAIL	n=11    # second order, helper.n was left at 11
exposing_order	none
leaked	none
```

`os.environ` and a side file do the same: first order writes, second order's "first" test already sees it, statuses agree FAIL, `leaked none`, `exposing_order none`. Marker file still on disk after rc=0.

CANDIDATE.md declined an other-module / env / fs tracer. That does not license a second order that is not a second process. In-spec FILE bindings that alias imported objects are already wrong.

### 2. FILE's directory is not on `sys.path`

`python3 "$CLI" FILE …` puts the **CLI's** directory on `sys.path[0]`, not FILE's directory and not cwd. `import helper` next to the test file is `ordleak: No module named 'helper'` (rc=1) even when cwd is that directory. Relative package import is `attempted relative import with no known parent package`. pytest would have put the rootdir on the path. The tool cannot load a normal two-file test layout without the caller exporting `PYTHONPATH`, and exporting it then triggers §1.

### 3. `leaked none` next to a real exposing order: skipped identities

`is_binding` drops `_`-prefixed names, functions, methods, classes, modules. The status split still happens. The name the developer needed does not.

| where the state actually lives | exposing_order | leaked |
| --- | --- | --- |
| `_acc = []` | `test_a test_b` | `none` |
| `class Store: acc = []` | `test_a test_b` | `none` |
| `def holder(): …; holder.acc = []` | `test_a test_b` | `none` |
| mutable default `def bag(xs=[]):` | `test_a test_b` | `none` |

Same FAIL `['a']` as specimen-009. The join the harvest promised is missing. `leaked none` is unsupported certainty: it reads as "no binding differed", not "we refused to look at the name that differed".

`@lru_cache` wrappers are the opposite bug: `inspect.isfunction` is false, so the wrapper is snapshotted. Two loads produce two objects. Report is two `leaked cached` rows of `<functools._lru_cache_wrapper object at 0x…>` with swapped ids — identity noise, not `currsize`.

### 4. Fresh module name makes class instances "leak" even when values match

Each order is `SourceFileLoader("_ordleak_" + uuid)`. Dataclass `S` in FILE is a **different type object** per load. `copy.deepcopy` succeeds; `==` is false because the types differ; `repr` is identical.

```text
exposing_order	test_a test_b
leaked	state	into	test_a	S(acc=[])	S(acc=[])	via	test_b
leaked	state	into	test_b	S(acc=[])	S(acc=['a'])	via	test_a
```

The first row is a false leak: `acc` is `[]` on both sides. Confirmed outside the CLI:

```text
type equal False
== False
repr S(acc=[]) S(acc=[])
acc equal True
```

Isolation-by-uuid and value-equality cannot both be naive. The same hole fires for `object()` rebinds, `StringIO` repr-by-id, and `threading.Lock` (deepcopy fails → `repr`; unlocked vs unlocked still differs by address; locked vs unlocked is only visible because `"locked"` appears in the string).

### 5. Import-time nondeterminism is reported as a leak

```python
stamp = time.time_ns()   # or random.random()
def test_a(): pass
def test_b(): pass
```

```text
exposing_order	none
leaked	stamp	into	test_a	1788318350797674000	1788318350797727000	via	test_b
leaked	stamp	into	test_b	1788318350797727000	1788318350797674000	via	test_a
rc=0
```

No test mutated `stamp`. "Leaked" here means "two imports disagreed". `float("nan")` is worse: `nan == nan` is false, so `leaked nan nan` with no test and no exposing order. A custom `__eq__` that always returns true hides a real `box.n` mutation (`leaked none`) while `exposing_order test_a test_b` still fires.

### 6. Advertised pytest nodeids do not run pytest tests

README: `ordleak FILE::LEFT FILE::RIGHT`. Parser is `split("::", 1)`. `FILE::TestOrder::test_a` becomes callable name `TestOrder::test_a`. `getattr` fails (rc=1). Dotted `TestOrder.test_a` fails. Unittest methods are not module globals; `test_a` is missing. 0-arg call of a fixture-parameterized function is `ERROR TypeError: missing … 'ready'` in both orders, `exposing_order none`. Harvest said no pytest plugin inference; the CLI still pretends nodeids are the interface.

`async def` is `PASS` with `RuntimeWarning: coroutine 'test_a' was never awaited` — tests did not run, `leaked none`. A generator `test_a` (`yield`) is the same silent PASS. Misleading exit zero.

### 7. `SystemExit` is the CLI's exit; `GeneratorExit` is an uncaught traceback

`invoke` catches `Exception` only.

```bash
# test_a: raise SystemExit(3)
python3 "$CLI" t.py test_a test_b
# rc=3, stdout 0 bytes, stderr 0 bytes, no report
```

```bash
# test_a: raise GeneratorExit()
# rc=1, traceback through ordleak:68 invoke, no `ordleak:` prefix
```

A test that calls `sys.exit` is indistinguishable from the tool succeeding at status 3. Infinite loops hang with no timeout (observed 2s kill).

### 8. TSV is not a TSV; exit 0 does not mean clean

Assertion detail is concatenated with tabs and raw newlines:

```text
status	test_b	FAIL	tab	here
and newline ['a']
```

`splitlines` becomes 11 rows instead of 10. `cut -f*` on the happy path is stable (`leaked` is 8 columns; FAIL-with-detail is 4). A tab in the failure message is not. 200k-char leftover `repr`s dump ~400k stdout with no cap.

Leak present and leak absent are both rc=0. Fine as a printer; hostile as a pipe predicate. pytest on the same pair is rc=1 vs rc=0.

### 9. `exposing_order` is a status split, not an order-dependent reason

Victim that fails on the leak **and** would fail anyway (`assert acc == []; assert False`):

```text
status	test_b	FAIL	['a']     # after test_a
status	test_b	FAIL           # run first, then assert False
exposing_order	none
leaked	acc	into	test_b	[]	['a']	via	test_a
```

Statuses agree, so the order that exposes the leak is `none`, while the leaked row tells the truth. Always-fail `test_a` plus order-dependent `test_b` does list `exposing_order test_a test_b` (because `test_b`'s status splits). The column is "which sequences contain a non-PASS that was PASS in the other sequence", not "which order is sufficient to expose the leak". Mutual flags list **both** orders, BA first, because the loop walks AB's names and appends the non-PASS side of each split.

### 10. Claimed unseen specimen is a byte copy

```bash
cmp "$S009" "$S012"   # IDENTICAL
```

specimen-012 is the same `acc = []` / `test_a` / `test_b` file. Transfer was not run. The set-bucket pair in the sibling leakorder fixture is a real rename and does work; that is not what CANDIDATE.md cited.

### 11. Empty / weird inputs (non-fatal)

| input | rc | note |
| --- | --- | --- |
| no args | 2 | argparse usage |
| missing path | 1 | `not a file` |
| directory | 1 | `not a file` |
| `/dev/null` | 1 | char device, `Path.is_file()` false |
| empty file / no such callable | 1 | `no test callable` |
| same name twice | 1 | `must be different` |
| 2 or 4 tokens | 2 | usage |
| syntax error | 1 | `invalid syntax` |
| NUL bytes | 1 | `cannot contain null bytes` |
| nodeids on two different files | 2 | even when contents match |
| space + `;` in filename | 0 | works (argv, not shell) |
| symlink | 0 | `file` row is the target after `resolve()` |

These are ordinary CLI edges. They do not save the isolation or identity holes.

---

## Primitive

Reality-stripped operation: `SourceFileLoader` the same path twice under unique module names, call two 0-arg callables, `deepcopy` the leftover module dict, `==` the start snapshots, print PASS/FAIL.

Nearest ordinary workflow: the specimen already ships `files/run_orders.py`, which runs both orders and prints `acc_after`. `python3 FILE` in two sequences, or two pytest nodeid lines, plus looking at `acc`, is the same observation. Observable capability lost if ordleak vanishes: the **join** (binding name + values at the start of the victim + exposing order) as one TSV. That join is real on a module-level list shared by two top-level functions. It is not a test runner, not a fixture tracer, not a permutation scanner (CANDIDATE.md removed that).

That is why this is not KILL: the *question* (which name leaked between these two tests when only order changed, and which order is enough) is a debugging object pytest will not emit. The current embodiment is a specimen-009 replay that pretends the two loads are isolated worlds and that snapshot inequality is leak provenance.

The ceiling is already written down, and it is too small for the claim:

- "only that file's module globals" + `is_binding` skips `_`, classes, functions, modules → the usual Python order-dependence sites are `leaked none`
- unique-module isolation + `==` → every instance of a FILE-defined class is a false leak
- one process → imported aliases, env, and fs smear the second order; `via` lies
- "leaked" = start snapshots differed, including `time.time_ns()` at import
- advertised `FILE::LEFT` is not a pytest nodeid
- specimen-012 is not unseen

Same-harvest sibling `leakorder` already disagrees on the object. It diffs pre/post **within** an order and prints leftover-after, not start-of-victim across orders. On specimen-009 both name `acc` and `test_a,test_b`. On a helper-module pair both go blind, for different reasons. Two groundings, two meanings of "leaked", one name in the harvest. Pick one.

---

## Mutation (what must change)

Keep the object: for a named pair, report the binding whose start value depended only on order, and the order that exposes a status (or assertion-reason) split.

Do not keep a same-process deepcopy of `vars(mod)` that only replays specimen-009.

1. **Isolate orders for real.** One subprocess per order, or an explicit reset of imported-module dicts plus env plus cwd. FILE's directory (and package parent) on `sys.path`. After that, `from helper import bucket` must show `[]` vs `['a']` into `test_b` via `test_a`, and the reverse order must PASS. If the second order still sees `n=11`, the README sentence is still a lie.
2. **Leak is a test-induced write, not import inequality.** Do not emit `leaked` for values that differ only because the file was imported twice (`time_ns`, `object()` id, uuid class identity). Compare structured values, not type-pointer `==` across loads. `S(acc=[])` vs `S(acc=[])` is not a leak. `nan` is not a leak.
3. **`via` is the writer.** If the start of `into` changed, name the callable that mutated that binding in the other order — or say `via <unknown>` / `via <prior-order>` rather than the other pair name by construction.
4. **`leaked none` is illegal next to `exposing_order` ≠ `none`.** Either snapshot `_` names, class attributes, function attributes, and mutable defaults, or print `leaked	<unseen>` (refused identity) instead of `none`. Status split with unnamed leak is the current product.
5. **Nodeids or not.** Implement `Class.method` by instantiating `Class()` and calling the method, or drop `FILE::LEFT FILE::RIGHT` from the README. Do not parse `split("::", 1)` and then `getattr` a pytest nodeid. `async def` / generators are ERROR, not PASS. Fixture parameters are ERROR with a one-line "not a pytest runner", which is already the research boundary.
6. **Catch `BaseException`.** `SystemExit` and `GeneratorExit` are test ERROR rows, not the CLI's rc and not a traceback. Bound the run. Cap `repr` length. Escape tabs/newlines in status detail. rc=1 when `exposing_order` is set or `leaked` is not `none`; rc=0 only for the clean pair.
7. **One meaning of leaked vs leftover.** Sibling `leakorder` reports within-order leftover; this CLI reports cross-order start. Keep the start-of-victim row (that is the join `run_orders.py` lacks) and do not grow a second leftover dialect under the same harvest.
8. **Dogfood that is not a copy of specimen-009.** specimen-012 is byte-identical. Next unseen must be a helper-module pair, a class-based pair, or an env/fs pair — and the tool must either name the leak or refuse with a non-`none` row.

If the mutation cannot do (1)+(2)+(4), the object is still `run_orders.py` with extra print, and a later destroyer should KILL.

---

MUTATE
