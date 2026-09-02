# bindiso

origin.method: specimen-hdd
origin.trial: hdd-identity
origin.kind: clean-room
parent: candidate-bind
specimens: [specimen-013]

classification: USEFUL_COMPOSITION

## Core operation

For a name, show the import path and the body that would run. Distinguish a
leftover same-name helper from a moved definition.

## Observable delta

One query distinguishes leftover same-name helpers from the moved definition.
`grep def parse` hits both files; `from pkg_util import parse` still binds the
leftover helper. bindiso prints that import path, the body that would run,
and the other same-name definition that this import did not bind.

A leftover `ast.py` in the import root is that helper, not the stdlib `ast`
this process already imported.

## Reality mapping

Load **only** the queried module, via `spec_from_file_location` under a unique
`_bindiso_<token>.<mod>` name. Do not call `importlib.import_module` against
`sys.modules`. Classify `kind`/`runs`/`source` from the queried file's last
static bind, not from `obj.__module__` (the unique name would make that a
synthetic id). Collect `also` from module-level `def` nodes, including `If`/
`Try` bodies; those files are not executed. If the queried import fails, say
so; do not substitute last-wins AST. `--file` is the last binding of NAME in
that file (a following `def` wins; `parse as parse_legacy` is queryable as
`parse_legacy`). Annotation-only is not a bind. Stdout is the TSV: queried
prints are captured; siblings are not imported. Nested defs are not import
bindings. Dynamic `importlib.import_module` in `--file` is out of scope.

## Research boundary

Does not reconstruct git moves or blame. Does not execute the bound function.
Importing the queried module runs its top-level code (stdout discarded).

## Removed

import-tracer daemon, bytecode signatures, tree-wide `import_module` for
`also`, `inspect.getsource` after a contaminated import.

## Smallest artifact

Python 3 stdlib CLI `bindiso`.
