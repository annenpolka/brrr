# DESTROYER bindname 13

Date: 2026-09-02 19:50–20:07 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0606 worker=destroyer-bindname-13

Target (archive, post-MUTATE-13 instance-follows-class / missing-attr If / class-body outer reads):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `d0e4fff4285380107fbccdceb2a4f0325be724b9f6950ea011c57d4460a06643` (64884 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-13 (`cli_sha256_after`, 98/98; worker `mutate-bindname-13` job-0600). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `c761d4f Record bindname mutate HEAD 16ed54d.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `c761d4fdc24f19cbc6209768ac88e638a72317eb`. Mutate-13 commit `16ed54d24c7d88cd16f53e7ab24ea424b5eb6d44`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 98/98 OK (11.192s / 11.350s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. `DESTROYER_bindname_6.md` **MUTATE**. `DESTROYER_bindname_7.md` **MUTATE**. `DESTROYER_bindname_8.md` **MUTATE**. `DESTROYER_bindname_9.md` **MUTATE**. `DESTROYER_bindname_10.md` **MUTATE**. `DESTROYER_bindname_11.md` **MUTATE**. `DESTROYER_bindname_12.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-13 claimed: instance follows class (`t = T(); T.x = 0; if t.x` dead-else); missing-attr If (`del T.x; if T.x` not a list bind); class-body outer reads (`flag = True; class T: x = flag`).

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; `t = T(); T.x = 0; if t.x` list live while honesty dead; `del T.x; if T.x` list `kind=def` while honesty AttributeError; THIN_WRAPPER of two greps. Those nine were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list last-wins of remaining const-known class-body If/For/walrus / FunctionDef sentinel / Name-bases / Delete-Name / missing-attr If-else (skip both, not polarity-dead orelse). Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname13_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

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
| 7 | `t = T(); T.x = 0; if t.x` list live while honesty dead | honesty / query / list `cai-dead` | no |
| 8 | `del T.x; if T.x` list `kind=def` while honesty AttributeError | honesty AttributeError; query `import failed`; list has no `delattr.parse` | no |
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

No `Cellar`, no `lib/python`. List mode `count 2` leftover + moved. After `isolated_import`, `sys.modules['ast']` is Homebrew 3.14 `ast.py` again (`restored True`). Isolate claim holds for the ungated fixture. (In-process `load_query` prints inside `isolated_import` are swallowed by its stdout redirect; CLI leftover from `/tmp` is the isolate evidence.)

### `also` does not execute siblings

`keep.py` leftover def, `killer.py` `sys.exit(9)` plus `def parse`, `side.py` writes `SIDE`, `osexit.py` `os._exit(11)`. `--from keep parse` rc=0, body `'kept'`, `also killer.parse` / `also osexit.parse` / `also side.parse`, `SIDE` does not exist. `aaa_patch.py` does not rewrite `--from pkg_util`: `kind=def`, source still `legacy`.

### Leftover `sys.py` / `io.py` / `encodings.py` / `os.py` is not `kind=def`

Honesty `from sys import parse` is ImportError. bindname `--from sys parse` rc≠0, stderr `sys has no name parse`, no leftover-sys body. `io` / `encodings` / `os` / `builtins` same. Mutate-5/6 refuse holds.

### Leftover frozen submodule `importlib.util` is not `kind=def`

Honesty `from importlib.util import parse` cannot bind (frozen). bindname `--from importlib.util parse` rc≠0, `importlib.util has no name parse`, no leftover-util body. `importlib.machinery` same (MATCH refuse). Mutate-6 item 1 holds.

### Leftover `importlib.py` file / leftover `importlib.abc` / leftover `importlib/` package still helper

Honesty leftover-importlib-file / leftover-importlib-abc / leftover-importlib-pkg. bindname `kind=def`, `file importlib.py` / `importlib/abc.py` / `importlib/__init__.py`, no Cellar. Honor KILL 6 does not fire. Leftover `tokenize.py` still leftover helper. Leftover `json.py` / `pathlib.py` / `inspect.py` / `typing.py` / `dataclasses.py` / `warnings.py` / `contextlib.py` / `argparse.py` / `tempfile.py` / `subprocess.py` / `typing_extensions.py` / `json.decoder` / `importlib.resources` / `importlib.metadata` MATCH leftover helper. Preimported / frozen `enum` / `operator` / `functools` / `abc` / `types` / `re` / `collections` / `copyreg` / `site` / `zipimport` / `collections.abc` / `os.path` / `encodings.utf_8` MATCH refuse.

### Mutate-13 claimed instance-follow / missing-attr If / class-body outer still matches query

`class T: x = 1; t = T(); T.x = 0; if t.x` list is `cai-dead`. Inverse new class attr `T.y = 1; if t.y` list is `icy-live`. Instance setattr still shadows (`t.x = 1; T.x = 0; if t.x` is `sk-live`). Two instances `t1.x = 0; if t2.x` list is `ti-live`. `t = T(); T.x = 0; if t.x` without else is **not** a list bind. `t = T(); del T.x; if t.x: def parse` without else is **not** a list bind.

`del T.x; if T.x: def parse` without else: honesty AttributeError; query `import failed`; list has no `delattr.parse`. `obj = T; del obj.x; if T.x: def parse` without else same (alias delete).

`flag = True; class T: x = flag; if T.x` list is `outer-live`. Sequential `class T: x = 1; class U: y = T.x; if U.y` list is `co2-live`. Class-body tuple unpack `class T: x, y = 1, 0; if T.x` list is `cu-live`.

Unpack / For Attribute targets MATCH as a side-effect of `_bind_target` Attribute: `T.x, T.y = 0, 0; if T.x` list is `ua-dead`. `T.x, = (0,)` list is `uoa-dead`. `for T.x in [0]:` then `if T.x` list is `fa-dead`. `for T.x in [0]: def parse` list is `fab-live`. `T.x = T.y = 0` still `ma2-dead`.

`class T: x = 1; T.x = 0; if T.x` list is still `cas-dead`. `t = T(); t.x = 0; if t.x` list is still `ias-dead`. `if [x for y in [[1]] for x in y]` / `if f'{1!s:s}'` / `for _ in (x for x in [1])` / `if f'{1:d}'` still match.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. Instance-follows-class / missing-attr If without else / class-body outer reads is the mutate-13 object. Remaining class-body If/For / method sentinel / Name-bases / Delete-Name / missing-attr If-else below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after mutate-13 instance-follows-class / missing-attr If / class-body outer reads, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if (x for x in []):` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `t = T(); if t.x:` / `if (lambda: 0):` / `if [1][0]:` / `if f'{1}':` / `if f'{1:d}':` / `if f'{1!s:s}':` / `if [*[1]]:` / `for _ in (x for x in [1]):` / `if [x for y in [[1]] for x in y]:` / `class T: x = 1; T.x = 0; if T.x:` / `t = T(); T.x = 0; if t.x:` / `flag = True; class T: x = flag` / `class U: y = T.x` / `T.x, T.y = 0, 0` / `for T.x in [0]:` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-13. It is real. List last-wins of remaining const-known class-body If/For / FunctionDef sentinel / Name-bases / Delete-Name / missing-attr If-else are not honesty leftover-identity.

---

## Implementation

### 1. Class body still does not walk const If / For / walrus

`update_const_env` on ClassDef body only handles Assign / AnnAssign / Delete. Const-known If inside the class is a no-op.

```python
# classifbody.py
class T:
    if True:
        x = 1
if T.x:
    def parse(x):
        return 'cif-live'
else:
    def parse(x):
        return 'cif-dead'
```

Honesty / query `'cif-live'`. List `cif-dead` (`T.x` missing → `_ATTR_MISSING` → polarity dead → orelse). `class T: for _ in [1]: x = 1; if T.x` same (`cfb-dead`). `class T: if (x := 1): y = x; if T.y` same (`cw-dead`). `class T: if True: x: int = 1; if T.x` same (`cai2-dead`). `class T: if False: x = 1; else: x = 0; if T.x` both dead (accidental MATCH, not a walk).

Walk const-known If / For inside ClassDef with the same polarity / first-item bind as module. Do not exec While. Do not unroll For.

### 2. FunctionDef / AsyncFunctionDef names are not stored on the class

```python
# methodtruthy.py
class T:
    def go(self):
        return 0
if T.go:
    def parse(x):
        return 'mt-live'
else:
    def parse(x):
        return 'mt-dead'
```

Honesty / query `'mt-live'` (function is truthy). List `mt-dead`. `t = T(); if t.go` same (`im-dead`). `async def go` (`am-dead`). `@classmethod` / `@staticmethod` same (`cm-dead` / `sm-dead`). Store a truthy sentinel for FunctionDef / AsyncFunctionDef names on the class namespace (do not exec the body or the decorator). Keep `__init__` as `_has_init` so `T()` stays `_MISSING` (do not exec `__init__`).

### 3. Subclass Name bases do not copy const attrs

```python
# classbase.py
class T:
    x = 1
class U(T):
    pass
if U.x:
    def parse(x):
        return 'cb-live'
else:
    def parse(x):
        return 'cb-dead'
```

Honesty / query `'cb-live'`. List `cb-dead`. `t = U(); if t.x` same (`sbi-dead`). `class U(T): x = 0; if U.x` already MATCH (`sbo-dead`, own assign). `class U(*(T,)): pass; if U.x` same family (`bs-dead`). When a base is a Name (or a const tuple/star of Names) bound to a `_Cls`, copy those const attrs into the subclass. Do not exec metaclass / decorators / `type(...)`. Nested class `class T: class U: y = x` must **not** see `T.x` as a Name (`y = x` is a global lookup; honesty NameError) — do not leak class-body names into nested class env.

### 4. Delete of a Name is a no-op; missing-attr If with else still last-wins orelse

`del T.x` without else is not a list bind (Honor KILL 8). `_ATTR_MISSING` is polarity `"dead"`, which still walks orelse.

```python
# delattreelse.py
class T:
    x = 1
del T.x
if T.x:
    def parse(x):
        return 'dae-live'
else:
    def parse(x):
        return 'dae-dead'
```

Honesty / query `has no name`. List `kind=def` (`dae-dead`). `x = 1; del x; if x: def parse` without else: Delete of Name is a no-op in `update_const_env` (only Attribute is handled), so list last-wins the body (`kind=def`) while honesty NameError. With else, list last-wins else.

Pop Name targets on Delete. After a known `_Cls` / `_Inst` loses an attr, `if T.x` is an AttributeError: skip **both** If branches (not polarity-dead orelse). Unknown names stay both. Do not exec. Do not claim list matches import failure for `assert False` / `raise` (declared).

### 5. Declared parks this cut (probed, not MUTATE)

- Nested defs (specimen-012 `test_a` inside `run()`): list `test_order.test_a`; `--from run_orders test_a` has no name.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign / `importlib.import_module` / `__dict__` / `itemgetter` / `[pkg_parse.parse][0]` / lambda wrap: honesty moved; `--from` follows; `--file` does not. Constant-getattr / getattr-with-default / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute already follow.
- FIFO `--file` remains `not a file` (0.040s).
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
- While: `while True: def parse; break` list miss while query live; `while False:` both miss. Do **not** exec While. Do not unroll.
- for-else after `break` (no break proof): honesty `feb-live`; list last-wins else.
- `for x in [0, 1]: if x: def parse` (For walks first item only; no unroll): honesty live; list miss. Do not unroll For.
- `for _ in range(1):` Call iterator (declared). Unknown Call currently walks body (`range(1)` accidental live; `range(0)` list `kind=def` while query has no name). Do not walk Call iterators.
- Format errors (`if f'{1:s}':` / `if f'{1!s:d}':` without else): honesty ValueError; list both because spec stays `_MISSING`. Do not claim list matches import failure.
- `T()` when the class body has `__init__`: Call stays `_MISSING` (both). Empty `def __init__(self): pass` then `t = T(); if t.x` honesty live; list last-wins `ei-dead`. `__init__` that zeros `x` then `if t.x: def parse` without else: query `has no name`; list `kind=def`. Do **not** exec `__init__`.
- Const Subscript / slice assign (`xs[0] = 0` / `d[1] = 0` / `xs[:] = []` / `T.x[0] = 0`): honesty dead; list last-wins live. Declared this cut. Do not exec Call. Do not fold AugAssign.
- `if __file__:` / `if __name__:` list last-wins else as dead while query is live. Scan-known, but injecting `__file__`/`__name__` is a new env seed, not this cut's object. Leave parked unless a later cut seeds them without executing the module.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` / Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'{1}':` / `if f'{1:d}':` / `if f'{1!s:s}':` / nested unpack `flag, (other,) = True, (True,)` / starred unpack `flag, *rest = True, True` / starred collections `if [*[1]]:` / For-body `for _ in [1]: def parse` / Attribute `if (1).real:` / class attr `if T.x:` / post-class `T.x = 0; if T.x:` / identity ListComp `if [x for x in [1]]:` / GeneratorExp-If `if (x for x in []):` / nonempty genexp-For `for _ in (x for x in [1]):` / SetComp `if {x for x in [1]}:` / DictComp / filtered ListComp / multi-generator `if [x for y in [[1]] for x in y]:` / no-arg `t = T(); if t.x:` / `if (lambda: 0):` / `t = T(); T.x = 0; if t.x` / `T.x, T.y = 0, 0` / `class U: y = T.x` / `del T.x; if T.x:` without else skip; `class T: if True: x = 1` / `class T: def go` / `class U(T)` / `del x; if x` / `del T.x; if T.x:` with else / `xs[0] = 0; if xs[0]` still last-wins both); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-13 made `t = T(); T.x = 0; if t.x` / `del T.x; if T.x` without else / `flag = True; class T: x = flag` list match query. Unpack / For Attribute and sequential `class U: y = T.x` match as the same const-env join. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded class-body-without-If-walk + method-without-sentinel + subclass-without-bases + Delete-Name-noop + missing-attr-as-false is the new ceiling:

- List last-wins `class T: if True: x = 1; if T.x:` / `class T: for _ in [1]: x = 1; if T.x` / `class T: if (x := 1): y = x; if T.y` else as dead while query is live.
- List last-wins `class T: def go(self): pass; if T.go` / `t = T(); if t.go` / `async def go` / `@classmethod` / `@staticmethod` else as dead while query is live.
- List last-wins `class U(T): pass; if U.x` / `t = U(); if t.x` else as dead while query is live.
- List `x = 1; del x; if x: def parse` without else as `kind=def` while query has no name. List `del T.x; if T.x: … else: def parse` as `kind=def` while query has no name.
- Const Subscript / slice assign stays declared (not this cut).
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try / assert / raise that can run, match without a static subject, lambda **bind** vs list, AugAssign / Call in If tests, While, for-else after break, For first-item only, Call For-iter, `T()` with `__init__`, format-error JoinedStr stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List last-wins of remaining const-known class-body If/For / FunctionDef sentinel / Name-bases / Delete-Name / missing-attr If-else are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list last-wins a const-live `class T: if True: x = 1; if T.x:` else / `if T.go` else / `class U(T): pass; if U.x` else as dead, or that list-binds `del x; if x: def parse` / `del T.x; if T.x: … else: def parse` while query has no name.

1. **Class-body const If / For / walrus.** `class T: if True: x = 1; if T.x:` orelse is dead; list currently last-wins `cif-dead` while query is live. `class T: for _ in [1]: x = 1; if T.x` orelse is dead (`cfb-dead`). `class T: if (x := 1): y = x; if T.y` orelse is dead (`cw-dead`). `class T: if True: x: int = 1; if T.x` orelse is dead (`cai2-dead`). Walk const-known If inside ClassDef with the same polarity as module If. Walk const-known For first-item the same as module For. Keep sequential `class U: y = T.x` / `flag = True; class T: x = flag` (already MATCH via `_ChainEnv`). Do not exec While. Do not unroll For. Nested class `class T: class U: y = x` must not treat `x` as `T.x` (honesty NameError).

2. **FunctionDef sentinel on the class.** `class T: def go(self): return 0; if T.go` orelse is dead; list currently last-wins `mt-dead`. `t = T(); if t.go` / `async def go` / `@classmethod def go` / `@staticmethod def go` same. Store a truthy sentinel for FunctionDef / AsyncFunctionDef names (do not exec body or decorator). Keep `__init__` as `_has_init` so `T()` stays `_MISSING` (do not exec `__init__`). Keep non-`__init__` methods from blocking the instance copy (`async def go` then `if t.x` already MATCH).

3. **Name bases copy const attrs.** `class T: x = 1; class U(T): pass; if U.x` orelse is dead; list currently last-wins `cb-dead`. `t = U(); if t.x` orelse is dead (`sbi-dead`). `class U(*(T,)): pass; if U.x` same (`bs-dead`). When a base is a Name bound to a `_Cls` (or a const tuple/star of such Names), copy those const attrs into the subclass. Own subclass assigns already match (`class U(T): x = 0`). Do not exec metaclass, decorators, or `type(...)`.

4. **Delete Name, and missing-attr If skips both branches.** `x = 1; del x; if x: def parse` without else: query `has no name`; list currently `kind=def`. `del T.x; if T.x: live else: dead`: query `has no name`; list currently `kind=def` (`dae-dead`) because `_ATTR_MISSING` is polarity `"dead"` and orelse still runs. Pop Name targets on Delete. After a known `_Cls` / `_Inst` loses an attr, skip **both** If branches (not polarity-dead orelse, not `_MISSING` both). Keep `del T.x; if T.x: def parse` without else as not a list bind (already MATCH). Unknown names stay both. Do not exec.

5. **Tests the current suite cannot see.** `class T: if True: x = 1; if T.x` list is live not `cif-dead`; `class T: def go(self): pass; if T.go` list is live; `class U(T): pass; if U.x` list is live; `t = U(); if t.x` list is live; `x = 1; del x; if x: def parse` without else is not a list bind; `del T.x; if T.x: live else: dead` is not a list bind; `t = T(); T.x = 0; if t.x` list is still dead; `del T.x; if T.x: def parse` without else is still not a list bind; `flag = True; class T: x = flag` list is still live; `class U: y = T.x; if U.y` list is still live; `T.x, T.y = 0, 0; if T.x` list is still dead; `class T: x = 1; T.x = 0; if T.x` list is still dead; `t = T(); t.x = 0; if t.x` list is still dead; `if [x for y in [[1]] for x in y]` list is still live; `if f'{1!s:s}'` list is still live; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `for _ in [1]` / `if (1).real` / `if T.x` / `if [x for x in [1]]` / `if (x for x in [])` / `if {x for x in [1]}` / `if [x for x in [1] if x]` / `t = T(); if t.x` after `class T: x = 1` / `if (lambda: 0)` / `for _ in (x for x in [1]):` list bind / `for _ in (x for x in []):` without else not a list bind / `if f'{1:d}'` list is live / `if [1][0]` / `if f'{1}'` / `if [*[1]]` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local TYPE_CHECKING still match (no regression).

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try / assert / raise that can run, match without a static subject, lambda **bind** vs list, While (do not exec), for-else after break (no break proof), For first-item only (do not unroll), Call For-iter `for _ in range(1):`, format-error JoinedStr `_MISSING`, `T()` with `__init__` `_MISSING` (do not exec `__init__`), const Subscript / slice assign (do not fold).

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, or list last-wins `t = T(); T.x = 0; if t.x:` as live while query is dead, or list-binds `del T.x; if T.x: def parse` without else while query has no name, KILL.

---

MUTATE
