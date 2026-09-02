# extraedge (reimpl)

origin.method: hdd
origin.trial: hdd-gitextra
origin.kind: clean-room
parent: candidate-extraedge
specimens: [specimen-021]

classification: USEFUL_COMPOSITION

## Primitive

Given two records of one package version and an extras table
(extra → extra-edge), name declared extras whose mapped targets did
not attach, and extra-edges that attached only on the second record.

## Why this might not exist

`poetry lock` after editing a git extra still succeeds. `poetry show`
lacks `psycopg2`. Reading pyproject plus both locks still leaves
“declared postgresql, extra-edge psycopg2 absent vs later present,
same version node” as a hand join.

## Core operation

Compile each record to JSON, ingest extras-table edges, attach resolved
extra-edge nodes, then walk declared extras. A miss is an extra whose
mapped neighbors are all unattached.

## Observable delta

One query names `missed_a postgresql` vs later `attached_b psycopg2` on
the same package version. Set-difference of extra names against resolved
package names is not the operation.

## Reality mapping

Owned records: extras table `postgresql → psycopg2`. Edit-lock
resolved empty; add-lock same package version, resolved psycopg2.
Poetry is not executed. The map is a record field, not a solver.

## Removed

poetry lock, Provider.complete_package, invented PR patches,
declared-vs-resolved set-difference, empty-resolved ⇒ dump declared.

## Smallest artifact

Python 3 stdlib CLI `extraedge` (JSON documents + attach graph, not a
TSV Record fold).
