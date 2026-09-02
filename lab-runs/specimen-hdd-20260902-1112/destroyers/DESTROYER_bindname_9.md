# DESTROYER bindname 9

Date: 2026-09-02 18:37–18:52 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0553 worker=destroyer-bindname-9

Target (archive, post-MUTATE-9 const For-body, Attribute, class attr, ListComp identity, GeneratorExp always-truthy):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `5dc2944551764460327c06648af72002f94d1e83510d33744c8b6e09892bbc12` (57227 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-9 (`cli_sha256_after`, 82/82; worker `mutate-bindname-9` job-0552). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `69fbdd6 Record bindname mutate HEAD 1f07315.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `69fbdd6a42ecc37c668e639f777569016cfe2820`. Mutate-9 commit `1f07315f20ed156580b09c9a423a789c400d984b`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 82/82 OK (8.875s / 8.932s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. `DESTROYER_bindname_6.md` **MUTATE**. `DESTROYER_bindname_7.md` **MUTATE**. `DESTROYER_bindname_8.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-9 claimed: `for _ in [1]: def parse` is a list bind; empty `for _ in ():` is not; for-else still runs after a completing loop (no break proof); `if (1).real` live; `class T: x = 1; if T.x` live; `if [x for x in [1]]` live; GeneratorExp always truthy so `if (x for x in [])` live.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; list misses `for _ in [1]: def parse` while query live; list `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` dead while query live; THIN_WRAPPER of two greps. Those nine were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list last-wins of remaining const-known SetComp/DictComp / ListComp filter and const elt / GeneratorExp-as-For-iter / JoinedStr format-spec / `if (lambda: …)` / no-arg `t = T(); if t.x` / post-class `T.x = 0`. Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname9_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

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
| 7 | list misses `for _ in [1]: def parse` while query live | list source `for-live`; empty `for _ in ():` not a list bind | no |
| 8 | list `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` dead while query live | list source `ar-live` / `ca-live` / `co-live` / `ga-live` | no |
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

### Mutate-9 claimed const For / Attribute / T.x / ListComp / GeneratorExp still matches query

`for _ in [1]:` / `xs = [1]; for _ in xs:` / `for _ in [1]: if True:` / `for _ in (1,):` / `for _ in {1}:` / `for _ in [0]:` / `for x in [1]: if x:` list source is live. Completing `for _ in [1]: def parse else: def parse` list is `fe-else` (for-else still runs; no break proof). Empty `for _ in ():` / `for _ in []:` without else is not a list bind. Empty for-else list is `fee-else`.

`if (1).real:` / `if (1).numerator:` / `if True.real:` / `if (1+0j).real:` / `if not (1).imag:` list is live. `if (0).real:` / `if (1).imag:` without else is not a list bind. `class T: x = 1; if T.x:` / AnnAssign class attr / `class T: x = 1; y = x; if T.y:` list is live. `class T: x = 0; if T.x: def parse` without else is not a list bind.

`if [x for x in [1]]:` / `xs = [1]; if [x for x in xs]:` / `if [*[x for x in [1]]]:` list is live. `if [x for x in []]:` without else is not a list bind. `if (x for x in []):` / `if (x for x in [1]):` list is live. `if [1][0]` / `if f'{1}'` / `if f'{1!s}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` with else / tuple unpack / local TYPE_CHECKING / `if [[1]][0][0]:` / static-subject `match [1][0]` still match.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. Const For-body / Attribute / T.x / identity ListComp / GeneratorExp-as-If is the mutate-9 object. Remaining SetComp/DictComp / ListComp filter-elt / GeneratorExp-as-For / format-spec / if-lambda / instance attr list last-wins below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after mutate-9 const For/Attribute/ListComp/GeneratorExp-If, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if (x for x in []):` / `if [1][0]:` / `if f'{1}':` / `if [*[1]]:` / nested unpack / `if +1:` / `if 1 in [1]:` / `if 1 + 1` / `if []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-9. It is real. List last-wins of remaining const-known SetComp/DictComp / ListComp filter and const elt / GeneratorExp used as a For iterator / format-spec JoinedStr / `if (lambda: …)` / no-arg instance attr are not honesty leftover-identity.

---

## Implementation

### 1. SetComp / DictComp in If tests is still `_MISSING`

`static_const` folds identity `ListComp` (`elt` is the generator target Name, no `ifs`, one generator). `SetComp` / `DictComp` fall through to `_MISSING`, so the whole test is unknown.

```python
# setcomp.py
if {x for x in [1]}:
    def parse(x):
        return 'sc-live'
else:
    def parse(x):
        return 'sc-dead'
```

Honesty / query `'sc-live'`. List source is `sc-dead` (later line; both branches yielded). `if {x: x for x in [1]}:` same (`dc-dead`).

Dead-only without else:

```python
# setcomp0.py
if {x for x in []}:
    def parse(x):
        return 'sc0-dead-only'
```

Honesty `cannot import name 'parse'`. Query `setcomp0 has no name parse`. List `kind=def` `sc0-dead-only`. Empty dictcomp same.

A set/dict comprehension over a const iterable of constants is a collection. Not Call (`if set()` stays park). Not a tracer. Same family as mutate-9's identity ListComp close.

### 2. ListComp still only identity `elt` without filters

`if [x for x in [1] if x]:` has `ifs` → `_MISSING`. Honesty / query `'ci-live'`. List `ci-dead`. `if [x for x in [1] if False]:` without else: honesty no name; list `kind=def`.

`if [1 for _ in [1]]:` / `if [x + 0 for x in [1]]:` elt is Constant / BinOp, not the target Name → `_MISSING`. Honesty live. List last-wins dead.

`if [[y for y in [1]]]:` is a **List** whose one elt is a ListComp (identity inner folds to `[1]`); outer `[ [1] ]` is truthy. That MATCH is not the remaining hole. The hole is ListComp whose **elt** is not the target name, and ListComp with a const-known filter.

DESTROYER_8 asked: fold when the iterable is a const collection (or Name already in env) and the elt/filter is const-known in the comprehension target. Mutate-9 only did identity elt, no filters.

### 3. GeneratorExp `return True` leaks out of If tests into For iterators

Mutate-9: `static_const` of any `ast.GeneratorExp` returns `True` (the object is truthy). That is correct for `if (x for x in []):`. It is wrong as a For iterator.

```python
# genfor0.py
for _ in (x for x in []):
    def parse(x):
        return 'gf0-dead-only'
```

Honesty `cannot import name 'parse'` (empty generator, body never runs). Query `has no name`. List: GeneratorExp → `True`, `elif it:` walks the body, `kind=def` `gf0-dead-only`.

`for _ in (x for x in [1]): def parse` MATCH live by accident (bool `True` is truthy so the body is walked once). `if [y for y in (x for x in [1])]:` list last-wins `cgi-dead` (`list(True)` TypeError → ListComp `_MISSING`).

The leftover-identity fold is: a GeneratorExp is truthy **as an If test**. It is not the iterator value `True`. Do not build or iterate a generator. `static_const` should stay `_MISSING` for GeneratorExp; `test_polarity` / If should treat GeneratorExp as live. Not `if next(...)` Call. Not While.

### 4. `if (lambda: 0):` is always truthy, same as GeneratorExp

A function object is always truthy.

```python
# iflambda.py
if (lambda: 0):
    def parse(x):
        return 'il-live'
else:
    def parse(x):
        return 'il-dead'
```

Honesty / query `'il-live'`. List `il-dead`. Same family as mutate-9's GeneratorExp-If close. Do not call the lambda. `parse = lambda x: ('lam', x)` as a **bind** stays the declared lambda-vs-list park (`kind=def` `runs=lambda_.<lambda>`, source is the assignment; query does not print `('lam', 'z')`).

### 5. JoinedStr **format-spec** still last-wins dead

Mutate-8 folded `if f'{1}':` / `if f'{1!s}':` and left format-spec for a later cut (`if v.format_spec is not None: return _MISSING`).

```python
# fmtspec.py
if f'{1:d}':
    def parse(x):
        return 'fmt-live'
else:
    def parse(x):
        return 'fmt-dead'
```

Honesty / query `'fmt-live'`. List `fmt-dead`. A const format-spec string (`:d`) does not need to exec a format-spec callable. Not a tracer.

### 6. Same-file no-arg instance `t = T(); if t.x` and post-class `T.x = 0`

Mutate-9 stores a `SimpleNamespace` of const class-body Name assigns, so `if T.x` matches. `t = T()` is a Call, so `t` is `_MISSING` and `if t.x` last-wins.

```python
# instattr.py
class T:
    x = 1
t = T()
if t.x:
    def parse(x):
        return 'ia-live'
else:
    def parse(x):
        return 'ia-dead'
```

Honesty / query `'ia-live'`. List `ia-dead`. `class T: x = 0; t = T(); if t.x: def parse` without else: query `has no name`; list `kind=def`. DESTROYER_8 asked this when `T` is that class and the constructor has no args. Do not fold `T = type(...)` Call. Do not exec `__init__`.

Post-class Attribute assign is the same env hole:

```python
# classassign.py
class T:
    x = 1
T.x = 0
if T.x:
    def parse(x):
        return 'cas-live'
else:
    def parse(x):
        return 'cas-dead'
```

Honesty / query `'cas-dead'`. List `cas-live` (`T` still `SimpleNamespace(x=1)`). Const Attribute assign to a name already in env is leftover-identity. Not AugAssign (`n += -1` stays park).

### 7. Frozen / path-shadowable leftovers that match (not this MUTATE)

| leftover | honesty | CLI |
|----------|---------|-----|
| `importlib.util` / `importlib.machinery` | cannot bind (frozen) | `has no name` / list miss |
| `importlib.py` file / `importlib/` package / `importlib.abc` | leftover helper | leftover helper |
| `importlib.resources` / `metadata` | leftover helper | leftover helper |
| `json` / `json.decoder` / `pathlib` / `inspect` / `typing` / `dataclasses` / `warnings` / `contextlib` / `argparse` / `tempfile` / `subprocess` / `typing_extensions` | leftover helper | leftover helper |
| `enum` / `operator` / `functools` / `abc` / `types` / `re` / `collections` / `copyreg` / `site` / `zipimport` / `collections.abc` / `os.path` / `encodings.utf_8` | refuse | refuse |
| `tokenize.py` | leftover helper | leftover helper |

No frozen-submodule leftover-identity remaining that honesty and CLI split. Do not refuse leftover `importlib/` package that honesty binds.

### 8. Declared parks this cut (probed, not MUTATE)

- Nested defs (specimen-012 `test_a` inside `run()`): list `test_order.test_a`; `--from run_orders test_a` has no name.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign / `importlib.import_module` / `__dict__` / `itemgetter` / `[pkg_parse.parse][0]` / lambda wrap: honesty moved; `--from` follows; `--file` does not. Constant-getattr / getattr-with-default / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute already follow.
- FIFO `--file` remains `not a file` (0.038s).
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a **list** bind: query may follow; list miss.
- `parse = lambda ...` as the bind (query `kind=def` `runs=.<lambda>`, list last-wins the assignment text).
- Huge `source` dump still includes the 4000-`H` docstring.
- `if flag:` both branches when the test is not const-known (`os.environ.get`).
- `if len([])` Call / `if set()` / `if (1).conjugate()` Call.
- AugAssign `n = 1; n += -1`.
- Try that can run (list last-wins except).
- match without a static subject (`match os.name`).
- While: `while True: def parse; break` list miss while query live; `while False:` both miss. Do **not** exec While. Do not unroll.
- for-else after `break` (mutate-9: no break proof): honesty `feb-live`; list last-wins else.
- `for _ in range(1):` Call iterator (declared). Unknown Call currently walks body (`range(1)` accidental live; `range(0)` would lie). Do not walk Call iterators.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` / Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'{1}':` / nested unpack `flag, (other,) = True, (True,)` / starred unpack `flag, *rest = True, True` / starred collections `if [*[1]]:` / **For-body `for _ in [1]: def parse`** / **Attribute `if (1).real:`** / **class attr `if T.x:`** / **identity ListComp `if [x for x in [1]]:`** / **GeneratorExp-If `if (x for x in []):` skip; SetComp `if {x for x in [1]}:` / DictComp / ListComp with filter or const elt / GeneratorExp as For-iter `for _ in (x for x in []):` / format-spec `if f'{1:d}':` / `if (lambda: 0):` / `t = T(); if t.x:` still last-wins both**); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-9 made For-body / Attribute / T.x / identity ListComp / GeneratorExp-If list match query. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded ListComp-identity-without-SetComp + GeneratorExp-True-as-value + class-namespace-without-instance is the new ceiling:

- List last-wins `if {x for x in [1]}:` / `if {x: x for x in [1]}:` else as dead while query is live. `if {x for x in []}:` / `if {x: x for x in []}:` without else as `kind=def` while query has no name.
- List last-wins `if [x for x in [1] if x]:` / `if [1 for _ in [1]]:` / `if [x + 0 for x in [1]]:` else as dead while query is live. `if [x for x in [1] if False]:` without else as `kind=def` while query has no name.
- List `for _ in (x for x in []): def parse` as `kind=def` while query has no name (GeneratorExp `True` leaked into For). `if [y for y in (x for x in [1])]:` else last-wins dead.
- List last-wins `if (lambda: 0):` else as dead while query is live.
- List last-wins `if f'{1:d}':` else as dead while query is live.
- List last-wins `t = T(); if t.x:` else as dead while query is live. `t = T(); if t.x: def parse` without else as `kind=def` while query has no name (`class T: x = 0`).
- List last-wins `class T: x = 1; T.x = 0; if T.x:` else as live while query is dead.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try that can run, match without a static subject, lambda **bind** vs list, AugAssign / Call in If tests, While, for-else after break, Call For-iter stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List last-wins of remaining const-known SetComp/DictComp / ListComp filter-elt / GeneratorExp-as-For / format-spec / if-lambda / no-arg instance attr are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list last-wins a const-dead `if {x for x in [1]}:` else / `if [x for x in [1] if x]:` else / `if f'{1:d}':` else / `if (lambda: 0):` else / `t = T(); if t.x:` else as the bind, or that list-binds `for _ in (x for x in []): def parse` while query has no name.

