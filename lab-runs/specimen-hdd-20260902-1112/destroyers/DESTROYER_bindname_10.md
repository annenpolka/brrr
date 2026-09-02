# DESTROYER bindname 10

Date: 2026-09-02 18:53–19:03 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0567 worker=destroyer-bindname-10

Target (archive, post-MUTATE-10 genexp sentinel, SetComp/DictComp/filter ListComp, instance Call, if-lambda):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `0bddedf8657f0dbc4eed4fe26f39676228bd31fc6ea2cb1be2a711d37c901570` (59886 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-10 (`cli_sha256_after`, 86/86; worker `mutate-bindname-10` job-0561). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `b4f03d1 Record bindname mutate HEAD 14790cb.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `b4f03d1155275eeb5bd0e25cb1ece8ede8ebf4e7`. Mutate-10 commit `14790cb271d2af481f17c0f1f595308db44941aa`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 86/86 OK (9.504s / 9.662s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. `DESTROYER_bindname_6.md` **MUTATE**. `DESTROYER_bindname_7.md` **MUTATE**. `DESTROYER_bindname_8.md` **MUTATE**. `DESTROYER_bindname_9.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-10 claimed: GeneratorExp is a truthy empty-iterable sentinel (`if (x for x in [])` still live; `for _ in (x for x in []): def parse` is NOT a list bind); SetComp/DictComp/filtered ListComp match query; `t = T(); if t.x` live; `if (lambda: 0)` live; `if len([])` Call with args still both.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; `for _ in (x for x in []): def parse` is list `kind=def` while honesty has no name; list SetComp/DictComp/filtered ListComp dead while query live; THIN_WRAPPER of two greps. Those nine were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list last-wins of remaining const-known JoinedStr format-spec / nonempty GeneratorExp as a sequence (For / comprehension / Starred) / post-class Attribute assign / no-arg `T()` that ignores `__init__` / multi-generator comprehensions. Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname10_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

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
| 7 | `for _ in (x for x in []): def parse` is list `kind=def` while honesty has no name | query `has no name`; list has no `genfor0.parse` (only `pkg_parse.parse`) | no |
| 8 | list SetComp / DictComp / filtered ListComp dead while query live | list source `sc-live` / `dc-live` / `ci-live` / `filt-live` | no |
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

### Mutate-10 claimed genexp-If / SetComp / DictComp / filter / instance / lambda still matches query

`if (x for x in []):` / `if (x for x in [1]):` list source is live. `for _ in (x for x in []): def parse` without else is **not** a list bind (query `has no name`). `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if {x: 1 for x in [1]}:` / `if [x for x in [1] if x]:` / `if [x for x in [1, 0] if x]:` / `if [1 for _ in [1]]:` / `if [x + 0 for x in [1]]:` / `if {x for x in [1] if x}:` / `if {x: x for x in [1] if x}:` list is live. Empty `if {x for x in []}:` / `if {x: x for x in []}:` / `if [x for x in [1] if False]:` without else is not a list bind. `class T: x = 1; t = T(); if t.x:` list is live. `class T: x = 0; t = T(); if t.x: def parse` without else is not a list bind. `if (lambda: 0):` / `if (lambda: 1):` list is live. Nested `if (x for y in [] for x in y):` still live (generator object is truthy).

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if [1][0]` / `if f'{1}'` / `if f'{1!s}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` with else / tuple unpack / local TYPE_CHECKING / `if [[1]][0][0]:` / static-subject `match [1][0]` still match.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. Genexp-If / SetComp / DictComp / filter ListComp / no-arg instance / if-lambda is the mutate-10 object. Remaining format-spec / nonempty genexp-as-sequence / Attribute assign / `T()` vs `__init__` / multi-gen below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after mutate-10 genexp-sentinel / SetComp / instance / lambda, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if (x for x in []):` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `t = T(); if t.x:` / `if (lambda: 0):` / `if [1][0]:` / `if f'{1}':` / `if [*[1]]:` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-10. It is real. List last-wins of remaining const-known format-spec JoinedStr / nonempty GeneratorExp used as a For/comprehension/Starred iterator / post-class Attribute assign / no-arg `T()` that copies a class namespace while honesty runs `__init__` / multi-generator comprehensions are not honesty leftover-identity.

---

## Implementation

### 1. JoinedStr **format-spec** still last-wins dead

Mutate-8 folded `if f'{1}':` / `if f'{1!s}':` and left format-spec (`if v.format_spec is not None: return _MISSING`). Mutate-10 did not close it.

```python
# fmtspec.py
if f'{1:d}':
    def parse(x):
        return 'fmt-live'
else:
    def parse(x):
        return 'fmt-dead'
```

Honesty / query `'fmt-live'`. List source is `fmt-dead` (later line; both branches yielded). `if f'{1:02d}':` same (`fw-dead`). `if f'{1:{1}}':` nested spec same (`fn-dead`). `if (s := f'{1:d}'):` walrus of the same hole (`wf-dead`).

A const format-spec string (`:d` / `:02d`) does not need to exec a format-spec callable. Conversion `!s`/`!r`/`!a` already match; keep them. `if f'{1:s}':` without else is a ValueError at honesty (import failed); list currently both because spec is `_MISSING`. After folding, format errors stay `_MISSING` (do not exec; do not claim list matches import failure).

### 2. GeneratorExp sentinel is empty for **every** iterator use

Mutate-10: `static_const` of any `ast.GeneratorExp` returns `_GENEXP`, a truthy empty iterable. That is correct for `if (x for x in []):` (live) and `for _ in (x for x in []): def parse` (not a list bind). It is wrong as a nonempty sequence.

```python
# genfor1.py
for _ in (x for x in [1]):
    def parse(x):
        return 'gf1-live'
```

Honesty / query `'gf1-live'`. List: `_GENEXP` iterates empty, no `genfor1.parse` bind.

```python
# assignedgen.py
xs = (x for x in [1])
for _ in xs:
    def parse(x):
        return 'ag-live'
```

Same miss (assigned name is the empty sentinel).

```python
# compgeniter.py
if [y for y in (x for x in [1])]:
    def parse(x):
        return 'cgi-live'
else:
    def parse(x):
        return 'cgi-dead'
```

Honesty / query `'cgi-live'`. List last-wins `cgi-dead` (`list(_GENEXP)` is `[]`, falsy). `if {y for y in (x for x in [1])}:` same. `if [*(x for x in [1])]:` / `if (*(x for x in [1]),):` Starred of the sentinel last-wins dead.

The leftover-identity fold is: a GeneratorExp is **always truthy as an If test**. As a For / comprehension / Starred iterator it is the const-folded sequence of its elts, not the empty sentinel. Do not replace `_GENEXP` with a tuple (empty tuple is falsy and would Honor-KILL `if (x for x in []):`). Do not return `_MISSING` for For of a const empty genexp (that walks the body → Honor KILL 7). Do not build or iterate a generator. Do not exec While. Unevaluable inner (`for _ in (x for x in range(1)):`) stays the declared Call-For park.

### 3. Post-class / instance Attribute assign is still the class-body snapshot

Mutate-9/10 store a `SimpleNamespace` of const class-body Name assigns, so `if T.x` and `t = T(); if t.x` match when nothing mutates after the class. `T.x = 0` is an Attribute target; `update_const_env` returns without writing.

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

Honesty / query `'cas-dead'`. List `cas-live` (`T` still `SimpleNamespace(x=1)`). Inverse `class T: x = 0; T.x = 1; if T.x` list last-wins `cal-dead` while query is live. New attr `T.y = 1; if T.y` list last-wins `cna-dead`.

```python
# instassign.py
class T:
    x = 1
t = T()
t.x = 0
if t.x:
    def parse(x):
        return 'ias-live'
else:
    def parse(x):
        return 'ias-dead'
```

Honesty / query `'ias-dead'`. List `ias-live` (copy of `x=1` never updated). Const Attribute assign onto a name already bound to a `SimpleNamespace` is leftover-identity. Not AugAssign (`n += -1` stays park). Not `T = type(...)` Call (declared).

### 4. No-arg `T()` copies the class namespace and ignores `__init__`

Mutate-10: `Call` with no args / no keywords of a `SimpleNamespace` copies that namespace. Class-body `FunctionDef` is not stored, so honesty `__init__` is invisible.

```python
# initzero.py
class T:
    x = 1
    def __init__(self):
        self.x = 0
t = T()
if t.x:
    def parse(x):
        return 'iz-dead-only'
```

Honesty `cannot import name 'parse'`. Query `has no name`. List `kind=def` `iz-dead-only`. Inverse `class T: x = 0; def __init__(self): self.x = 1; t = T(); if t.x` honesty live; list last-wins `izl-dead`.

Do **not** exec `__init__`. When the ClassDef body contains `FunctionDef` / `AsyncFunctionDef`, no-arg Call stays `_MISSING` (both). Keep the mutate-10 copy for const-only class namespaces (`class T: x = 1; t = T(); if t.x` already matches).

### 5. Multi-generator comprehensions still `_MISSING`

`_eval_comprehension` / `_eval_comprehension_pairs` require `len(generators) == 1`. Nested `if [[y for y in [1]]]:` already matches as a List of a folded ListComp; that is not this hole.

```python
# multigen.py
if [x for y in [[1]] for x in y]:
    def parse(x):
        return 'mg-live'
else:
    def parse(x):
        return 'mg-dead'
```

Honesty / query `'mg-live'`. List `mg-dead`. SetComp / DictComp of two generators same. Single-gen `if {1 for _ in [1]}:` / `if {x + 0 for x in [1]}:` / `if {k: v for k, v in [(1, 2)]}:` / `xs = [1]; if {x for x in xs}:` already MATCH. Fold nested generators of const iterables. Do not exec Call in the elt.

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
- FIFO `--file` remains `not a file` (0.038s).
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a **list** bind: query may follow; list miss.
- `parse = lambda ...` as the bind (query `kind=def` `runs=.<lambda>`, source is the assignment; query does not print `('lam', 'z')`).
- Huge `source` dump still includes the 4000-`H` docstring.
- `if flag:` both branches when the test is not const-known (`os.environ.get`).
- `if len([])` Call / `if set()` / `if (1).conjugate()` Call / `if [len(x) for x in ['a']]` Call in elt / `T = type('T', (), {'x': 1})` Call.
- AugAssign `n = 1; n += -1`.
- Try that can run (list last-wins except).
- match without a static subject (`match os.name`).
- While: `while True: def parse; break` list miss while query live; `while False:` both miss. Do **not** exec While. Do not unroll.
- for-else after `break` (no break proof): honesty `feb-live`; list last-wins else.
- `for _ in range(1):` Call iterator (declared). Unknown Call currently walks body (`range(1)` accidental live; `range(0)` list `kind=def` while query has no name). Do not walk Call iterators.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` / Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'{1}':` / nested unpack `flag, (other,) = True, (True,)` / starred unpack `flag, *rest = True, True` / starred collections `if [*[1]]:` / For-body `for _ in [1]: def parse` / Attribute `if (1).real:` / class attr `if T.x:` / identity ListComp `if [x for x in [1]]:` / GeneratorExp-If `if (x for x in []):` / SetComp `if {x for x in [1]}:` / DictComp / filtered ListComp / no-arg `t = T(); if t.x:` / `if (lambda: 0):` skip; format-spec `if f'{1:d}':` / nonempty genexp-For `for _ in (x for x in [1]):` / ListComp over genexp / post-class `T.x = 0` / `T()` with `__init__` / multi-generator `if [x for y in [[1]] for x in y]:` still last-wins both); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-10 made empty genexp-For not a list bind and SetComp/DictComp/filter/instance/if-lambda list match query. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded truthy-empty-genexp-as-every-iterator + format-spec `_MISSING` + class-namespace-without-Attribute-assign + `T()` without `__init__` is the new ceiling:

