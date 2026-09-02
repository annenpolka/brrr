# DESTROYER bindpath

Date: 2026-09-02 15:39 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0375 worker=destroyer-bindpath

Target (clean-room reimpl): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/reimpl-bindname/bindpath`

sha256 `b66ee9e477b5e1aea13661891bd8fbcd2e6a178b529daa3de7a44c499ef66645` (12728 bytes, 415 lines). Worktree `reimpl-bindname-bindname-cr` HEAD `069c477`. Parent tree is coordinator-only; this object is not on `main` and was not merged.

Compare (mutated KEEP, not this target): `lineages/candidate-bind/bindname` sha256 `a1ba68cde9550dd15893e4a83ffd5e46c796f45660dfc446a772697a0b830575` (30927 bytes, 984 lines). Tests 30/30. `spec_from_file_location` + unique `_bindname_N_*`. No `importlib.import_module` of the query.

Origin claim (`CANDIDATE.md`): for a name, show the import path and the body that would run. Distinguish a leftover same-name helper from a moved definition. Reality mapping in the reimpl itself: AST-scan, then **import those modules and inspect the bound object**.

Happy path is real. Specimen-013 leftover vs moved is reproduced. Tests 11/11 pass. `demo.sh` twice, `demo-1.log` / `demo-2.log` byte-identical (`cmp` rc=0, 2007 bytes). That is not enough.

This is the **pre-mutation bindname primitive**: `importlib.import_module` of every module-level hit, plus `inspect.getsource`, against a process that has already imported `ast` and `inspect`. Leftover `ast.py` is Homebrew 3.14 `ast.parse` line 26. `also` executes siblings. First reimpl KEEP is not automatic. `DESTROYER_bindname` leftover: if the mutation cannot isolate the query, collect `also` statically, and keep stdout as the TSV, a later destroyer should KILL. `candidate-bind/MUTATE.md` leftover: if a later object loads `also` by importing the whole tree, or answers leftover `ast.py` as Homebrew `ast.parse`, KILL. Job kill condition: same `import_module`. Honor that.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/reimpl-bindname/bindpath
KEEP=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
S013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
S010=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-010/files
```

Python 3.14.5. Stdlib `ast.__file__` = `/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/ast.py`. Attacks under `destroyers/_bindpath_scratch/`. No merge onto `main`.

---

## What still works

Specimen-013: `from pkg_util import parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. The moved body is `return ('moved', x.strip())`. Same TSV shape as mutated bindname on this owned fixture.

```bash
python3 "$CLI" -C "$S013" --from pkg_util parse
```

Reexport `from pkg_parse import parse` left in util: `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`. Assignment alias `parse = pkg_parse.parse` is the same. Nested def is not an import binding (stated). Missing NAME: nonzero rc. `--from boom parse` after `raise RuntimeError` is `cannot import` rc=1 (no last-wins AST substitute). Annotation-only `--from ann parse` is `has no name parse` rc=1.

That is the whole useful delta. It is the owned leftover/moved pair. Attacks below are the same primitive DESTROYER_bindname already killed-if-unfixed.

---

## Implementation

Load path (query and list):

```python
def load_module(modname: str):
    return importlib.import_module(modname)

# --from / --import / MODULE.NAME:
world = resolve_many(discover_binders(root, name), name, required=False)
bound = resolve(module, name, required=True)
```

`prepare_root` inserts `-C` on `sys.path`. `import ast` / `import inspect` already ran. There is no `spec_from_file_location`, no unique module name, no stdout redirect, no static `also`.

### 1. Leftover `ast.py` is reported as stdlib `ast.parse`

The origin question with a leftover whose module name is already in `sys.modules`. Fresh Python in that directory binds the leftover. bindpath binds Homebrew 3.14 `ast.parse`.

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
file	ast.py
line	26
source	'def parse(source, filename=\'<unknown>\', ...'
also	pkg_parse.parse
same_function	False
```

`file` is `os.path.basename` of `inspect.getsourcefile`. Stdlib and leftover both display as `ast.py`. `kind=def` plus `file ast.py` looks like the leftover. The body is stdlib (`type_comments`, `PyCF_ONLY_AST`, line 26).

Honesty, same cwd, same files:

```bash
python3 -c "from ast import parse; print(parse('z')); import ast; print(ast.__file__)"
# ('leftover-ast', 'z')
# .../destroyers/_bindpath_scratch/ast_leftover/ast.py
```

Mutated bindname on the same tree: `file ast.py`, `line 1`, `source` contains `leftover-ast`. That is the isolate this reimpl does not have.

Names the stdlib does **not** bind still fail, they do not fall back. `inspect.py` with `def parse` (CLI already imported `inspect`): `bindpath: inspect has no name parse` rc=1. Mutated bindname reports the leftover inspect helper. The lie is reserved for the collision that matters (`ast`); the miss is reserved for the collision the process already loaded without `parse`.

### 2. `--from MODULE` imports every other same-name module

`also` is `resolve_many(discover_binders(...))` before the query. Asking what `pkg_util.parse` binds is not an isolated import.

**sys.exit hostage.** `keep.py` defines `parse`. `killer.py` also defines `parse` and calls `sys.exit(9)` at import time.

```bash
python3 "$CLI" -C "$ROOT" --from keep parse ; echo rc=$?
# (no stdout, no stderr)
# rc=9
```

The queried module never gets a chance to answer. Mutated bindname: rc=0, `runs keep.parse`, `also killer.parse`, `same_function False`.

