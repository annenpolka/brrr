# pathnode

origin.method: hdd
origin.trial: hdd-pytest003
specimens: [specimen-003]

classification: USEFUL_COMPOSITION

## Primitive

Given collection events, name whether the same path is still the same
collection object, and which fixture definition is bound to which node.

## Why this might not exist

`pytest dir1 dir2 dir1 --collect-only` can print `dir1` twice. Fixtures
registered on the first directory node miss on the second. Printing CLI
args plus collect output still leaves the join — same path, two node ids,
fixture bound to the first — as a hand comparison.

## Core operation

Read `collect path node`, `register fixture node`, `lookup fixture node found|missing`.
Print duplicate paths with their node ids (`same_node yes/no`) and fixture
lookups that missed, with the nodes that registered that fixture.

## Observable delta

One query names path-vs-node identity and the fixture miss. Path equality
is the wrong object.

## Reality mapping

Owned events `fixtures/003-collect.rec`: dir1 collected as n1 then n3 after
dir2; `shared_fixture` registered on n1; lookup on n3 missing. pytest is
not executed.

## Research boundary

Does not run pytest. Does not invent node ids. `--keep-duplicates` file
collection twice is a different object.

## Removed

`pytest --trace-config`, invented numeric node IDs from the dream.

## Smallest artifact

Python 3 stdlib CLI `pathnode`.

## How to run

```
python3 tests/test_pathnode.py
./demo.sh
```
