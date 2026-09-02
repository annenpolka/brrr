# DESTROYER bindname 12

Date: 2026-09-02 19:28–19:40 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0590 worker=destroyer-bindname-12

Target (archive, post-MUTATE-12 post-class attr assign / multi-generator comps / conversion-then-spec):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `8f019efdab17ab25c2d136adc84761b9f5051cac71bed8321c5c87879354ff15` (62525 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-12 (`cli_sha256_after`, 94/94; worker `mutate-bindname-12` job-0589). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `3728e24 Record bindname mutate HEAD c3280c1.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `3728e24f3471418ccaf43db6ccea7af9be0ca5a8`. Mutate-12 commit `c3280c10c685aab828956a87ac70173fdeb6d95d`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 94/94 OK (10.695s / 10.988s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. `DESTROYER_bindname_6.md` **MUTATE**. `DESTROYER_bindname_7.md` **MUTATE**. `DESTROYER_bindname_8.md` **MUTATE**. `DESTROYER_bindname_9.md` **MUTATE**. `DESTROYER_bindname_10.md` **MUTATE**. `DESTROYER_bindname_11.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-12 claimed: post-class `T.x = 0` list matches query; multi-generator comps live; conversion-then-spec `f'{1!s:s}'` live; `T()` copies namespace unless class body has `__init__` (then Call unknown — do not exec `__init__`).

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; `class T: x = 1; T.x = 0; if T.x:` list live while honesty dead; THIN_WRAPPER of two greps. Those eight were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list last-wins of remaining const-known instance-follows-class (`t = T(); T.x = 0; if t.x`) / unpack-or-For Attribute targets / class-body outer env / Delete-then-missing If / const Subscript assign. Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname12_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

`rg import_module` / `_bindname_` on the CLI: no matches. Load path is `importlib.util.spec_from_file_location` under the logical name after `drop_foreign_cache`. `unshadowable_reason` is builtin / `_imp.is_frozen(modname)` **full name** then frozen top / `interpreter_preimported()` (subprocess `sys.modules` listing, cwd `/`, not `import_module` of the query).

| # | condition | host | fire? |
|---|-----------|------|-------|
| 1 | leftover `ast.py` reports Cellar / `lib/python` `ast.parse` | leftover body `('leftover-ast', x)`, `file ast.py`, no Cellar | no |
| 2 | load uses `import_module` against `sys.modules` | `has_import_module False`; `spec_from_file_location` | no |
| 3 | `also` executes siblings (`sys.exit` in `killer.py` hijacks `--from keep`) | rc=0 body `'kept'`; `SIDE` does not exist | no |
| 4 | leftover `io.py` / `sys.py` is `kind=def` while honesty ImportError | `io` / `encodings` / `os` / `sys` / `builtins` all `has no name`; no leftover body | no |
| 5 | leftover `importlib.util` is `kind=def` while honesty cannot bind | honesty cannot bind; CLI `has no name`; list miss; `importlib.machinery` same | no |
| 6 | leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper | both `kind=def` leftover helper, no Cellar | no |
| 7 | `class T: x = 1; T.x = 0; if T.x:` list live while honesty dead | honesty / query / list `cas-dead` | no |
| 8 | THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join | naive `inspect.getsource(ast.parse)` from `/tmp` is Cellar; bindname leftover + `also pkg_parse.parse` | no |

### Leftover `ast.py` is the leftover helper, not Cellar `ast.parse`

Tree: `ast.py` `def parse(x): return ('leftover-ast', x)` plus `pkg_parse.py` moved. Honesty `cwd` that tree, `python3 -c "from ast import parse; print(parse('z'))"` → `('leftover-ast', 'z')`. bindname invoked from `/tmp`:

```bash
python3 "$CLI" -C "$ROOT" --from ast parse
```

```text
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

No `Cellar`, no `lib/python`. List mode `count 2` leftover + moved. After `isolated_import`, `sys.modules['ast']` is Homebrew 3.14 `ast.py` again (`restored True`). Isolate claim holds for the ungated fixture. (In-process `load_query` prints inside `isolated_import` are swallowed by its stdout redirect; CLI leftover from `/tmp` is the isolate evidence.)

### `also` does not execute siblings

`keep.py` leftover def, `killer.py` `sys.exit(9)` plus `def parse`, `side.py` writes `SIDE`, `osexit.py` `os._exit(11)`. `--from keep parse` rc=0, body `'kept'`, `also killer.parse` / `also osexit.parse` / `also side.parse`, `SIDE` does not exist. `aaa_patch.py` does not rewrite `--from pkg_util`: `kind=def`, source still `legacy`.

### Leftover `sys.py` / `io.py` / `encodings.py` / `os.py` is not `kind=def`

Honesty `from sys import parse` is ImportError. bindname `--from sys parse` rc≠0, stderr `sys has no name parse`, no leftover-sys body. `io` / `encodings` / `os` / `builtins` same. Mutate-5/6 refuse holds.

### Leftover frozen submodule `importlib.util` is not `kind=def`

Honesty `from importlib.util import parse` cannot bind (frozen). bindname `--from importlib.util parse` rc≠0, `importlib.util has no name parse`, no leftover-util body. `importlib.machinery` same (MATCH refuse). Mutate-6 item 1 holds.

### Leftover `importlib.py` file / leftover `importlib.abc` / leftover `importlib/` package still helper

Honesty leftover-importlib-file / leftover-importlib-abc / leftover-importlib-pkg. bindname `kind=def`, `file importlib.py` / `importlib/abc.py` / `importlib/__init__.py`, no Cellar. Honor KILL 6 does not fire. Leftover `tokenize.py` still leftover helper. Leftover `json.py` / `pathlib.py` / `inspect.py` / `typing.py` / `dataclasses.py` / `warnings.py` / `contextlib.py` / `argparse.py` / `tempfile.py` / `subprocess.py` / `typing_extensions.py` / `json.decoder` / `importlib.resources` / `importlib.metadata` MATCH leftover helper. Preimported / frozen `enum` / `operator` / `functools` / `abc` / `types` / `re` / `collections` / `copyreg` / `site` / `zipimport` / `collections.abc` / `os.path` / `encodings.utf_8` MATCH refuse.

### Mutate-12 claimed post-class attr / multi-gen / conversion-then-spec still matches query

`class T: x = 1; T.x = 0; if T.x` list is `cas-dead`. Inverse `T.x = 1` after class `x = 0` list is `cal-live`. New attr `T.y = 1; if T.y` list is `cna-live`. `t = T(); t.x = 0; if t.x` list is `ias-dead` (setattr on the copy). AnnAssign `T.x: int = 0` list is `aa-dead`. `T.x = T.x - 1` list is `txs-dead`. `match T.x` after `T.x = 0` list is `ma-dead`. `T.x = T.y = 0` list is `ma2-dead`. `if not T.x` / `if T.x < 1` / `if T.x.real` after `T.x = 0` MATCH. `if T.x[0]` after `class T: x = [1]` MATCH.

`if [x for y in [[1]] for x in y]` / `if [x+y for x in [1] for y in [0]]` / `if {x: 1 for y in [[1]] for x in y}` / three-gen / filtered multi-gen list is live. Host re-run `if {x for y in [[1]] for x in y}` list is `ms2-live` (C2 fixture had a `y]:` syntax typo; not a SetComp lie). Empty multi-gen `if [x for y in [[]] for x in y]:` without else is **not** a list bind.

`if f'{1!s:s}'` / `if f'{1!r:s}'` / `if f'{1!a}'` / `if f'{1=}'` list is live. `if f'{1!s:d}'` without else: honesty ValueError; list currently both (`_MISSING`) — declared format-error park, not Honor KILL 7.

`class T: x = 1; async def go; t = T(); if t.x` list is `adc-live` (non-`__init__` methods do not block the copy). `t = T(); t.x = 1; T.x = 0; if t.x` list is `sk-live` (instance setattr shadows). Two instances `t1.x = 0; if t2.x` list is `ti-live`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `t = T(); if t.x:` after `class T: x = 1` / `if (lambda: 0):` / `if [1][0]` / `if f'{1}'` / `if f'{1:d}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` with else / tuple unpack / local TYPE_CHECKING / `if [[1]][0][0]:` / static-subject `match [1][0]` / `for _ in (x for x in [1]):` still match.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. Post-class Attribute assign / multi-gen / conversion-then-spec is the mutate-12 object. Remaining instance-follows-class / unpack-attr / class-body-outer / Delete-miss If / Subscript assign below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after mutate-12 post-class Attribute assign / multi-gen / conversion-then-spec, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if (x for x in []):` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `t = T(); if t.x:` / `if (lambda: 0):` / `if [1][0]:` / `if f'{1}':` / `if f'{1:d}':` / `if f'{1!s:s}':` / `if [*[1]]:` / `for _ in (x for x in [1]):` / `if [x for y in [[1]] for x in y]:` / `class T: x = 1; T.x = 0; if T.x:` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-12. It is real. List last-wins of remaining const-known instance lookup after class setattr / unpack onto Attribute / class body that cannot see outer `T` / Delete-then-`if` missing / const Subscript assign are not honesty leftover-identity.

