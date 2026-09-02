# DESTROYER bindname

Date: 2026-09-02

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

sha256 `35160e389926274b368c123f8217d13d6a7c2504b3c3fd44628b3b1f0bba5bb7` (18543 bytes). Worktree copy at `candidate-bind-bind` is byte-identical. Tests 11/11 pass.

Origin claim: for a name, show the import path and the body that would run. Distinguish a leftover same-name helper from a moved definition. `grep def parse` hits both; `from pkg_util import parse` still binds the leftover.

Happy path is real. Specimen-013 leftover vs moved is reproduced. That is not enough. The implementation is `importlib.import_module` of **every** module-level hit for the name, plus `inspect.getsource`, against a process that has already imported `ast`. The primitive cannot answer “what would this import bind” without executing the rest of the tree.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
```

---

## What still works

Specimen-013: `from pkg_util import parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. The moved body is `return ('moved', x.strip())`.

```bash
python3 "$CLI" -C lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files --from pkg_util parse
```

Reexport `from pkg_parse import parse` left in util: `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`. Relative `from .moved import parse` in a package is the same. Assignment alias `parse = moved.parse` (module name that does not shadow stdlib) is `kind=reexport`, `runs=moved.parse`, `same_function True` and matches `aliaser.parse is moved.parse`.

Empty dir / missing name / missing `--file` / star `--import` / NAME mismatch: nonzero rc, no fake TSV.

That is the whole useful delta. Attacks below break the claim around it, or show the primitive cannot grow.

---

## Implementation

### 1. Leftover `ast.py` is reported as stdlib `ast.parse`

The origin question with a leftover whose module name is already in `sys.modules`. Fresh Python in that directory binds the leftover. bindname binds Homebrew 3.14 `ast.py:26`.

```bash
# tree: ast.py  def parse(x): return ('leftover-ast', x)
#       pkg_parse.py  def parse(x): return ('moved', x)
python3 "$CLI" -C "$ROOT" --from ast parse
```

```text
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

Honesty, same cwd, same files:

```bash
python3 -c "from ast import parse; print(parse('z'))"
# ('leftover-ast', 'z')
# ast.__file__ is ROOT/ast.py
```

`bindname` does `import ast` at process start, then `importlib.import_module("ast")` which returns the cached stdlib module. `getattr(ast, "parse")` succeeds, so there is no static fallback. `kind=def` is unsupported certainty: it is not the leftover helper.

Names the stdlib does **not** bind (`inspect.py` with `def parse`) fall back to the AST and accidentally look local. The lie is reserved for the case that matters: leftover and stdlib **share the name**.

### 2. `--from MODULE` imports every other same-name module

`binding_from_import` calls `bindings_for_name(root, name)`, which loads every static hit. Asking what `pkg_util.parse` binds is not an isolated import.

**sys.exit hostage.** `keep.py` defines `parse`. `killer.py` also defines `parse` and calls `sys.exit(9)` at import time.

```bash
python3 "$CLI" -C "$ROOT" --from keep parse ; echo rc=$?
# (no stdout, no stderr)
# rc=9
```

The queried module never gets a chance to answer.

**Stdout is not a record.** `--from pkg_util parse` still executes `pkg_parse.py`. A print there is prepended to the TSV. Marker file written. Observed:

```text
SIDE_EFFECT_STDOUT
query	from pkg_util import parse
...
```

Unseen specimens in this run do it without being adversarial. `-C specimens/specimen-010/files load_skip_empty` prints loader.py's `skip_empty '/x' '2'` lines, then the TSV. `-C specimens/specimen-015/files side` prints `after_eval 1 calls 1` first. `grep` does not execute those files.

**Alphabetical patcher rewrites the queried bind.** `aaa_patch.py` (name sorts before `pkg_util`) imports `pkg_util` and replaces `pkg_util.parse`. Isolated `from pkg_util import parse` is still the leftover. bindname reports the patch:

```text
query	from pkg_util import parse
runs	aaa_patch.parse
kind	reexport
file	aaa_patch.py
same_function	True
```

No `also`. The leftover identity is gone. `zzz_patch.py` (sorts after) does **not** rewrite, because `pkg_util` is snapshotted first. The answer depends on module-name order, not on the import the user typed.

### 3. Static last-wins is not the runtime bind when import fails

```python
# boom.py
def parse(x):
    return 'actually-bound-then-raise'