1. **SetComp / DictComp of const iterables.** `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if {x for x in [1] if x}:` orelse is dead; list currently last-wins `sc-dead` / `dc-dead`. `if {x for x in []}:` / `if {x: x for x in []}:` without else is not a list bind (query `has no name`). Fold like identity ListComp when the iterable is a const collection (or Name already in env) and the elt/key/value/filter is const-known in the comprehension target. Do not exec Call in the elt.

2. **ListComp remaining filter and const-known elt.** `if [x for x in [1] if x]:` / `if [1 for _ in [1]]:` / `if [x + 0 for x in [1]]:` orelse is dead; list currently last-wins `ci-dead` / `cte-dead` / `be-dead`. `if [x for x in [1] if False]:` without else is not a list bind. Identity `if [x for x in [1]]:` already matches; keep it. Do not exec Call in the elt. Nested `if [[y for y in [1]]]:` already matches as a List of a folded ListComp; keep it.

3. **GeneratorExp is truthy only as an If test, not as a For iterator.** `if (x for x in []):` already matches (keep). `for _ in (x for x in []): def parse` currently list `kind=def` while query has no name because `static_const` returns `True` and For walks a truthy iter. `if [y for y in (x for x in [1])]:` list last-wins dead. Keep GeneratorExp as live in `test_polarity` / If. Do **not** return `True` from `static_const` as a value For/ListComp can iterate. Do not build or iterate a generator. Do not exec While.