- List last-wins `if f'{1:d}':` / `if f'{1:02d}':` / `if f'{1:{1}}':` else as dead while query is live.
- List `for _ in (x for x in [1]): def parse` as miss while query is live. `xs = (x for x in [1]); for _ in xs:` same. `if [y for y in (x for x in [1])]:` / `if {y for y in (x for x in [1])}:` / `if [*(x for x in [1])]:` else last-wins dead.
- List last-wins `class T: x = 1; T.x = 0; if T.x:` else as live while query is dead. Inverse `T.x = 1` after `x = 0` else as dead while query is live. `t = T(); t.x = 0; if t.x` else as live while query is dead.
- List `class T: x = 1; def __init__(self): self.x = 0; t = T(); if t.x: def parse` without else as `kind=def` while query has no name. Inverse `__init__` sets 1 after class `x = 0` else as dead while query is live.
- List last-wins `if [x for y in [[1]] for x in y]:` / SetComp / DictComp else as dead while query is live.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try that can run, match without a static subject, lambda **bind** vs list, AugAssign / Call in If tests, While, for-else after break, Call For-iter stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List last-wins of remaining const-known format-spec / nonempty genexp-as-sequence / Attribute assign / `T()` vs `__init__` / multi-gen are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list last-wins a const-dead `if f'{1:d}':` else / `if [y for y in (x for x in [1])]:` else / `class T: x = 1; T.x = 0; if T.x:` else as the bind, or that list-misses `for _ in (x for x in [1]): def parse` while query is live, or that list-binds `t = T(); if t.x` while honesty `__init__` left no name.