raise RuntimeError('import dies')
from moved import parse
```

`--from boom parse` rc=0:

```text
runs	moved.parse
kind	reexport
source	'from moved import parse'
same_function	True
```

The `from moved import parse` never ran. At the raise, `parse` is the local def. List mode agrees with the lie (`count 2`, `same_function True`).

Annotation-only is the same family:

```python
# ann.py
from typing import Callable
parse: Callable
```

List and `--from` both rc=0, `kind=def`, `source='parse: Callable'`, `same_function True`. Honesty: `hasattr(ann, 'parse') is False`. An import that would fail is printed as a bind.

### 4. `UnicodeDecodeError` is not `SyntaxError`

`static_hits` catches `OSError` and `SyntaxError` only. A non-UTF-8 `.py` next to a valid leftover dumps a traceback and rc=1. The valid bind is not reported.

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 26
```

A leftover with a **syntax** error is the opposite lie: skipped silently, list mode `count 1 same_function True` on the moved def only. `--from pkg_util parse` → `pkg_util has no name parse` rc=1. Partial miss, exit 0 on the list.

### 5. `--file` is mention, not the bind that would run

Dead imports in functions / `if False` are reported as uses (rc=0, both leftover and moved). `importlib.import_module('pkg_parse'); parse = m.parse` is `no uses` rc=1.

Local override after import:

```python
from pkg_util import parse
def parse(x):
    return 'overridden-in-file'
```

`--file override.py parse` prints `pkg_util.parse` leftover `kind=def`. Honesty: `override.parse('x')` is `'overridden-in-file'`.

As-alias is not queryable. File has `from pkg_util import parse as parse_legacy`. `--file NAME=parse` lists **both** imports (including the one whose local name is not `parse`). `--file NAME=parse_legacy` → `no uses of parse_legacy` rc=1. `bindings_for_name` then `getattr(module, "parse_legacy")` on a module that only has `parse`.

`--file /dev/stdin` and `--file /dev/fd/0` while stdin is a pipe: `not a file` rc=1 (`Path.is_file()` is false on a FIFO). FIFO path same. Stdin is unused in list mode.

### 6. Symlink vs hardlink identity

`module_name_for` uses `path.resolve()`. Two names for one inode via **symlink** (`pkg_parse.py -> pkg_util.py`) collapse to one module in list mode: `count 1 same_function True`. Honesty: `pkg_util.parse is pkg_parse.parse` is **False** (two module objects, two functions). `--from pkg_parse` sees both (`same_function False`). List vs query disagree on the leftover/moved pair.

**Hardlink** of the same bytes does not resolve to one path: list mode `count 2 same_function False`, matching `is False`. Same content, two answers, keyed on how the second name was attached.

Symlink directory cycle `loop -> root` does not hang here (walk dies on `OSError` around path length; resolve() collapses names so `count` stays 1). No visited-inode set. A fan-out bomb is untested; the walk is not a tree.

### 7. List mode vs `--from`: split identity

Module-level `if flag: def parse` is not `tree.body` FunctionDef. List mode misses it (`count 1 same_function True` on the other file). `--from pkg_util parse` finds the leftover and `also` the moved def. Same split for `exec("def parse...")`, PEP 562 `__getattr__`, `from pkg_parse import *`, `import pkg_parse as parse` (list misses the alias module).

`from pkg import parse` when `parse` is a **submodule**: `--from pkg parse` reports `runs=pkg.parse.pkg.parse`, `kind=reexport`, `source` = the whole `pkg/parse.py` file (looks like the function). List mode omits `pkg.parse` as a bind of the package. The bound object is a module, not `def parse` inside it.