---

## Implementation

### 1. `T()` still snapshots the class namespace; later class setattr does not follow

Mutate-12 copies `vars(T)` on no-arg Call unless `_bindname_has_init`. Instance setattr (`t.x = 0`) updates that copy (MATCH). Class setattr after the copy does not.

```python
# classafterinst.py
class T:
    x = 1
t = T()
T.x = 0
if t.x:
    def parse(x):
        return 'cai-live'
else:
    def parse(x):
        return 'cai-dead'
```

Honesty / query `'cai-dead'` (instance looks up class attr). List `cai-live` (copy of `x=1` never updated). Inverse new class attr after the instance:

```python
# instthenclassy.py
class T:
    x = 1
t = T()
T.y = 1
if t.y:
    def parse(x):
        return 'icy-live'
else:
    def parse(x):
        return 'icy-dead'
```

Honesty / query `'icy-live'`. List last-wins `icy-dead` (`t` has no `y`). `t = T(); del T.x; if t.x: def parse` without else: honesty AttributeError / query `has no name`; list `kind=def` (copy still has `x=1`, test live).

Keep instance-shadow MATCH (`t.x = 1; T.x = 0; if t.x` is `sk-live`). Do not exec `__init__`. Represent instances as class-name plus instance dict so `if t.x` reads the class namespace unless shadowed.