**Stdout is not a record.** `--from pkg_util parse` still executes `pkg_parse.py`. A print there is prepended to the TSV:

```text
SIDE_EFFECT_STDOUT
query	from pkg_util import parse
...
```

Unseen specimen-010 does it without being adversarial. `-C specimens/specimen-010/files load_skip_empty` prints `skip_empty '/x' '2'` / `assign '' '2'` / `unset_vs_empty False None`, then the TSV. Mutated bindname list mode is static: the record starts with `name	load_skip_empty`. `grep` does not execute those files.

**Any patcher rewrites the queried bind.** World import runs first, then `resolve` returns the cached module. `aaa_patch.py` (sorts before) and `zzz_patch.py` (sorts after) both `import pkg_util; pkg_util.parse = parse`. Isolated `from pkg_util import parse` is still `('legacy', z)`. bindpath reports the patch either way:

```text
query	from pkg_util import parse
runs	aaa_patch.parse   # or zzz_patch.parse
kind	reexport
file	aaa_patch.py
```

Mutated bindname: `runs pkg_util.parse`, `kind def`, leftover body, `also` lists the patcher as a static def. The answer no longer depends on who else in the tree defined `parse`.

### 3. `--file` is mention, not the bind that would run

Dead imports in functions / `if False` are reported as uses (rc=0, leftover and moved). Honesty: those imports did not run.

Local override after import:

```python
from pkg_util import parse
def parse(x):
    return 'overridden-in-file'
```

`--file override.py parse` prints `pkg_util.parse` leftover `kind=def`. Honesty: `override.parse('x')` is `'overridden-in-file'`. Mutated bindname: `bind override.parse`, source is the following def.

As-alias is not queryable. File has `from pkg_util import parse as parse_legacy`. `--file NAME=parse_legacy` → `pkg_util has no name parse_legacy` rc=1 (`getattr` of the original name on a module that only has `parse`). Mutated bindname: last binding, queryable as `parse_legacy`.

### 4. Empty dir is a fake TSV

`bindpath -C empty parse` → rc=0, `count 0`, `same_function True`. No bindings is printed as “every listed bind is the same object.” Mutated bindname: `no bindings for parse` rc=1.

Non-UTF-8 sibling is skipped silently (no `miss` row). Query of the leftover still works; `same_function False` on what remains, with no record that a file was unreadable. Mutated bindname emits `miss zzz_bin.py UnicodeDecodeError`.

### 5. Huge inputs / pipes

Not retested as fatal. 200 kB bodies would still dump `source` as `repr` of the whole def (same as parent). `--file /dev/stdin` is `not a file` / cannot-read. Not the kill axis.

---

## Primitive

Reality-stripped operation: scan module-level `def` / `assign` / `from … import` for NAME; `importlib.import_module` each hit in the current process; `inspect.getsource` the object; print other hits as `also`.

Nearest ordinary workflow, host-executed on specimen-013:

```bash
python3 -c "from pkg_util import parse; import inspect; print(inspect.getfile(parse)); print(inspect.getsource(parse))"
grep -n "def parse" -r .
```

That pair is leftover body + the other `def parse`. bindpath’s load-bearing delta is combining them in one query, plus `kind` reexport vs def, plus `same_function`.

That delta is real on the owned fixture and on a true reexport. It is not real once `also` is implemented by **executing every other same-name module**, or once the leftover name collides with something already in `sys.modules`.

Observable capability lost if bindpath vanishes: none that isolated import+inspect plus grep do not already have, **except** the pairing. The pairing already lives in mutated bindname, which isolates the query. bindpath is not a second style of that pairing. It is the contaminated import DESTROYER_bindname said to KILL if unfixed.

THIN_WRAPPER of `import_module` + `inspect.getsource` after a contaminated import. Constitution: a THIN_WRAPPER does not gain exotic features to escape. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” Do not mutate bindpath into bindname’s unique-name loader as a “fix”; that mutation already landed on `candidate-bind`.

---

## Versus mutated bindname (brief)

| attack | bindpath (this) | bindname (KEEP, post-mutate) |
| --- | --- | --- |
| leftover `ast.py` | stdlib `ast.parse` line 26 | leftover body line 1 |
| leftover `inspect.py` | `has no name parse` rc=1 | leftover body |
| `sys.exit` sibling | rc=9, empty stdout | query answers, `also` static |
| sibling `print` | prepended to TSV | TSV only |
| specimen-010 list | loader prints first | static, no exec |
| `aaa_patch` / `zzz_patch` | `runs` is the patcher | leftover, patcher in `also` |
| `--file` override | leftover import | last `def` in file |
| `--file` as-alias | rc=1 | queryable |
| empty dir | `count 0 same_function True` rc=0 | rc=1 |
| loader | `import_module` vs `sys.modules` | `spec_from_file_location` unique name |

Same CLI surface. Same owned specimen-013 TSV. Different primitive. First reimpl of the old primitive is not a KEEP of the new one.

---

## Why not MUTATE

DESTROYER_bindname already spent the mutation slot: isolate query, static `also`, leftover `ast.py`, stdout is the TSV. That mutation is `candidate-bind` 30/30. bindpath is a clean-room of the **pre-mutation** calculator. First reimpl KEEP is not automatic. Growing unique-name loading here would be copying the KEEP lineage, not recovering a second object.

Do not send this back to R1. Do not fold `spec_from_file_location` onto bindpath as a survival trick.

---

KILL
