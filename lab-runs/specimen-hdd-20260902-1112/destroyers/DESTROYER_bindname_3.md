# DESTROYER bindname 3

Date: 2026-09-02 16:17–16:20 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0424 worker=destroyer-bindname-3

Target (archive, post-MUTATE logical-name load):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `85f64d12c500e11d58f392da8a8c945e77255d8a79943405252e08790f94717b` (33336 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-2 (`cli_sha256_after`, 37/37). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `19a309a Record bindname mutate HEAD 6a76228.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `19a309af49118498994285072d6bd8bfa5ddec27`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 37/37 OK (1.320s / 1.322s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-2 claimed: load queried module under logical name after `drop_foreign_cache` (not `_bindname_N_*`); leftover `if __name__=='ast'` reports leftover body; submodule `from PKG import NAME` is `kind=module`; `if False` / `TYPE_CHECKING` not in `also`; latin-1 cookie scan does not self-miss; stderr redirected.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules`; `also` executes siblings; unique `__name__` still lies; THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join. Those five were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is builtin leftovers, list last-wins of dead complements, `--file` assignment alias, `runs=functools.parse`. Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname3_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

`rg import_module` / `_bindname_` on the CLI: no matches. Load path is `importlib.util.spec_from_file_location` under the logical name after `drop_foreign_cache`.

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

No `Cellar`, no `lib/python`. List mode `count 2` leftover + moved. Leftover `inspect.py` / `json.py` same shape (`leftover-inspect` / `leftover-json`, not stdlib).

In-process: `load_query` returns logical `ast`, `mod.__name__ == 'ast'` (prints inside `isolated_import` are redirected; restore after is Homebrew 3.14 `ast.py`). `sys.modules['ast']` after `isolated_import` is the original stdlib. Isolate claim holds for the ungated fixture.

### `also` does not execute siblings

`keep.py` leftover def, `killer.py` `sys.exit(9)` plus `def parse`, `side.py` writes `SIDE`, `osexit.py` `os._exit(11)`. `--from keep parse` rc=0, body `'kept'`, `also killer.parse` / `also osexit.parse` / `also side.parse`, `SIDE` does not exist. `aaa_patch.py` does not rewrite `--from pkg_util`: `kind=def`, `runs=pkg_util.parse`, source still `legacy`.

### Unique `__name__` does not lie

```python
# ast.py
if __name__ == 'ast':
    def parse(x):
        return ('name-gated-leftover', x)
```

Honesty: `('name-gated-leftover', 'z')`. bindname `--from ast parse` rc=0, `kind=def`, `runs=ast.parse`, `file ast.py`, source contains `name-gated-leftover`. Opposite branch `if __name__ != 'ast'` reports `honesty-leftover`, not `unique-only`.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. That leftover-stdlib isolate plus pairing is the object. A two-grep replica does not answer leftover `ast.py`.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after logical-name load, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`. Package relative `from .moved import parse` reexports (`pkg.util` → `pkg.moved.parse`). Namespace package `ns/keep.py` without `__init__.py` binds. Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`, not last-wins reexport. Non-UTF-8 sibling is a `miss` row, queried leftover still prints. Symlink / hardlink pairs `count 2 same_function False`. Queried stdout/stderr is not mixed into the TSV. Specimen-010 `loader.py` stdout pollution is gone.

`from pkg import parse` submodule: `kind=module`, `runs=pkg.parse`, list `count 2 same_function False` (package module vs inner `def parse`). If `__init__.py` defines `parse`, honesty's function wins over the submodule; bindname matches (`kind=def`, `file pkg/__init__.py`). latin-1 leftover does not `miss` itself. `if False` / `if TYPE_CHECKING` defs are not `also`. `import pkg_parse as parse` query is `kind=module`, `runs=pkg_parse` (mutate-2 `pkg_parse.pkg_parse` is gone).

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-2. It is real. Builtin leftover, list last-wins of dead complements, `--file` assignment alias, and `runs=functools.parse` are not honesty leftover-identity.

---

## Implementation

### 1. Leftover `sys.py` / `builtins.py` is reported as a bind honesty cannot make

Honor KILL (1) is leftover `ast.py` answering Homebrew. The inverse: a leftover file whose name is a **builtin** (`sys`, `builtins`). Honesty cannot shadow those.

Tree: `sys.py` `def parse(x): return ('leftover-sys', x)` plus `builtins.py` the same shape.

```bash
python3 -c "from sys import parse; print(parse('z'))"
# ImportError: cannot import name 'parse' from 'sys' (unknown location)
python3 "$CLI" -C "$ROOT" --from sys parse
```

```text
query	from sys import parse
bind	sys.parse
runs	sys.parse
kind	def
file	sys.py
source	"def parse(x):\n    return ('leftover-sys', x)\n"
```

rc=0. `builtins.py` same. File-shadowable stdlib (`ast` / `inspect` / `json`) still matches honesty leftover. `may_drop_cached` already refuses `sys` / `builtins`; `load_query` still `spec_from_file_location("sys", leftover)` and `sys.modules['sys'] = leftover`. Query of leftover `inspect` also lists `also sys.parse` / `also builtins.parse` — ghost binds of names that import would not bind.

This is the leftover-stdlib isolate incomplete: only path-shadowable names, not builtins. Unsupported certainty: `kind=def` for a helper `from sys import parse` never binds.

### 2. List last-binding still names dead complements mutate-2 skipped only one way

Mutate-2: `if False` / `if TYPE_CHECKING` defs are not `also`. Query of those modules is `has no name`. Host, the **complements** and Match last-wins:

```python
# nottyped.py
from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    def parse(x):
        return 'live'
else:
    def parse(x):
        return 'typed-else'
```

Honesty / `--from nottyped parse`: `'live'`. List mode `source` is `typed-else` (last line in both branches). `if not False` list is `dead-else`; query is `live-not-false`. Reverse `match` (live case first, dead case last): query `live-first`; list `dead-last`.

`iter_bind_nodes` treats only a test that **is** `False`/`0`/`TYPE_CHECKING` as dead. `if not TYPE_CHECKING` / `if not False` yields body **and** orelse; `last_hits_by_module` keeps the later line. Match yields every case. Query executes, so it is honest. List/`also` last-wins a branch that import would not bind. Mutate-2 item 3 is incomplete, not a new object.

`if flag:` / Try that can run stay (declared). Do not exec the tree to prove match patterns.

### 3. `--file` last binding of `NAME = module.NAME` is still the assignment text

Declared remaining: `importlib.import_module` inside `--file`. Host, the **static** alias is the same split without `import_module`:

```python
# assign.py
import pkg_parse
parse = pkg_parse.parse
```

Honesty: `('moved', 'z')`. `--from assign parse`: `kind=reexport`, `runs=pkg_parse.parse`, moved body. `--file assign.py parse`: `kind=assign`, `runs=assign.parse`, source `parse = pkg_parse.parse`. `dyn.py` (`m = importlib.import_module('pkg_parse'); parse = m.parse`) is the declared park: `--file` assign text, `--from` follows. `from pkg_parse import parse` in `--file` already follows.

Mutation 1 asked `--file` last binding, not mention. ImportFrom is followed. Attribute assign is not. `--file` vs `--from` on the same file disagree about which body would run.

### 4. Query `runs=functools.parse`; list does not

```python
# partialer.py
parse = functools.partial(_p, 'pre')
```

Honesty: `partial`, call `'pre z'`. `--from partialer parse`: `kind=reexport`, `runs=functools.parse` (no such name), source the assignment. List: `kind=assign`, `runs=partialer.parse`. Query vs list disagree. Mutate-2 item 5 asked this; this cut parked it (`runs=functools.parse` remains an inspect artifact).

Unwrapped decorator: `runs=decer.inner`, source is `inner` — inspect-honest about the bound object. `@wraps`: `runs=wraps.parse`, source the decorated def. `import pkg_parse as parse`: query `kind=module` (fixed). `parse = lambda`: `runs=lam.<lambda>`. `class parse` is `kind=def` and appears in `also` (a same-name bind, not a method; nested `Holder.parse` is skipped).

### 5. Declared remaining, host-confirmed (not this MUTATE)

Nested defs: specimen-012 list `test_order.test_a` only, `same_function True`. `--from run_orders test_a` → `has no name test_a`. Nested `parse` inside `run()` is not the import bind; module-level leftover is. Declared boundary.

FIFO `--file` / `/dev/stdin`: `not a file`, elapsed 0.03s, no hang. Declared.

Star / PEP 562 / `exec("def parse...")` **query** can succeed (star → `pkg_parse.parse`; pep → nested source; exec → `file <string>` empty `source`). List mode `count 1 same_function True` on the moved def only. Declared as list binds.

Huge 200 kB body: rc=0 in 0.035s, stdout 200212 bytes, starts `query\t`. Not fatal; not a pipe component.

Query of a module that `import`s `killer` still dies (`SystemExit(9)` wrapped as `import failed`) — dependency, not `also`. Parent `__init__.py` `sys.exit(7)` same. Honesty also dies.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; `if not TYPE_CHECKING` / Match all cases still last-wins); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, which honesty cannot shadow); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`. Mutate-2 made logical-name load real and stopped executing siblings. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded last-wins + inspect `runs` is the new ceiling:

- Builtin leftovers (`sys.py`) are `kind=def` while honesty is ImportError.
- List last-wins `if not TYPE_CHECKING` else / later match case; query is the live branch.
- `--file` Attribute assign is the assignment text; `--from` follows the moved body.
- Query `runs=functools.parse` vs list `kind=assign`.
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level (parent `__init__` `sys.exit`, dependency `sys.exit`) stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. Builtin leftovers and list last-wins of dead complements are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Do not grow an import tracer.

Do not keep a calculator that reports a leftover builtin as `kind=def`, or list last-wins a dead complement as the bind.

1. **Builtin leftovers honesty cannot shadow.** leftover `sys.py` / `builtins.py`: honesty `from sys import parse` is ImportError. bindname must not print `kind=def` leftover. Do not `spec_from_file_location` over a builtin module name. Report miss / `has no name`. `also` must not list those ghosts. Path-shadowable stdlib (`ast`, `inspect`, `json`) stays the leftover helper. If this is done by answering leftover `ast.py` as Homebrew `ast.parse`, that is a regression — KILL.

2. **List last-binding of dead complements matches query.** `if not TYPE_CHECKING` / `if not False` orelse is dead; list currently last-wins `typed-else` / `dead-else` while `--from` is live. Reverse `match` (live case first) list last-wins `dead-last`. Static last-binding must not name a branch query would not bind. `if False` / `TYPE_CHECKING` skip stays. If/Try that can run stay. Do not execute siblings to prove match patterns.

3. **`--file` last binding of `NAME = module.NAME`.** `parse = pkg_parse.parse` honesty is the moved body. `--from` already follows; `--file` must follow Attribute assign the same way ImportFrom is followed. `importlib.import_module` inside `--file` remains out of scope (declared). FIFO `--file` remains `not a file` (declared).

4. **Query `runs` / `kind` for `functools.partial`.** Do not invent `functools.parse`. List already `kind=assign` `runs=partialer.parse`. Query must not disagree. Unwrapped decorator `runs=decer.inner` may stay inspect-honest about the bound object, or be stated. `import mod as NAME` query `kind=module` already holds. `also` is other independent defs; `class parse` is a bind, nested methods are not.

5. **Tests the current suite cannot see.** leftover `sys.py` vs honesty ImportError; leftover `builtins.py` same; `if not TYPE_CHECKING` list is live not `typed-else`; reverse match list vs query; `--file` `parse = pkg_parse.parse` follows moved body; partial query `runs` is not `functools.parse`.

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or unique `__name__` lies again (`if __name__=='ast'` leftover is unique-only / missing), KILL.

---

MUTATE
