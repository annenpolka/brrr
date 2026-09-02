# FIX bindname

Date: 2026-09-02

Destroyer: `DESTROYER_bindname.md` §1 leftover `ast.py` reported as stdlib `ast.parse`.

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/`

Branch: `specimen-hdd/candidate-bind-bind`

Commit: `d90ca1bf8c5bafa7b3036cc3bfde4a3c4671bc5f`

Archive: `lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/`

This is FIX of a first-selection survivor, not KILL. The pairing on
specimen-013 remains the object. Other destroyer items (tree-wide import
for `also`, `sys.exit` sibling, `aaa_patch` order, annotation-only,
`--file` mentions) are still open and are not this patch.

## Leftover `ast.py`

bindname does `import ast` at process start, then `importlib.import_module("ast")`.
That hit `sys.modules` and returned Homebrew 3.14 `ast.py:26`. Fresh Python in
the same directory bound the leftover helper.

Tree:

```
ast.py        def parse(x): return ('leftover-ast', x)
pkg_parse.py  def parse(x): return ('moved', x)
```

Before:

```
query	from ast import parse
bind	ast.parse
runs	ast.parse
kind	def
file	/opt/homebrew/Cellar/python@3.14/.../lib/python3.14/ast.py
line	26
source	'def parse(source, filename=\'<unknown>\', ...'
also	pkg_parse.parse
same_function	False
```

Honesty, same files:

```
python3 -c "from ast import parse; print(parse('z'))"
# ('leftover-ast', 'z')
```

Now `--from ast parse` loads the leftover file via `spec_from_file_location`
under the real name `ast` after dropping the preloaded stdlib entry. Unique
module names would make `kind=reexport` and `runs` a synthetic id; that is
not the bind.

```
query	from ast import parse
bind	ast.parse
runs	ast.parse
kind	def
file	ast.py
line	1
source	"def parse(x):\n    return ('leftover-ast', x)\n"
also	pkg_parse.parse
same_function	False
```

`kind=def` is the leftover helper. `file` is `ast.py`, not Cellar.

## Tests

`python3 tests/test_bindname.py` — leftover `ast.py` CLI and in-process bind
match honesty; specimen-013 leftover vs moved still `kind=def`,
`runs=pkg_util.parse`, `also pkg_parse.parse`, `same_function False`.

## Demo

`./demo.sh` twice. Specimen-013 unchanged: leftover `return ('legacy', x)`,
moved `return ('moved', x.strip())`, not the same function.
