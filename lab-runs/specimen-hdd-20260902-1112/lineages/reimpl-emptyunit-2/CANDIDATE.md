# emptyunit (reimpl-2, index partitions)

origin.method: hdd
origin.trial: hdd-s063
origin.kind: clean-room
parent: candidate-emptyunit
style: idxpart
specimens: [specimen-063]

classification: USEFUL_COMPOSITION

## Primitive

Name leftover empty-unit identity as the collection-index list a replacement
would be sent. Hang is any burst partition whose index list is `()`.

## Why this might not exist

Printing the crashed node's workqueue dict still leaves “this unit is already
done, so the replacement is sent `()` and waits forever” as a hand join.
First-FIFO-only misses the `_reschedule` second assign when the first
partition has 1–2 incompletes. Dist as a key sticker misses why loadgroup
hangs and loadscope on the same tests does not.

## Core operation

Flatten inner `{nodeid: completed}` pairs (caller keys ignored). Partition by
dist: loadgroup is the full nodeid, or `@` after `]`; loadscope is
`rsplit("::", 1)`. Each partition's send is
`[collection.index(n) for n, done in partition if not done]`. Requeue only if
any incomplete remains. Burst is the first partition, plus the next when that
first partition's incomplete count is 1 or 2. `hang_risk` is any of those
sends being `()`. Missing incomplete nodeids are `index-error`, not hang.

## Observable delta

Same tests under loadgroup vs loadscope change hang_risk without the caller
regrouping. Live-first + completed-only second is hang even though the first
caller dict is not all-True. `print(workqueue)` does not name the send
indexes.

## Reality mapping

Owned dump `fixtures/063-hang.dump`: loadgroup partitions `test_1=True`,
`test_2=False`; first send `()`; hang_risk yes; rc=1. Same dump with
`dist=loadscope` is one module partition, send `(1)`, hang_risk no.
Live-first + completed-only second: first send `(1)`, reschedule second
`()`; hang_risk yes. First pending=3 then completed-only: no second assign;
hang_risk no. pytest-xdist is not executed.

## Removed

Invented pytest `--debug` traces and live xdist runs. Queue-object drain
without dist regroup (reimpl-emptyunit). First-dict empty-list / dist sticker.

## Smallest artifact

Python 3 stdlib CLI `emptyunit` (collection-index partitions, not a named-dict
walk of caller keys).
