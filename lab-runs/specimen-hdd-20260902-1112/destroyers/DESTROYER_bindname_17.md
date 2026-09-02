# DESTROYER bindname 17

Date: 2026-09-02 21:43–21:49 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0658 worker=destroyer-bindname-17

Target (archive, post-MUTATE-16 BoolOp operand / mixed assign / `_ATTR_MISSING` through collections / MatchSequence):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `c7d985ed9b0ebb42f775ff3bacefc3c27e9505ff37f25a03abdd82a18609755f` (73327 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-16 (`cli_sha256_after`, 119/119; worker `mutate-bindname-16` job-0646). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `c612e8a Record bindname mutate HEAD a0a6fec.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `c612e8a6a2c2acdc8b4c2b513c9f1878f12361c2`. Mutate-16 commit `a0a6fecd978ebf6f35ea7d7347680ffa555b9174`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited this pass.

`python3 tests/test_bindname.py` twice — 119/119 OK (13.675s / 13.877s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `_2` through `_14` **MUTATE**. `_15` **KEEP**. `_16` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-16 claimed: BoolOp returns the operand; mixed Name+Attribute Assign binds each target; `_ATTR_MISSING` through List/Tuple/Set/Dict/JoinedStr/Starred/comprehension/genexp; const MatchSequence / MatchMapping / MatchStar / MatchAs capture.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `sys.py` is `kind=def` while honesty is ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; `del T.x; if T.x: … else:` list `kind=def` while honesty AttributeError; `del x; if x:` list `kind=def` while honesty NameError; `t = T(); T.x = 0; if t.x` list live while honesty dead; THIN_WRAPPER of two greps. Those ten were host-executed. They do **not** fire (`HONOR_ANY False`). Decision is not KILL. Mutate-16 leftover-identity claims all MATCH. Remaining list miss is the declared nested-class object park (`class T: class U: y = 1; if T.U.y` query live, list miss) plus FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While. Those require executing user code or a new object. Decision: **KEEP**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname17_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

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

## Mutate-16 claimed leftover-identity MATCH

Host `check_list_vs_honesty` on the archive after mutate-16:

| fixture | honesty / query | list |
|---|---|---|
| `if (1 and 2) == 2` | `ae-live` | live |
| `if (1 and 2) is True` | `ait-dead` | dead |
| `if (0 or 3) == 3` | `oe-live` | live |
| `class T: x = 1 and 2; if T.x == 2` | `caand-live` | live |
| `T.x = y = 0; if T.x` | `mx-dead` | dead |
| `del T.x; if [T.x]: … else:` | AttributeError | no bind |
| `match (1,): case (1,):` | `msq-live` | live |
| `class T: match (1,): case (1,): x = 1; if T.x` | `cms-live` | live |
| `class T: match 1: case x: y = x; if T.y` | `mas-live` | live |
| `class T: match 1: case 1 as x: y = x; if T.y` | `mav-live` | live |
| `match [1, 2]: case [1, *rest]:` | `mst-live` | live |
| mutate-15 class-body For / nested If / MatchValue / walrus / `if not T.x` after del | MATCH | MATCH |

`AST_STATIC_DIVERGES` is only `list_nestedcls` (declared nested-class object park). Attack fixture `multiset` still has the syntax typo (`{x for y in [[1]] for x in y]:`); `lambda_` query vs honesty print is the declared lambda-bind park. Those are not leftover-identity.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file` constant-getattr / getattr-with-default / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute follow the moved body. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`for _ in [1]:` / `if (1).real:` / `if T.x:` / `if [x for x in [1]]:` / `if (x for x in []):` / `t = T(); T.x = 0; if t.x` / `class T: for _ in [1]: x = 1` / `class T: if (x := 1): y = x` / `del T.x; if T.x` skip both / `del T.x; if not T.x` skip both / `if (1 and 2) == 2` / `T.x = y = 0` / `del T.x; if [T.x]` skip both / `match (1,): case (1,):` list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-16. It is real. Remaining list miss of nested class object / FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While is parked, not a const-known leftover-identity lie this cut can close without becoming an interpreter.

---

## Declared parks this cut (probed, not MUTATE)

- Nested class object: `class T: class U: y = 1; if T.U.y` honesty / query `'ncl-live'`; list miss. Storing a nested `_Cls` is a new object next to FunctionDef sentinel. `class T: class U: y = x` honesty NameError; already MATCH (do not leak `T.x` as a Name).
- FunctionDef / AsyncFunctionDef / `@classmethod` / `@staticmethod` sentinel on the class: `class T: def go(self): return 0; if T.go` honesty / query `'mt-live'`; list miss. Do not exec the body or the decorator. Keep `__init__` as `_has_init` so `T()` stays `_MISSING`.
- Name bases: `class U(T): pass; if U.x` honesty / query `'cb-live'`; list miss. `t = U(); if t.x` / `class U(*(T,)): pass` same. Copying const attrs from a Name base is a new object. Own subclass assigns already MATCH (`class U(T): x = 0` is `sbo-dead`).
- Nested defs (specimen-012 `test_a` inside `run()`): list `test_order.test_a`; `--from run_orders test_a` has no name.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign / `importlib.import_module` / `__dict__` / `itemgetter` / `[pkg_parse.parse][0]` / lambda wrap: honesty moved; `--from` follows; `--file` does not.
- FIFO `--file` remains `not a file`.
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a **list** bind: query may follow; list miss.
- `parse = lambda ...` as the bind (query `kind=def`; query does not print `('lam', 'z')`).
- Huge `source` dump still includes the 4000-`H` docstring.
- `if flag:` both branches when the test is not const-known (`os.environ.get`).
- `if len([])` Call / `if set()` / `if (1).conjugate()` Call / `T = type('T', (), {'x': 1})` Call.
- AugAssign `n = 1; n += -1` / `T.x += -1`. Do not fold AugAssign.
- Try that can run (list last-wins except).
- `assert False` / `raise ValueError` then `def parse`: honesty no name; list `kind=def`. Do **not** exec.
- `del t.x` when `x` is a class attr: honesty AttributeError at the `del`; list no-op then still sees class `x`. Do **not** exec.
- match without a static subject (`match os.name`). MatchClass (`case int():`) stays parked.
- While: `while True: def parse; break` list miss while query live; `class T: while False: x = 0; else: x = 1; if T.x` query live, list miss. Do **not** exec While.
- for-else after `break` (no break proof). For first-item only (do not unroll). Call For-iter `for _ in range(1):`.
- Format errors (`if f'{1:s}':`) `_MISSING`. Do not claim list matches import failure.
- `T()` when the class body has `__init__`: Call stays `_MISSING`. Do **not** exec `__init__`.
- Const Subscript / slice assign (`xs[0] = 0` / `d[1] = 0` / `xs[:] = []` / `T.x[0] = 0`): honesty dead; list last-wins live. Do not fold.
- `if __file__:` / `if __name__:` list last-wins else as dead while query is live. Injecting `__file__`/`__name__` is a new env seed.

EXEC_PARK from the host log: `list_initzero` / `list_initlive` / `list_initonly` / `list_emptyinit` / `list_subassign` / `list_dictassign` / `list_sliceassign` / `list_methodtruthy` / `list_instmethod` / `list_classbase` / `list_txlistsub` / `list_whiletrue` / `list_subclassinst` / `list_asyncmethod` / `list_classmethod_` / `list_staticmethod_` / `list_basesstar` / `list_classwhile`. Nested class `list_nestedcls` is the new-object park above.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (dead `if False` / `TYPE_CHECKING` skipped; const-known If / For / Match / BoolOp operand value / mixed Name+Attribute Assign / `_ATTR_MISSING` through operators and collections skip both; class-body For / nested If / Match / walrus; MatchSequence / Mapping / Star / MatchAs capture); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` still helper. Mutate-16 made BoolOp operand / mixed assign / collections-missing / MatchSequence list match query. That is why this is not KILL and not THIN_WRAPPER.

Remaining ceiling is declared parks, not a const-known leftover-identity lie:

- Nested class object / FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While stay declared (would require executing user code or a new object).
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, Try / assert / raise that can run, match without a static subject, lambda **bind** vs list, AugAssign / Call in If tests, While, for-else after break, For first-item only, Call For-iter, `T()` with `__init__`, format-error JoinedStr stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. Remaining list miss of nested class object / FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While is parked, not a new identity lie this cut can close without becoming an interpreter.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list-misses `if (1 and 2) == 2` / `T.x = y = 0; if T.x` dead / `match (1,): case (1,):` / class-body For / If-test walrus, or that list-binds `del T.x; if [T.x]: … else:` while query has no name. Those are MATCH after mutate-16.

Nothing this cut: remaining parks require executing user code (`__init__` / While / Call / AugAssign / assert / raise) or a new object (FunctionDef sentinel; Name-base attr copy; nested `_Cls`). Do not exec. Do not unroll For. Nested class `class T: class U: y = 1` stays parked.

Keep declared boundaries listed above.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, or list last-wins `t = T(); T.x = 0; if t.x:` as live while query is dead, or list-binds `del T.x; if T.x: … else:` / `del x; if x:` / `del T.x; if not T.x: … else:` / `del T.x; if [T.x]: … else:` while query has no name, KILL.

---

KEEP
