# bindpath

origin.method: specimen-hdd
origin.trial: hdd-identity
origin.kind: clean-room
specimens: [specimen-013]

classification: USEFUL_COMPOSITION

## Core operation

For a name, show the import path and the body that would run. Distinguish a
leftover same-name helper from a moved definition.

## Observable delta

One query distinguishes leftover same-name helpers from the moved definition.
`grep def parse` hits both files; `from pkg_util import parse` still binds the
leftover helper. bindpath prints that import path, the body that would run,
and the other same-name definition that this import did not bind.

## Reality mapping

AST-scan a directory for module-level defs, assignments, and `from … import`
of the name, then import those modules and inspect the bound object. A local
`def` is `kind=def`. A name that imports another module's object is
`kind=reexport` and `runs` names the defining module. No tracer, no bytecode
signatures.

## Research boundary

Does not reconstruct git moves or blame. Does not execute the bound function.
Importing a module runs its top-level code. Nested defs are not import
bindings.

## Removed

import-tracer daemon, bytecode signatures.

## Smallest artifact

Python 3 stdlib CLI `bindpath`.