1. **JoinedStr format-spec when the spec is const.** `if f'{1:d}':` / `if f'{1:02d}':` / `if f'{1:{1}}':` / `if (s := f'{1:d}'):` orelse is dead; list currently last-wins `fmt-dead` / `fw-dead` / `fn-dead` / `wf-dead`. Fold `FormattedValue` when `format_spec` is a const string (or a JoinedStr that already folds) without calling a format-spec callable. Conversion `!s`/`!r`/`!a` already match; keep them. Format errors (`f'{1:s}'`) stay `_MISSING`. Do not exec.

2. **GeneratorExp is truthy as an If test and a const sequence as an iterator.** Keep `if (x for x in []):` live. Keep `for _ in (x for x in []): def parse` not a list bind. `for _ in (x for x in [1]): def parse` currently list miss while query is live because `_GENEXP` iterates empty. `xs = (x for x in [1]); for _ in xs:` same. `if [y for y in (x for x in [1])]:` / `if {y for y in (x for x in [1])}:` / `if [*(x for x in [1])]:` / `if (*(x for x in [1]),):` orelse last-wins dead. Fold GeneratorExp to a **always-truthy** sequence of const-known elts for For / comprehension / Starred. Do **not** return a Python tuple (empty tuple is falsy → Honor KILL `if (x for x in []):`). Do **not** return `_MISSING` for For of a const empty genexp (walks body → Honor KILL 7). Do not build or iterate a generator. Do not exec While. Unevaluable inner Call stays the declared Call-For park.

