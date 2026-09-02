# emptyunit (clean-room reimpl)

Name a completed work unit that was requeued to a replacement worker as an
empty `send_runtest_some`.

This copy drives a two-pass FIFO: crash `update`s the assigned workload,
then each popped unit sends collection indexes of incomplete nodeids.

```
emptyunit RECORD
emptyunit < RECORD
```

RECORD is a TSV table (`collection` / `unit` rows) or JSON events
(`collect`, `mark`, `crash`).
