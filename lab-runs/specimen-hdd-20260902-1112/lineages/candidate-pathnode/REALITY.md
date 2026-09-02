# Reality assessment (pre-implementation)

classification: USEFUL_COMPOSITION

## Core operation

Name path-vs-node identity and which fixture definition is bound to which node.

## Nearest existing operation

Print CLI args plus `--collect-only` output.

## Observable delta

One query names two node ids for one path and a fixture miss on the later
node. Seeing `dir1` twice still leaves that join as a hand comparison.

## Reality mapping

Owned collection events: path, node id, fixture register, fixture lookup.
pytest is not executed.

## Research boundary

Does not import pytest. Does not claim a Directory node implementation.
`--keep-duplicates` on files is a different object.

## Removed

Invented `pytest --trace-config`.

## Smallest artifact

Python 3 stdlib CLI `pathnode`.
