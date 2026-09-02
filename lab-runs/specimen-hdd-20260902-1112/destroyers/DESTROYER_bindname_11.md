# DESTROYER bindname 11

Date: 2026-09-02 19:11–19:21 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0579 worker=destroyer-bindname-11

Target (archive, post-MUTATE-11 nonempty genexp rows / format-spec JoinedStr):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `bf07a0ef52c21723b676558e313eba79e89cb3d35432800726b954b2f3be2c8f` (60655 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-11 (`cli_sha256_after`, 90/90; worker `mutate-bindname-11` job-0578). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `76acbda Record bindname mutate HEAD 4d2fa1b.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `76acbdaf1f19f197addd12918a0efa957a993bae`. Mutate-11 commit `4d2fa1bca095f1b05db0fa43b312131e14a75f1c`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 90/90 OK (10.169s / 10.229s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. `DESTROYER_bindname_6.md` **MUTATE**. `DESTROYER_bindname_7.md` **MUTATE**. `DESTROYER_bindname_8.md` **MUTATE**. `DESTROYER_bindname_9.md` **MUTATE**. `DESTROYER_bindname_10.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-11 claimed: nonempty genexp iterates produced values (`_TruthyRows`) so `for _ in (x for x in [1]): def parse` is a list bind; empty genexp For is not; `if f'{1:d}'` list is live.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; `for _ in (x for x in [1]): def parse` list miss while honesty live; `for _ in (x for x in []): def parse` list `kind=def` while honesty has no name; `if f'{1:d}'` list dead while query live; THIN_WRAPPER of two greps. Those ten were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list last-wins of remaining const-known post-class Attribute assign / AnnAssign / del (`T.x = 0`, `t.x = 0`, `T.y = 1`, `del T.x`) / no-arg `T()` that ignores `__init__` / multi-generator comprehensions / JoinedStr conversion-then-format-spec (`f'{1!s:d}'` / `f'{1!s:s}'`). Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname11_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

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
| 7 | `for _ in (x for x in [1]): def parse` list miss while honesty live | query `gf1-live`; list `kind=def` `gf1-live` | no |
| 8 | `for _ in (x for x in []): def parse` list `kind=def` while honesty has no name | query `has no name`; list has no `genfor0.parse` (only `pkg_parse.parse`) | no |
| 9 | `if f'{1:d}'` list dead while query live | list source `fmt-live` not `fmt-dead` | no |
| 10 | THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join | naive `inspect.getsource(ast.parse)` from `/tmp` is Cellar; bindname leftover + `also pkg_parse.parse` | no |

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

### Mutate-11 claimed nonempty genexp rows / format-spec still matches query

`for _ in (x for x in [1]): def parse` list is `gf1-live`. `xs = (x for x in [1]); for _ in xs:` list is `ag-live`. `if [y for y in (x for x in [1])]:` / `if {y for y in (x for x in [1])}:` / `if [*(x for x in [1])]:` / `if (*(x for x in [1]),):` list is live. Empty `for _ in (x for x in []): def parse` without else is **not** a list bind (query `has no name`). Filtered empty `for _ in (x for x in [1] if False):` / assigned empty `xs = (x for x in []); for _ in xs:` / `if [*(x for x in [])]:` without else is not a list bind. `if (x for x in []):` / `if (x for x in [1]):` / `xs = (x for x in []); if xs:` / `if (x for x in [1] if False):` list is live (generator object is truthy). `if not (x for x in []):` list is dead.

`if f'{1:d}':` / `if f'{1:02d}':` / `if f'{1:{1}}':` / `if (s := f'{1:d}'):` / `if f'{1=}':` list is live. `if f'{1:s}':` without else is honesty ValueError; list currently both (`_MISSING`) — declared format-error park, not Honor KILL 9.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `t = T(); if t.x:` after `class T: x = 1` / `if (lambda: 0):` / `if [1][0]` / `if f'{1}'` / `if f'{1!s}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` with else / tuple unpack / local TYPE_CHECKING / `if [[1]][0][0]:` / static-subject `match [1][0]` still match.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. Nonempty genexp-For / format-spec JoinedStr is the mutate-11 object. Remaining Attribute assign / `T()` vs `__init__` / multi-gen / conversion-then-spec below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after mutate-11 nonempty genexp rows / format-spec, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if (x for x in []):` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `t = T(); if t.x:` / `if (lambda: 0):` / `if [1][0]:` / `if f'{1}':` / `if f'{1:d}':` / `if [*[1]]:` / `for _ in (x for x in [1]):` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-11. It is real. List last-wins of remaining const-known post-class Attribute assign / no-arg `T()` that copies a class namespace while honesty runs `__init__` / multi-generator comprehensions / JoinedStr conversion-then-format-spec are not honesty leftover-identity.

---

## Implementation

### 1. Post-class / instance Attribute assign is still the class-body snapshot

Mutate-9/10/11 store a `SimpleNamespace` of const class-body Name assigns, so `if T.x` and `t = T(); if t.x` match when nothing mutates after the class. `T.x = 0` is an Attribute target; `update_const_env` returns without writing.

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

Honesty / query `'cas-dead'`. List `cas-live` (`T` still `SimpleNamespace(x=1)`). Inverse `class T: x = 0; T.x = 1; if T.x` list last-wins `cal-dead` while query is live. New attr `T.y = 1; if T.y` list last-wins `cna-dead`. AnnAssign `T.x: int = 0` same (`aa-live` vs honesty dead). `del T.x; if T.x: def parse` without else: honesty AttributeError / query `has no name`; list `kind=def`. `match T.x` after `T.x = 0` list last-wins the `_` case (`ma-live`) while honesty is `ma-dead`.

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

Honesty / query `'ias-dead'`. List `ias-live` (copy of `x=1` never updated).

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

Honesty / query `'cai-dead'` (instance looks up class attr after the class assign). List `cai-live` (instance copy independent of later class setattr). Const Attribute assign / AnnAssign / `del` onto a name already bound to a `SimpleNamespace` is leftover-identity. Not AugAssign (`T.x += -1` stays park; query matches honesty because query executes). Not `T = type(...)` Call (declared).

### 2. No-arg `T()` copies the class namespace and ignores `__init__`

Mutate-10/11: `Call` with no args / no keywords of a `SimpleNamespace` copies that namespace. Class-body `FunctionDef` is not stored, so honesty `__init__` is invisible.

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

```python
# initonly.py
class T:
    def __init__(self):
        self.x = 1
t = T()
if t.x:
    def parse(x):
        return 'io-live'
else:
    def parse(x):
        return 'io-dead'
```

Honesty / query `'io-live'`. List last-wins `io-dead` (empty namespace copy, `t.x` is `_MISSING`).

Do **not** exec `__init__`. When the ClassDef body contains a `FunctionDef` / `AsyncFunctionDef` named `__init__`, no-arg Call stays `_MISSING` (both). Keep the mutate-10 copy for const-only class namespaces (`class T: x = 1; t = T(); if t.x` already matches) and for classes whose methods are not `__init__` (`async def go` + `x = 1` currently MATCH; keep that copy). Empty `__init__` that `pass` currently MATCH; after this cut it becomes `_MISSING` (both) — acceptable, do not exec to recover it.

### 3. Multi-generator comprehensions still `_MISSING`

`_eval_comprehension` / `_eval_comprehension_pairs` require `len(generators) == 1`. Nested `if [[y for y in [1]]]:` already matches as a List of a folded ListComp; that is not this hole. DictComp still early-returns `_MISSING` when `len(generators) != 1` even if ListComp/SetComp later fold.

```python
# multigen.py
if [x for y in [[1]] for x in y]:
    def parse(x):
        return 'mg-live'
else:
    def parse(x):
        return 'mg-dead'
```

Honesty / query `'mg-live'`. List `mg-dead`. SetComp / DictComp of two generators same (`ms2-dead` / `md-dead`). Three generators `if [z for a in [[[1]]] for b in a for z in b]:` same (`mg3-dead`). Filtered `if [x for y in [[1, 0]] for x in y if x]:` same (`mgf-dead`). Single-gen `if {1 for _ in [1]}:` / `if {x + 0 for x in [1]}:` / `if {k: v for k, v in [(1, 2)]}:` / `xs = [1]; if {x for x in xs}:` already MATCH. Fold nested generators of const iterables. Do not exec Call in the elt.

### 4. JoinedStr **conversion then format-spec** still last-wins wrong

Mutate-11 folded `if f'{1:d}':` via `format(inner, spec)` and left conversion ignored whenever `format_spec` is present (`if spec: format(inner, spec)` else conversion). Honesty applies conversion first, then the spec.

```python
# fmtconvspec.py
if f'{1!s:d}':
    def parse(x):
        return 'fcs-live'
else:
    def parse(x):
        return 'fcs-dead'
```

Honesty ValueError (`format('1', 'd')`). Query `has no name`. List `kind=def` (CLI `format(1, 'd')` → `'1'` truthy). Inverse `if f'{1!s:s}':` honesty `'fcss-live'`; list last-wins `fcss-dead` (CLI `format(1, 's')` ValueError → `_MISSING` both).

Apply conversion (`!s`/`!r`/`!a`) to the const inner first, then `format` with the const spec. Conversion-only `if f'{1!s}':` already MATCH; keep it. Spec-only `if f'{1:d}':` already MATCH; keep it. Format errors stay `_MISSING` (do not exec; do not claim list matches import failure). `if f'{1:s}':` without else remains the declared format-error park.

### 5. Frozen / path-shadowable leftovers that match (not this MUTATE)

| leftover | honesty | CLI |
|----------|---------|-----|
| `importlib.util` / `importlib.machinery` | cannot bind (frozen) | `has no name` / list miss |
| `importlib.py` file / `importlib/` package / `importlib.abc` | leftover helper | leftover helper |
| `importlib.resources` / `metadata` | leftover helper | leftover helper |
| `json` / `json.decoder` / `pathlib` / `inspect` / `typing` / `dataclasses` / `warnings` / `contextlib` / `argparse` / `tempfile` / `subprocess` / `typing_extensions` | leftover helper | leftover helper |
| `enum` / `operator` / `functools` / `abc` / `types` / `re` / `collections` / `copyreg` / `site` / `zipimport` / `collections.abc` / `os.path` / `encodings.utf_8` | refuse | refuse |
| `tokenize.py` | leftover helper | leftover helper |

No frozen-submodule leftover-identity remaining that honesty and CLI split. Do not refuse leftover `importlib/` package that honesty binds.

### 6. Declared parks this cut (probed, not MUTATE)

- Nested defs (specimen-012 `test_a` inside `run()`): list `test_order.test_a`; `--from run_orders test_a` has no name.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign / `importlib.import_module` / `__dict__` / `itemgetter` / `[pkg_parse.parse][0]` / lambda wrap: honesty moved; `--from` follows; `--file` does not. Constant-getattr / getattr-with-default / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute already follow.
- FIFO `--file` remains `not a file` (0.037s).
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a **list** bind: query may follow; list miss.
- `parse = lambda ...` as the bind (query `kind=def` `runs=.<lambda>`, source is the assignment; query does not print `('lam', 'z')`).
- Huge `source` dump still includes the 4000-`H` docstring.
- `if flag:` both branches when the test is not const-known (`os.environ.get`).
- `if len([])` Call / `if set()` / `if (1).conjugate()` Call / `if [len(x) for x in ['a']]` Call in elt / `T = type('T', (), {'x': 1})` Call.
- AugAssign `n = 1; n += -1` / `T.x += -1` (query matches honesty; list does not — do not fold AugAssign).
- Try that can run (list last-wins except).
- match without a static subject (`match os.name`).
- While: `while True: def parse; break` list miss while query live; `while False:` both miss. Do **not** exec While. Do not unroll.
- for-else after `break` (no break proof): honesty `feb-live`; list last-wins else.
- `for x in [0, 1]: if x: def parse` (For walks first item only; no unroll): honesty live; list miss. Do not unroll For.
- `for _ in range(1):` Call iterator (declared). Unknown Call currently walks body (`range(1)` accidental live; `range(0)` list `kind=def` while query has no name). Do not walk Call iterators.
- Format errors (`if f'{1:s}':` without else): honesty ValueError; list both because spec stays `_MISSING`. Do not claim list matches import failure.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` / Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'{1}':` / `if f'{1:d}':` / nested unpack `flag, (other,) = True, (True,)` / starred unpack `flag, *rest = True, True` / starred collections `if [*[1]]:` / For-body `for _ in [1]: def parse` / Attribute `if (1).real:` / class attr `if T.x:` / identity ListComp `if [x for x in [1]]:` / GeneratorExp-If `if (x for x in []):` / nonempty genexp-For `for _ in (x for x in [1]):` / SetComp `if {x for x in [1]}:` / DictComp / filtered ListComp / no-arg `t = T(); if t.x:` / `if (lambda: 0):` skip; post-class `T.x = 0` / `T()` with `__init__` / multi-generator `if [x for y in [[1]] for x in y]:` / conversion-then-spec `if f'{1!s:d}':` still last-wins both); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-11 made nonempty genexp-For a list bind and format-spec JoinedStr list match query. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded class-namespace-without-Attribute-assign + `T()` without `__init__` + single-gen-only comprehension + conversion-ignored-when-spec is the new ceiling:

- List last-wins `class T: x = 1; T.x = 0; if T.x:` else as live while query is dead. Inverse `T.x = 1` after `x = 0` else as dead while query is live. `t = T(); t.x = 0; if t.x` else as live while query is dead. `t = T(); T.x = 0; if t.x` else as live while query is dead. `T.x: int = 0` / `del T.x` / `match T.x` after assign same family.
- List `class T: x = 1; def __init__(self): self.x = 0; t = T(); if t.x: def parse` without else as `kind=def` while query has no name. Inverse `__init__` sets 1 after class `x = 0` else as dead while query is live. `__init__` only (no class `x`) else as dead while query is live.
- List last-wins `if [x for y in [[1]] for x in y]:` / SetComp / DictComp / three-gen / filtered multi-gen else as dead while query is live.
- List `if f'{1!s:d}':` without else as `kind=def` while honesty ValueError. Inverse `if f'{1!s:s}':` else as dead while query is live.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try that can run, match without a static subject, lambda **bind** vs list, AugAssign / Call in If tests, While, for-else after break, For first-item only, Call For-iter stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List last-wins of remaining const-known Attribute assign / `T()` vs `__init__` / multi-gen / conversion-then-spec are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list last-wins a const-dead `class T: x = 1; T.x = 0; if T.x:` else / `if [x for y in [[1]] for x in y]:` else as the bind, or that list-binds `t = T(); if t.x` while honesty `__init__` left no name, or that list-binds `if f'{1!s:d}':` while honesty ValueError.

1. **Const Attribute assign / AnnAssign / del onto a name already in env.** `class T: x = 1; T.x = 0; if T.x:` orelse is live; list currently last-wins `cas-live` while query is dead. Inverse `T.x = 1` after class `x = 0` orelse is dead; list last-wins `cal-dead`. `T.y = 1; if T.y` orelse is dead. `t = T(); t.x = 0; if t.x` orelse is live while query is dead. `t = T(); T.x = 0; if t.x` orelse is live while query is dead (instance looks up class). `T.x: int = 0` same. `del T.x; if T.x: def parse` without else is not a list bind (query `has no name`; list currently `kind=def`). `match T.x` after `T.x = 0` orelse is dead; list last-wins `ma-live`. Attribute assign / AnnAssign of a const onto a `SimpleNamespace` already in env; `del` pops that attr. `t = T()` is already a copy (mutate-10); setattr on `T` must not rewrite that copy, but later `if t.x` without an instance attr still reads the class namespace in honesty — instance copies used for `if t.x` must follow class updates unless `t.x = …` already shadowed. Do not fold `type(...)` Call. Do not fold AugAssign.

2. **No-arg `T()` when the class body has `__init__`.** `class T: x = 1; def __init__(self): self.x = 0; t = T(); if t.x: def parse` without else is not a list bind (query `has no name`; list currently `kind=def`). Inverse `__init__` sets 1 after class `x = 0` orelse is dead; list last-wins `izl-dead`. `__init__` only (no class `x`) orelse is dead; list last-wins `io-dead`. When `T` is a const-only `SimpleNamespace`, keep the mutate-10 copy. When the ClassDef body contains `FunctionDef` / `AsyncFunctionDef` named `__init__`, no-arg Call stays `_MISSING` (both). Other methods (`async def go`) do not block the copy. Do not exec `__init__`.

3. **Multi-generator ListComp / SetComp / DictComp of const iterables.** `if [x for y in [[1]] for x in y]:` / `if {x for y in [[1]] for x in y}:` / `if {x: 1 for y in [[1]] for x in y}:` / three-gen / filtered multi-gen orelse is dead; list currently last-wins `mg-dead` / `ms2-dead` / `md-dead` / `mg3-dead` / `mgf-dead`. Fold nested generators like single-gen `_eval_comprehension` when each iterable/elt/filter is const-known. DictComp currently early-returns `_MISSING` when `len(generators) != 1`; fold it too. Single-gen SetComp const/binop elt and dict unpack already match; keep them. Do not exec Call in the elt.

4. **JoinedStr conversion then format-spec.** `if f'{1!s:d}':` without else is not a list bind (honesty ValueError; list currently `kind=def`). `if f'{1!s:s}':` orelse is dead; list currently last-wins `fcss-dead`. Apply `!s`/`!r`/`!a` to the const inner first, then `format` with the const spec. Spec-only `if f'{1:d}':` / conversion-only `if f'{1!s}':` already match; keep them. Format errors stay `_MISSING`. Do not exec.

5. **Tests the current suite cannot see.** `T.x = 0; if T.x` list is dead not `cas-live`; `t = T(); t.x = 0; if t.x` list is dead; `t = T(); T.x = 0; if t.x` list is dead; `class T` with `__init__` zeroing `x` then `t = T(); if t.x: def parse` without else is not a list bind; `__init__` only setting `x = 1` list is live; `if [x for y in [[1]] for x in y]` list is live; `if f'{1!s:s}'` list is live; `if f'{1!s:d}'` without else is not a list bind; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `for _ in [1]` / `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` / `if {x for x in [1]}` / `if [x for x in [1] if x]` / `t = T(); if t.x` after `class T: x = 1` / `if (lambda: 0)` / `for _ in (x for x in [1]):` list bind / `for _ in (x for x in []):` without else not a list bind / `if f'{1:d}'` list is live / `if [1][0]` / `if f'{1}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local TYPE_CHECKING still match (no regression).

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try that can run, match without a static subject, lambda **bind** vs list, While (do not exec), for-else after break (no break proof), For first-item only (do not unroll), Call For-iter `for _ in range(1):`, format-error JoinedStr `_MISSING`.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, or list `for _ in (x for x in [1]): def parse` is miss while query is live, or list `for _ in (x for x in []): def parse` is `kind=def` while query has no name, or list last-wins `if f'{1:d}'` as dead while query is live, KILL.

---

MUTATE
