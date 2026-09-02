# bindiso

For a name, show the import path and the body that would run.

After a move, two functions can share a name. Grep hits both. The question is
which body `from pkg_util import parse` actually binds: the leftover helper
still defined in util, or the moved definition.

The queried module is loaded from its file under a unique module name. Other
same-name defs are read from the AST and are not executed. There is no tracer
daemon and no bytecode fingerprint.

Clean-room reimplementation of the harvested identity primitive (second
style: isolate leftover `ast.py`; static `also`).

origin.method: specimen-hdd
origin.trial: hdd-identity
origin.kind: clean-room
specimens: [specimen-013]

## Usage

```
bindiso [-C DIR] NAME
bindiso [-C DIR] --from MODULE NAME
bindiso [-C DIR] --import 'from MODULE import NAME'
bindiso [-C DIR] --file PATH NAME
bindiso [-C DIR] MODULE.NAME
```

| flag | meaning |
| --- | --- |
| `NAME` | the bound name, or `MODULE.NAME` |
| `-C DIR` | import root (default: `.`) |
| `--from MODULE` | resolve `from MODULE import NAME` |
| `--import STMT` | resolve that import statement |
| `--file PATH` | last binding of NAME in PATH (else module-level uses) |

## Output

Tab-separated fields. `source` is Python `repr` so the body stays one line.

A leftover helper: `--from pkg_util parse` has `kind=def`, `runs=pkg_util.parse`,
and `also pkg_parse.parse` with `same_function False`.

A leftover `ast.py` in the import root is that helper, not the stdlib `ast`
this process already imported. `--from ast parse` prints the leftover body.
A fresh `from ast import parse` in that directory binds the same object.

A true move that left `from pkg_parse import parse` behind: `--from pkg_util parse`
has `kind=reexport`, `runs=pkg_parse.parse`, and `same_function True`.

## Example (specimen-013)

```
bindiso -C files parse
bindiso -C files --from pkg_util parse
bindiso -C files --import 'from pkg_parse import parse'
bindiso -C files --file files/test_parse_identity.py parse
```

`from pkg_util import parse` runs the leftover `return ('legacy', x)`.
`from pkg_parse import parse` runs the moved `return ('moved', x.strip())`.
They are not the same function. Grep `def parse` hits both.
