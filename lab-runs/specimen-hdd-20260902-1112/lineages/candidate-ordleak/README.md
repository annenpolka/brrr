# ordleak

Run two tests in both orders. Report which binding differed when only
order changed, and which order is enough to expose it.

Not a whole-suite scanner. The pair is explicit.

## Usage

```
ordleak FILE LEFT RIGHT
ordleak FILE::LEFT FILE::RIGHT
```

| argument | meaning |
| --- | --- |
| `FILE` | Python file with test callables |
| `LEFT`, `RIGHT` | function names, or `Class.method` |

`FILE::TestOrder::test_a` is `TestOrder.test_a`: instantiate `TestOrder` and
call the method. Each order is a **subprocess** with FILE's directory and
package parent on `sys.path` and a fresh copy of the importable tree (package
dirs, sibling `.py`, parent-level helpers). `from pkg.helper import bucket`
and `from .helper import bucket` load from that copy. A helper outside the
copy is `ordleak: … outside the copied tree`, not a bare `No module named`.
Worker JSON is a side-channel file, not test stdout.

Exit 1 when a leak is named, when `exposing_order` is set, when a status
split has no snapshotted binding (`leaked <unseen>`), or when any status is
FAIL/ERROR with no named write (dual-FAIL smear is not a clean pair). Exit 0
only when every status is PASS and no test-induced binding differed. Exit 2
on usage.

`async def` and generator tests are ERROR, not PASS. Fixture parameters are
ERROR (`not a pytest runner`). `SystemExit` / `GeneratorExit` are ERROR rows.

## Output

Tab-separated rows. Binding values are structured `repr` so `[]` and `['a']`
stay distinct. A name missing from one start snapshot is `<absent>`.

```
file	/path/test_order.py
pair	test_a	test_b
order	test_a test_b
status	test_a	PASS
status	test_b	FAIL	['a']
order	test_b test_a
status	test_b	PASS
status	test_a	PASS
exposing_order	test_a test_b
leaked	acc	into	test_b	[]	['a']	via	test_a
```

| row | meaning |
| --- | --- |
| `order` / `status` | one isolated subprocess of that sequence |
| `exposing_order` | sequence where a test fails that passed in the other order; `none` if statuses agree |
| `leaked` | binding whose **start-of-victim** value differed because a test wrote it: first column is the value when that test ran first, second is the value when it ran after `via` (the writer). `none` only if every status is PASS and no test-induced start split. `<unseen>` if statuses disagree or any FAIL/ERROR happened but no snapshotted binding differed |

Import-time noise (`time.time_ns()`, `object()` ids, class identity across
loads, `nan`) is not a leak. `via` is the callable that mutated the binding
in the other order, not "the other pair name" by construction.

## Example (specimen-009)

```
ordleak files/test_order.py test_a test_b
```

`test_a` appends `"a"` onto module-level `acc`. `test_b` asserts `acc == []`.
Default order fails; reverse order passes. The leak row names `acc`.

## Boundary

Only the two named tests. Snapshots that file's module globals (including
`_`-prefixed data), class attributes, instance `__dict__` / `__slots__`
fields, function attributes, mutable defaults, closure cells, and helper
data imported from the copied tree. `lru_cache` wrappers are skipped
(`currsize` stays `<unseen>` on a split). Does not permute a suite, attach
to pytest, or guess fixtures. Does not trace `os.environ` or the filesystem:
a status split there is `leaked <unseen>`, not `leaked none`. Does not
report leftover-after (that is a different tool); this CLI reports
start-of-victim across orders.
