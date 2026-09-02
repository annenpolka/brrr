# MUTATE ordleak (2) (applied 2026-09-02)

From `destroyers/DESTROYER_ordleak.md` after First Selection KEEP.
Required cut: (1) isolate subprocess, (2) leak is a test-induced write not
import inequality, (4) `leaked none` illegal next to `exposing_order`.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-order
  mutation: isolate-orders / test-induced-write / leaked-none-illegal
  parent: candidate-ordleak
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-ordleak-ordleak
branch: specimen-hdd/candidate-ordleak-ordleak
parent_commit: 995c670b8da33cbed4dd094d714deede62bebb35
parent_cli_sha256: 439765165f037112179690356642a69a0ec9857b4f188da14a1b1f4192771de5
first_mutate_commit: 885095826c38e95d6db9d0b9868e51dbb32b8fef
first_mutate_cli_sha256: d3cec45bc522aa61de3342b69aae50bc64b4fddf840225cdd1914a01a24fa4f8
commit: deb64d00e7d5e514710fde095cc73d750de914a9
cli_sha256: ad60324a37b1063287b018563d019bba19eb4a3bb4a663326962551d6200887a
```

Not merged to `main`. Not installed on PATH. Not merged with `leakorder`.

`python3 tests/test_ordleak.py -v` — 26 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

The object: for a named pair, report the binding whose **start-of-victim**
value depended only on order, and the order that exposes a status split.
Hidden PASS leaks still name the binding. Independent pairs still print
`leaked none`. This is not leftover-after (that is leakorder).

## What changed (DESTROYER_ordleak §1, §2, §4)

1. **One subprocess per order.** Parent spawn-pickle (`995c670`) died as
   `Can't pickle … No module named 'ordleak_cli'` when `contrast()` was
   imported under a loader name, and still shared the host filesystem.
   Each order is now `python3 ordleak --exec-order` with FILE's directory
   (and package parent) on `sys.path`, a temp copy of sibling `.py` files,
   and that copy as cwd. `from helper import bucket` names `bucket`
   `[]` vs `['a']` into `test_b` via `test_a`; reverse order PASSes.
   `import helper` names `helper.bucket` the same way.
2. **Leak is a test-induced write, not import inequality.** Start snapshots
   are structured encodings (not type-pointer `==` across uuid loads).
   A start split is reported only when a callable in the other order
   actually mutated that binding (`via` is that writer). `time.time_ns()`,
   `object()` ids, dataclass type identity (`S(acc=[])` vs `S(acc=[])`),
   and `nan` are not leaks. A real `state.acc.append` still names `state`.
3. **`leaked none` is illegal next to `exposing_order` ≠ `none`.** Status
   split with no snapshotted write is `leaked <unseen>` (refused identity),
   never `none`. `_acc`, class attributes, function attributes, mutable
   defaults, and closure cells are snapshotted so the usual in-FILE sites
   are named rather than unseen.

Also landed because isolation made them cheap: `Class.method` /
`FILE::Class::method` instantiates and calls; `async def` / generators /
fixture parameters are ERROR not PASS; `SystemExit` / `GeneratorExit` are
ERROR rows; tabs/newlines in detail are escaped; order timeout 30s;
repr cap 500.

## Before (DESTROYER_ordleak / parent spawn)

Same-process (and the broken spawn that still imported helpers into one
world when pickle worked as `__main__`):

```
# helper.py bucket=[]; from helper import bucket
order test_a test_b  test_b FAIL ['a']
order test_b test_a  test_b FAIL ['a']   # order 1's append still in helper
exposing_order	none
leaked	none                            # or a lying via
rc=0
```

```
stamp = time.time_ns()
exposing_order	none
leaked	stamp	into	test_a	<t1>	<t2>	via	test_b
```

```
class Box: items = []     # first mutate named this
_acc = []                 # first mutate: leaked unknown
os.environ write          # statuses agree FAIL; leaked none
```

## After (this mutation)

```
== ordleak test_a test_b (both orders) ==
exposing_order	test_a test_b
leaked	acc	into	test_b	[]	['a']	via	test_a
exit: 1

== helper-module from helper import bucket ==
exposing_order	test_a test_b
leaked	bucket	into	test_b	[]	['a']	via	test_a
exit: 1

== class-method TestOrder.test_a ==
exposing_order	TestOrder.test_a TestOrder.test_b
leaked	TestOrder.acc	into	TestOrder.test_b	[]	['a']	via	TestOrder.test_a
exit: 1

== import-time time_ns is not a leak ==
exposing_order	none
leaked	none
exit: 0

== env split is unseen, not none ==
exposing_order	test_a test_b
leaked	<unseen>
exit: 1

== private _acc is named ==
exposing_order	test_a test_b
leaked	_acc	into	test_b	[]	['a']	via	test_a
exit: 1
```

## Remaining holes (not this cut)

- **Filesystem outside the sibling copy still smears.** Isolation copies
  FILE plus same-dir `.py` into a temp tree. A marker next to `__file__`
  is isolated (fresh copy). A hardcoded path (`/tmp/ordleak.marker`) is
  still one disk. That split is `<unseen>`, not a tracer.
- **Packages / nested helpers are not copied.** Only sibling `*.py`.
- **Custom `__eq__` that always returns true** can hide a real mutation;
  then `exposing_order` plus `leaked <unseen>`. Not faked.
- **`lru_cache` wrappers are skipped** (identity noise). `currsize` is
  not named.
- **Not a pytest runner.** Fixture-parameterized tests are ERROR.
  `Class.method` is instantiate-and-call, not collection.
- **Not leftover-after.** Do not grow leakorder's within-order leftover
  dialect under this harvest. Stop.
