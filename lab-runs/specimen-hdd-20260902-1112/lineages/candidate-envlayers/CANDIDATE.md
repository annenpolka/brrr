# envlayers

origin.method: specimen-hdd
origin.trial: hdd-env-empty
specimens: [specimen-010]

classification: USEFUL_COMPOSITION

## Core operation

For one environment key, show inherited value, file assignment (including
empty), skip-empty loader result, assign-all loader result, and process env,
labeled by layer.

## Observable delta

One query distinguishes empty assignment from unset and names the value at
each layer. Ordinary `printenv` cannot see a file's `KEY=` once a skip-empty
loader left inherited `/x` in place.

## Reality mapping

Read a declared dotenv subset (export, quotes, comments, strip, BOM) and
apply two explicit loader policies from the specimen (`if v:` vs always
assign) to parsed events. Print a table with presence and source.
Inherited is caller-supplied (not a copy of process env). Process env is
this process unless `--process` injects a snapshot.

## Research boundary

Does not infer which policy a third-party tool used unless that tool is the
fixture. Does not attach to another process.

## Removed

process attach, envprobe, POSIX-empty-means-unset oracle.

## Smallest artifact

Python 3 stdlib CLI `envlayers`.
