# DESTROYER bindname 14

Date: 2026-09-02 20:14–20:25 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0613 worker=destroyer-bindname-14

Target (archive, post-MUTATE-14 If-fail polarity / del-Name missing marker / class-body If assigns):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `20f81016e90c9a15ea0251a56d143188fb67a834c8220af37b5f01b4b7c06224` (65799 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-14 (`cli_sha256_after`, 102/102; worker `mutate-bindname-14` job-0612). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `753034f Record bindname mutate HEAD 35fff7d.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `753034f24a6dd5a07e6c424ced074ea425003a43`. Mutate-14 commit `35fff7df4f63bb7ebfdd60490e1a1ad03c5af5a1`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 102/102 OK (12.002s / 11.925s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. `DESTROYER_bindname_6.md` **MUTATE**. `DESTROYER_bindname_7.md` **MUTATE**. `DESTROYER_bindname_8.md` **MUTATE**. `DESTROYER_bindname_9.md` **MUTATE**. `DESTROYER_bindname_10.md` **MUTATE**. `DESTROYER_bindname_11.md` **MUTATE**. `DESTROYER_bindname_12.md` **MUTATE**. `DESTROYER_bindname_13.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-14 claimed: If fail polarity (`_ATTR_MISSING` skips both branches); `del Name` stores a missing marker; class-body If assigns (`class T: if True: x = 1; else: x = 0` then `if T.x` list live).

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; `del T.x; if T.x: … else:` list `kind=def` while honesty AttributeError; `del x; if x:` list `kind=def` while honesty NameError; `t = T(); T.x = 0; if t.x` list live while honesty dead; THIN_WRAPPER of two greps. Those ten were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list miss / last-wins of remaining const-known class-body For / nested If / Match / If-test walrus, and `_ATTR_MISSING` treated as a truthy object through Not/BoolOp/Compare/BinOp/Subscript. FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While stay declared parks (would require executing user code or a new object). Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname14_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

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
| 7 | `del T.x; if T.x: … else:` list `kind=def` while honesty AttributeError | honesty AttributeError; query `import failed`; list has no `delattreelse.parse` | no |
| 8 | `del x; if x:` list `kind=def` while honesty NameError | honesty NameError; query `import failed`; list has no `delname.parse` | no |
| 9 | `t = T(); T.x = 0; if t.x` list live while honesty dead | honesty / query / list `cai-dead` | no |
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

### Mutate-14 claimed fail-If / del-Name / class-body If still matches query

`del T.x; if T.x: live else: dead`: honesty AttributeError; query `import failed`; list has no `delattreelse.parse` (skip both, not polarity-dead orelse). `del T.x; if T.x: def parse` without else still not a list bind. `obj = T; del obj.x; if T.x` without else same. `t = T(); del T.x; if t.x` without else not a list bind.

`x = 1; del x; if x: def parse` without else: honesty NameError; query `import failed`; list has no `delname.parse`. With else, list also has no bind.

`class T: if True: x = 1; else: x = 0; if T.x` list is `cif-live`. Inverse `if False: x = 1; else: x = 0; if T.x` list is `cff-dead`. `class T: if True: x: int = 1; if T.x` list is `cai2-live`. One-level class-body If assigns MATCH.

`t = T(); T.x = 0; if t.x` list is still `cai-dead`. Inverse new class attr `T.y = 1; if t.y` list is `icy-live`. Instance setattr still shadows (`t.x = 1; T.x = 0; if t.x` is `sk-live`). Two instances `t1.x = 0; if t2.x` list is `ti-live`. `flag = True; class T: x = flag` list is `outer-live`. Sequential `class U: y = T.x` list is `co2-live`. Class-body tuple unpack `class T: x, y = 1, 0; if T.x` list is `cu-live`. `T.x, T.y = 0, 0; if T.x` list is `ua-dead`. `for T.x in [0]:` then `if T.x` list is `fa-dead`. `class T: x = 1; T.x = 0; if T.x` list is still `cas-dead`. Nested class `class T: class U: y = x; if T.U.y` honesty NameError; list no bind (does not leak `T.x` as a Name).

`if [x for y in [[1]] for x in y]` / `if f'{1!s:s}'` / `for _ in (x for x in [1])` / `if f'{1:d}'` still match.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. If-fail polarity / del-Name missing marker / one-level class-body If assigns is the mutate-14 object. Remaining class-body For / nested If / Match / If-test walrus / `_ATTR_MISSING` through operators below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after mutate-14 If-fail / del-Name / class-body If assigns, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if (x for x in []):` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `t = T(); if t.x:` / `if (lambda: 0):` / `if [1][0]:` / `if f'{1}':` / `if f'{1:d}':` / `if f'{1!s:s}':` / `if [*[1]]:` / `for _ in (x for x in [1]):` / `if [x for y in [[1]] for x in y]:` / `class T: x = 1; T.x = 0; if T.x:` / `t = T(); T.x = 0; if t.x:` / `flag = True; class T: x = flag` / `class U: y = T.x` / `T.x, T.y = 0, 0` / `for T.x in [0]:` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target / `del T.x; if T.x:` skip both / `del x; if x:` skip both / `class T: if True: x = 1` / `class T: if True: x: int = 1` list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-14. It is real. List miss / last-wins of remaining const-known class-body For / nested If / Match / If-test walrus, and `_ATTR_MISSING` through Not/BoolOp/Compare/BinOp/Subscript, are not honesty leftover-identity.

---

## Implementation

### 1. Class body still does not walk const For (or For inside If)

`update_const_env` on ClassDef body walks one-level If then Assign / AnnAssign / Delete. For is a no-op.

```python
# classforbody.py
class T:
    for _ in [1]:
        x = 1
if T.x:
    def parse(x):
        return 'cfb-live'
else:
    def parse(x):
        return 'cfb-dead'
```

Honesty / query `'cfb-live'`. List no bind (`T.x` missing → `_ATTR_MISSING` → fail → skip both). `class T: if True: for _ in [1]: x = 1; if T.x` same (`cifor-dead` miss). `class T: for _ in []: x = 1; else: x = 0; if T.x` honesty / query `'cff2-dead'`; list miss.

Walk const-known For first-item inside ClassDef with the same polarity / first-item bind as module For. Do not exec While. Do not unroll For.

### 2. Class-body If is not recursive; Match is a no-op

```python
# classnestedif.py
class T:
    if True:
        if True:
            x = 1
if T.x:
    def parse(x):
        return 'cni-live'
else:
    def parse(x):
        return 'cni-dead'
```

Honesty / query `'cni-live'`. List no bind (inner If passed to `update_const_env`, which ignores If). `class T: match 1: case 1: x = 1; if T.x` same (`cmh-live` query, list miss).

Walk class-body statements with the same If/For/Match polarity as module, for const env only (do not yield class-body FunctionDef as a module-level bind). Nested class `class T: class U: y = x` must **not** see `T.x` as a Name (honesty NameError; already MATCH).

### 3. Class-body If-test walrus writes vanish because empty `_ChainEnv` is falsy

```python
# classwalrus.py
class T:
    if (x := 1):
        y = x
if T.y:
    def parse(x):
        return 'cw-live'
else:
    def parse(x):
        return 'cw-dead'
```

Honesty Python 3.14 stores the walrus **on the class** (`T.x is 1`, `T.y is 1`, not the module). Honesty / query `'cw-live'`. List no bind. `test_polarity` does `env = env or {}`; an empty `_ChainEnv` is an empty dict, hence falsy, so NamedExpr writes go to a throwaway `{}`. `y = (x := 1)` already MATCH (`cwa-live`) because Assign `static_const` uses the real inner env. `class T: if True: x: int = 1` already MATCH.

Use `if env is None: env = {}` in `test_polarity` so an empty class env is kept. Then If-test NamedExpr writes stay on the class. Do not leak class-body walrus as a module Name.

### 4. `_ATTR_MISSING` is a truthy object through Not / BoolOp / Compare / BinOp / Subscript

Bare `if T.x` after `del T.x` is fail (Honor KILL 7). Operators do not propagate the marker.

```python
# notdelattreelse.py
class T:
    x = 1
del T.x
if not T.x:
    def parse(x):
        return 'nda2-live'
else:
    def parse(x):
        return 'nda2-dead'
```

Honesty / query AttributeError (`has no name`). List `kind=def` (`nda2-dead`): `not _ATTR_MISSING` is `False` because the sentinel is truthy. `if T.x or True` list `oda-live`. `if T.x and True` list `ada-live`. `if T.x == 1` list `cda-dead`. `if T.x + 1` list `bda-dead`. `if T.x[0]` list `sda-dead`. `x = 1; del x; if not x: … else:` list `ndn-dead` while honesty NameError.

`if T.x if True else 0` after del accidentally MATCH (IfExp test is the constant `True`, body is `T.x` → `_ATTR_MISSING` → fail). Do not treat that as a walk.

Propagate `_ATTR_MISSING` through Not / BoolOp / Compare / BinOp / Subscript / IfExp so the If is fail (skip both), not polarity-dead orelse and not a truthy object. Unknown names stay both. Do not exec.

### 5. Declared parks this cut (probed, not MUTATE)

- FunctionDef / AsyncFunctionDef sentinel on the class: `class T: def go(self): return 0; if T.go` honesty / query `'mt-live'`; list miss (`T.go` missing → fail). `t = T(); if t.go` / `async def go` / `@classmethod` / `@staticmethod` same. Storing a truthy sentinel is a new object next to `_has_init`; do not exec the body or the decorator. Keep `__init__` as `_has_init` so `T()` stays `_MISSING`.
- Name bases: `class U(T): pass; if U.x` honesty / query `'cb-live'`; list miss. `t = U(); if t.x` / `class U(*(T,)): pass` same. Copying const attrs from a Name base is a new object. Do not exec metaclass / decorators / `type(...)`. Own subclass assigns already MATCH (`class U(T): x = 0` is `sbo-dead`).
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
- `del t.x` when `x` is a class attr: honesty AttributeError at the `del`; list no-op then still sees class `x`. Same family as assert/raise. Do **not** exec.
- match without a static subject (`match os.name`).
- While: `while True: def parse; break` list miss while query live; `while False:` both miss; `class T: while False: x = 0; else: x = 1; if T.x` query live, list miss. Do **not** exec While. Do not unroll.
- for-else after `break` (no break proof): honesty `feb-live`; list last-wins else.
- `for x in [0, 1]: if x: def parse` (For walks first item only; no unroll): honesty live; list miss. Do not unroll For.
- `for _ in range(1):` Call iterator (declared). Unknown Call currently walks body (`range(1)` accidental live; `range(0)` list `kind=def` while query has no name). Do not walk Call iterators.
- Format errors (`if f'{1:s}':` / `if f'{1!s:d}':` without else): honesty ValueError; list both because spec stays `_MISSING`. Do not claim list matches import failure.
- `T()` when the class body has `__init__`: Call stays `_MISSING` (both). Empty `def __init__(self): pass` then `t = T(); if t.x` honesty live; list last-wins `ei-dead`. `__init__` that zeros `x` then `if t.x: def parse` without else: query `has no name`; list `kind=def`. Do **not** exec `__init__`.
- Const Subscript / slice assign (`xs[0] = 0` / `d[1] = 0` / `xs[:] = []` / `T.x[0] = 0`): honesty dead; list last-wins live. Declared this cut. Do not exec Call. Do not fold AugAssign.
- `if __file__:` / `if __name__:` list last-wins else as dead while query is live. Scan-known, but injecting `__file__`/`__name__` is a new env seed, not this cut's object. Leave parked unless a later cut seeds them without executing the module.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` / Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'{1}':` / `if f'{1:d}':` / `if f'{1!s:s}':` / nested unpack `flag, (other,) = True, (True,)` / starred unpack `flag, *rest = True, True` / starred collections `if [*[1]]:` / For-body `for _ in [1]: def parse` / Attribute `if (1).real:` / class attr `if T.x:` / post-class `T.x = 0; if T.x:` / identity ListComp `if [x for x in [1]]:` / GeneratorExp-If `if (x for x in []):` / nonempty genexp-For `for _ in (x for x in [1]):` / SetComp `if {x for x in [1]}:` / DictComp / filtered ListComp / multi-generator `if [x for y in [[1]] for x in y]:` / no-arg `t = T(); if t.x:` / `if (lambda: 0):` / `t = T(); T.x = 0; if t.x` / `T.x, T.y = 0, 0` / `class U: y = T.x` / `del T.x; if T.x:` skip both / `del x; if x:` skip both / `class T: if True: x = 1` one-level If assigns / `class T: for _ in [1]: x = 1` / `class T: if True: if True: x = 1` / `class T: match 1: case 1: x = 1` / `class T: if (x := 1): y = x` / `del T.x; if not T.x` / `class T: def go` / `class U(T)` / `xs[0] = 0; if xs[0]` still last-wins both); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-14 made `del T.x; if T.x: … else:` skip both / `del x; if x:` skip both / `class T: if True: x = 1; if T.x` list match query. Unpack / For Attribute and sequential `class U: y = T.x` still match as the same const-env join. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded class-body-without-For-or-nested-If + empty-ChainEnv-falsy If-test walrus + missing-as-truthy-through-operators is the new ceiling:

- List miss `class T: for _ in [1]: x = 1; if T.x:` / `class T: if True: for _ in [1]: x = 1; if T.x` / `class T: for _ in []: … else: x = 0; if T.x` while query is live (or dead-else).
- List miss `class T: if True: if True: x = 1; if T.x` / `class T: match 1: case 1: x = 1; if T.x` while query is live.
- List miss `class T: if (x := 1): y = x; if T.y` while query is live (empty `_ChainEnv` dropped by `env or {}`).
- List `del T.x; if not T.x: … else:` / `if T.x or True` / `if T.x and True` / `if T.x == 1` / `if T.x + 1` / `if T.x[0]` / `del x; if not x: … else:` as `kind=def` while query has no name.
- FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While stay declared.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try / assert / raise that can run, match without a static subject, lambda **bind** vs list, AugAssign / Call in If tests, While, for-else after break, For first-item only, Call For-iter, `T()` with `__init__`, format-error JoinedStr stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List miss / last-wins of remaining const-known class-body For / nested If / Match / If-test walrus, and `_ATTR_MISSING` through operators, are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list-misses a const-live `class T: for _ in [1]: x = 1; if T.x:` / nested class-body If / class-body Match / If-test walrus, or that list-binds `del T.x; if not T.x: … else:` / `if T.x or True` while query has no name.

1. **Class-body const For.** `class T: for _ in [1]: x = 1; if T.x:` list currently miss while query is live (`cfb-live`). `class T: if True: for _ in [1]: x = 1; if T.x` same (`cifor-live`). `class T: for _ in []: x = 1; else: x = 0; if T.x` list miss while query is `cff2-dead`. Walk const-known For first-item inside ClassDef with the same polarity as module For. Keep sequential `class U: y = T.x` / `flag = True; class T: x = flag` / one-level `class T: if True: x = 1` (already MATCH). Do not exec While. Do not unroll For. Nested class `class T: class U: y = x` must not treat `x` as `T.x` (honesty NameError; already MATCH).

2. **Class-body nested If / Match.** `class T: if True: if True: x = 1; if T.x` list currently miss while query is live (`cni-live`). `class T: match 1: case 1: x = 1; if T.x` same (`cmh-live`). Walk class-body with the same If/For/Match polarity as module, for const env only. Do not yield class-body FunctionDef as a module-level bind.

3. **Class-body If-test walrus / empty `_ChainEnv`.** `class T: if (x := 1): y = x; if T.y` list currently miss while query is live (`cw-live`). Honesty Python 3.14 stores the walrus on the class (`T.x` and `T.y`), not the module. `test_polarity` does `env = env or {}`; empty `_ChainEnv` is falsy so NamedExpr writes vanish. Use `if env is None: env = {}`. Keep `y = (x := 1); if T.x` (already MATCH via Assign `static_const`). Keep `class T: if True: x: int = 1` (already MATCH).

4. **`_ATTR_MISSING` through operators.** `del T.x; if not T.x: live else: dead`: query `has no name`; list currently `kind=def` (`nda2-dead`) because `not _ATTR_MISSING` is `False`. `if T.x or True` list `oda-live`. `if T.x and True` list `ada-live`. `if T.x == 1` list `cda-dead`. `if T.x + 1` list `bda-dead`. `if T.x[0]` list `sda-dead`. `del x; if not x: … else:` list `ndn-dead`. Propagate `_ATTR_MISSING` through Not / BoolOp / Compare / BinOp / Subscript / IfExp so the If is fail (skip both). Keep bare `del T.x; if T.x: … else:` / `del x; if x:` as not a list bind (already MATCH). Unknown names stay both. Do not exec.

5. **Tests the current suite cannot see.** `class T: for _ in [1]: x = 1; if T.x` list is live not miss; `class T: if True: if True: x = 1; if T.x` list is live; `class T: match 1: case 1: x = 1; if T.x` list is live; `class T: if (x := 1): y = x; if T.y` list is live; `del T.x; if not T.x: live else: dead` is not a list bind; `del T.x; if T.x or True: … else:` is not a list bind; `del x; if not x: … else:` is not a list bind; `class T: if True: x = 1; if T.x` list is still live; `del T.x; if T.x: … else:` is still not a list bind; `del x; if x:` is still not a list bind; `t = T(); T.x = 0; if t.x` list is still dead; `flag = True; class T: x = flag` list is still live; `class U: y = T.x; if U.y` list is still live; `T.x, T.y = 0, 0; if T.x` list is still dead; `class T: x = 1; T.x = 0; if T.x` list is still dead; `t = T(); t.x = 0; if t.x` list is still dead; `if [x for y in [[1]] for x in y]` list is still live; `if f'{1!s:s}'` list is still live; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `for _ in [1]` / `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` / `if {x for x in [1]}` / `if [x for x in [1] if x]` / `t = T(); if t.x` after `class T: x = 1` / `if (lambda: 0)` / `for _ in (x for x in [1]):` list bind / `for _ in (x for x in []):` without else not a list bind / `if f'{1:d}'` list is live / `if [1][0]` / `if f'{1}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local TYPE_CHECKING still match (no regression).

Keep declared boundaries: FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While (do not exec), nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try / assert / raise that can run, match without a static subject, lambda **bind** vs list, for-else after break (no break proof), For first-item only (do not unroll), Call For-iter `for _ in range(1):`, format-error JoinedStr `_MISSING`, `T()` with `__init__` `_MISSING` (do not exec `__init__`), const Subscript / slice assign (do not fold).

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, or list last-wins `t = T(); T.x = 0; if t.x:` as live while query is dead, or list-binds `del T.x; if T.x: … else:` / `del x; if x:` while query has no name, KILL.

---

MUTATE
