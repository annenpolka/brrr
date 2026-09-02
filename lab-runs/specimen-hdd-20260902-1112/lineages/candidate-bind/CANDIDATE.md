# bindname

origin.method: specimen-hdd
origin.trial: hdd-identity
specimens: [specimen-013]

classification: USEFUL_COMPOSITION

## Core operation

For a name, show the import path and the body that would run. Distinguish a
leftover same-name helper from a moved definition.

## Observable delta

One query distinguishes leftover same-name helpers from the moved definition.
`grep def parse` hits both files; `from pkg_util import parse` still binds the
leftover helper. bindname prints that import path, the body that would run,
and the other same-name definition that this import did not bind.

## Reality mapping

AST-scan a directory for module-level defs (including If/Try bodies that can
run), assignments, and `from … import` of the name. `if False` /
`TYPE_CHECKING` and their `not` complements, const-known `if flag:` /
`if 1 == 1` / `if 1 + 1` / `if +1` / `if ~0` / `if 1 in [1]` / `if []:` / `if __debug__` / TYPE_CHECKING aliases
(including `typing_extensions`) skip the dead branch; match cases that cannot
bind are not last-wins. Import only the queried module, via
`spec_from_file_location` under the logical name after dropping a foreign
cache, then inspect that object. Do not load leftover `sys.py` / `builtins.py`
over a builtin, leftover `io.py` / `encodings.py` / `os.py` over a frozen or
already-imported stdlib, or leftover frozen **submodules** (`importlib.util`,
`importlib.machinery`) honesty cannot shadow. Leftover `importlib.py` /
leftover `importlib/` package / leftover `importlib.abc` still bind when
honesty binds them. `also` is static and does not execute siblings. A leftover
file that shares a path-shadowable stdlib name (`ast.py`, `tokenize.py`) is
that helper, not Homebrew `ast.parse`, including `if __name__ == 'ast'` gates.
Stdout is the TSV: queried-module prints are not mixed into the record. A
local `def` is `kind=def`. A name that imports another module's object is
`kind=reexport` and `runs` names the defining module. `--file` `NAME =
module.NAME` / `getattr(module, 'NAME')` / `NAME = alias` follows that body.
`functools.partial` `runs` names the wrapped callable. A submodule bind is
`kind=module`. Annotation-only is not a bind. No tracer, no bytecode
signatures.

## Research boundary

Does not reconstruct git moves or blame. Does not execute the bound function.
Only the queried module's top-level code runs. Nested defs are not import
bindings. `importlib.import_module` of a name inside `--file` is out of scope.

## Removed

import-tracer daemon, bytecode signatures.

## Smallest artifact

Python 3 stdlib CLI `bindname`.
