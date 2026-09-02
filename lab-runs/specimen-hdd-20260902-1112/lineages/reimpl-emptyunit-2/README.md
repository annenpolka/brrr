# emptyunit (clean-room reimpl-2)

Name a completed-only work unit a replacement would be sent as
`send_runtest_some([])`, including the `_reschedule` second assign when the
first partition’s pending is 1 or 2.

Style: flatten inner nodeids, partition by dist, report collection-index
sends of the replacement burst. Not a first-dict empty-list check. Not a
copy of the archive CLI.

```
emptyunit DUMP
emptyunit < DUMP
```

DUMP is `print(workqueue)` / `OrderedDict` / a nested dict, or a JSON /
Python envelope with `collection` and `workqueue` / `assigned`. TSV
`collection` + `unit` rows are accepted. Caller scope keys are ignored.
Hang logs are refused.

`hang_risk yes` exits 1. `hang_risk no` with no index-error exits 0.
Empty lists print `-`, not `none`. Nodeid `-` is refused (sentinel).
`none` is an identity. `dist none` is an error.