4. **`if (lambda: …)` is truthy.** `if (lambda: 0):` / `if (lambda: 1):` orelse is dead; list currently last-wins `il-dead`. Any `ast.Lambda` as an If test is live (the object is truthy). Do not call the lambda. `parse = lambda ...` as the **bind** stays declared park.

5. **JoinedStr format-spec when the spec is const.** `if f'{1:d}':` orelse is dead; list currently last-wins `fmt-dead`. Fold `FormattedValue` when `format_spec` is a const string (or a JoinedStr that already folds) without calling a format-spec callable. Conversion `!s`/`!r`/`!a` already match; keep them.

6. **No-arg same-file instance and post-class const Attribute assign.** `class T: x = 1; t = T(); if t.x:` orelse is dead; list currently last-wins `ia-dead`. `class T: x = 0; t = T(); if t.x: def parse` without else is not a list bind. When `T` is a `SimpleNamespace` already in env and the Call has no args / no keywords, `t` is that namespace. `T.x = 0` after the class body: Attribute assign of a const onto a name already in env; `if T.x` currently list last-wins live while query is dead. Do not fold `type(...)` Call. Do not exec `__init__`. Do not fold AugAssign.

7. **Tests the current suite cannot see.** `if {x for x in [1]}` list is live not `sc-dead`; `if {x for x in []}:` without else list is not `kind=def`; `if {x: x for x in [1]}` list is live; `if [x for x in [1] if x]` list is live; `if [1 for _ in [1]]` list is live; `for _ in (x for x in []): def parse` list is not `kind=def`; `if (lambda: 0)` list is live not `il-dead`; `if f'{1:d}'` list is live not `fmt-dead`; `t = T(); if t.x` after `class T: x = 1` list is live; `T.x = 0; if T.x` list is dead; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `for _ in [1]` / `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` / `if [1][0]` / `if f'{1}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local TYPE_CHECKING still match (no regression).

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try that can run, match without a static subject, lambda **bind** vs list, While (do not exec), for-else after break (no break proof), Call For-iter `for _ in range(1):`.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, or list misses `for _ in [1]: def parse` while query is live, or list last-wins `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` as dead while query is live, KILL.

---

MUTATE