### 2. Unpack / For Attribute targets still miss `_set_namespace_attr`

Simple `T.x = 0` and `T.x = T.y = 0` write the namespace. Tuple unpack and For targets do not.

```python
# unpackattr.py
class T:
    x = 1
    y = 1
T.x, T.y = 0, 0
if T.x:
    def parse(x):
        return 'ua-live'
else:
    def parse(x):
        return 'ua-dead'
```

Honesty / query `'ua-dead'`. List `ua-live`. `for T.x in [0]:` then `if T.x` same (`fa-live` vs honesty dead). `_bind_target` should call `_set_namespace_attr` for Attribute targets. Do not fold AugAssign (`T.x += -1` stays park).

### 3. Class body env starts empty; const If / methods / bases are invisible

```python
# classouter.py
class T:
    x = 1
class U:
    y = T.x
if U.y:
    def parse(x):
        return 'co2-live'
else:
    def parse(x):
        return 'co2-dead'
```

Honesty / query `'co2-live'`. List `co2-dead` (inner `{}` does not see `T`). `class T: if True: x = 1; if T.x` list last-wins `cif-dead`. `class T: def go(self): return 0; if T.go` list last-wins `mt-dead` (FunctionDef is not stored). `t = T(); if t.go` same (`im-dead`). `class U(T): pass; if U.x` list last-wins `cb-dead`.

Class-body const env should see outer names already in env. Walk const-known If in the class body with the same polarity as module If. Store a truthy sentinel for `FunctionDef` / `AsyncFunctionDef` names (do not exec). When bases are Names bound to a `SimpleNamespace`, copy those const attrs into the subclass. Do not exec metaclass / decorators / `type(...)`.

