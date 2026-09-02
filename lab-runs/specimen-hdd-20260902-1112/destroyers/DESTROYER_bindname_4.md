# DESTROYER bindname 4

Date: 2026-09-02 16:47–16:52 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0443 worker=destroyer-bindname-4

Target (archive, post-MUTATE-4 builtin leftover refuse):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `381984e8412c146ac8d59c19f45702f52130b8532e950d1643c1d15923a4eb77` (41548 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-4 (`cli_sha256_after`, 47/47). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `b16b721 Record bindname mutate HEAD 3b9fa46.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `b16b7213950d2e0d1f354276410393ffe38cc5b0`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 47/47 OK (2.101s / 2.245s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-4 claimed: leftover `sys.py` / `builtins.py` is not `kind=def` while honesty is ImportError; list last-wins live of `if not TYPE_CHECKING` / reverse match; `--file` `NAME = module.NAME` follows moved body; `functools.partial` `runs` names the wrapped callable.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings (sys.exit sibling hijacks); leftover `sys.py` / `builtins.py` is `kind=def` while honesty is ImportError; THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join. Those five were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is already-imported stdlib leftovers honesty cannot shadow (`io.py`, `encodings.py`, …), leftover `tokenize.py` / `os.py` self-hosting miss, list last-wins of const-known `if flag:` / `if 1 == 1` / TYPE_CHECKING alias. Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname4_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

`rg import_module` / `_bindname_` on the CLI: no matches. Load path is `importlib.util.spec_from_file_location` under the logical name after `drop_foreign_cache`. `is_unshadowable` is `top in sys.builtin_module_names`.

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

No `Cellar`, no `lib/python`. List mode `count 2` leftover + moved. Leftover `inspect.py` / `json.py` / `pathlib.py` / `typing.py` same shape (`leftover-inspect` / `leftover-json`, not stdlib).

In-process: `load_query` returns logical `ast`, `mod.__name__ == 'ast'`, `mod.parse('z')` is `('leftover-ast', 'z')` (prints inside `isolated_import` are redirected; capture after load is leftover). `sys.modules['ast']` after `isolated_import` is the original Homebrew 3.14 `ast.py`. Isolate claim holds for the ungated fixture.

### `also` does not execute siblings

`keep.py` leftover def, `killer.py` `sys.exit(9)` plus `def parse`, `side.py` writes `SIDE`, `osexit.py` `os._exit(11)`. `--from keep parse` rc=0, body `'kept'`, `also killer.parse` / `also osexit.parse` / `also side.parse`, `SIDE` does not exist. `aaa_patch.py` does not rewrite `--from pkg_util`: `kind=def`, `runs=pkg_util.parse`, source still `legacy`.

### Leftover `sys.py` / `builtins.py` is not `kind=def`

Honesty `from sys import parse` is ImportError (`unknown location`). bindname `--from sys parse` rc≠0, stderr `sys has no name parse`, no leftover-sys body. `builtins.py` same. List `miss	sys.py	builtin` / `miss	builtins.py	builtin`, `count 1` on the moved def only. Query of leftover `inspect` does not list `also sys.parse` / `also builtins.parse`. Mutate-4 item 1 holds for the two named builtins. `_thread` / `marshal` / `posix` / `gc` / `itertools` / `errno` / `time` same (builtin_module_names).

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. That leftover-stdlib isolate plus pairing is the object. A two-grep replica does not answer leftover `ast.py`.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after builtin refuse, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body (`runs=pkg_parse.parse`, source `strip`). `import pkg_parse as p; parse = p.parse` `--file` follows. `parse = other = pkg_parse.parse` `--file` follows. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`, not `functools.parse`. List agrees.

`if not TYPE_CHECKING` / `if not False` list source is live, not `typed-else` / `dead-else`. Reverse `match x=1` list is `live-first`, not `dead-last`. `if not not False` polarity unwraps to dead, list `nn-live`. `if True and False` last-wins else (`and-live`) matches query (accidental: else is later).

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`, not last-wins reexport. Non-UTF-8 sibling is a `miss` row. Symlink / hardlink pairs `count 2 same_function False`. Queried stdout/stderr is not mixed into the TSV. Specimen-010 `loader.py` stdout pollution is gone. `if __name__ == '__main__'` leftover takes the import-body (logical name is not `__main__`; honesty the same). Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-4. It is real. Already-imported stdlib leftovers, leftover `tokenize.py` / `os.py` self-hosting, and list last-wins of const-known If tests are not honesty leftover-identity.

---

## Implementation

### 1. Leftover `io.py` / `encodings.py` is reported as a bind honesty cannot make

Honor KILL (4) is leftover `sys.py` / `builtins.py` answering `kind=def`. Mutate-4 special-cased `sys.builtin_module_names`. The inverse that remains: a leftover file whose name is **already in `sys.modules` at process start** and is not a builtin. Honesty cannot shadow those.

Tree: `io.py` `def parse(x): return ('leftover-io', x)` plus `pkg_parse.py` moved.

```bash
python3 -c "from io import parse; print(parse('z'))"
# ImportError: cannot import name 'parse' from 'io' (.../lib/python3.14/io.py)
python3 "$CLI" -C "$ROOT" --from io parse
```

```text
query	from io import parse
bind	io.parse
runs	io.parse
kind	def
file	io.py
source	"def parse(x):\n    return ('leftover-io', x)\n"
also	pkg_parse.parse
```

rc=0. Host, same shape for leftover `encodings.py`, `codecs.py`, `types.py`, `functools.py`, `collections.py`, `posixpath.py`, `genericpath.py`, `stat.py`, `_collections_abc.py`, `_sitebuiltins.py`. Honesty ImportError names Cellar `lib/python3.14/…`. bindname `kind=def` leftover. `drop_foreign_cache` may drop those names (`may_drop_cached` is True); `load_query` still `spec_from_file_location("io", leftover)` and `sys.modules['io'] = leftover`.

Path-shadowable stdlib that honesty **does** bind from cwd (`ast` / `inspect` / `json` / `pathlib` / `typing`) still matches leftover. Builtin names still miss. The lie is reserved for already-imported non-builtins.

**leftover `os.py`:** honesty ImportError from Cellar `os.py`. Query `import failed: os: AttributeError: module 'os' has no attribute 'stat'` (drop leftover `os` poisons bindname's own `os.stat` / inspect). List still `kind=def` leftover-os, `count 2`. Query dies; list is the unsupported certainty.

**leftover `tokenize.py`:** honesty `('leftover-tokenize', 'z')` — a leftover helper that **would** bind. Query `import failed: tokenize: AttributeError: module 'tokenize' has no attribute 'open'` (`inspect.getsourcelines` uses `tokenize.open` after `drop_foreign_cache` replaced stdlib tokenize). Inverse of leftover `ast.py`: isolate hid a leftover that import would bind.

`python3 -c` preimported (host): `builtins codecs collections encodings functools os sys types` (plus `io`). Mutate-4's builtin refuse does not cover that set.

This is leftover-stdlib isolate incomplete: only `builtin_module_names`, not names a fresh `from NAME import parse` in that tree cannot bind.

### 2. List last-binding still names dead complements of const-known If tests

Mutate-4: `if False` / `TYPE_CHECKING` / `not` complements skip; match with a static subject last-wins the live case. `iter_bind_nodes` already tracks a const env for match subjects. `test_polarity` does not use that env.

```python
# flagtrue.py
flag = True
if flag:
    def parse(x):
        return 'live-flag'
else:
    def parse(x):
        return 'dead-else'
```

Honesty / `--from flagtrue parse`: `'live-flag'`. List source is `dead-else` (later line; both branches yielded). `if 1 == 1` query `eq-live`; list `eq-dead`. `if __debug__` query `debug-live`; list `debug-dead`. `if (flag := True)` query `walrus-live`; list `walrus-dead`.

`from typing import TYPE_CHECKING as TC; if not TC:` query `'live-not-tc'`; list `typed-else-tc`. `is_type_checking` looks at Name `TYPE_CHECKING`, not the alias. Mutate-4 item 2 is incomplete for aliases and for const-assigned flags the env already knows.

`try: def parse → try-body / except: def parse → except-body`: query `try-body`; list `except-body`. Declared “If/Try that can run stay” for runtime-unknown tests. Const-known If is the same last-wins lie mutate-4 closed for match.

Runtime `flag = os.environ.get(...)` both branches stay (declared). Do not exec the tree to prove match patterns.

### 3. `--file` last binding of `NAME = getattr(module, 'NAME')` / `NAME = alias`

Mutate-4 followed Attribute `parse = pkg_parse.parse`. Host, Call and Name aliases still split:

```python
# getattrer.py
import pkg_parse
parse = getattr(pkg_parse, 'parse')
```

Honesty: `('moved', 'z')`. `--from getattrer parse`: `kind=reexport`, `runs=pkg_parse.parse`, moved body. `--file getattrer.py parse`: `kind=assign`, `runs=getattrer.parse`, source `parse = getattr(pkg_parse, 'parse')`.

`from pkg_parse import parse as p; parse = p`: `--from` follows moved; `--file` is `parse = p` assign. `import pkg_parse as p; parse = p.parse` `--file` already follows (alias map). `importlib.import_module` inside `--file` remains the declared park.

### 4. Query `runs` / `kind` for lambda vs list

`parse = lambda x: ('lam', x)`: query `kind=def` `runs=lam.<lambda>`; list `kind=assign` `runs=lam.parse`. Unwrapped decorator query `runs=decer.inner` source wrapper; list source the decorated def. `@wraps` query/list agree on `wraps.parse`. Mutate-4 parked unwrapped decorator as inspect-honest. Lambda query vs list is the same inspect/static split partial used to be.

### 5. Declared remaining, host-confirmed (not this MUTATE)

Nested defs: specimen-012 list `test_order.test_a` only, `same_function True`. `--from run_orders test_a` → `has no name test_a`. Nested `parse` inside `run()` is not the import bind; module-level leftover is. Declared boundary.

FIFO `--file` / `/dev/stdin`: `not a file`, elapsed 0.03s, no hang. Declared.

Star / PEP 562 / `exec("def parse...")` **query** can succeed (star → `pkg_parse.parse`; pep → nested source; exec → `file <string>` empty `source`). List mode `count 1 same_function True` on the moved def only. Declared as list binds.

Huge 200 kB body: rc=0 in 0.038s, stdout 200190 bytes, starts `query\t`. Not fatal; not a pipe component.

Query of a module that `import`s `killer` still dies (`SystemExit(9)` wrapped as `import failed`) — dependency, not `also`. Parent `__init__.py` `sys.exit(7)` same. Honesty also dies.

Match without a static subject last-wins the wildcard (`m-wild`) while query is `m-one`. Declared.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / TYPE_CHECKING alias / Try still last-wins both); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, which honesty cannot shadow; **not** including already-imported stdlib `io` / `encodings` / `tokenize`); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` not `kind=def`. Mutate-4 made builtin refuse real and stopped list last-wins of `if not TYPE_CHECKING`. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded builtin_module_names + polarity-without-env is the new ceiling:

- Already-imported stdlib leftovers (`io.py`) are `kind=def` while honesty is ImportError.
- Leftover `tokenize.py` honesty leftover helper; query `tokenize.open` miss. Leftover `os.py` query `os.stat` miss; list `kind=def`.
- List last-wins `flag = True` else / `if 1 == 1` else / `if __debug__` else / TYPE_CHECKING alias else; query is the live branch.
- `--file` `getattr(module, 'NAME')` / `NAME = alias` is the assignment text; `--from` follows the moved body.
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level (parent `__init__` `sys.exit`, dependency `sys.exit`) stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin leftover refuse. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. Already-imported stdlib leftovers and list last-wins of const-known If tests are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` as miss / `has no name`. Do not grow an import tracer.

Do not keep a calculator that reports a leftover already-imported stdlib as `kind=def`, or list last-wins a const-dead else as the bind.

1. **Already-imported stdlib leftovers honesty cannot shadow.** leftover `io.py` / `encodings.py` / `codecs.py` / `types.py` / `functools.py` / `collections.py` / `posixpath.py` / `genericpath.py` / `stat.py` / `_collections_abc.py` / `_sitebuiltins.py`: honesty `from io import parse` is ImportError. bindname must not print `kind=def` leftover. leftover `os.py` query must not die `os.stat` and list must not `kind=def`. leftover `tokenize.py` honesty leftover helper must report that leftover (`kind=def`, `file tokenize.py`), not `tokenize.open` miss. Do not `spec_from_file_location` over a name a fresh `from NAME import parse` in that tree cannot bind — except path-shadowable leftovers honesty **does** bind (`ast`, `inspect`, `json`, `pathlib`, `typing`). Builtin refuse stays. If this is done by answering leftover `ast.py` as Homebrew `ast.parse`, that is a regression — KILL.

2. **List last-binding of const-known If tests matches query.** `flag = True; if flag:` orelse is dead; list currently last-wins `dead-else` while `--from` is live. `if 1 == 1` / `if __debug__` / `if (flag := True)` / `from typing import TYPE_CHECKING as TC; if not TC` same. Const env already used for match subjects must apply to If tests (and walrus / comparisons of constants). `if False` / `TYPE_CHECKING` skip stays. `if flag:` with a runtime-unknown test still both branches (declared). Try that can run stay, or last-wins the try body when except cannot run. Do not execute siblings to prove match patterns.

3. **`--file` last binding of `NAME = getattr(module, 'NAME')` and `NAME = alias`.** Honesty is the moved body. `--from` already follows; `--file` must follow Call-getattr / Name alias the same way Attribute assign is followed. `importlib.import_module` inside `--file` remains out of scope (declared). FIFO `--file` remains `not a file` (declared).

4. **Tests the current suite cannot see.** leftover `io.py` vs honesty ImportError; leftover `encodings.py` same; leftover `tokenize.py` honesty leftover vs query miss; leftover `os.py` list not `kind=def`; `flag = True; if flag:` list is live not `dead-else`; `if 1 == 1` list vs query; `TYPE_CHECKING as TC; if not TC` list is live; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` still miss.

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` is `kind=def` while honesty is ImportError, KILL.

---

MUTATE
