# nilkeep (reimpl)

origin.method: hdd
origin.trial: hdd-helmnull
origin.kind: clean-room
parent: candidate-nilkeep
specimens: [specimen-079]

classification: USEFUL_COMPOSITION

## Primitive

Name a user-null key dropped by empty-map default coalesce and kept by a
null chart default.

## Why this might not exist

Printing both maps still leaves “empty-map default deleted baz, null
default kept present-nil” as a hand join.

## Core operation

Compile a record to JSON chart/user values maps. Walk chart keys. A table
chart value runs two-pass coalesce tables (copy dest nils into src, then
delete dest nils). A null chart value skips that walk. Print user-nulls,
kept, dropped, and the quoted coalesced table.

## Observable delta

One query names dropped baz vs kept baz. Printing both maps does not.

## Reality mapping

Owned records: `fixtures/079-empty-map.rec` (and the same facts as JSON)
drop baz, keep foo, rc=1. `fixtures/079-null-default.rec` drops none,
keeps foo+baz, rc=0. Helm is not executed.

## Removed

Invented helm template / coalesce.go theater.

## Smallest artifact

Python 3 stdlib CLI `nilkeep` (JSON values maps + two-pass tables, not a
TSV empty-map branch).
