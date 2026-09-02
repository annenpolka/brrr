# DESTROYER bindname 7

Date: 2026-09-02 18:02–18:13 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0534 worker=destroyer-bindname-7

Target (archive, post-MUTATE-7 const UAdd/Invert/In, tuple unpack, local TYPE_CHECKING):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `d6bff2a14b02279082718b25a4b6ed6c101b78ae5846ee05431c7d7cd4e8e281` (51244 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-7 (`cli_sha256_after`, 73/73; worker `mutate-bindname-7` job-0533). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `127d072 Record bindname mutate HEAD 06ba4c0.` on `specimen-hdd/candidate-bind-bind`. Archive `HEAD.txt` `127d0725104d2a6ffb2b97ce6eee4bfcd7cf68d3`. Mutate-7 commit `06ba4c0a63c6236c638d3c652b7ef8f70e8ed6e6`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` twice — 73/73 OK (6.707s / 6.715s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. `DESTROYER_bindname_2.md` **MUTATE**. `DESTROYER_bindname_3.md` **MUTATE**. `DESTROYER_bindname_4.md` **MUTATE**. `DESTROYER_bindname_5.md` **MUTATE**. `DESTROYER_bindname_6.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). First KEEP/MUTATE is not protection. Mutate-7 claimed: UAdd/Invert (`if +1` / `if ~0` live; `if +0` without else not a list bind); Compare In/NotIn (`if 1 in [1]` live; `if 1 in []` without else not a list bind); tuple unpack `flag, other = True, True`; local `TYPE_CHECKING = True` uses const env before unbound-TYPE_CHECKING-is-False default.

Honor KILL if leftover `ast.py` reports Homebrew/stdlib `ast.parse`; load uses `import_module` against `sys.modules` for the query; `also` executes siblings; leftover `io.py` / `encodings.py` / `os.py` is `kind=def` while honesty is ImportError; leftover `sys.py` is `kind=def` while honesty ImportError; leftover `importlib.util` is `kind=def` while honesty cannot bind; leftover `importlib.py` file or leftover `importlib.abc` is miss while honesty leftover helper; list last-wins `if +1` / `if ~0` as dead else while query live; list `if 1 in [1]` as dead while query live; list `flag, other = True, True; if flag` as dead while query live; list `TYPE_CHECKING = True; if TYPE_CHECKING` as dead while query live; THIN_WRAPPER of two greps / `importlib.util`. Those twelve were host-executed. They do **not** fire. Decision is not KILL. Remaining leftover-identity is list last-wins of remaining const-known Subscript/Slice (`if [1][0]:`) / JoinedStr (`if f'x':`) / nested and starred unpack (`flag, (other,) = True, (True,)` / `flag, *rest = True, True`) / starred collections (`if [*[1]]:` / `if {**{}}:`). Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
SPEC012=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname7_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

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
| 6 | leftover `importlib.util` is `kind=def` while honesty cannot bind | honesty `<frozen importlib.util>` / `importlib._abc` miss; CLI `has no name`; list miss | no |
| 7 | leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper | both `kind=def` leftover helper, no Cellar | no |
| 8 | list last-wins `if +1` / `if ~0` as dead else while query is live | list source `uadd-live` / `inv-live`; `if +0:` without else not a list bind | no |
| 9 | list `if 1 in [1]` as dead while query live | list source `in-live`; `if 1 in []:` without else not a list bind | no |
| 10 | list `flag, other = True, True; if flag` as dead while query live | list source `tu-live` | no |
| 11 | list `TYPE_CHECKING = True; if TYPE_CHECKING` as dead while query live | list source `ltc-live` | no |
| 12 | THIN_WRAPPER of two greps / `importlib.util` with no leftover-identity join | naive `inspect.getsource(ast.parse)` from `/tmp` is Cellar; bindname leftover + `also pkg_parse.parse` | no |

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

