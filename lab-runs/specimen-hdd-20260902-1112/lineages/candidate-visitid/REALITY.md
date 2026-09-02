# Reality assessment (pre-implementation)

Copied from harvest before code. origin.trial: hdd-nixptr.

classification: USEFUL_COMPOSITION

## Core operation

Show whether a visit set used pointer identity or value identity.
Address reuse skips a distinct node.

## Nearest existing operation

Print object ids (`id(obj)` / `%p`). A set of those ids.

## Observable delta

One query names skipped-because-pointer versus distinct-value. Printing
ids still leaves that join as a hand comparison.

## Reality mapping

Owned addr/name event table. Each row is a visit attempt: lock-node name
and the address recorded in the done-set. Walk twice:

- pointer: Python `set` of addresses (`id(obj)`)
- value: Python `set` of names

Name which names pointer skipped that value would still visit. Nix is not
executed.

## Research boundary

Does not run nix. Does not allocate C++ bind temporaries. Does not invent
`--debug` address logs. The live `--live` walk is CPython objects, not
lock-graph nodes.

## Removed

Invented nix `prefetch-inputs` runs and `%p` logs.

## Smallest artifact

Python 3 stdlib CLI `visitid`.

## Why existing tools are not enough

`id(obj)` prints an integer. Two sequential prints can be equal because
the first object died. That does not name "this later name was skipped
because the done-set still held that address."
