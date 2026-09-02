# emptyunit

origin.method: hdd
origin.trial: hdd-s063
specimens: [specimen-063]

classification: USEFUL_COMPOSITION

## Primitive

Name completed-only work units that requeue into `send_runtest_some` of an
empty index list as a unit the replacement actually receives.

## Why this might not exist

The hang log shows a crashed worker being replaced. Printing the workqueue
dict still leaves “this unit is already done, so the replacement is sent
`()` and waits forever” as a hand join. First-FIFO-only misses the
`_reschedule` second assign when assigned pending ≤ 2. Dist as a key
sticker misses why loadgroup hangs and loadscope on the same tests does
not.

## Core operation

Read a worker `collection` plus a workqueue dump. Flatten `{scope:
{nodeid: bool}}` (caller keys ignored) and group by dist: loadgroup is
the full nodeid, or `@` after `]`; loadscope is `rsplit("::", 1)`.
Requeue only if `_pending_of > 0`. FIFO first unit is `first_assigned`.
If that unit’s pending ≤ 2, `_reschedule` assigns the next FIFO unit too.
`hang_risk` is any of those assigns sending `()`. Missing incomplete
nodeids are `index-error`, not hang. rc=1 on hang_risk.

## Observable delta

Same tests under loadgroup vs loadscope change hang_risk without the
caller regrouping. One query names completed-only vs first-assign send vs
the reschedule second assign vs hang_risk. `print(workqueue)` does not.

## Reality mapping

Owned dump `fixtures/063-hang.dump`: loadgroup units `test_1=True`,
`test_2=False`; first assign `send ()`; hang_risk yes; rc=1. Same dump
with `dist=loadscope` is one module unit, `send (1)`, hang_risk no.
Live-first + completed-only second: first `send (1)`, reschedule second
`send ()`; hang_risk yes; rc=1. First pending=3 then completed-only: no
second assign; hang_risk no. pytest-xdist is not executed.

## Removed

Invented pytest `--debug` traces and live xdist runs. Scope-mismatch as
the only loadscope-vs-loadgroup effect.

## Smallest artifact

Python 3 stdlib CLI `emptyunit`.