Honesty leftover-importlib-file / leftover-importlib-abc / leftover-importlib-pkg. bindname `kind=def`, `file importlib.py` / `importlib/abc.py` / `importlib/__init__.py`, no Cellar. Honor KILL 7 does not fire. Leftover `tokenize.py` still leftover helper. Leftover `json.py` / `pathlib.py` / `inspect.py` / `typing.py` / `dataclasses.py` / `warnings.py` / `contextlib.py` / `argparse.py` / `tempfile.py` / `subprocess.py` / `typing_extensions.py` / `json.decoder` / `importlib.resources` / `importlib.metadata` MATCH leftover helper. Preimported / frozen `enum` / `operator` / `functools` / `abc` / `types` / `re` / `collections` / `copyreg` / `site` / `zipimport` / `collections.abc` / `os.path` / `encodings.utf_8` MATCH refuse.

### Mutate-7 claimed const-env If still matches query

`if +1:` / `if ~0:` / `if 1 in [1]` / `if 1 not in []` / `if 'a' in 'ab'` / `if 1 in {1}` / `if 1 in {1: 2}` / `if 1 in (1,)` / `if b'a' in b'ab'` list source is live. `if +0:` / `if 1 in []:` / `if ~-1:` without else is not a list bind. `flag, other = True, True` / `[flag, other] = [True, True]` / `TYPE_CHECKING = True` / `TYPE_CHECKING: bool = True` / `from typing import TYPE_CHECKING` then `TYPE_CHECKING = True` list is live. `if 1 + 1` / `if []:` with else / IfExp / multi-target / `if not []:` / `if 1 < 2 < 3` / `n = n + -1` (plain assign, not AugAssign) match. `if +True` / `if not not 1` / `if ...:` match.

### Not THIN_WRAPPER of two greps / importlib.util

Naive `inspect.getsource(ast.parse)` from `/tmp` is Homebrew `lib/python3.14/ast.py`. `grep -n "def parse"` hits leftover + moved. bindname joins them: leftover body, `also pkg_parse.parse`, `same_function False`. Const UAdd/Invert/In plus tuple unpack plus local TYPE_CHECKING is the mutate-7 object. Remaining Subscript / JoinedStr / nested-star unpack list last-wins below are incomplete const env, not absence of the join.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are leftover-identity remaining after mutate-7 const UAdd/Invert/In/unpack/local TYPE_CHECKING, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches archive.

Reexport `from pkg_parse import parse` still `kind=reexport`. `--file assign.py` with `parse = pkg_parse.parse` follows the moved body. `parse = getattr(pkg_parse, 'parse')` / `getattr(..., 'parse', None)` / `builtins.getattr(...)` / AnnAssign Attribute / parenthesized Attribute `--file` follow. Query `functools.partial(_p, 'pre')` is `runs=partialer._p`.

`if +1:` / `if ~0:` / `if 1 in [1]:` / `if 1 in []:` without else / tuple unpack / local `TYPE_CHECKING = True` / BinOp / empty collections / IfExp / multi-target list source is live (or no name), not the dead complement.

Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`. Non-UTF-8 sibling is a `miss` row. Queried stdout/stderr is not mixed into the TSV. Nested `def parse` inside `run()` is not the import bind; module-level leftover is.

Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

That is mutate-7. It is real. List last-wins of remaining const-known Subscript / JoinedStr / nested-star unpack / starred collections are not honesty leftover-identity.

---

## Implementation

### 1. List last-binding still names dead complements of const-known Subscript / Slice

Mutate-7: UAdd/Invert, Compare In/NotIn, flat tuple unpack of Names, local TYPE_CHECKING env-first. `static_const` evaluates List/Tuple/Set/Dict/str/bytes as values, then `return _MISSING` for every other node. It never subscripts.

```python
# subl.py
if [1][0]:
    def parse(x):
        return 'subl-live'
else:
    def parse(x):
        return 'subl-dead'
