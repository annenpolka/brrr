# DESTROYER bindname 8

Date: 2026-09-02 18:21–18:30 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0551 worker=destroyer-bindname-8

Target (archive, post-MUTATE-8 const Subscript/Slice, JoinedStr, nested/star unpack, starred collections):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `650d990f42e32e808600bbb81f1ea350467cea4770aee36e28ba44ad18e95944` (55153 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-8 (`cli_sha256_after`, 78/78; worker `mutate-bindname-8` job-0543). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `8496b3c Record bindname mutate HEAD 1a12a94.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `8496b3c85ef4ff781e3d25fb748f7a55e4dc6e55`. Mutate-8 commit `1a12a94f7f01e3aa9eb0fa3047ba98c67c034cd8`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 78/78 OK (7.562s / 7.592s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. `DESTROYER_bindname_6.md` **MUTATE**. `DESTROYER_bindname_7.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-8 claimed: Subscript/Slice `if [1][0]` live / `if [0][0]` without else not a list bind; JoinedStr `if f'{1}'` live / `if f''` not a list bind; nested/star unpack `flag, (other,) = True, (True,)` / `flag, *rest = True, True` / `pair = True, True; flag, other = pair`; starred collections `if [*[1]]` live / `if [*[]]` not a list bind.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; list last-wins `if [1][0]` / `if f'{1}'` / `if [*[1]]` as dead while query live; nested/star unpack list dead while query live; THIN_WRAPPER of two greps. Those nine were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list last-wins of remaining const-known For-body module-level `def` / Attribute of constants (`if (1).real:`) / class attr (`if T.x:`) / comprehensions / GeneratorExp. Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname8_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

`rg import_module` / `_bindname_` on the CLI: no matches. Load path is `importlib.util.spec_from_file_location` under the logical name after `drop_foreign_cache`. `unshadowable_reason` is builtin / `_imp.is_frozen(modname)` **full name** then frozen top / `interpreter_preimported()` (subprocess `sys.modules` listing, cwd `/`, not `import_module` of the query).

| # | condition | host | fire? |
|---|-----------|------|-------|
| 1 | leftover `ast.py` reports Cellar / `lib/python` `ast.parse` | leftover body `('leftover-ast', x)`, `file ast.py`, no Cellar | no |
| 2 | load uses `import_module` against `sys.modules` | `rg import_module` empty; `spec_from_file_location` | no |
| 3 | `also` executes siblings (`sys.exit` in `killer.py` hijacks `--from keep`) | rc=0 body `'kept'`; `SIDE` does not exist | no |
| 4 | leftover `io.py` / `sys.py` is `kind=def` while honesty ImportError | `io` / `encodings` / `os` / `sys` / `builtins` all `has no name`; no leftover body | no |
| 5 | leftover `importlib.util` is `kind=def` while honesty cannot bind | honesty cannot bind; CLI `has no name`; list miss; `importlib.machinery` same | no |
| 6 | leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper | both `kind=def` leftover helper, no Cellar | no |
| 7 | list last-wins `if [1][0]` / `if f'{1}'` / `if [*[1]]` as dead while query live | list source `subl-live` / `ff-live` / `sn-live`; `if [0][0]:` / `if f'':` / `if [*[]]:` without else not a list bind | no |
| 8 | nested/star unpack list dead while query live | list source `nu-live` / `su-live` / `tv-live` | no |
| 9 | THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join | naive `inspect.getsource(ast.parse)` from `/tmp` is Cellar; bindname leftover + `also pkg_parse.parse` | no |

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

No `Cellar`, no `lib/python`. List mode `count 2` leftover + moved. After `isolated_import`, `sys.modules['ast']` is Homebrew 3.14 `ast.py` again (`restored True`). Isolate claim holds for the ungated fixture.

### `also` does not execute siblings

`keep.py` leftover def, `killer.py` `sys.exit(9)` plus `def parse`, `side.py` writes `SIDE`, `osexit.py` `os._exit(11)`. `--from keep parse` rc=0, body `'kept'`, `also killer.parse` / `also osexit.parse` / `also side.parse`, `SIDE` does not exist. `aaa_patch.py` does not rewrite `--from pkg_util`: `kind=def`, source still `legacy`.

### Leftover `sys.py` / `io.py` / `encodings.py` / `os.py` is not `kind=def`

Honesty `from sys import parse` is ImportError. bindname `--from sys parse` rc≠0, stderr `sys has no name parse`, no leftover-sys body. `io` / `encodings` / `os` / `builtins` same. Mutate-5/6 refuse holds.

### Leftover frozen submodule `importlib.util` is not `kind=def`

Honesty `from importlib.util import parse` cannot bind (frozen). bindname `--from importlib.util parse` rc≠0, `importlib.util has no name parse`, no leftover-util body. `importlib.machinery` same (MATCH refuse). Mutate-6 item 1 holds.

### Leftover `importlib.py` file / leftover `importlib.abc` / leftover `importlib/` package still helper

Honesty leftover-importlib-file / leftover-importlib-abc / leftover-importlib-pkg. bindname `kind=def`, `file importlib.py` / `importlib/abc.py` / `importlib/__init__.py`, no Cellar. Honor KILL 6 does not fire. Leftover `tokenize.py` still leftover helper. Leftover `json.py` / `pathlib.py` / `inspect.py` / `typing.py` / `dataclasses.py` / `warnings.py` / `contextlib.py` / `argparse.py` / `tempfile.py` / `subprocess.py` / `typing_extensions.py` / `json.decoder` / `importlib.resources` / `importlib.metadata` MATCH leftover helper. Preimported / frozen `enum` / `operator` / `functools` / `abc` / `types` / `re` / `collections` / `copyreg` / `site` / `zipimport` / `collections.abc` / `os.path` / `encodings.utf_8` MATCH refuse.

### Mutate-8 claimed const-env If still matches query

`if [1][0]:` / `if {0: 1}[0]:` / `if (1,)[0]:` / `if 'x'[0]:` / `if b'a'[0]:` / `if [1, 2][-1]:` / `if [1][:1]:` / `if [0, 1][1:2]:` / `flag = [True][0]; if flag:` / walrus / BoolOp / Compare / `if 1 in [1][:]:` / `X = 1; if [X][0]:` list source is live. `if [0][0]:` / `if [1][1:]:` without else is not a list bind. `if f'x':` / `if f'{1}':` / `if f'{1}' in f'{1}':` / `if f'{1!s}':` list is live. `if f'':` without else is not a list bind. `if [*[1]]:` / `if {**{0: 1}}:` / `if (*[1],):` list is live. `if [*[]]:` / `if {**{}}:` / `if {*[]}:` without else is not a list bind. `flag, (other,) = True, (True,)` / `flag, *rest = True, True` / `flag, *rest = False, True; if rest:` / `*rest, flag = False, True` / `pair = True, True; flag, other = pair` list is live. `if +1` / `if ~0` / `if 1 in [1]` / `if 1 + 1` / `if []:` with else / tuple unpack / local TYPE_CHECKING / IfExp / `if +True` / `if not not 1` / `if ...:` still match. Nested Subscript `if [[1]][0][0]:` list is live. Static-subject match `match [1][0]: case 1` / `match 1: case 1` list is live (Subscript fold is now in the const env that `iter_match_bind_nodes` already consults).

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. Const Subscript / JoinedStr / nested-star unpack / starred collections is the mutate-8 object. Remaining For-body / Attribute / class attr / comprehension / GeneratorExp list last-wins below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after mutate-8 const Subscript/JoinedStr/unpack/starred collections, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`if [1][0]:` / `if f'{1}':` / `if [*[1]]:` / nested unpack / `pair = True, True; flag, other = pair` / `if +1:` / `if 1 in [1]:` / `if 1 + 1` / `if []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-8. It is real. List last-wins of remaining const-known For-body / Attribute of constants / class attr / comprehensions / GeneratorExp are not honesty leftover-identity.

---

## Implementation

### 1. List last-binding still misses For-body module-level `def` that query binds

Mutate-8: Subscript/Slice, JoinedStr, nested/star unpack, starred collections. `iter_bind_nodes` walks If / Try / With / Match. It never walks `ast.For` / `ast.While`. A For node is yielded as a statement; the inner `FunctionDef` is not a list bind.

```python
# forlive.py
for _ in [1]:
    def parse(x):
        return 'for-live'
```

Honesty / `--from forlive parse`: `'for-live'` (`kind=def`, `file forlive.py`). List has no `forlive.parse` row (miss while query live). Same family as mutate-7's `if +1` close, except the scanner never enters the loop body.

Same lie: `xs = [1]; for _ in xs: def parse` (const sequence already in env); `for _ in [1]: if True: def parse`. `while True: def parse; break` same (list miss, query live).

Dead-only without a running body is already honest:

```python
# forempty.py
for _ in []:
    def parse(x):
        return 'for-dead-only'
```

Honesty `cannot import name 'parse'`. Query `forempty has no name parse`. List miss. `while False: def parse` same. The lie is the **live** const iterator, not the empty one.

Do **not** walk `for _ in range(1):` (Call, declared park). Const List/Tuple/Set already in `static_const` / const env is the leftover-identity hole. Not a tracer.

### 2. Attribute of constants is not in the const env that Constant ints now are

`static_const` handles `ast.Attribute` only when `attr == "TYPE_CHECKING"` (False). Every other Attribute is `_MISSING`.

```python
# attrreal.py
if (1).real:
    def parse(x):
        return 'ar-live'
else:
    def parse(x):
        return 'ar-dead'
```

Honesty / query `'ar-live'`. List source is `ar-dead` (later line; both branches yielded). Same family as mutate-8's `if [1][0]` close.

Same lie: `if (1).numerator:` / `if True.real:` / `if (1+0j).real:`. Dead-only without else:

```python
# attr0.py
if (0).real:
    def parse(x):
        return 'a0-dead-only'
```

Honesty `cannot import name 'parse'`. Query `attr0 has no name parse`. List `kind=def` `a0-dead-only`. `if (1).imag:` (0.0) same.

Numeric data attrs (`real` / `imag` / `numerator` / `denominator`) of a const int/float/complex/bool are constants. Not Call (`(1).conjugate()` / `if len([])` stay park). Not `__class__` / arbitrary getattr.

### 3. Same-file class attr `T.x` is not in the const env

```python
# classattr.py
class T:
    x = 1
if T.x:
    def parse(x):
        return 'ca-live'
else:
    def parse(x):
        return 'ca-dead'
```

Honesty / query `'ca-live'`. List `ca-dead`. `class T: x = 0` then `if T.x: def parse` without else: query `has no name`; list `kind=def`. Instance of that class with no constructor args (`t = T(); if t.x:`) same last-wins lie.

This is same-file const class body, not an import tracer. Do not fold `T = type(...)` Call.

### 4. Comprehensions in If tests

`static_const` List/Tuple/Set/Dict folds literals (including Starred after mutate-8). ListComp / SetComp / DictComp is `_MISSING`, so the whole test is unknown.

```python
# compone.py
if [x for x in [1]]:
    def parse(x):
        return 'co-live'
else:
    def parse(x):
        return 'co-dead'
```

Honesty / query `'co-live'`. List `co-dead`. `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `if [[y for y in [1]]]:` same.

Dead-only without else:

```python
# compempty.py
if [x for x in []]:
    def parse(x):
        return 'ce-dead-only'
```

Honesty no name. Query `has no name`. List `kind=def`. Empty set/dict comprehensions same.

A comprehension over a const iterable of constants (elt Name or Constant; filter const-known in the comprehension target) is a collection. Not Call (`if list([])` stays park). Not a tracer.

### 5. GeneratorExp in If tests is always truthy

A generator object is always truthy, even over an empty iterator.

```python
# genalways.py
if (x for x in []):
    def parse(x):
        return 'ga-live'
else:
    def parse(x):
        return 'ga-dead'
```

Honesty / query `'ga-live'`. List `ga-dead`. `if (x for x in [1]):` same.

`static_const` can return `True` for any `ast.GeneratorExp` without evaluating the iterator (the object is truthy; do not build a live generator). That is the leftover-identity fold. Not `if next(...)` Call.

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

### 7. `--file` remaining alias shapes (declared park this cut)

`parse = pkg_parse.__dict__['parse']` / `vars(pkg_parse)['parse']` / `operator.attrgetter('parse')(pkg_parse)` / dynamic `getattr(pkg_parse, name)` / IfExp assign / `importlib.import_module` / `__dict__.get` / `itemgetter` / `[pkg_parse.parse][0]`: honesty moved body; `--from` follows; `--file` does not. Declared. Constant-getattr / getattr-with-default / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute already follow. FIFO `--file` remains `not a file` (0.037s). Do not grow a full alias tracer this cut.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` / Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'{1}':` / nested unpack `flag, (other,) = True, (True,)` / starred unpack `flag, *rest = True, True` / starred collections `if [*[1]]:` skip; **For-body `for _ in [1]: def parse` still a list miss; Attribute `if (1).real:` / class attr `if T.x:` / ListComp `if [x for x in [1]]:` / GeneratorExp `if (x for x in []):` still last-wins both**); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-8 made Subscript/JoinedStr/nested-star unpack/starred collections list match query. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded If-without-For + constants-without-Attribute + collections-without-comprehension is the new ceiling:

