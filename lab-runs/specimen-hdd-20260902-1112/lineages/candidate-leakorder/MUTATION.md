# MUTATION — leakorder class-attribute isolation

Ordinary mutation of `candidate-leakorder` after DESTROYER / bakeoff
KEEP + MUTATE isolation: class-attribute leaks are named, not `leaked=none`.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-order
  mutation: ordinary class-attribute isolation
  parent: candidate-leakorder
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/leakorder-leakorder
branch: specimen-hdd/leakorder-leakorder
parent_commit: 7ea58e89a04597e8198bc55cd46d5cd24731db68
commit: fbb697b4e22601694e077bec6f6792a8482cd57f
cli_sha256: 0f70b0735fbf2d2a9ce909f1246f74d6ae9267e9651256c57db1b64dd674bca7
```

Not merged to `main`. Not installed on PATH.

## What was kept

The object: for named callables, report leftover names whose value
changed within an order, and the first order that is not all-PASS.
Specimen-009 module-global `acc` is unchanged: `leaked=acc`,
`leftover={'acc': ['a']}`, `sufficient_exposing_order test_a,test_b`.
`leaked` is still leftover-after (pre/post of each callable), not
ordleak's start-of-victim row.

## What changed

**Class attributes are snapshotted as `Class.attr`.** The parent walked
`vars(mod)` and skipped callables. Classes are callable. `Box` was
dropped, so specimen-060 (`class Box: bucket = []`) printed
`leaked=none` / `leftover={}` next to a real PASS/FAIL split.
The mutation copies non-callable, non-`_` class attributes before
skipping the class itself.

## Before (parent, DESTROYER / bakeoff)

```
python3 leakorder specimen-009/files/test_order.py
order test_a,test_b  test_a=PASS test_b=FAIL  leaked=acc  leftover={'acc': ['a']}
leaked_names  acc
sufficient_exposing_order  test_a,test_b

python3 leakorder specimen-060/files/test_class_leak.py
order test_a,test_b  test_a=PASS test_b=FAIL  leaked=none  leftover={}
leaked_names  none
sufficient_exposing_order  test_a,test_b
```

ordleak on the same 060 file already named `Box.bucket`.

## After (this mutation, archive `./demo.sh` ×2 identical)

`python3 tests/test_leakorder.py -v` — 5 OK.

`./demo.sh` exit 0. CLI rows:

```
== leakorder specimen-009 (module global acc) ==
file  .../specimen-009/files/test_order.py
order test_a,test_b  test_a=PASS test_b=FAIL  leaked=acc  leftover={'acc': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leaked=acc  leftover={'acc': ['a']}
leaked_names  acc
sufficient_exposing_order  test_a,test_b
order_axis  fail=['test_a,test_b'] pass=['test_b,test_a']

== leakorder class-attribute Box.bucket ==
file  .../specimen-060/files/test_class_leak.py
order test_a,test_b  test_a=PASS test_b=FAIL  leaked=Box.bucket  leftover={'Box.bucket': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leaked=Box.bucket  leftover={'Box.bucket': ['a']}
leaked_names  Box.bucket
sufficient_exposing_order  test_a,test_b
order_axis  fail=['test_a,test_b'] pass=['test_b,test_a']
```

Transcripts: `demo-1.log`, `demo-2.log` (byte-identical).

## Remaining holes (not this cut)

- Function attributes, mutable defaults, closure cells, and `_`-prefixed
  globals are still invisible. A status split on those still prints
  `leaked_names none`.
- Orders still share this process: imported helpers, `os.environ`, and
  filesystem writes can poison order 2.
- FILE's directory is still not on `sys.path`.
- `leaked` is still leftover-after, including on an all-PASS order.
- `sufficient_exposing_order` is still first non-PASS, not a unique
  status split.
- Exit remains 0 when a leak is named.

Unix / DESTROYER also asked for a fresh process per order and for
`leaked unknown` instead of `none` on unseen bindings. Later cuts.
This cut only stops class-attribute leaks from being silent-wrong.