- **Env/fs are not named bindings.** Process/copy isolation makes the
  order axis real; the join still refuses those identities as `<unseen>`.

If a later destroyer still finds same-process helper smear, or `leaked none`
next to a status split, or `time_ns` as a leak, KILL.

Do not merge onto main. Do not become leakorder.

---

# MUTATE ordleak (3) (applied 2026-09-02)

From `destroyers/DESTROYER_ordleak_2.md` after First Selection KEEP.
Required cut: (1) copy the importable tree, (2) dual-FAIL smear is not a
clean pair, (3) FILE-level slots named or honestly unseen, (4) worker
stdio is not test stdio. Keep start-of-victim + one subprocess per order.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-order
  mutation: copy-import-tree / dual-fail-unseen / slots / report-fd
  parent: candidate-ordleak
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-ordleak-ordleak
branch: specimen-hdd/candidate-ordleak-ordleak
parent_commit: 1f368b74262b67840a2e8ad1758d029f47822439
parent_cli_sha256: ad60324a37b1063287b018563d019bba19eb4a3bb4a663326962551d6200887a
commit: e01b5013e600bc1f16a5a1d763f87ab13a30ea85
cli_sha256: 4a4bc7d73f16688ad0330302bc4c0f0f3fcdbdbf8888ae75117ad5111faa3306
cli_bytes: 28423
```

Not merged to `main`. Not installed on PATH. Not merged with `leakorder`
(`cmp` rc=1).

`python3 tests/test_ordleak.py -v` — 35 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

The object: for a named pair, one isolated order per subprocess, report
the binding whose **start-of-victim** value depended only on order, and
the order that exposes a split. Hidden PASS leaks still name the binding.
Import-time `time_ns` / `object()` / `nan` / dataclass type identity are
not leaks. This is not leftover-after (that is leakorder).

## What changed (DESTROYER_ordleak_2 §1–§4)

1. **Copy the importable tree, not only sibling `*.py`.** FILE's directory
   and package parent are on `sys.path`. Package dirs, sibling `.py`, and
   parent-level helpers are copied. FILE is loaded as a package member so
   `from pkg.helper import bucket` and `from .helper import bucket` load
   from the copy (no caller `PYTHONPATH`) and name `bucket` `[]` vs
   `['a']` into `test_b` via `test_a`; reverse PASSes. A helper in FILE's
   parent is copied when that parent is a bounded tree. A helper outside
   the copy is `ordleak: imported module 'helper' is outside the copied
   tree (FILE directory / package parent)`, not a bare `No module named`.
2. **Dual-FAIL smear is not a clean pair.** `leaked none` + rc=0 is legal
   only when every status is PASS. Any FAIL/ERROR with no snapshotted
   write is `leaked <unseen>` rc=1 — including a hardcoded `/tmp` leftover
   that makes both orders FAIL (`exposing_order none` may stay). Always-fail
   independent of order is the same: not a green pair.
3. **FILE-level `__slots__` are named.** `box.n` is `0` vs `1` via
   `test_a`, same as `__dict__` / dataclass. `lru_cache` wrappers stay
   skipped; a `currsize` split is `<unseen>`, not `none`.
4. **Worker JSON is a `--report` file, not test stdout.** A test that
   writes `\xff\xfe` to stdout is ignored bytes and still yields a report,
   not `utf-8 codec can't decode` with empty stdout.

## Before (DESTROYER_ordleak_2 leftovers)

```
# pkg/helper.py bucket=[]; from pkg.helper import bucket
ordleak: No module named 'pkg'    rc=1

# pkg/test_mod.py: from .helper import bucket
ordleak: attempted relative import with no known parent package    rc=1

# MARKER = Path("/tmp/ordleak2-hard.marker")  both orders FAIL
exposing_order	none
leaked	none
rc=0

# class Box: __slots__ = ("n",); box.n += 1
leaked	<unseen>

# sys.stdout.buffer.write(b"\xff\xfe")
ordleak: 'utf-8' codec can't decode byte 0xff
stdout empty
```

## After (this mutation)

```
== package from pkg.helper import bucket ==
exposing_order	test_a test_b
leaked	bucket	into	test_b	[]	['a']	via	test_a
exit: 1

== relative from .helper import bucket ==
exposing_order	test_a test_b
leaked	bucket	into	test_b	[]	['a']	via	test_a
exit: 1

== dual-FAIL /tmp smear is unseen not none ==
exposing_order	none
leaked	<unseen>
exit: 1

== slots box.n ==
leaked	box.n	into	test_b	0	1	via	test_a
exit: 1

== binary stdout is not a utf-8 crash ==
exposing_order	none
leaked	none
exit: 0
```

## Remaining holes (not this cut)

- **Hardcoded `/tmp` (and other shared disks) still smear.** Isolation
  copies the importable tree. The leftover is now `<unseen>` rc=1, not a
  tracer and not a green pair.
- **`lru_cache` `currsize` is refused** (wrapper skipped). Status split
  stays `<unseen>`.
- **Custom `__eq__` that always returns true** can hide a real mutation;
  then `exposing_order` plus `leaked <unseen>`. Not faked.
- **`exposing_order` is still a status split, not an assertion-reason
  split.** Always-fail `test_b` may keep `exposing_order none` while a
  leaked row names the write.
- **Not a pytest runner.** Fixture-parameterized tests are ERROR.
- **Not leftover-after.** Do not grow leakorder's within-order leftover
  dialect under this harvest. Stop.
- **Copy is bounded** (py tree, depth/file caps). A helper two directories
  above FILE is outside the copy and says so.

If a later destroyer still finds nested helpers that do not load, or
unsandboxed smear that prints `leaked none` rc=0, KILL.

Do not merge onto main. Do not become leakorder.
