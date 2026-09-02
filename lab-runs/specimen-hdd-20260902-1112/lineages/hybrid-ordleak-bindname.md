# Hybrid: ordleak × bindname

Date: 2026-09-02
Job: job-0342 (`hybrid-ord-bind`)
RUN_ID: specimen-hdd-20260902-1112

Verdict: **NON-JOIN / thin concat**. No binary.

Proposed join: name whether leftover-bind is (a) a leftover start-of-victim
binding after only order changed, or (b) a leftover same-name helper vs a
moved body. One query, two leftover reports.

That is two parent reports glued under the English word "leftover". It is
not a relation unavailable from concatenating parent outputs
(Constitution 13.5). Kill condition on the job was "thin concat".

"Leftover bind" does not even mean the same object in both parents.
ordleak's `leaked acc` is after **order**: `test_b` starts as `[]` when it
runs first and as `['a']` when it runs after `test_a`. The CLI has no
import-path field; rc=1 when a leak is named. bindname's leftover helper
is after a **move**: `from pkg_util import parse` still binds
`return ('legacy', x)` while `pkg_parse.parse` is the moved
`return ('moved', x.strip())`, `same_function False`. rc=0 on that query.
Opposite axes, opposite leftover objects.

## Parents (host-executed)

`ordleak` on specimen-009 owned pair (`files/test_order.py` `test_a`
`test_b`). CLI tests OK. `./demo.sh` twice, logs identical to each other
and to archived `demo-1.log`.

```
file	…/specimens/specimen-009/files/test_order.py
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

`test_a` appends `"a"` onto module-level `acc`. `test_b` asserts
`acc == []`. Default order fails; reverse passes. That is reason (a).
Class-attribute `Box.items` and function-local `holder.acc` are the same
shape. Unseen `_acc` is `leaked unknown`, not `none`. Independent pairs
are `leaked none`. rc=1 on a named or unknown leak.

`bindname` on specimen-013 leftover-vs-moved (`files/pkg_util.py` /
`pkg_parse.py`, `--from pkg_util parse`). Tests 13/13 OK. `./demo.sh`
twice, logs identical to each other and to archived `demo-1.log`.

```
query	from pkg_util import parse
import	from pkg_util import parse
bind	pkg_util.parse
runs	pkg_util.parse
kind	def
file	pkg_util.py
line	1
source	"def parse(x):\n    return ('legacy', x)\n"
also	pkg_parse.parse
same_function	False
```

`grep def parse` hits both files. `from pkg_util import parse` still
runs the leftover helper. `from pkg_parse import parse` runs the moved
body. That is reason (b). A true reexport is `kind=reexport`,
`same_function True`. Leftover `ast.py` is that helper, not stdlib
`ast.parse`.

## Concat already names both reasons

```
python3 ordleak files/test_order.py test_a test_b
# exposing_order test_a test_b / leaked acc into test_b [] ['a'] via test_a

python3 bindname -C files --from pkg_util parse
# kind def / runs pkg_util.parse / also pkg_parse.parse / same_function False
```

A wrapper that prints `why leftover-after-order` vs
`why leftover-same-name-helper` is `uniq(parent claims)`. The exclusive
class reconstructs from those two stdout blocks. Pairing a two-order
test pair with a two-module import bind is caller-invented: no owned
event is both.

## No shared object

| | ordleak | bindname |
| --- | --- | --- |
| domain | order-dependent test pair | leftover same-name helper vs moved body |
| input | FILE LEFT RIGHT (importable callables) | `-C DIR` NAME / `--from` / `--import` / `--file` |
| leftover | start-of-victim binding that differed when only order changed | independent `def` still bound by the stale import |
| time axis | two orders of one pair | after a move; no run-order |
| identity | module global / class attr / fn attr / default / cell | import path vs defining `runs` |
| success model | rc=1 when leak named or unknown | rc=0 on a leftover helper |
| nearest miss | two pytest nodeid orders plus staring at `acc` | `grep def parse` plus `inspect.getsource` |

The analogical map (leftover value after order ≈ leftover helper after
move) fails on the owned rows. ordleak does not consult import path or
function identity. bindname does not run two orders or snapshot start
state. There is no test-pair-plus-import-bind fixture.

Host-executed cross-apply:

- bindname `-C specimen-009/files acc` → `kind=reexport`,
  `runs=list.acc`, `same_function True`, empty `source`. `acc` is a list
  assignment, not a leftover helper. The leaked `[]` vs `['a']` is
  invisible. `--file test_order.py acc` is `no uses of acc` (no import
  of that name). `--from test_class_attr items` is `has no name items`
  (class attribute is not an import bind). `--from test_fnattr holder`
  names the empty `def holder`, not `holder.acc`.
- ordleak on `test_parse_identity.py test_a test_b` →
  `LookupError: no test callable 'test_a'` (the file prints identity; it
  is not a pair). `pkg_util.py::parse` vs `pkg_parse.py::parse` is
  `nodeids must refer to the same file`. Same-name `parse parse` is
  `left and right tests must be different`.
- Caller-invented wrap of leftover/moved as `test_a`/`test_b` that only
  call each `parse` → `exposing_order none` / `leaked none` / rc=0. The
  leftover helper is not an order-axis leak.
- Recoding specimen-013 as specimen-009 (`seen.append(leftover(…))` plus
  `assert seen == []`) does yield `leaked seen`. That is a caller-invented
  shared list, not the owned leftover-vs-moved bind. bindname on that
  wrapdir still reports `parse` `count 2` `same_function False`
  independently of `seen`.

This is the same mashup shape as `hybrid-zerowhy` (XOR of independent
parent claims), `hybrid-emptyunit-waitoneshot`,
`hybrid-unusedfp-lockident`, and `hybrid-peerleft-silentadd`
("one query, two leftover reports"). zerowhy was already attacked this
run as a calculator over concatenated stdout. Do not mint another one.

Host capture: `lineages/_hybrid-ordleak-bindname-scratch/`.

## What was not done

Did not run `scripts/make_worktree.sh hybrid-ordbind ordbind`.
Did not invent pytest or an import tracer. Did not merge onto main.

Keep the parents. Archive this note only.