### 4. Delete of a known name / attr then `if` is not a list bind

`del T.x` does `delattr` on the namespace. `if T.x` then `getattr` → `_MISSING` → both branches. Without else, list `kind=def` while honesty AttributeError has no name.

```python
# delattr.py
class T:
    x = 1
del T.x
if T.x:
    def parse(x):
        return 'da-dead-only'
```

Honesty / query `has no name`. List `kind=def`. `x = 1; del x; if x: def parse` same: Delete of Name is a no-op in `update_const_env` (only Attribute is handled), so list last-wins the body. Missing attr/name on a **known** namespace or env tombstone is import-stopping: skip both If branches (do not claim list matches import failure for unknown names — those stay both). Do not exec.

### 5. Const Subscript / slice assign does not update env

```python
# subassign.py
xs = [1]
xs[0] = 0
if xs[0]:
    def parse(x):
        return 'sa-live'
else:
    def parse(x):
        return 'sa-dead'
```

Honesty / query `'sa-dead'`. List `sa-live`. `d[1] = 0` / `xs[:] = []` / `T.x[0] = 0` after `class T: x = [1]` same. Read subscript already MATCH (`if T.x[0]` / `if xs[0]` before assign). Fold Assign whose target is a const-known list/dict Subscript or Slice when the container is already in env. Do not exec Call. Do not fold AugAssign.

### 6. Frozen / path-shadowable leftovers that match (not this MUTATE)

| leftover | honesty | CLI |
|----------|---------|-----|
| `importlib.util` / `importlib.machinery` | cannot bind (frozen) | `has no name` / list miss |
| `importlib.py` file / `importlib/` package / `importlib.abc` | leftover helper | leftover helper |
| `importlib.resources` / `metadata` | leftover helper | leftover helper |
| `json` / `json.decoder` / `pathlib` / `inspect` / `typing` / `dataclasses` / `warnings` / `contextlib` / `argparse` / `tempfile` / `subprocess` / `typing_extensions` | leftover helper | leftover helper |
| `enum` / `operator` / `functools` / `abc` / `types` / `re` / `collections` / `copyreg` / `site` / `zipimport` / `collections.abc` / `os.path` / `encodings.utf_8` | refuse | refuse |
| `tokenize.py` | leftover helper | leftover helper |

No frozen-submodule leftover-identity remaining that honesty and CLI split. Do not refuse leftover `importlib/` package that honesty binds.

### 7. Declared parks this cut (probed, not MUTATE)