- List miss `for _ in [1]: def parse` / `xs = [1]; for _ in xs: def parse` / `while True: def parse; break` while query is live.
- List last-wins `if (1).real:` else / `if (1).numerator:` else / `if True.real:` else as dead while query is live.
- List `if (0).real:` / `if (1).imag:` without else as `kind=def` while query has no name.
- List last-wins `class T: x = 1; if T.x:` else / `t = T(); if t.x:` else as dead while query is live. `class T: x = 0; if T.x: def parse` without else as `kind=def` while query has no name.
- List last-wins `if [x for x in [1]]:` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` else as dead while query is live. `if [x for x in []]:` without else as `kind=def` while query has no name.
- List last-wins `if (x for x in []):` else as dead while query is live (generator objects are truthy).
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try that can run, match without a static subject, lambda vs list, AugAssign / Call in If tests stay as declared.
- JoinedStr **format-spec** (`if f'{1:d}':`) still last-wins dead — remaining after this cut (mutate-8 said do not exec format-spec callables; not this mutate's required change; not a tracer).

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List last-wins of remaining const-known For-body / Attribute of constants / class attr / comprehensions / GeneratorExp are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a scanner that list-misses a live `for _ in [1]: def parse`, or a calculator that list last-wins a const-dead `if (1).real:` else / `if T.x:` else / `if [x for x in [1]]:` else / `if (x for x in []):` else as the bind.

1. **List last-binding of const-known For / While bodies matches query.** `for _ in [1]: def parse` currently list-misses while `--from` is live. Const sequence already in env (`xs = [1]; for _ in xs:`) and nested live If inside that For same. `while True: def parse; break` same (const-true test; body runs once before break — walking the body once is enough; do not unroll). `for _ in []:` / `while False:` without a running body stay not a list bind (already match). Do **not** walk `for _ in range(1):` / other Call iterators (declared Call park).

2. **Attribute of constants.** `if (1).real:` / `if (1).numerator:` / `if True.real:` / `if (1+0j).real:` orelse is dead; list currently last-wins `ar-dead`. `if (0).real:` / `if (1).imag:` without else is not a list bind (query `has no name`). Fold `real` / `imag` / `numerator` / `denominator` of a const int/float/complex/bool. Do not fold Call methods (`conjugate`) or arbitrary attrs.

3. **Same-file class attr `T.x`.** `class T: x = 1; if T.x:` orelse is dead; list currently last-wins `ca-dead`. `class T: x = 0; if T.x: def parse` without else is not a list bind. `t = T(); if t.x:` same when `T` is that class and the constructor has no args. Const class-body Name assigns only. Do not fold `type(...)` Call.

4. **Comprehensions of const iterables.** `if [x for x in [1]]:` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` orelse is dead; list currently last-wins `co-dead`. `if [x for x in []]:` / `if {x for x in []}:` / `if {x: x for x in []}:` without else is not a list bind. Fold ListComp/SetComp/DictComp when the iterable is a const collection (or Name already in env) and the elt/filter is const-known in the comprehension target. Do not exec Call in the elt.

5. **GeneratorExp is truthy.** `if (x for x in []):` / `if (x for x in [1]):` orelse is dead; list currently last-wins `ga-dead`. Any `ast.GeneratorExp` as an If test is live (the object is truthy). Do not build or iterate a generator.

6. **Tests the current suite cannot see.** `for _ in [1]: def parse` list is live not miss; `xs = [1]; for _ in xs: def parse` list is live; `if (1).real` list is live not `ar-dead`; `if (0).real: def parse` without else list is not `kind=def`; `if T.x` after `class T: x = 1` list is live; `if [x for x in [1]]` list is live; `if [x for x in []]:` without else list is not `kind=def`; `if (x for x in [])` list is live; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `if [1][0]` / `if f'{1}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local TYPE_CHECKING still match (no regression).

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try that can run, match without a static subject, lambda query vs list.

Leave for a later cut (not this mutate, not parks): JoinedStr **format-spec** (`if f'{1:d}':` still last-wins `fmt-dead` while query is live; mutate-8 said do not exec format-spec callables).

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, KILL.

---

MUTATE
