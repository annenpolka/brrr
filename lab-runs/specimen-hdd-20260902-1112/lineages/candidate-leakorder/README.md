# leakorder

```
leakorder FILE
leakorder --order test_a,test_b --order test_b,test_a FILE
```

For named callables, report the binding whose *start* value depended only
on order, and the order that exposes a status split.

Each order runs in its own subprocess. FILE's directory is on `sys.path`.
`leaked_names` is the order-dependent start (with a writer in FILE).
`leftover=` is leftover-after within that order, not the leak column.
`sufficient_exposing_order` is a unique fail-vs-pass split, not the first
non-PASS. A split with no snapshotted binding is `leaked_names unknown`,
never `none`.

Snapshots FILE globals (including `_` names), class attributes
(`Class.attr`), function attributes, mutable defaults, closure cells, and
sibling imported modules. `async def` / generators are ERROR. `Class.method`
is `Class()` then the method.

Exit 1 when a leak is named or a split is unnamed. Exit 0 only for a clean
pair. Exit 2 on missing file / usage.

Default orders are discovered `test_*` names and the reverse — not a
hardcoded `test_a,test_b` pair.