- Nested defs (specimen-012 `test_a` inside `run()`): list `test_order.test_a`; `--from run_orders test_a` has no name.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign / `importlib.import_module` / `__dict__` / `itemgetter` / `[pkg_parse.parse][0]` / lambda wrap: honesty moved; `--from` follows; `--file` does not. Constant-getattr / getattr-with-default / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute already follow.
- FIFO `--file` remains `not a file` (0.041s).
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a **list** bind: query may follow; list miss.
- `parse = lambda ...` as the bind (query `kind=def` `runs=.<lambda>`, source is the assignment; query does not print `('lam', 'z')`).
- Huge `source` dump still includes the 4000-`H` docstring.
- `if flag:` both branches when the test is not const-known (`os.environ.get`).
- `if len([])` Call / `if set()` / `if (1).conjugate()` Call / `if [len(x) for x in ['a']]` Call in elt / `T = type('T', (), {'x': 1})` Call.
- AugAssign `n = 1; n += -1` / `T.x += -1` (query matches honesty; list does not — do not fold AugAssign).
- Try that can run (list last-wins except).
- `assert False` / `raise ValueError` then `def parse`: honesty no name; list `kind=def`. Same family as Try. Do **not** exec. Do not claim list matches import failure.
- match without a static subject (`match os.name`).
- While: `while True: def parse; break` list miss while query live; `while False:` both miss. Do **not** exec While. Do not unroll.
- for-else after `break` (no break proof): honesty `feb-live`; list last-wins else.
- `for x in [0, 1]: if x: def parse` (For walks first item only; no unroll): honesty live; list miss. Do not unroll For.
- `for _ in range(1):` Call iterator (declared). Unknown Call currently walks body (`range(1)` accidental live; `range(0)` list `kind=def` while query has no name). Do not walk Call iterators.
- Format errors (`if f'{1:s}':` / `if f'{1!s:d}':` without else): honesty ValueError; list both because spec stays `_MISSING`. Do not claim list matches import failure.
- `T()` when the class body has `__init__`: Call stays `_MISSING` (both). Empty `def __init__(self): pass` then `t = T(); if t.x` honesty live; list last-wins `ei-dead`. `__init__` that zeros `x` then `if t.x: def parse` without else: query `has no name`; list `kind=def`. Do **not** exec `__init__`.
- `if __file__:` / `if __name__:` list last-wins else as dead while query is live. Scan-known, but injecting `__file__`/`__name__` is a new env seed, not this cut's object. Leave parked unless a later cut seeds them without executing the module.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` / Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'{1}':` / `if f'{1:d}':` / `if f'{1!s:s}':` / nested unpack `flag, (other,) = True, (True,)` / starred unpack `flag, *rest = True, True` / starred collections `if [*[1]]:` / For-body `for _ in [1]: def parse` / Attribute `if (1).real:` / class attr `if T.x:` / post-class `T.x = 0; if T.x:` / identity ListComp `if [x for x in [1]]:` / GeneratorExp-If `if (x for x in []):` / nonempty genexp-For `for _ in (x for x in [1]):` / SetComp `if {x for x in [1]}:` / DictComp / filtered ListComp / multi-generator `if [x for y in [[1]] for x in y]:` / no-arg `t = T(); if t.x:` / `if (lambda: 0):` skip; `t = T(); T.x = 0; if t.x` / `T.x, T.y = 0, 0` / `class U: y = T.x` / `del T.x; if T.x:` / `xs[0] = 0; if xs[0]` still last-wins both); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-12 made post-class `T.x = 0` / multi-gen / `f'{1!s:s}'` list match query. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded `T()`-copy-without-class-lookup + Attribute-assign-without-unpack + class-body-without-outer-env is the new ceiling:

- List last-wins `t = T(); T.x = 0; if t.x:` else as live while query is dead. `t = T(); T.y = 1; if t.y` else as dead while query is live. `t = T(); del T.x; if t.x: def parse` without else as `kind=def` while query has no name.
- List last-wins `T.x, T.y = 0, 0; if T.x:` / `for T.x in [0]: if T.x` else as live while query is dead.
- List last-wins `class T: x = 1; class U: y = T.x; if U.y` / `class T: if True: x = 1; if T.x` / `class T: def go(self): pass; if T.go` / `class U(T): pass; if U.x` else as dead while query is live.
- List `del T.x; if T.x: def parse` / `x = 1; del x; if x: def parse` without else as `kind=def` while query has no name.
- List last-wins `xs = [1]; xs[0] = 0; if xs[0]:` / `d[1] = 0` / `xs[:] = []` / `T.x[0] = 0` else as live while query is dead.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try / assert / raise that can run, match without a static subject, lambda **bind** vs list, AugAssign / Call in If tests, While, for-else after break, For first-item only, Call For-iter, `T()` with `__init__`, format-error JoinedStr stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List last-wins of remaining const-known instance-follows-class / unpack-attr / class-body-outer / Delete-miss If / Subscript assign are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list last-wins a const-dead `t = T(); T.x = 0; if t.x:` else / `T.x, T.y = 0, 0; if T.x:` else / `class U: y = T.x; if U.y` else as the bind, or that list-binds `del T.x; if T.x: def parse` while query has no name, or that list-binds `xs[0] = 0; if xs[0]:` else as live.

