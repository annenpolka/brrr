# DESTROYER bindname 5

Date: 2026-09-02 17:14–17:27 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0485 worker=destroyer-bindname-5

Target (archive, post-MUTATE-5 already-imported / frozen leftover refuse):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `ba3237304c2b09c9c346832cd0ebc3258c9915d4f62669cbac4b093c9b0a920f` (47191 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-4 (`cli_sha256_after`, 57/57; worker `mutate-bindname-5` job-0468). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `d3ff9dc Record bindname mutate HEAD 2d35105.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `d3ff9dc660f0ebb89c13bae3e37a271e25d3e288`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 57/57 OK (4.586s / 4.556s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-5 claimed: leftover `io.py` / `encodings.py` / `os.py` is not `kind=def` while honesty is ImportError; leftover `tokenize.py` is leftover helper not `tokenize.open` miss; list last-wins live of const-known `if flag:` / `if 1 == 1` / TYPE_CHECKING alias; `--file` `getattr(module, 'NAME')` / `NAME = alias` follows moved body.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `encodings.py` / `os.py` is `kind=def` while honesty is ImportError; leftover `sys.py` is `kind=def` while honesty ImportError; THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join. Those six were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is frozen *submodule* leftovers (`importlib.util` / `importlib.machinery`) honesty cannot shadow, list last-wins of const-known `if 1 + 1` / empty-collection `if []:` (including `if []: def parse` without else as list `kind=def` while query has no name). Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname5_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

`rg import_module` / `_bindname_` on the CLI: no matches. Load path is `importlib.util.spec_from_file_location` under the logical name after `drop_foreign_cache`. `unshadowable_reason` is builtin / `_imp.is_frozen(top)` / `interpreter_preimported()` (subprocess `sys.modules` listing, cwd `/`, not `import_module` of the query).

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

### Leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` is not `kind=def`

Honesty `from sys import parse` is ImportError (`unknown location`). bindname `--from sys parse` rc≠0, stderr `sys has no name parse`, no leftover-sys body. `builtins.py` same. `from io import parse` honesty ImportError names Cellar `io.py`; bindname `io has no name parse`, no leftover-io body, no `os.stat` poison. `encodings.py` / `os.py` same. List `miss	io.py	imported` (and encodings/os/sys/builtins), `count 1` on the moved def only. Mutate-5 item 1 holds for the named already-imported / frozen / builtin tops.

### Leftover `tokenize.py` is leftover helper, not `tokenize.open` miss

Honesty `from tokenize import parse; parse('z')` is `('leftover-tokenize', 'z')`. Query `kind=def`, `file tokenize.py`, source leftover, `also pkg_parse.parse`, no `tokenize.open` miss, no Cellar. Mutate-5 tokenize claim holds. Top-level leftover-stdlib sweep of ~130 names: **zero** honesty/CLI divergences (`SWEEP_diverge []`). Path-shadowable leftovers (`ast` / `inspect` / `json` / `pathlib` / `typing` / `tokenize` / `importlib` file) still bind. Builtin / frozen / preimported tops still miss.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. That leftover-stdlib isolate plus pairing is the object. A two-grep replica does not answer leftover `ast.py`. Frozen-submodule leftovers below are incomplete isolate, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after already-imported / frozen-*top* refuse, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` `--file` follows. `from pkg_parse import parse as p; parse = p` `--file` follows. `getattr(pkg_parse, 'parse', None)` / `builtins.getattr(pkg_parse, 'parse')` `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`. List agrees.

`flag = True; if flag:` / `if 1 == 1` / `if __debug__` / `if (flag := True)` / `from typing import TYPE_CHECKING as TC; if not TC` list source is live, not the dead else. `if not TYPE_CHECKING` / reverse `match` stay. `if True and False` last-wins else matches query.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`, not last-wins reexport. Non-UTF-8 sibling is a `miss` row. Symlink / hardlink pairs `count 2 same_function False`. Queried stdout/stderr is not mixed into the TSV. Specimen-010 `loader.py` stdout pollution is gone. `if __name__ == '__main__'` leftover takes the import-body. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-5. It is real. Frozen *submodule* leftovers and list last-wins of const-known BinOp / empty-collection If tests are not honesty leftover-identity.

---

## Implementation

### 1. Leftover frozen submodule is reported as a bind honesty cannot make

Honor KILL (4) is leftover `io.py` / `encodings.py` / `os.py` answering `kind=def`. Mutate-5 special-cased `sys.builtin_module_names`, `_imp.is_frozen(top)`, and a fresh interpreter's `sys.modules` **top** names. The inverse that remains: a leftover file whose **full** module name is frozen, while the parent top is path-shadowable.

`_imp.is_frozen`: `importlib` False, `importlib.util` True, `importlib.machinery` True, `importlib.abc` False. Fresh `python3 -c` does **not** have `importlib` in `sys.modules`, so leftover `importlib.py` / leftover `importlib/` package honesty **does** bind.

Tree: `importlib/__init__.py` leftover parse, `importlib/util.py` leftover parse, `importlib/machinery.py` leftover parse, `importlib/abc.py` leftover parse.

```bash
python3 -c "from importlib import parse; print(parse('z'))"
# ('leftover-importlib', 'z')
python3 -c "from importlib.util import parse; print(parse('z'))"
# ModuleNotFoundError: No module named 'importlib._abc'
# (traceback File "<frozen importlib.util>")
python3 "$CLI" -C "$ROOT" --from importlib.util parse
```

```text
query	from importlib.util import parse
bind	importlib.util.parse
runs	importlib.util.parse
kind	def
file	importlib/util.py
source	"def parse(x):\n    return ('leftover-importlib-util', x)\n"
```

rc=0. Host, same shape for leftover `importlib.machinery` (`<frozen importlib.machinery>` / `importlib._bootstrap` miss; bindname `kind=def` leftover-mach). Leftover `importlib` package and leftover `importlib.abc` (`is_frozen` False) honesty leftover and bindname leftover — match. Leftover `importlib.py` **file** honesty leftover-importlib-file; bindname `kind=def` — match.

`unshadowable_reason` uses `top = modname.split(".", 1)[0]` then `_imp.is_frozen(top)`. Frozen **submodules** of a shadowable parent are loaded via `spec_from_file_location`. That is leftover-stdlib isolate incomplete: frozen check is the top name only.

Do not refuse leftover `importlib.py` / leftover `importlib/` package that honesty **does** bind. If this is done by answering leftover `ast.py` as Homebrew `ast.parse`, that is a regression — KILL.

### 2. List last-binding still names dead complements of const-known BinOp / empty-collection If

Mutate-5: Name / Compare / BoolOp / walrus / `__debug__` / TYPE_CHECKING alias skip the dead branch. `static_const` has no `BinOp`, no empty `List`/`Tuple`/`Dict`/`Set`, no `IfExp`. `update_const_env` requires `len(targets)==1`.

```python
# add.py
if 1 + 1:
    def parse(x):
        return 'add-live'
else:
    def parse(x):
        return 'add-dead'
```

Honesty / `--from add parse`: `'add-live'`. List source is `add-dead` (later line; both branches yielded). Same family as mutate-5's `if 1 == 1` close.

```python
# emptyif.py
if []:
    def parse(x):
        return 'dead-only'
```

Honesty `cannot import name 'parse'`. Query rc≠0 `emptyif has no name parse`. List `count 1 same_function True` `kind=def` `dead-only`. Unsupported certainty: a bind that would not exist.

`if []:` / `if ():` with an else last-wins the live else (accidental: else is later). `flag = True if True else False; if flag:` query `ifexp-live`; list `ifexp-dead`. `flag = other = True; if flag:` query `multi-live`; list `multi-dead`. `from typing_extensions import TYPE_CHECKING as TC; if not TC:` query `'live-tex'`; list `typed-tex` (`update_const_env` only tags `typing`).

`if len([])` Call stays both branches (declared: do not exec). `n = 1; n += -1; if n:` AugAssign stays (declared ceiling). Runtime `flag = os.environ.get(...)` both branches stay (declared). Try that can run stay (query `try-body`; list last-wins `except-body`). Match without a static subject last-wins the wildcard (declared). Do not exec the tree to prove match patterns.

### 3. `--file` remaining alias shapes (declared park this cut)

Mutate-5 followed Constant-getattr and Name alias. Host, Subscript / attrgetter / dynamic getattr / IfExp assign still split:

`parse = pkg_parse.__dict__['parse']` / `parse = vars(pkg_parse)['parse']` / `parse = operator.attrgetter('parse')(pkg_parse)` / `name = 'parse'; parse = getattr(pkg_parse, name)` / `parse = pkg_parse.parse if True else None`: honesty moved body; `--from` follows `pkg_parse.parse`; `--file` is `kind=assign` the assignment text.

`importlib.import_module` inside `--file` remains the declared park. FIFO `--file` remains `not a file` (declared). Do not grow a full alias tracer this cut.

### 4. Declared remaining, host-confirmed (not this MUTATE)

Nested defs: specimen-012 list `test_order.test_a` only, `same_function True`. `--from run_orders test_a` → `has no name test_a`. Nested `parse` inside `run()` is not the import bind; module-level leftover is. Declared boundary.

FIFO `--file` / `/dev/stdin`: `not a file`, elapsed 0.038s, no hang. Declared.

Star / PEP 562 / `exec("def parse...")` **query** can succeed (star → `pkg_parse.parse`; pep → nested source; exec → `file <string>` empty `source`). List mode `count 1 same_function True` on the moved def only. Declared as list binds.

Huge 200 kB body: rc=0 in 0.061s, stdout 200190 bytes, starts `query\t`. Not fatal; not a pipe component.

Query of a module that `import`s `killer` still dies (`SystemExit(9)` wrapped as `import failed`) — dependency, not `also`. Parent `__init__.py` `sys.exit(7)` same. Honesty also dies.

Lambda query `kind=def` `runs=lam.<lambda>`; list `kind=assign` `runs=lam.parse`. Unwrapped decorator query `runs=decer.inner` source wrapper; list source the decorated def. Declared inspect-honest.

`while False:` / `for _ in ():` dead bodies are not last-wins (While/For not walked); query/list `before-while` / `before-for`. Accidental match, not a new object.

Query of leftover `tokenize.py` / leftover `ast.py` still helpers. Leftover `sys.py` / `io.py` still miss.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` skip; **BinOp `if 1 + 1` / empty `if []:` / IfExp / multi-target still last-wins both**); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **tops**, and already-imported names; **not** including frozen **submodules** of a shadowable parent such as `importlib.util`); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper. Mutate-5 made already-imported / frozen-top refuse real and stopped list last-wins of `if flag:` / `if 1 == 1`. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded frozen-top + polarity-without-BinOp/empty-collections is the new ceiling:

- Frozen submodule leftovers (`importlib.util.py`) are `kind=def` while honesty cannot bind.
- List last-wins `if 1 + 1` else / `if []:` dead-only as `kind=def` while query has no name / IfExp / multi-target assign; query is the live branch (or no name).
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body.
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level (parent `__init__` `sys.exit`, dependency `sys.exit`), Try that can run, match without a static subject, lambda vs list stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / already-imported leftover refuse, plus leftover `tokenize.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. Frozen submodule leftovers and list last-wins of const-known BinOp / empty-collection If tests are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Do not grow an import tracer.

Do not keep a calculator that reports a leftover frozen submodule as `kind=def`, or list last-wins a const-dead `if 1 + 1` else / empty `if []:` as the bind.

1. **Frozen submodule leftovers honesty cannot shadow.** leftover `importlib.util` / `importlib.machinery`: honesty `from importlib.util import parse` cannot bind (frozen). bindname must not print `kind=def` leftover. Check `_imp.is_frozen` on the **full** module name, not only the top. Do not refuse leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty **does** bind. Leftover `ast.py` / `tokenize.py` / `inspect.py` still bind the leftover helper. Builtin / frozen-top / already-imported refuse stays. If this is done by answering leftover `ast.py` as Homebrew `ast.parse`, that is a regression — KILL.

2. **List last-binding of const-known BinOp / empty-collection If tests matches query.** `if 1 + 1:` orelse is dead; list currently last-wins `add-dead` while `--from` is live. `if []:` / `if ():` body is dead; `if []: def parse` without else is not a list bind (query `has no name`). Const env already used for match subjects / Name / Compare must apply to BinOp of constants, empty List/Tuple/Dict/Set, IfExp of constants, and multi-target `flag = other = True`. `from typing_extensions import TYPE_CHECKING as TC` same as `typing` (any ImportFrom of name `TYPE_CHECKING`). `if False` / `TYPE_CHECKING` skip stays. `if flag:` with a runtime-unknown test still both branches. `if len([])` Call stays both (declared: do not exec). AugAssign stays (declared). Try that can run stay. Match patterns are AST-static; siblings are not executed.

3. **Tests the current suite cannot see.** leftover `importlib.util` vs honesty cannot bind; leftover `importlib.machinery` same; leftover `importlib.py` file still helper; leftover `importlib.abc` still helper; leftover `io.py` still miss; leftover `tokenize.py` still helper; `if 1 + 1` list is live not `add-dead`; `if []: def parse` without else list is not `kind=def` / query has no name; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` still miss.

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, Try that can run, match without a static subject, lambda query vs list, AugAssign / Call in If tests.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, KILL.

---

MUTATE
