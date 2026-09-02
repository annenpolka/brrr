# DESTROYER bindname 15

Date: 2026-09-02 21:03–21:14 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0630 worker=destroyer-bindname-15

Target (archive, post-MUTATE-15 class-body For/Match/walrus / `_ATTR_MISSING` through operators):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `9fbf4f6e466abcd39c6a9f64474c3574c64a8ade2cacf2f1f26f19f468c6d6e5` (68040 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-15 (`cli_sha256_after`, 112/112; worker `mutate-bindname-15` job-0619). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `e0c4da8 Record bindname mutate HEAD f341558.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `e0c4da8f89f4c9fe33f23b7222fd231142301615`. Mutate-15 commit `f341558de47cfebd6f7c2d6cc3738c606f0bf88c`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited this pass.

`python3 tests/test_bindname.py` twice — 112/112 OK (12.269s / 12.342s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `_2` through `_14` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-15 claimed: class-body const For / nested If / Match; If-test walrus on empty `_ChainEnv`; `_ATTR_MISSING` through Not/BoolOp/Compare/BinOp/Subscript/IfExp.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; `del T.x; if T.x: … else:` list `kind=def` while honesty AttributeError; `del x; if x:` list `kind=def` while honesty NameError; `t = T(); T.x = 0; if t.x` list live while honesty dead; THIN_WRAPPER of two greps. Those ten were host-executed. They do **not** fire (`HONOR_ANY False`). Mutate-15 leftover-identity claims all MATCH (`AST_STATIC_DIVERGES []`). Remaining misses are declared parks that would require executing user code or a new object (FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While). Decision: **KEEP**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname15_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

`rg import_module` / `_bindname_` on the CLI: no matches. Load path is `importlib.util.spec_from_file_location` under the logical name after `drop_foreign_cache`.

| # | condition | host | fire? |
|---|-----------|------|-------|
| 1 | leftover `ast.py` reports Cellar / `lib/python` `ast.parse` | leftover body `('leftover-ast', x)`, `file ast.py`, no Cellar | no |
| 2 | load uses `import_module` against `sys.modules` | `has_import_module False`; `spec_from_file_location` | no |
| 3 | `also` executes siblings (`sys.exit` in `killer.py` hijacks `--from keep`) | rc=0 body `'kept'`; `SIDE` does not exist | no |
| 4 | leftover `io.py` / `sys.py` is `kind=def` while honesty ImportError | `io` / `encodings` / `os` / `sys` / `builtins` all `has no name` | no |
| 5 | leftover `importlib.util` is `kind=def` while honesty cannot bind | honesty cannot bind; CLI `has no name`; `importlib.machinery` same | no |
| 6 | leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper | both `kind=def` leftover helper, no Cellar | no |
| 7 | `del T.x; if T.x: … else:` list `kind=def` while honesty AttributeError | honesty AttributeError; query `import failed`; list has no bind | no |
| 8 | `del x; if x:` list `kind=def` while honesty NameError | honesty NameError; query `import failed`; list has no bind | no |
| 9 | `t = T(); T.x = 0; if t.x` list live while honesty dead | honesty / query / list `cai-dead` | no |
| 10 | THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join | naive `inspect.getsource(ast.parse)` from `/tmp` is Cellar; bindname leftover + `also pkg_parse.parse` | no |

Leftover `tokenize.py` still leftover helper. Leftover `json.py` / `pathlib.py` / `inspect.py` / `typing.py` / `dataclasses.py` / `warnings.py` / `contextlib.py` / `argparse.py` / `tempfile.py` / `subprocess.py` / `typing_extensions.py` / `json.decoder` / `importlib.resources` / `importlib.metadata` MATCH leftover helper. Preimported / frozen `enum` / `operator` / `functools` / `abc` / `types` / `re` / `collections` / `copyreg` / `site` / `zipimport` / `collections.abc` / `os.path` / `encodings.utf_8` / `importlib.machinery` MATCH refuse.

---

## Mutate-15 claimed leftover-identity MATCH

Host `check_list_vs_honesty` on the archive after mutate-15:

| fixture | honesty / query | list |
|---|---|---|
| `class T: for _ in [1]: x = 1; if T.x` | `cfb-live` | live |
| `class T: if True: for _ in [1]: x = 1; if T.x` | `cifor-live` | live |
| `class T: for _ in []: x = 1; else: x = 0; if T.x` | `cff2-dead` | dead |
| `class T: if True: if True: x = 1; if T.x` | `cni-live` | live |
| `class T: match 1: case 1: x = 1; if T.x` | `cmh-live` | live |
| `class T: if (x := 1): y = x; if T.y` | `cw-live` | live |
| `class T: y = (x := 1); if T.x` | `cwa-live` | live |
| `del T.x; if not T.x: … else:` | AttributeError | no bind |
| `del T.x; if T.x or True` / `and` / `==` / `+` / `[0]` / IfExp | AttributeError | no bind |
| `del x; if not x: … else:` | NameError | no bind |
| `del T.x; if T.x: … else:` / `del x; if x:` | no name | no bind |
| `t = T(); T.x = 0; if t.x` | `cai-dead` | dead |
| `class T: class U: y = x; if T.U.y` | NameError | no bind |

`AST_STATIC_DIVERGES []`. Attack `DIVERGE_COUNT 4` is not leftover-identity: attack-fixture `multiset` has a syntax typo (`{x for y in [[1]] for x in y]:`); `lambda_` query vs honesty print is the declared lambda-bind park.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if (x for x in []):` / `if {x for x in [1]}:` / `if {x: x for x in [1]}:` / `if [x for x in [1] if x]:` / `t = T(); if t.x:` / `if (lambda: 0):` / `if [1][0]:` / `if f'{1}':` / `if f'{1:d}':` / `if f'{1!s:s}':` / `if [*[1]]:` / `for _ in (x for x in [1]):` / `if [x for y in [[1]] for x in y]:` / `class T: x = 1; T.x = 0; if T.x:` / `t = T(); T.x = 0; if t.x:` / `flag = True; class T: x = flag` / `class U: y = T.x` / `T.x, T.y = 0, 0` / `for T.x in [0]:` / nested unpack / `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target / `del T.x; if T.x:` skip both / `del x; if x:` skip both / `class T: if True: x = 1` / `class T: for _ in [1]: x = 1` / nested class-body If / class-body Match / If-test walrus / `del T.x; if not T.x` skip both list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-15. It is real. Remaining list miss / last-wins are declared parks, not honesty leftover-identity that AST-static const-env can cut without executing user code.

---

## Declared parks this cut (probed, not MUTATE)

- FunctionDef / AsyncFunctionDef / `@classmethod` / `@staticmethod` sentinel on the class: `class T: def go(self): return 0; if T.go` honesty / query `'mt-live'`; list miss. Storing a truthy sentinel is a new object next to `_has_init`; do not exec the body or the decorator. Keep `__init__` as `_has_init` so `T()` stays `_MISSING`.
- Name bases: `class U(T): pass; if U.x` honesty / query `'cb-live'`; list miss. `t = U(); if t.x` / `class U(*(T,)): pass` same. Copying const attrs from a Name base is a new object. Do not exec metaclass / decorators / `type(...)`. Own subclass assigns already MATCH (`class U(T): x = 0` is `sbo-dead`).
- Nested defs (specimen-012 `test_a` inside `run()`): list `test_order.test_a`; `--from run_orders test_a` has no name.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign / `importlib.import_module` / `__dict__` / `itemgetter` / `[pkg_parse.parse][0]` / lambda wrap: honesty moved; `--from` follows; `--file` does not. Constant-getattr / getattr-with-default / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute already follow.
- FIFO `--file` remains `not a file` (0.04s).
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
- `if __file__:` / `if __name__:` list last-wins else as dead while query is live. Scan-known, but injecting `__file__`/`__name__` is a new env seed, not this cut's object.

EXEC_PARK from the host log: `list_initzero` / `list_initlive` / `list_initonly` / `list_emptyinit` / `list_subassign` / `list_dictassign` / `list_sliceassign` / `list_methodtruthy` / `list_instmethod` / `list_classbase` / `list_txlistsub` / `list_whiletrue` / `list_subclassinst` / `list_asyncmethod` / `list_classmethod_` / `list_staticmethod_` / `list_basesstar` / `list_classwhile`.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` / Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'{1}':` / `if f'{1:d}':` / `if f'{1!s:s}':` / nested unpack / starred unpack / starred collections / For-body `for _ in [1]: def parse` / Attribute `if (1).real:` / class attr `if T.x:` / post-class `T.x = 0; if T.x:` / identity ListComp / GeneratorExp-If / nonempty genexp-For / SetComp / DictComp / filtered ListComp / multi-generator / no-arg `t = T(); if t.x:` / `if (lambda: 0):` / `t = T(); T.x = 0; if t.x` / `T.x, T.y = 0, 0` / `class U: y = T.x` / `del T.x; if T.x:` skip both / `del x; if x:` skip both / `class T: if True: x = 1` / `class T: for _ in [1]: x = 1` / `class T: if True: if True: x = 1` / `class T: match 1: case 1: x = 1` / `class T: if (x := 1): y = x` / `del T.x; if not T.x` skip both / FunctionDef sentinel / Name-bases / Subscript assign / While stay last-wins or miss); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-15 made class-body For / nested If / Match / If-test walrus list match query, and `_ATTR_MISSING` through operators skip both. Unpack / For Attribute and sequential `class U: y = T.x` still match as the same const-env join. That is why this is not KILL and not THIN_WRAPPER.

Remaining ceiling is declared parks, not a const-known leftover-identity lie:

- FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While stay declared (would require executing user code or a new object).
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try / assert / raise that can run, match without a static subject, lambda **bind** vs list, AugAssign / Call in If tests, While, for-else after break, For first-item only, Call For-iter, `T()` with `__init__`, format-error JoinedStr stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. Remaining list miss of FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While is parked, not a new identity lie this cut can close without becoming an interpreter.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list-misses a const-live `class T: for _ in [1]: x = 1; if T.x:` / nested class-body If / class-body Match / If-test walrus, or that list-binds `del T.x; if not T.x: … else:` / `if T.x or True` while query has no name. Those are MATCH after mutate-15.

Nothing this cut: remaining parks require executing user code (`__init__` / While / Call / AugAssign / assert / raise) or a new object (FunctionDef sentinel next to `_has_init`; Name-base attr copy). Do not exec. Do not unroll For. Nested class `class T: class U: y = x` honesty NameError; already MATCH.

Keep declared boundaries listed above.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, or list last-wins `t = T(); T.x = 0; if t.x:` as live while query is dead, or list-binds `del T.x; if T.x: … else:` / `del x; if x:` / `del T.x; if not T.x: … else:` while query has no name, KILL.

---

KEEP