1. **Instance follows class namespace unless shadowed.** `class T: x = 1; t = T(); T.x = 0; if t.x:` orelse is live; list currently last-wins `cai-live` while query is dead. `t = T(); T.y = 1; if t.y` orelse is dead; list last-wins `icy-dead`. `t = T(); del T.x; if t.x: def parse` without else is not a list bind (query `has no name`; list currently `kind=def`). Keep instance setattr shadow (`t.x = 1; T.x = 0; if t.x` already MATCH) and two-instance independence (`t1.x = 0; if t2.x` already MATCH). Keep no-arg copy when nothing mutates the class after `T()` (`class T: x = 1; t = T(); if t.x` already MATCH). When the class body has `__init__`, Call stays `_MISSING` (do not exec). Do not fold `type(...)` Call.

2. **Attribute targets of unpack and For.** `T.x, T.y = 0, 0; if T.x:` orelse is live; list currently last-wins `ua-live`. `for T.x in [0]:` then `if T.x` orelse is live; list last-wins `fa-live`. `_bind_target` / For first-item bind should `_set_namespace_attr` when the target is Attribute on a Name already bound to a `SimpleNamespace`. Simple `T.x = 0` and `T.x = T.y = 0` already match; keep them. Do not fold AugAssign.

3. **Class body const env.** `class T: x = 1; class U: y = T.x; if U.y` orelse is dead; list currently last-wins `co2-dead`. Inner class env must see outer const names. `class T: if True: x = 1; if T.x` orelse is dead; walk const-known If inside ClassDef with the same polarity as module If. `class T: def go(self): return 0; if T.go` / `t = T(); if t.go` orelse is dead; store a truthy sentinel for FunctionDef / AsyncFunctionDef names (do not exec). `class T: x = 1; class U(T): pass; if U.x` orelse is dead; when a base is a Name bound to a `SimpleNamespace`, copy those const attrs. Do not exec metaclass, decorators, or `type(...)`.

4. **Delete then missing If is not a list bind.** `del T.x; if T.x: def parse` without else: query `has no name`; list currently `kind=def`. `x = 1; del x; if x: def parse` same (`del` Name currently does not pop env). Pop Name targets on Delete. After a known SimpleNamespace loses an attr, `if T.x` is an AttributeError: skip both branches (not `_MISSING` both). Unknown names stay both. Do not exec.

5. **Const Subscript / slice assign.** `xs = [1]; xs[0] = 0; if xs[0]:` orelse is live; list currently last-wins `sa-live`. `d = {1: 1}; d[1] = 0; if d[1]:` / `xs[:] = []; if xs:` / `class T: x = [1]; T.x[0] = 0; if T.x[0]:` same. Update the container already in env when the index/slice and value are const-known. Read subscript already matches; keep it. Do not exec Call. Do not fold AugAssign.

6. **Tests the current suite cannot see.** `t = T(); T.x = 0; if t.x` list is dead not `cai-live`; `t = T(); T.y = 1; if t.y` list is live; `T.x, T.y = 0, 0; if T.x` list is dead; `class U: y = T.x; if U.y` list is live; `del T.x; if T.x: def parse` without else is not a list bind; `xs[0] = 0; if xs[0]` list is dead; `if T.go` after a method list is live; `class T: x = 1; T.x = 0; if T.x` list is still dead; `t = T(); t.x = 0; if t.x` list is still dead; `if [x for y in [[1]] for x in y]` list is still live; `if f'{1!s:s}'` list is still live; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `for _ in [1]` / `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` / `if {x for x in [1]}` / `if [x for x in [1] if x]` / `t = T(); if t.x` after `class T: x = 1` / `if (lambda: 0)` / `for _ in (x for x in [1]):` list bind / `for _ in (x for x in []):` without else not a list bind / `if f'{1:d}'` list is live / `if [1][0]` / `if f'{1}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local TYPE_CHECKING still match (no regression).

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try / assert / raise that can run, match without a static subject, lambda **bind** vs list, While (do not exec), for-else after break (no break proof), For first-item only (do not unroll), Call For-iter `for _ in range(1):`, format-error JoinedStr `_MISSING`, `T()` with `__init__` `_MISSING` (do not exec `__init__`).

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, or list last-wins `class T: x = 1; T.x = 0; if T.x:` as live while query is dead, KILL.

---

MUTATE
