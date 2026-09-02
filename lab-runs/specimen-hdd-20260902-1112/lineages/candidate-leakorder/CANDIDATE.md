# leakorder

origin:
  method: specimen-hdd
  trial: hdd-order
  kind: competing-reimplementation
  mutation: isolate orders, class attrs, sufficient split
  parent: candidate-leakorder
  specimens: [specimen-009, specimen-012, specimen-060]

CLI over a Python file of test_* callables. Reports the binding whose
start depended only on order, leftover-after labeled leftover, and the
order sufficient to expose a status split.

Module-level lists (specimen-009 `acc`) stay named. Class attributes
(specimen-060 `Box.bucket`) are named as `Class.attr`. Helper-module
`from helper import bucket` is isolated per order. `_acc` is named, not
`none`. A status split with no snapshotted binding is `unknown`.