3. **Const Attribute assign onto a name already in env.** `class T: x = 1; T.x = 0; if T.x:` orelse is live; list currently last-wins `cas-live` while query is dead. Inverse `T.x = 1` after class `x = 0` orelse is dead; list last-wins `cal-dead`. `T.y = 1; if T.y` orelse is dead. `t = T(); t.x = 0; if t.x` orelse is live while query is dead. Attribute assign of a const onto a `SimpleNamespace` already in env. `t = T()` is already a copy (mutate-10); setattr on `T` must not rewrite that copy. Do not fold `type(...)` Call. Do not fold AugAssign.

4. **No-arg `T()` when the class body has `FunctionDef`.** `class T: x = 1; def __init__(self): self.x = 0; t = T(); if t.x: def parse` without else is not a list bind (query `has no name`; list currently `kind=def`). Inverse `__init__` sets 1 after class `x = 0` orelse is dead; list last-wins `izl-dead`. When `T` is a const-only `SimpleNamespace`, keep the mutate-10 copy. When the ClassDef body contains `FunctionDef` / `AsyncFunctionDef`, no-arg Call stays `_MISSING` (both). Do not exec `__init__`.

5. **Multi-generator ListComp / SetComp / DictComp of const iterables.** `if [x for y in [[1]] for x in y]:` / `if {x for y in [[1]] for x in y}:` / `if {x: 1 for y in [[1]] for x in y}:` orelse is dead; list currently last-wins `mg-dead` / `ms2-dead` / `md-dead`. Fold nested generators like single-gen `_eval_comprehension` when each iterable/elt/filter is const-known. Single-gen SetComp const/binop elt and dict unpack already match; keep them. Do not exec Call in the elt.

6. **Tests the current suite cannot see.** `if f'{1:d}'` list is live not `fmt-dead`; `for _ in (x for x in [1]): def parse` list is `kind=def` not miss; `if [y for y in (x for x in [1])]` list is live; `T.x = 0; if T.x` list is dead not `cas-live`; `t = T(); t.x = 0; if t.x` list is dead; `class T` with `__init__` zeroing `x` then `t = T(); if t.x: def parse` without else is not a list bind; `if [x for y in [[1]] for x in y]` list is live; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `for _ in [1]` / `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` / `if {x for x in [1]}` / `if [x for x in [1] if x]` / `t = T(); if t.x` after `class T: x = 1` / `if (lambda: 0)` / `for _ in (x for x in []):` without else not a list bind / `if [1][0]` / `if f'{1}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local TYPE_CHECKING still match (no regression).

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try that can run, match without a static subject, lambda **bind** vs list, While (do not exec), for-else after break (no break proof), Call For-iter `for _ in range(1):`.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, or list `for _ in (x for x in []): def parse` is `kind=def` while query has no name, or list last-wins `if {x for x in [1]}` / `if {x: x for x in [1]}` / `if [x for x in [1] if x]` as dead while query is live, KILL.

---

MUTATE
