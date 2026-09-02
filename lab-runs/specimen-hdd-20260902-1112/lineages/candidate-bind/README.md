# bindname

For a name, show the import path and the body that would run.

After a move, two functions can share a name. Grep hits both. Blame and tags
disagree. The question is which body `from pkg_util import parse` actually
binds: the leftover helper still defined in util, or the moved definition.

Only the queried module is imported, via `spec_from_file_location` under its
logical import name after dropping a foreign `sys.modules` cache. Builtin
names (`sys`, `builtins`), frozen stdlib (`io`, `os`, `codecs`, …), and
names a fresh interpreter already imported (`encodings`, `functools`,
`types`, …) cannot be shadowed by a leftover file. Frozen **submodules**
honesty cannot bind (`importlib.util`, `importlib.machinery`) also miss;
leftover `importlib.py` / leftover `importlib.abc` still bind. Path-shadowable
leftovers honesty does bind (`ast`, `inspect`, `tokenize`, `json`) stay leftover
helpers. Other same-name defs are collected from the AST (`if False` /
`TYPE_CHECKING` / `flag = True; if flag` / `if 1 == 1` / `if 1 + 1` /
`if []:` / TYPE_CHECKING aliases including `typing_extensions` and dead match
cases are not binds) and are not executed. There is no tracer daemon and no
bytecode fingerprint.

## Usage

```
bindname [-C DIR] NAME
bindname [-C DIR] --from MODULE NAME
bindname [-C DIR] --import 'from MODULE import NAME'
bindname [-C DIR] --file PATH NAME
bindname [-C DIR] MODULE.NAME
```

| flag | meaning |
| --- | --- |
| `NAME` | the bound name, or `MODULE.NAME` |
| `-C DIR` | import root (default: `.`) |
| `--from MODULE` | resolve `from MODULE import NAME` |
| `--import STMT` | resolve that import statement |
| `--file PATH` | last binding of NAME in PATH (dead imports are not uses) |

## Output

Tab-separated fields. `source` is Python `repr` so the body stays one line.

List mode (`bindname parse`):

```
name	parse
count	2
same_function	False

import	from pkg_util import parse
bind	pkg_util.parse
runs	pkg_util.parse
kind	def
file	pkg_util.py
line	1
source	"def parse(x):\n    return ('legacy', x)"

import	from pkg_parse import parse
bind	pkg_parse.parse
runs	pkg_parse.parse
kind	def
file	pkg_parse.py
line	1
source	"def parse(x):\n    return ('moved', x.strip())"
```

| field | what it is |
| --- | --- |
| `import` | the import statement that binds this path |
| `bind` | import path (`module.name`) |
| `runs` | defining identity of the body that would run |
| `kind` | `def` if this module defines it; `reexport` if it aliases another |
| `file`/`line`/`source` | the body that would run |
| `also` | other independent defs of the same name (static; query mode) |
| `miss` | SyntaxError / UnicodeDecodeError on a tree file |
| `same_function` | whether every listed bind is the same object |

`--file` uses the last live binding of NAME. A following `def parse` wins
over an earlier import. `from pkg_util import parse as parse_legacy` is
queryable as `parse_legacy`. `parse = pkg_parse.parse`,
`parse = getattr(pkg_parse, 'parse')`, and `parse = p` after
`from pkg_parse import parse as p` follow the moved body the same way
ImportFrom does. `importlib.import_module(...)` in the file is out of
scope. Module-level `module.NAME` uses are listed only when NAME is not
bound locally. `functools.partial` `runs` names the wrapped callable, not
`functools.parse`.

A leftover helper: `--from pkg_util parse` has `kind=def`, `runs=pkg_util.parse`,
and `also pkg_parse.parse` with `same_function False`.

A leftover `ast.py` in the import root is that helper, not the stdlib `ast`
this process already imported. `--from ast parse` loads it as `__name__ ==
'ast'` after dropping the cached stdlib entry, then restores stdlib. A
fresh `from ast import parse` in that directory binds the same object.
`from PKG import NAME` when NAME is a submodule is `kind=module`.

A true move that left `from pkg_parse import parse` behind: `--from pkg_util parse`
has `kind=reexport`, `runs=pkg_parse.parse`, and `same_function True`.

## Example (specimen-013)

```
bindname -C files parse
bindname -C files --from pkg_util parse
bindname -C files --import 'from pkg_parse import parse'
bindname -C files --file files/test_parse_identity.py parse
```

`from pkg_util import parse` runs the leftover `return ('legacy', x)`.
`from pkg_parse import parse` runs the moved `return ('moved', x.strip())`.
They are not the same function.
