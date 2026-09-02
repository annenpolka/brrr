# DESTROYER bindname 6

Date: 2026-09-02 17:43–17:54 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0518 worker=destroyer-bindname-6

Target (archive, post-MUTATE-6 frozen-submodule leftover refuse / BinOp empty-collection If list):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `39b159bc04c4bb14248ee82f98ca6d448266db73f69537a5879c287a217e6011` (49672 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-6 (`cli_sha256_after`, 67/67; worker `mutate-bindname-6` job-0507). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `ab57764 Record bindname mutate HEAD e8e3edd.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `ab577640a5a43072b61c3d1b0c6d564925d970f0`. Mutate-6 commit `e8e3edd6bbbc08a644b35caf4934a5e1b8670b21`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 67/67 OK (5.501s / 5.502s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-6 claimed: leftover frozen submodule `importlib.util` / `importlib.machinery` is not `kind=def` while honesty cannot bind; leftover `importlib.py` file / leftover `importlib.abc` still helper; list last-wins of const-known BinOp `if 1 + 1` / empty `if []:` / IfExp / multi-target `flag = other = True` / `typing_extensions TYPE_CHECKING` matches query.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `encodings.py` / `os.py` is `kind=def` while honesty is ImportError; leftover `sys.py` is `kind=def` while honesty ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.machinery` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; list last-wins `if 1 + 1` else as add-dead while query is add-live; list `if []: def parse` without else as `kind=def` while query has no name; THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join. Those eleven were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list last-wins of remaining const-known UnaryOp (`if +1:` / `if ~0:`) / Compare In/NotIn (`if 1 in [1]`) / tuple unpack `flag, other = True, True` / local `TYPE_CHECKING = True` (hardcoded False before env). Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname6_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

`rg import_module` / `_bindname_` on the CLI: no matches. Load path is `importlib.util.spec_from_file_location` under the logical name after `drop_foreign_cache`. `unshadowable_reason` is builtin / `_imp.is_frozen(modname)` **full name** then frozen top / `interpreter_preimported()` (subprocess `sys.modules` listing, cwd `/`, not `import_module` of the query).

| # | condition | host | fire? |
|---|-----------|------|-------|
| 1 | leftover `ast.py` reports Cellar / `lib/python` `ast.parse` | leftover body `('leftover-ast', x)`, `file ast.py`, no Cellar | no |
| 2 | load uses `import_module` against `sys.modules` | `rg import_module` empty; `spec_from_file_location` | no |
| 3 | `also` executes siblings (`sys.exit` in `killer.py` hijacks `--from keep`) | rc=0 body `'kept'`; `SIDE` does not exist | no |
| 4 | leftover `io.py` / `encodings.py` / `os.py` is `kind=def` while honesty ImportError | all `has no name`; no leftover body | no |
| 5 | leftover `sys.py` is `kind=def` while honesty ImportError | `sys has no name parse`; builtins same | no |
| 6 | leftover `importlib.util` is `kind=def` while honesty cannot bind (frozen) | honesty `<frozen importlib.util>` / `importlib._abc` miss; CLI `has no name`; list `miss importlib/util.py imported` | no |
| 7 | leftover `importlib.machinery` is `kind=def` while honesty cannot bind | honesty `<frozen importlib.machinery>`; CLI `has no name` | no |
| 8 | leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper | both `kind=def` leftover helper, no Cellar | no |
| 9 | list last-wins `if 1 + 1` else as add-dead while query is add-live | list source `add-live` | no |
| 10 | list `if []: def parse` without else as `kind=def` while query has no name | query `has no name`; list has no `emptyif.parse` | no |
| 11 | THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join | naive `inspect.getsource(ast.parse)` from `/tmp` is Cellar; bindname leftover + `also pkg_parse.parse` | no |

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

`keep.py` leftover def, `killer.py` `sys.exit(9)` plus `def parse`, `side.py` writes `SIDE`, `osexit.py` `os._exit(11)`. `--from keep parse` rc=0, body `'kept'`, `also killer.parse` / `also osexit.parse` / `also side.parse` / `also ast.parse`, `SIDE` does not exist. `aaa_patch.py` does not rewrite `--from pkg_util`: `kind=def`, source still `legacy`.

### Leftover `sys.py` / `io.py` / `encodings.py` / `os.py` is not `kind=def`

Honesty `from sys import parse` is ImportError. bindname `--from sys parse` rc≠0, stderr `sys has no name parse`, no leftover-sys body. `io` / `encodings` / `os` / `builtins` same. Mutate-5/6 refuse holds.

### Leftover frozen submodule `importlib.util` / `importlib.machinery` is not `kind=def`

Honesty `from importlib.util import parse` is `ModuleNotFoundError: No module named 'importlib._abc'` (`File "<frozen importlib.util>"`). bindname `--from importlib.util parse` rc≠0, `importlib.util has no name parse`, no leftover-util body. List `miss	importlib/util.py	imported`. `importlib.machinery` same (`<frozen importlib.machinery>` / `importlib._bootstrap` miss). Mutate-6 item 1 holds.

### Leftover `importlib.py` file / leftover `importlib.abc` / leftover `importlib/` package still helper

Honesty leftover-importlib-file / leftover-importlib-abc / leftover-importlib-pkg. bindname `kind=def`, `file importlib.py` / `importlib/abc.py` / `importlib/__init__.py`, no Cellar. Honor KILL 8 does not fire. Leftover `tokenize.py` still leftover helper (no `tokenize.open` miss).

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. Frozen-submodule refuse plus BinOp/empty-collection list is the mutate-6 object. Remaining UnaryOp / In / tuple-unpack list last-wins below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after frozen-submodule refuse and BinOp/empty-collection If, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `parse = builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`if 1 + 1:` / `if []:` without else / IfExp / `flag = other = True` / `flag = other = False` / `from typing_extensions import TYPE_CHECKING as TC` list source is live (or no name), not the dead complement. `if not []:` / `if 1 - 1:` / `if {}` / `if ():` / `if 2 * 0:` / chained `if 1 + 1 + 1` / `if 1 < 2` / bitops / nested BinOp / nonempty collections match query. `if 1 < 2 < 3` Compare chain stays live.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-6. It is real. List last-wins of remaining const-known UAdd / Invert / In / tuple unpack / local TYPE_CHECKING are not honesty leftover-identity.

---

## Implementation

### 1. List last-binding still names dead complements of remaining const-known UnaryOp / Compare In

Mutate-6: BinOp of constants, empty List/Tuple/Dict/Set, IfExp, multi-target Name assign. `static_const` UnaryOp handles `USub` and `Not` only. `_cmp_op` handles Eq/NotEq/Is/Lt/Gt, not `In` / `NotIn`.

```python
# uadd.py
if +1:
    def parse(x):
        return 'uadd-live'
else:
    def parse(x):
        return 'uadd-dead'
```

Honesty / `--from uadd parse`: `'uadd-live'`. List source is `uadd-dead` (later line; both branches yielded). Same family as mutate-6's `if 1 + 1` close.

```python
# invert.py
if ~0:
    def parse(x):
        return 'inv-live'
else:
    def parse(x):
        return 'inv-dead'
```

Honesty / query `'inv-live'`. List `inv-dead`.

```python
# inlist.py
if 1 in [1]:
    def parse(x):
        return 'in-live'
else:
    def parse(x):
        return 'in-dead'
```

Honesty / query `'in-live'`. List `in-dead`. `if 1 not in []:` / `if 'a' in 'ab':` same.

Dead-only without else (Honor KILL 10 family remaining):

```python
# inempty.py
if 1 in []:
    def parse(x):
        return 'in-dead-only'
```

Honesty `cannot import name 'parse'`. Query `inempty has no name parse`. List `kind=def` `in-dead-only`. `if +0: def parse` / `if ~-1: def parse` (`~-1 == 0`) same unsupported certainty.

`if +0:` with an else last-wins the live else (accidental: else is later). Mutation of UAdd must not rely on that.

### 2. Tuple unpack is not in the const env that chained assign now is

Mutate-6 `update_const_env` walks `Assign.targets` only when every target is a `Name` (`flag = other = True`). Tuple unpack is a single target `Tuple`:

```python
# tupleunp.py
flag, other = True, True
if flag:
    def parse(x):
        return 'tu-live'
else:
    def parse(x):
        return 'tu-dead'
```

Honesty / query `'tu-live'`. List `tu-dead`. `flag, other = True, False` / `if other:` without else: query `has no name`; list `kind=def` `other-dead-only`.

Same-file const env. Not a tracer. Not the declared AugAssign park (`n += -1` still last-wins `aug-live` while honesty `aug-dead` — leave it).

### 3. Local `TYPE_CHECKING = True` is hardcoded False before env lookup

```python
def static_const(node, env):
    if isinstance(node, ast.Constant):
        return node.value
    if is_type_checking(node):          # Name TYPE_CHECKING → False, before env
        return False
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
```

```python
# localtc.py
TYPE_CHECKING = True
if TYPE_CHECKING:
    def parse(x):
        return 'ltc-live'
else:
    def parse(x):
        return 'ltc-dead'
```

Honesty / query `'ltc-live'` (`update_const_env` even stores `True`). List `ltc-dead` because `is_type_checking` short-circuits. `from typing import TYPE_CHECKING` / `from typing_extensions import TYPE_CHECKING` stay False (mutate-6). Do **not** follow leftover `typing.TYPE_CHECKING` Attribute across files (that would be an import tracer). Local assignment already in the const env is the lie.

### 4. Frozen / path-shadowable leftovers that match (not this MUTATE)

Host `_imp.is_frozen`: `importlib.util` True, `importlib.machinery` True, `importlib.abc` False, `importlib` False, `importlib._bootstrap` False, `zipimport` True, `encodings.utf_8` False (top `encodings` preimported).

| leftover | honesty | CLI |
|----------|---------|-----|
| `importlib.util` / `importlib.machinery` | cannot bind (frozen) | `has no name` / list miss |
| `importlib.py` file / `importlib/` package / `importlib.abc` | leftover helper | leftover helper |
| `importlib.resources` / `metadata` / `readers` / `simple` / `resources.abc` / `_bootstrap` | leftover helper | leftover helper |
| `json.decoder` / `typing_extensions.py` | leftover helper | leftover helper |
| `encodings.utf_8` / `zipimport` / `_frozen_importlib` / `collections.abc` / `os.path` | refuse | refuse |
| `tokenize.py` | leftover helper | leftover helper |

No frozen-submodule leftover-identity remaining that honesty and CLI split. Do not refuse leftover `importlib/` package that honesty binds.

### 5. `--file` remaining alias shapes (declared park this cut)

`parse = pkg_parse.__dict__['parse']` / `vars(pkg_parse)['parse']` / `operator.attrgetter('parse')(pkg_parse)` / dynamic `getattr(pkg_parse, name)` / IfExp assign / `importlib.import_module` / `__dict__.get` / `itemgetter`: honesty moved body; `--from` follows; `--file` does not. Declared. Constant-getattr / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute already follow. FIFO `--file` remains `not a file` (0.039s). Do not grow a full alias tracer this cut.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / empty `if []:` skip; **UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / tuple unpack `flag, other = True, True` / local `TYPE_CHECKING = True` still last-wins both**); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-6 made frozen-submodule refuse real and stopped list last-wins of `if 1 + 1` / empty `if []:`. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded USub-without-UAdd/Invert + Compare-without-In + Name-targets-only + TYPE_CHECKING-before-env is the new ceiling:

- List last-wins `if +1:` else / `if ~0:` else / `if 1 in [1]` else as dead while query is live.
- List `if 1 in []:` / `if +0:` / `if ~-1:` without else as `kind=def` while query has no name.
- List last-wins tuple unpack `flag, other = True, True` else; query is live.
- List last-wins local `TYPE_CHECKING = True` else; query is live.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try that can run, match without a static subject, lambda vs list, AugAssign / Call in If tests stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List last-wins of remaining const-known UAdd / Invert / In / tuple unpack / local TYPE_CHECKING are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list last-wins a const-dead `if +1:` else / `if 1 in [1]` else / tuple-unpack else / local `TYPE_CHECKING = True` else as the bind.

1. **List last-binding of remaining const-known UnaryOp / Compare In matches query.** `if +1:` orelse is dead; list currently last-wins `uadd-dead` while `--from` is live. `if ~0:` same (`inv-dead`). `if 1 in [1]` / `if 1 not in []` / `if 'a' in 'ab'` same. `if 1 in []: def parse` / `if +0: def parse` / `if ~-1: def parse` without else is not a list bind (query `has no name`). Const env already used for BinOp / empty collections / Compare Lt must apply to UAdd, Invert, and In/NotIn of constants. `if False` / `TYPE_CHECKING` skip stays. `if flag:` with a runtime-unknown test still both branches. `if len([])` Call stays both (declared: do not exec). AugAssign stays (declared). Try that can run stay. Match patterns are AST-static; siblings are not executed.

2. **Tuple unpack into the const env.** `flag, other = True, True; if flag:` orelse is dead; list currently last-wins `tu-dead`. Mutate-6 chained `flag = other = True` (all Name targets) must apply to a Tuple/List target of equal-length const values. `flag, other = True, False; if other:` without else is not a list bind.

3. **Local `TYPE_CHECKING` assignment uses the const env.** `TYPE_CHECKING = True; if TYPE_CHECKING:` query `'ltc-live'`; list currently `ltc-dead` because `is_type_checking` returns False before env lookup. Look up Name `TYPE_CHECKING` in env first; default False only when unbound (so `from typing import TYPE_CHECKING` / `from typing_extensions import TYPE_CHECKING` stay False). Do not follow leftover `typing.TYPE_CHECKING` Attribute across files (import tracer). `if False` / unbound `TYPE_CHECKING` skip stays.

4. **Tests the current suite cannot see.** `if +1` list is live not `uadd-dead`; `if ~0` list is live; `if 1 in [1]` list is live; `if 1 in []: def parse` without else list is not `kind=def`; `flag, other = True, True` list is live; local `TYPE_CHECKING = True` list is live; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `if 1 + 1` / `if []:` without else still match (no regression).

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try that can run, match without a static subject, lambda query vs list.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, KILL.

---

MUTATE
