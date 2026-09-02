# bindslot

For a name in one module, show every binding slot and which body would run.

After a move, two functions can share a name. Concatenating the files (or
loading the module from a blob with no filesystem path) removes the path
split. Grep still hits both defs. Last-wins import still binds one body.
The leftover helper is in the same module.

This process does not import the module and does not use a path as identity.
Slots are source order in one blob. Stdin needs no file.

## Usage

```
bindslot NAME
bindslot NAME -s FILE
bindslot NAME --concat FILE --concat FILE
bindslot NAME --code TEXT
```

| flag | meaning |
| --- | --- |
| `NAME` | module-global name |
| `-s FILE` | one module source (`-` is stdin) |
| `--concat FILE` | append FILE into that one module (repeatable) |
| `--code TEXT` | source string; no filesystem path |

Default source is stdin when it is not a tty.

## Output

Tab-separated fields. `source` is Python `repr` so the body stays one line.

```
name	parse
slots	2
runs_slot	1
same_function	False

slot	0
role	leftover
kind	def
line	1
source	"def parse(x):\n    return ('legacy', x)"

slot	1
role	runs
kind	def
line	4
source	"def parse(x):\n    return ('moved', x.strip())"
```

| field | what it is |
| --- | --- |
| `slots` | how many times NAME is bound in this module |
| `runs_slot` | last slot; the body that would run if the module finished |
| `role` | `runs` or `leftover` |
| `kind` | `def` / `class` / `assign` / `import` |
| `from` | imported module, import slots only |
| `same_function` | whether every slot's source equals the runs source |

There is no `file` field. Line numbers are in the blob, not a path.

A leftover helper after concatenation: `role leftover` plus a later `role runs`
with `same_function False`.

A true move that left `from pkg_parse import parse` in the same blob:
`kind import` on `runs`, leftover `kind def`.

## Example (specimen-013 concatenated)

```
bindslot parse --concat files/pkg_util.py --concat files/pkg_parse.py
bindslot parse --code "$(cat files/pkg_util.py files/pkg_parse.py)"
python3 bindslot parse < concat.py
```

`from that blob import parse` runs the moved `return ('moved', x.strip())`.
The leftover `return ('legacy', x)` is still a slot.
They are not the same function.