```

Honesty / `--from subl parse`: `'subl-live'`. List source is `subl-dead` (later line; both branches yielded). Same family as mutate-7's `if +1` / mutate-6's `if 1 + 1` close.

Same lie: `if {0: 1}[0]:` / `if (1,)[0]:` / `if 'x'[0]:` / `if b'a'[0]:` / `if [1, 2][-1]:` / `if [1][:1]:` / `if [0, 1][1:2]:` / `flag = [True][0]; if flag:` / `if (flag := [1][0]):` / `if [1][0] and [1][0]:` / `if [1][0] == 1:` / `if 1 in [1][:]:` / `X = 1; if [X][0]:`. Query live; list last-wins dead.

Dead-only without else (Honor KILL 8/9 family remaining):

```python
# sub0.py
if [0][0]:
    def parse(x):
        return 'sub0-dead-only'
```

Honesty `cannot import name 'parse'`. Query `sub0 has no name parse`. List `kind=def` `sub0-dead-only`. `if [1][1:]:` (empty slice) same.

`--file` `parse = pkg_parse.__dict__['parse']` stays a declared park (assignment alias, not an If test). Const-known Subscript **in If tests / const env** is the leftover-identity lie.

### 2. JoinedStr of constants is not in the const env that Constant strings now are

```python
# fstr.py
if f'x':
    def parse(x):
        return 'fs-live'
else:
    def parse(x):
        return 'fs-dead'
```

Honesty / query `'fs-live'`. List `fs-dead`. `if f'{1}':` same. `if f'{1}' in f'{1}':` same. `if f'':` without else: query `has no name`; list `kind=def`.

`if ''` / `if 'x'` Constant already match. JoinedStr with no interpolations, or FormattedValue of constants, is a string. Not a tracer. Not Call (`if len([])` stays park).

### 3. Nested / starred unpack is not in the const env that flat Name unpack now is

Mutate-7 `update_const_env` unpacks only when every target elt is a `Name` of equal-length Tuple/List values. Nested Tuple and Starred are skipped (`return` without updating).

```python
# nestedunp.py
flag, (other,) = True, (True,)
if flag:
    def parse(x):
        return 'nu-live'
else:
    def parse(x):
        return 'nu-dead'
```

Honesty / query `'nu-live'`. List `nu-dead`.

```python
# starunp.py
flag, *rest = True, True
if flag:
    def parse(x):
        return 'su-live'
else:
    def parse(x):
        return 'su-dead'
```

Honesty / query `'su-live'`. List `su-dead`. `flag, *rest = False, True; if rest:` (rest is `[True]`, truthy) same. `*rest, flag = False, True; if flag:` same.

Unpack of a const sequence already in env is the same hole:

```python
# tupleval.py
pair = True, True
flag, other = pair
if flag:
    def parse(x):
        return 'tv-live'
else:
    def parse(x):
        return 'tv-dead'
```

Honesty / query `'tv-live'`. List `tv-dead`. Mutate-7 stores `pair` as `(True, True)` then refuses to unpack a Name. Same-file const env. Not a tracer. Not the declared AugAssign park (`n += -1` still last-wins `aug-live` while honesty `aug-dead` — leave it).

### 4. Starred collections in If tests

`static_const` List/Tuple/Set maps each elt through `static_const`; `Starred` is `_MISSING`, so the whole collection is unknown. Dict treats `key is None` (`{**x}`) as `_MISSING`.

```python
# starnonempty.py
if [*[1]]:
    def parse(x):
        return 'sn-live'
else:
    def parse(x):
        return 'sn-dead'
```

Honesty / query `'sn-live'`. List `sn-dead`. `if {**{0: 1}}:` same.

Dead-only without else:

```python
# starlist.py
if [*[]]:
    def parse(x):
        return 'star-dead-only'
