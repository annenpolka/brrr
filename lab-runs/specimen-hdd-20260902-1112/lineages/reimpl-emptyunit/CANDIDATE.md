# emptyunit (reimpl)

origin.method: hdd
origin.trial: hdd-s063
origin.kind: clean-room
parent: candidate-emptyunit
specimens: [specimen-063]

classification: USEFUL_COMPOSITION

## Primitive

Name completed-only work units that requeue into `send_runtest_some` of an
empty index list.

## Why this might not exist

Printing the crashed node's workqueue dict still leaves “this scope is
already done, so the replacement is sent `()` and waits forever” as a hand
join.

## Core operation

Drive a two-pass loadscope queue from TSV rows or JSON events. Pass 1 is
`workqueue.update(workload)` after crash. Pass 2 pops each unit and builds
`[collection.index(n) for n, done in unit.items() if not done]`. Print
completed_only, send indexes, empty_send, hang_risk.

## Observable delta

One query names completed-only vs send `()` vs hang_risk. Printing the dict
does not.

## Reality mapping

Owned events `fixtures/063-hang.rec` (and the same facts as JSONL): both
tests in `testing/test_timeout.py` already done; send `()`; hang_risk yes.
pytest-xdist is not executed.

## Removed

Invented pytest `--debug` traces and live xdist runs.

## Smallest artifact

Python 3 stdlib CLI `emptyunit` (queue object + JSON events, not an
OrderedDict TSV fold).