### 8. `kind` / `runs` / `also` noise

`parse = functools.partial(_p, 'pre')`: `kind=reexport`, `runs=functools.parse`, empty source. Decorator without `wraps`: `runs=dec.wrap`, source is the wrapper. `import pkg_parse as parse`: `runs=pkg_parse.pkg_parse`. Query mode `also` lists every other def in the tree (lambda, class, wrap) as if they were leftover helpers of the same move.

`from weird name import parse` is printed for `weird name.py`. That statement is not Python.

### 9. Huge inputs survive; they dump the body

200 kB function body, rc=0 in 0.03s, stdout ~200 kB (`source` is `repr` of the whole def). 80 extra defs: 81 import rows. No cap. Not fatal; not a pipe component.

---

## Primitive

Reality-stripped operation: scan module-level `def` / `assign` / `from … import` for NAME; `importlib.import_module` each hit in the current process; `inspect.getsource` the object; print other hits as `also`.

Nearest ordinary workflow:

```bash
python3 -c "from pkg_util import parse; import inspect; print(inspect.getfile(parse)); print(inspect.getsource(parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is exactly leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def, plus `same_function`.

That delta is real on the owned fixture and on a true reexport. It is not real once “also” is implemented by **executing every other same-name module**, or once the leftover name collides with something already in `sys.modules`.

Observable capability lost if bindname vanishes: none that isolated import+inspect plus grep do not already have, **except** the pairing. The pairing is why this is not KILL. The current embodiment pretends a tree-wide import is the same as the import the user wrote.

Hardcoded scan+import is the ceiling:

- There is no isolated query. `also` requires executing leftovers. `sys.exit`, prints, and patchers are in-spec.
- `import_module` cannot see a leftover that shadows a preloaded stdlib module. `spec_from_file_location` with a unique name can (honesty did).
- Nested defs are a stated boundary. Unseen specimen-012's identities that actually ran are nested `test_a` / `test_b` inside `run()`. bindname reports only `test_order.test_a` and `same_function True`. Transfer to that packet is a miss by construction.
- `--file` is an AST mention index, not the last binding in that file.
- `same_function True` at `count 1` after a silent miss (syntax error, if/else, symlink collapse) reads as “one identity” when the leftover was dropped.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind.

Do not keep a calculator that imports the whole tree to fill `also`.

1. **Isolate the queried import.** Load only that module, via `spec_from_file_location` and a unique module name, not `importlib.import_module` against `sys.modules`. A leftover `ast.py` must report the leftover body. Stdlib `ast.parse` is the wrong identity.
2. **Collect `also` without executing those modules.** Static defs (including `If`/`Try` bodies, or a stated refusal). If import of the *query* fails, say it failed; do not substitute last-wins AST (`from moved import parse` after `raise`).
3. **`--file` is last binding, not mentions.** Dead imports are not uses. A following `def parse` wins. `parse as parse_legacy` is queryable as `parse_legacy`. `importlib.import_module` remains out of scope only if declared.
4. **Presence vs bind.** Annotation-only is not `kind=def`. SyntaxError/UnicodeDecodeError/missing module are visible misses, not `same_function True` on whatever remains. Catch `UnicodeDecodeError`.
5. **Identity of files.** Do not `resolve()` away a second name before comparing objects. Symlink pair and hardlink pair must use the same rule, and that rule must match `is` of the two imports. Directory walk needs a visited inode set.
6. **Stdout is the TSV.** Import side effects of non-queried modules must not run. Queried module side effects must not be mixed into the record (separate stream, or static source only).
7. **Tests the current suite cannot see.** Leftover `ast.py`, `sys.exit` sibling, `aaa_patch` order, annotation-only, boom.py last-wins, `--file` as-alias + override, non-UTF-8 skip, symlink vs hardlink, specimen-010 stdout pollution.

If the mutation cannot do (1)+(2)+(6), the object is still `inspect.getsource` after a contaminated import, and a later destroyer should KILL.

---

MUTATE