```

Honesty no name. Query `has no name`. List `kind=def`. `if {**{}}:` same.

This is not the declared **star import as a list bind** park (`from pkg_parse import *` still list-miss while honesty moved). Starred **collection literals** in If tests are incomplete const env, same as empty `if []:` before mutate-6.

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

### 6. `--file` remaining alias shapes (declared park this cut)

`parse = pkg_parse.__dict__['parse']` / `vars(pkg_parse)['parse']` / `operator.attrgetter('parse')(pkg_parse)` / dynamic `getattr(pkg_parse, name)` / IfExp assign / `importlib.import_module` / `__dict__.get` / `itemgetter` / `[pkg_parse.parse][0]`: honesty moved body; `--from` follows; `--file` does not. Declared. Constant-getattr / getattr-with-default / `builtins.getattr` / AnnAssign Attribute / parenthesized Attribute already follow. FIFO `--file` remains `not a file` (0.037s). Do not grow a full alias tracer this cut.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (`if False` / `TYPE_CHECKING` skipped; const-assigned `if flag` / `if 1 == 1` / BinOp `if 1 + 1` / UAdd `if +1:` / Invert `if ~0:` / `if 1 in [1]` / empty `if []:` / IfExp / tuple unpack / local `TYPE_CHECKING = True` skip; **Subscript `if [1][0]:` / Slice `if [1][:1]:` / JoinedStr `if f'x':` / nested unpack `flag, (other,) = True, (True,)` / starred unpack `flag, *rest = True, True` / starred collections `if [*[1]]:` still last-wins both**); load **only** the queried file via `spec_from_file_location` under its logical name after dropping foreign `sys.modules` entries whose files are not that tree (including builtins, frozen **full names** such as `importlib.util`, frozen tops, and already-imported names; **not** including leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` that honesty binds); `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect; spec=importlib.util.spec_from_file_location('ast', 'ast.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is combining them in one query, plus `kind` reexport vs def vs module, plus leftover `ast.py` not Homebrew, including `if __name__ == 'ast'`, plus leftover `sys.py` / `io.py` not `kind=def`, plus leftover `tokenize.py` the leftover helper, plus leftover frozen submodule `importlib.util` not `kind=def`, plus leftover `importlib.py` / leftover `importlib/` package still helper. Mutate-7 made UAdd/Invert/In and tuple unpack and local TYPE_CHECKING list match query. That is why this is not KILL and not THIN_WRAPPER.

Hardcoded collections-without-Subscript + strings-without-JoinedStr + flat-Name-unpack-only is the new ceiling:

- List last-wins `if [1][0]:` else / `if [1][:1]:` else / `if f'x':` else / nested unpack else / `if [*[1]]:` else as dead while query is live.
- List `if [0][0]:` / `if [1][1:]:` / `if f'':` / `if [*[]]:` / `if {**{}}:` without else as `kind=def` while query has no name.
- List last-wins `flag, (other,) = True, (True,)` / `flag, *rest = True, True` / `pair = True, True; flag, other = pair` else; query is live.
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign is the assignment text; `--from` follows the moved body (declared).
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, huge `source`, query top-level, Try that can run, match without a static subject, lambda vs list, AugAssign / Call in If tests stay as declared.
- For-body module-level `def` (`for _ in [1]: def parse`) is a list miss while query is live — remaining after this cut (scanner still does not walk For; not this mutate's required change; not a tracer).
- Attribute of constants (`if (1).real:`) / class attr (`if T.x:`) / comprehensions / GeneratorExp stay remaining (not this cut).

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for path-shadowable helpers, including name-gated `ast.py`, plus builtin / frozen-top / frozen-submodule / already-imported leftover refuse, plus leftover `tokenize.py` / leftover `importlib.py` as leftover. Isolated `spec_from_file_location` under the logical name + `inspect.getsource` + grep still do the rest. List last-wins of remaining const-known Subscript / JoinedStr / nested-star unpack / starred collections are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper under logical-name load. Keep leftover `sys.py` / `builtins.py` / `io.py` / `encodings.py` / `os.py` as miss / `has no name`. Keep leftover `tokenize.py` as leftover helper. Keep leftover `importlib.py` / leftover `importlib/` package / leftover `importlib.abc` as leftover when honesty binds them. Keep leftover `importlib.util` / `importlib.machinery` as miss when honesty cannot bind. Do not grow an import tracer.

Do not keep a calculator that list last-wins a const-dead `if [1][0]:` else / `if f'x':` else / nested-unpack else / `if [*[1]]:` else as the bind.

1. **List last-binding of const-known Subscript / Slice matches query.** `if [1][0]:` orelse is dead; list currently last-wins `subl-dead` while `--from` is live. Dict/tuple/str/bytes subscript, negative index, slices (`if [1][:1]:` live; `if [1][1:]:` without else not a list bind) same. `flag = [True][0]; if flag:` / walrus / BoolOp / Compare / `in` that already exist in `static_const` start matching once Subscript of a const collection with a const index is a const. `if [0][0]: def parse` without else is not a list bind (query `has no name`). Do **not** treat `--file` `parse = pkg_parse.__dict__['parse']` as this item (declared park).

2. **JoinedStr of constants.** `if f'x':` / `if f'{1}':` orelse is dead; list currently last-wins `fs-dead`. `if f'':` without else is not a list bind. FormattedValue of constants concatenates; no interpolations is the Constant string. Do not exec format-spec callables.

3. **Nested and starred unpack into the const env, including unpack of a const sequence already in env.** `flag, (other,) = True, (True,); if flag:` orelse is dead; list currently last-wins `nu-dead`. `flag, *rest = True, True; if flag:` same. `pair = True, True; flag, other = pair` same (mutate-7 only unpacked a Tuple/List **literal** onto flat Names). Recursive Tuple/List targets of equal-length const sequences; Starred takes the remainder. `flag, other = True, False; if other:` without else stays not a list bind.

4. **Starred collection literals in If tests.** `if [*[1]]:` / `if {**{0: 1}}:` list is live. `if [*[]]:` / `if {**{}}:` without else is not a list bind. `static_const` List/Tuple/Set/Dict already folds constants; Starred elts and dict `**` of a const mapping are the missing fold. This is not star-import list bind (declared park).

5. **Tests the current suite cannot see.** `if [1][0]` list is live not `subl-dead`; `if [0][0]: def parse` without else list is not `kind=def`; `if [1][:1]` list is live; `if f'x'` / `if f'{1}'` list is live; `if f'':` without else list is not `kind=def`; nested unpack list is live; starred unpack list is live; `pair = True, True; flag, other = pair` list is live; `if [*[1]]` list is live; `if [*[]]:` without else list is not `kind=def`; leftover `importlib.util` still miss; leftover `importlib.py` file / leftover `importlib/` package still helper; leftover `ast.py` still helper (no `import_module`); leftover `sys.py` / `io.py` still miss; leftover `tokenize.py` still helper; `if +1` / `if 1 in [1]` / `if 1 + 1` / `if []:` without else / tuple unpack / local TYPE_CHECKING still match (no regression).

Keep declared boundaries: nested defs (specimen-012 `test_a` inside `run()`), `importlib.import_module` inside `--file`, `--file` Subscript / attrgetter / dynamic getattr / IfExp assign, FIFO `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout/stderr), huge `source` dump, `if flag:` both branches when the test is not const-known, `if len([])` Call both, AugAssign, Try that can run, match without a static subject, lambda query vs list.

Leave for a later cut (not this mutate, not parks): For/While module-level `def` (`for _ in [1]: def parse` is a list miss while query is live), Attribute of constants (`if (1).real:`), class attr (`if T.x:`), comprehensions, GeneratorExp.

If a later mutation cannot keep leftover `ast.py` as the leftover helper under logical-name load (answers Homebrew `ast.parse`), or does load by `import_module` against `sys.modules`, or fills `also` by executing siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is ImportError, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `importlib.py` file / leftover `importlib.abc` is miss while honesty leftover helper, KILL.

---

MUTATE
