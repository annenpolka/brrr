# extraedge

origin.method: hdd
origin.trial: hdd-gitextra
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

## Reality mapping

Owned records: extras table `postgresql → psycopg2`. Edit-lock
resolved empty; add-lock same package version, resolved psycopg2.
Poetry is not executed. The map is a record field, not a solver.

## Removed

poetry lock, Provider.complete_package, invented PR patches,
declared-vs-resolved set-difference, empty-resolved ⇒ dump declared.

## Smallest artifact

Python 3 stdlib CLI `extraedge`.
