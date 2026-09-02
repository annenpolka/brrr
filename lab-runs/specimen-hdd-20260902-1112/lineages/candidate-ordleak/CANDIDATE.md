# ordleak

origin.method: specimen-hdd
origin.trial: hdd-order
origin.mutation: DESTROYER_ordleak_2 copy-import-tree / dual-fail-unseen / slots / report-fd
origin.parent: candidate-ordleak
specimens: [specimen-009]
unseen: helper-module pair, class-method pair, env/fs refuse

classification: USEFUL_COMPOSITION

## Core operation

Run a pair of tests in two orders and report what leaked when only order
changed. One query names the leaked binding (start-of-victim) and the
sufficient exposing order.

## Observable delta

`test_a` then `test_b` fails; `test_b` then `test_a` passes. The report names
`acc` as `[]` when `test_b` runs first and `['a']` when it runs after `test_a`,
and names `test_a test_b` as the exposing order. A helper-module pair
(`from helper import bucket`) names `bucket` the same way. Two pytest nodeid
orders still leave that join as a hand comparison of traces.

## Reality mapping

One subprocess per order. FILE's directory and package parent are on
`sys.path`. The importable tree is copied so package helpers / relative
imports / parent helpers load from the copy. Snapshot FILE globals, class
attributes, instance slots, function-local state, and copied-tree helper
data before each test. Diff start-of-victim across orders only when a test
wrote the binding. `via` is that writer. A status split with no snapshotted
binding is `leaked <unseen>`, not `leaked none`. Dual-FAIL smear (including
hardcoded `/tmp`) is `<unseen>` rc=1, never a green pair. Exit 1 when a leak
is named, a status split exists, or any status is FAIL/ERROR without a named
write.

## Research boundary

Only the named pair. No whole-suite permutation, no pytest plugin inference.
Env and filesystem are isolated (process / copy) but not traced: splits
there are `<unseen>`. Import-time inequality is not a leak. Worker JSON is
not test stdout. This is start-of-victim, not leftover-after.

## Removed

automatic whole-suite mutable-state scanner.

## Smallest artifact

Python 3 stdlib CLI `ordleak`.
