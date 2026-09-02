# bindpath

For a name, show the import path and the body that would run.

After a move, two functions can share a name. Grep hits both. Blame and tags
disagree. The question is which body `from pkg_util import parse` actually
binds: the leftover helper still defined in util, or the moved definition.

This process imports the named modules. There is no tracer daemon and no
bytecode fingerprint.

Clean-room reimplementation of the harvested identity primitive.

origin.method: specimen-hdd
origin.trial: hdd-identity
origin.kind: clean-room
specimens: [specimen-013]

## Usage

```
bindpath [-C DIR] NAME
bindpath [-C DIR] --from MODULE NAME
bindpath [-C DIR] --import 'from MODULE import NAME'
bindpath [-C DIR] --file PATH NAME
bindpath [-C DIR] MODULE.NAME
```

| flag | meaning |
| --- | --- |
| `NAME` | the bound name, or `MODULE.NAME` |
| `-C DIR` | import root (default: `.`) |
| `--from MODULE` | resolve `from MODULE import NAME` |
| `--import STMT` | resolve that import statement |
| `--file PATH` | resolve imports and `module.NAME` uses in PATH |

## Output

Tab-separated fields. `source` is Python `repr` so the body stays one line.

List mode (`bindpath parse`):

```
name	parse
count	2
same_function	False

import	from pkg_parse import parse
bind	pkg_parse.parse
runs	pkg_parse.parse
kind	def
file	pkg_parse.py
line	1
source	"def parse(x):\n    return ('moved', x.strip())\n"

import	from pkg_util import parse
bind	pkg_util.parse
runs	pkg_util.parse
kind	def
file	pkg_util.py
line	1
source	"def parse(x):\n    return ('legacy', x)\n"
```

| field | what it is |
| --- | --- |
| `import` | the import statement that binds this path |
| `bind` | import path (`module.name`) |
| `runs` | defining identity of the body that would run |
| `kind` | `def` if this module defines it; `reexport` if it aliases another |
| `file`/`line`/`source` | the body that would run |
| `also` | other independent defs of the same name (query mode) |
| `same_function` | whether every listed bind is the same object |

A leftover helper: `--from pkg_util parse` has `kind=def`, `runs=pkg_util.parse`,
and `also pkg_parse.parse` with `same_function False`.

A true move that left `from pkg_parse import parse` behind: `--from pkg_util parse`
has `kind=reexport`, `runs=pkg_parse.parse`, and `same_function True`.

## Example (specimen-013)

```
bindpath -C files parse
bindpath -C files --from pkg_util parse
bindpath -C files --import 'from pkg_parse import parse'
bindpath -C files --file files/test_parse_identity.py parse
```

`from pkg_util import parse` runs the leftover `return ('legacy', x)`.
`from pkg_parse import parse` runs the moved `return ('moved', x.strip())`.
They are not the same function. Grep `def parse` hits both.
