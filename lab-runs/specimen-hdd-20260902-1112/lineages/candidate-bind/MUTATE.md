# MUTATE bindname

Date: 2026-09-02

From `destroyers/DESTROYER_bindname.md` after MUTATE (not KILL). First-selection KEEP leftovers.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: isolate queried import; static also; leftover ast.py unique name
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind
branch: specimen-hdd/candidate-bind-bind
parent_commit: d90ca1bf8c5bafa7b3036cc3bfde4a3c4671bc5f
commit: 5f5356182a6a6bae7f6ccc4ba17dc67b9f95ecaf
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 626e5492914b1f14d0387cf94b1dd3664007121f393b8302918204135a273415
cli_bytes_before: 21372
cli_sha256_after: a1ba68cde9550dd15893e4a83ffd5e46c796f45660dfc446a772697a0b830575
cli_bytes_after: 30927
```

Not merged to `main`. No `importlib.import_module` of the query against `sys.modules`.

`python3 tests/test_bindname.py -v` twice — 30/30 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

The object: for one import, the body that would run, versus other same-name
defs that this import did not bind.

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`,
body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`.
The moved body is `return ('moved', x.strip())`. Reexport still
`kind=reexport`, `runs=pkg_parse.parse`, `same_function True`.

## Change (DESTROYER_bindname mutation 1–7)

1. **Isolate the queried import.** Load only that module via
   `spec_from_file_location` and a unique `_bindname_N_*` module name.
   Leftover `ast.py` reports the leftover body (`file ast.py`,
   `source` contains `leftover-ast`). Stdlib `ast.parse` is not the bind.
   `runs` stays `ast.parse`, not the synthetic id.
2. **`also` is static.** Other same-name defs (including If/Try bodies) are
   not executed. `sys.exit` in `killer.py` does not hijack `--from keep`.
   `aaa_patch.py` does not rewrite `pkg_util.parse`. If the query import
   fails (`boom.py` raise after a local def), the CLI says it failed; it
   does not substitute last-wins `from moved import parse`.
3. **`--file` is last binding.** Dead imports (`def f(): …`, `if False:`)
   are not uses. A following `def parse` wins. `parse as parse_legacy` is
   queryable as `parse_legacy`. `importlib.import_module` in the file is
   out of scope (declared). Module-level `module.NAME` uses remain when
   NAME is not bound locally (specimen-013 test file).
4. **Presence vs bind.** Annotation-only is not `kind=def`.
   SyntaxError / UnicodeDecodeError / missing module are visible `miss`
   rows or query failures. `UnicodeDecodeError` is caught; a valid leftover
   still prints.
5. **Identity of files.** `module_name_for` does not `resolve()` away a
   second name. Symlink pair and hardlink pair both `count 2 same_function
   False`, matching `is` of the two imports. Directory walk uses a visited
   inode set (symlink `loop -> root` does not hang).
6. **Stdout is the TSV.** Non-queried modules are not imported. Queried
   module prints (specimen-010 `loader.py`, `print('QUERY_PRINT')`) are
   redirected away from stdout. The record starts with `query\t`.
7. **Tests the previous suite could not see.** Leftover `ast.py` unique
   name, `sys.exit` sibling, `aaa_patch` order, annotation-only, boom.py
   last-wins, `--file` as-alias + override, non-UTF-8 skip, symlink vs
   hardlink, specimen-010 stdout pollution.

## Leftover `ast.py`

```
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

Honesty in that directory: `from ast import parse; parse('z')` is
`('leftover-ast', 'z')`.

## Remaining (not faked)

- Nested defs remain a stated boundary (specimen-012 `test_a` inside `run()`).
- `importlib.import_module('pkg_parse'); parse = m.parse` in `--file` is
  out of scope.
- List mode is static last-binding; it does not exec `boom.py` to prove the
  raise. Query of `boom` is the failure. Do not treat list last-wins as the
  runtime bind.
- `--file /dev/stdin` FIFO is still `not a file`.
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a bind
  remain out of scope.
- Querying a module still runs that module's top-level code (captured off
  stdout). Dependencies of that module import normally.
- Huge bodies are still dumped in `source`.

If a later mutation loads `also` by importing the whole tree, or answers
leftover `ast.py` as Homebrew `ast.parse`, KILL.

---

# MUTATE bindname 2 (applied 2026-09-02 15:58 JST)

From `destroyers/DESTROYER_bindname_2.md` after MUTATE (not KILL). First-selection KEEP leftovers.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: logical-name load after drop_foreign_cache; leftover if __name__==ast; submodule bind; live also; cookie scan
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: 9eec7076d3fdfde981d154276f6140ee05a132d1
commit: 6a762281b843ff37baa1a97e5e3258b8b493e3c4
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: a1ba68cde9550dd15893e4a83ffd5e46c796f45660dfc446a772697a0b830575
cli_bytes_before: 30927
cli_sha256_after: 85f64d12c500e11d58f392da8a8c945e77255d8a79943405252e08790f94717b
cli_bytes_after: 33336
```

Not merged to `main`. No `importlib.import_module` of the query against `sys.modules`. `also` is still static (siblings are not executed).

`python3 tests/test_bindname.py -v` twice — 37/37 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

The object: for one import, the body that would run, versus other same-name
defs that this import did not bind.

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`,
body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`.
Reexport still `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`.

Isolate: only the queried file (and a named submodule of that query) is
loaded via `spec_from_file_location`. `sys.exit` sibling does not hijack.
`aaa_patch.py` does not rewrite `--from pkg_util`. Leftover `ast.py` is the
leftover helper, not Homebrew `ast.parse`. Stdlib `ast` is restored after.

## Change (DESTROYER_bindname_2 mutation 1–4, 6, 7)

1. **Load the queried module under its logical name** after
   `drop_foreign_cache`, not `_bindname_N_*`. Leftover
   `if __name__ == 'ast': def parse` reports the leftover body
   (`kind=def`, `runs=ast.parse`, `file ast.py`).
   `if __name__ != 'ast'` reports honesty-leftover, not unique-only.
   Stdlib is restored when `isolated_import` exits.

2. **`from PKG import NAME` when NAME is a submodule.** Bound module is
   `kind=module`, `runs=pkg.parse`, not `has no name`. List mode is
   `count 2 same_function False` (package module bind vs inner `def parse`),
   not `same_function True` on the inner function.

3. **Static `also` / list last-binding skip dead branches.** `if False`
   and `if TYPE_CHECKING` defs are not `also`. `if flag:` / Try that can
   run stay.

4. **Scan encoding matches exec.** Coding cookies / BOM via
   `tokenize.detect_encoding`. A latin-1 leftover does not `miss` itself.
   Sibling decode failures stay visible `miss` rows.

6. **Stderr of the queried module is not the record.** Redirected like
   stdout. FIFO `--file` remains `not a file` (declared).

7. **Tests the previous suite could not see.** `__name__ == 'ast'` leftover;
   `__name__` unique-only branch; `from pkg import parse` submodule;
   latin-1 self-miss; TYPE_CHECKING / `if False` not in `also`; logical-name
   load + stdlib restore; queried stderr.

## Leftover `ast.py` (`if __name__ == 'ast'`)

Honesty, same tree: `from ast import parse; parse('z')` is
`('name-gated-leftover', 'z')`, `__name__ == 'ast'`.

```
query	from ast import parse
bind	ast.parse
runs	ast.parse
kind	def
file	ast.py
line	2
source	"    def parse(x):\n        return ('name-gated-leftover', x)\n"
also	pkg_parse.parse
same_function	False
```

Opposite branch reports `honesty-leftover`, not `unique-only`. Ungated
leftover still `leftover-ast`. No `Cellar`, no `lib/python`. After the
query, `sys.modules['ast']` is Homebrew 3.14 `ast.py` again.

## Remaining (not faked)

- Nested defs remain a stated boundary (specimen-012 `test_a` inside `run()`).
- `importlib.import_module('pkg_parse'); parse = m.parse` in `--file` is
  out of scope.
- List mode is static last-binding; it does not exec `boom.py` to prove the
  raise.
- `--file /dev/stdin` FIFO is still `not a file`.
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a **list**
  bind remain out of scope. Query still runs that module's top-level
  (captured off stdout/stderr).
- Huge bodies are still dumped in `source`.
- `runs` / `kind` for `functools.partial`, unwrapped decorator, and
  `import mod as NAME` were not this cut (`runs=functools.parse` remains
  an inspect artifact).

If a later mutation cannot keep leftover `ast.py` as the leftover helper
under logical-name load (answers Homebrew `ast.parse`), or does (1) by
`import_module` against `sys.modules`, or fills `also` by executing
siblings, KILL.

---

# MUTATE bindname 3 (applied 2026-09-02 16:38 JST)

From `destroyers/DESTROYER_bindname_3.md` after MUTATE (not KILL). First-selection KEEP leftovers.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: builtin leftover refuse; dead complement list; --file attr follow; partial wrapped runs
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: 19a309af49118498994285072d6bd8bfa5ddec27
commit: 3b9fa46eeb2862381f81f12bfec84001ce5775bc
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 85f64d12c500e11d58f392da8a8c945e77255d8a79943405252e08790f94717b
cli_bytes_before: 33336
cli_sha256_after: 381984e8412c146ac8d59c19f45702f52130b8532e950d1643c1d15923a4eb77
cli_bytes_after: 41548
```

Not merged to `main`. No `importlib.import_module` of the query against `sys.modules`. `also` is still static (siblings are not executed). Leftover `ast.py` is still the leftover helper under logical-name load.

`python3 tests/test_bindname.py -v` twice — 47/47 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## What was kept

The object: for one import, the body that would run, versus other same-name
defs that this import did not bind.

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`,
body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`.
Reexport still `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`.

Isolate: only the queried file (and a named submodule of that query) is
loaded via `spec_from_file_location`. `sys.exit` sibling does not hijack.
`aaa_patch.py` does not rewrite `--from pkg_util`. Leftover `ast.py` is the
leftover helper, not Homebrew `ast.parse`. Stdlib `ast` is restored after.
Path-shadowable leftovers (`inspect`, `json`) still bind.

## Change (DESTROYER_bindname_3 mutation 1–4, 5)

1. **Builtin leftovers honesty cannot shadow.** leftover `sys.py` /
   `builtins.py`: honesty `from sys import parse` is ImportError. bindname
   does not `spec_from_file_location` over a builtin module name. Query is
   `has no name` (rc≠0, no `kind=def`). List/`also` do not count those
   ghosts (`miss	sys.py	builtin`). Leftover `ast.py` / `inspect.py` still
   bind the leftover helper.

2. **List last-binding of dead complements matches query.** `if not
   TYPE_CHECKING` / `if not False` orelse is dead; list source is `live` /
   `live-not-false`, not `typed-else` / `dead-else`. Reverse `match` with a
   constant subject last-wins the live case (`live-first`), not `dead-last`.
   `if False` / `TYPE_CHECKING` skip stays. `if flag:` / Try that can run
   stay. Match patterns are AST-static; siblings are not executed.

3. **`--file` last binding of `NAME = module.NAME`.** `parse = pkg_parse.parse`
   follows the moved body the same way ImportFrom is followed (`runs=pkg_parse.parse`,
   source `return ('moved', x.strip())`). `importlib.import_module` inside
   `--file` remains `kind=assign` (declared). FIFO `--file` remains `not a file`.

4. **Query `runs` for `functools.partial`.** `parse = functools.partial(_p, 'pre')`
   names the wrapped callable (`runs=partialer._p`), not `functools.parse`.
   List agrees. Unwrapped decorator `runs=decer.inner` stays inspect-honest.

5. **Tests the previous suite could not see.** leftover `sys.py` vs honesty
   ImportError; leftover `builtins.py` same; `also` omits builtin ghosts;
   leftover `ast.py` still helper (no `import_module`); `if not TYPE_CHECKING`
   list is live; reverse match list vs query; `--file` Attribute assign
   follows moved body; partial query `runs` is not `functools.parse`.

## Leftover `sys.py`

Honesty, same tree: `from sys import parse` is ImportError.

```
bindname: sys has no name parse
```

rc≠0. No `kind=def`. No leftover-sys body.

## Remaining (not faked)

- Nested defs remain a stated boundary (specimen-012 `test_a` inside `run()`).
- `importlib.import_module('pkg_parse'); parse = m.parse` in `--file` is
  out of scope.
- List mode is static last-binding; it does not exec `boom.py` to prove the
  raise.
- `--file /dev/stdin` FIFO is still `not a file`.
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a **list**
  bind remain out of scope. Query still runs that module's top-level
  (captured off stdout/stderr).
- Huge bodies are still dumped in `source`.
- `if flag:` both branches stay (declared). Match without a static subject
  still yields cases that can run.

If a later mutation cannot keep leftover `ast.py` as the leftover helper
under logical-name load (answers Homebrew `ast.parse`), or does load by
`import_module` against `sys.modules`, or fills `also` by executing
siblings, or leftover `sys.py` is `kind=def` while honesty is ImportError,
KILL.

---

# MUTATE bindname 4 (applied 2026-09-02 17:10 JST)

From `destroyers/DESTROYER_bindname_4.md` after MUTATE (not KILL). First-selection KEEP leftovers.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: already-imported/frozen leftover refuse; const-known If list; --file getattr/alias follow
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: b16b7213950d2e0d1f354276410393ffe38cc5b0
commit: 2d35105138b56c262b5683fb63b217a9b26c081c
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 381984e8412c146ac8d59c19f45702f52130b8532e950d1643c1d15923a4eb77
cli_bytes_before: 41548
cli_sha256_after: ba3237304c2b09c9c346832cd0ebc3258c9915d4f62669cbac4b093c9b0a920f
cli_bytes_after: 47191
```

Not merged to `main`. No `import_module` of the query against `sys.modules`. `also` is still static (siblings are not executed). Leftover `ast.py` is still the leftover helper under logical-name load. Leftover `sys.py` / `builtins.py` still miss.

`python3 tests/test_bindname.py -v` twice — 57/57 OK (4.553s / 4.773s).

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0. Specimen-013 demo matches the previous archive log.

## What was kept

The object: for one import, the body that would run, versus other same-name
defs that this import did not bind.

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`,
body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`.
Reexport still `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`.

Isolate: only the queried file (and a named submodule of that query) is
loaded via `spec_from_file_location`. `sys.exit` sibling does not hijack.
`aaa_patch.py` does not rewrite `--from pkg_util`. Leftover `ast.py` is the
leftover helper, not Homebrew `ast.parse`. Stdlib `ast` is restored after.
Path-shadowable leftovers (`inspect`, `json`, `tokenize`) still bind.

## Change (DESTROYER_bindname_4 mutation 1–3, 4)

1. **Already-imported / frozen stdlib leftovers honesty cannot shadow.**
   leftover `io.py` / `encodings.py` / `codecs.py` / `types.py` /
   `functools.py` / `os.py`: honesty `from io import parse` is ImportError.
   bindname does not `spec_from_file_location` over a builtin, a frozen
   module (`_imp.is_frozen`, `io` / `os` / `codecs`), or a name a fresh
   interpreter already has in `sys.modules` (subprocess probe, cwd `/`,
   not `import_module` of the query). Query is `has no name` (rc≠0, no
   `kind=def`). List/`also` miss those ghosts (`miss	io.py	imported`).
   leftover `os.py` query does not die `os.stat`. leftover `tokenize.py`
   honesty leftover helper still reports that leftover (`kind=def`,
   `file tokenize.py`), not `tokenize.open` miss. Leftover `ast.py` /
   `inspect.py` still bind the leftover helper.

2. **List last-binding of const-known If tests matches query.**
   `flag = True; if flag:` orelse is dead; list source is `live-flag`, not
   `dead-else`. `if 1 == 1` / `if __debug__` / `if (flag := True)` /
   `from typing import TYPE_CHECKING as TC; if not TC` same. Const env
   already used for match subjects now applies to If tests (walrus,
   comparisons, BoolOp, TYPE_CHECKING aliases). `if False` /
   `TYPE_CHECKING` skip stays. `if flag:` with a runtime-unknown test
   still both branches. Try that can run stay. Match patterns are
   AST-static; siblings are not executed.

3. **`--file` last binding of `NAME = getattr(module, 'NAME')` and
   `NAME = alias`.** Honesty is the moved body. `--from` already followed;
   `--file` now follows Call-getattr / Name alias the same way Attribute
   assign is followed (`runs=pkg_parse.parse`, source `strip`).
   `importlib.import_module` inside `--file` remains `kind=assign`
   (declared). FIFO `--file` remains `not a file`.

4. **Tests the previous suite could not see.** leftover `io.py` vs honesty
   ImportError; leftover `encodings.py` same; leftover `tokenize.py`
   honesty leftover vs query miss; leftover `os.py` list not `kind=def`;
   `flag = True; if flag:` list is live; `if 1 == 1` list vs query;
   `TYPE_CHECKING as TC; if not TC` list is live; leftover `ast.py` still
   helper (no `import_module`); leftover `sys.py` still miss; `--file`
   getattr / Name alias follow moved body.

## Leftover `io.py`

Honesty, same tree: `from io import parse` is ImportError (frozen `io`).

```
bindname: io has no name parse
```

rc≠0. No `kind=def`. No leftover-io body.

## Leftover `tokenize.py`

Honesty, same tree: `from tokenize import parse; parse('z')` is
`('leftover-tokenize', 'z')`.

```
query	from tokenize import parse
bind	tokenize.parse
runs	tokenize.parse
kind	def
file	tokenize.py
source	"def parse(x):\n    return ('leftover-tokenize', x)\n"
also	pkg_parse.parse
same_function	False
```

No `tokenize.open` miss. No `Cellar`.

## Remaining (not faked)

- Nested defs remain a stated boundary (specimen-012 `test_a` inside `run()`).
- `importlib.import_module('pkg_parse'); parse = m.parse` in `--file` is
  out of scope.
- List mode is static last-binding; it does not exec `boom.py` to prove the
  raise.
- `--file /dev/stdin` FIFO is still `not a file`.
- `exec("def parse...")` / PEP 562 `__getattr__` / star import as a **list**
  bind remain out of scope. Query still runs that module's top-level
  (captured off stdout/stderr).
- Huge bodies are still dumped in `source`.
- `if flag:` both branches stay when the test is not const-known. Match
  without a static subject still yields cases that can run.
- Query `runs` / `kind` for lambda vs list, and unwrapped decorator
  `runs=decer.inner`, stay inspect-honest (declared).

If a later mutation cannot keep leftover `ast.py` as the leftover helper
under logical-name load (answers Homebrew `ast.parse`), or does load by
`import_module` against `sys.modules`, or fills `also` by executing
siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is
ImportError, KILL.

---

# MUTATE bindname 6 (applied 2026-09-02 17:41 JST)

From `destroyers/DESTROYER_bindname_5.md` after MUTATE (not KILL). First-selection KEEP leftovers. First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: frozen-submodule leftover refuse; const BinOp/empty-collection/IfExp/multi-target If list; typing_extensions TYPE_CHECKING
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: d3ff9dc660f0ebb89c13bae3e37a271e25d3e288
commit: e8e3edd6bbbc08a644b35caf4934a5e1b8670b21
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: ba3237304c2b09c9c346832cd0ebc3258c9915d4f62669cbac4b093c9b0a920f
cli_bytes_before: 47191
cli_sha256_after: 39b159bc04c4bb14248ee82f98ca6d448266db73f69537a5879c287a217e6011
cli_bytes_after: 49672
```

Not merged to `main`. No `import_module` of the query against `sys.modules`. `also` is still static. Leftover `ast.py` is still the leftover helper under logical-name load. Leftover `sys.py` / `io.py` still miss.

`python3 tests/test_bindname.py -v` twice — 67/67 OK (5.773s / 5.885s).

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0. Specimen-013 demo matches the previous archive log.

## What was kept

The object: for one import, the body that would run, versus other same-name
defs that this import did not bind.

Specimen-013: `--from pkg_util parse` is `kind=def`, leftover helper,
`also pkg_parse.parse`, `same_function False`. Reexport still
`kind=reexport`. Isolate: only the queried file is loaded via
`spec_from_file_location`. Leftover `ast.py` is the leftover helper, not
Homebrew `ast.parse`. Leftover `sys.py` / `io.py` / `encodings.py` / `os.py`
miss. Leftover `tokenize.py` is leftover helper. Leftover `importlib.py`
file and leftover `importlib.abc` still bind when honesty binds them.

## Change (DESTROYER_bindname_5 mutation 1–3)

1. **Frozen submodule leftovers honesty cannot shadow.** leftover
   `importlib.util` / `importlib.machinery`: honesty cannot bind (frozen).
   bindname checks `_imp.is_frozen` on the **full** module name, not only
   the top. Query is `has no name` (rc≠0, no `kind=def`). List/`also` miss
   those ghosts (`miss	importlib/util.py	imported`). Leftover
   `importlib.py` file / leftover `importlib/` package / leftover
   `importlib.abc` still `kind=def` leftover helper. Leftover `ast.py` /
   `tokenize.py` still bind. Builtin / frozen-top / already-imported refuse
   stays. If this were done by answering leftover `ast.py` as Homebrew
   `ast.parse`, that would be a regression — KILL.

2. **List last-binding of const-known BinOp / empty-collection If tests
   matches query.** `if 1 + 1:` orelse is dead; list source is `add-live`,
   not `add-dead`. `if []: def parse` without else is not a list bind
   (query `has no name`; honesty `cannot import name 'parse'`). Const env
   now covers BinOp of constants, empty List/Tuple/Dict/Set, IfExp of
   constants, and multi-target `flag = other = True`. `from
   typing_extensions import TYPE_CHECKING as TC` same as `typing`.
   `if False` / `TYPE_CHECKING` skip stays. `if flag:` with a
   runtime-unknown test still both branches. `if len([])` Call stays both
   (declared: do not exec). AugAssign stays. Try that can run stay.

3. **Tests the previous suite could not see.** leftover `importlib.util`
   vs honesty cannot bind; leftover `importlib.machinery` same; leftover
   `importlib.py` file still helper; leftover `importlib.abc` still helper;
   leftover `io.py` still miss; leftover `tokenize.py` still helper;
   `if 1 + 1` list is live not `add-dead`; `if []: def parse` without else
   list is not `kind=def`; leftover `ast.py` still helper (no
   `import_module`); leftover `sys.py` still miss; IfExp /
   multi-target / `typing_extensions` TYPE_CHECKING list is live.

## Remaining (not faked)

- Nested defs remain a stated boundary (specimen-012 `test_a` inside `run()`).
- `importlib.import_module` inside `--file` stays `kind=assign` (declared).
- `--file` Subscript / attrgetter / dynamic getattr / IfExp assign stay
  the assignment text (declared park).
- FIFO `--file` remains `not a file`.
- `exec` / PEP 562 / star as a **list** bind remain out of scope.
- Huge bodies are still dumped in `source`.
- `if flag:` both branches stay when the test is not const-known.
- Query `runs` / `kind` for lambda vs list stay inspect-honest.

If a later mutation cannot keep leftover `ast.py` as the leftover helper
under logical-name load (answers Homebrew `ast.parse`), or does load by
`import_module` against `sys.modules`, or fills `also` by executing
siblings, or leftover `sys.py` / `io.py` is `kind=def` while honesty is
ImportError, or leftover `importlib.util` is `kind=def` while honesty
cannot bind, KILL.

---

# MUTATE bindname 7 (applied 2026-09-02 18:01 JST)

From `destroyers/DESTROYER_bindname_6.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: const UAdd/Invert/In; tuple unpack; local TYPE_CHECKING assign
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: ab577640a5a43072b61c3d1b0c6d564925d970f0
commit: 06ba4c0a63c6236c638d3c652b7ef8f70e8ed6e6
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 39b159bc04c4bb14248ee82f98ca6d448266db73f69537a5879c287a217e6011
cli_bytes_before: 49672
cli_sha256_after: d6bff2a14b02279082718b25a4b6ed6c101b78ae5846ee05431c7d7cd4e8e281
cli_bytes_after: 51244
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper. leftover `importlib.util` still miss. leftover `sys.py` / `io.py` still miss.

`python3 tests/test_bindname.py -v` twice — 73/73 OK (6.435s / 6.462s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_6 mutation 1–4)

1. **UAdd / Invert.** `if +1:` / `if ~0:` list is live. `if +0:` without else is not a list bind (query `has no name`).
2. **Compare In/NotIn.** `if 1 in [1]:` list is live. `if 1 in []:` without else is not a list bind.
3. **Tuple unpack.** `flag, other = True, True; if flag:` list is live (mutate-6 only did chained Name assign).
4. **Local `TYPE_CHECKING = True`.** Const env is consulted before the unbound-TYPE_CHECKING-is-False default, so list is live.

## Remaining (not faked)

Declared parks from mutate-6 stay: nested defs, `--file` Subscript/attrgetter, FIFO `--file`, `if len([])` Call, AugAssign, Try that can run.

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or does load by `import_module`, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or leftover `sys.py` / `io.py` is `kind=def` while honesty ImportError, KILL.

---

# MUTATE bindname 8 (applied 2026-09-02 18:20 JST)

From `destroyers/DESTROYER_bindname_7.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: const Subscript/JoinedStr/starred collections; nested/star unpack
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: 127d0725104d2a6ffb2b97ce6eee4bfcd7cf68d3
commit: 1a12a94f7f01e3aa9eb0fa3047ba98c67c034cd8
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: d6bff2a14b02279082718b25a4b6ed6c101b78ae5846ee05431c7d7cd4e8e281
cli_bytes_before: 51244
cli_sha256_after: 650d990f42e32e808600bbb81f1ea350467cea4770aee36e28ba44ad18e95944
cli_bytes_after: 55153
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py -v` twice — 78/78 OK (7.585s / 7.644s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_7 mutation 1–4)

1. **Subscript/Slice.** `if [1][0]:` list is live. `if [0][0]:` without else is not a list bind.
2. **JoinedStr.** `if f'{1}':` list is live. `if f'':` without else is not a list bind.
3. **Nested/starred unpack.** `flag, (other,) = True, (True,)`; `flag, *rest = True, True`; `pair = True, True; flag, other = pair` list is live.
4. **Starred collections.** `if [*[1]]:` list is live. `if [*[]]:` without else is not a list bind. Dict `**` unpack same.

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.

---

# MUTATE bindname 9 (applied 2026-09-02 18:36 JST)

From `destroyers/DESTROYER_bindname_8.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: const For-body; Attribute; class attr; ListComp; GeneratorExp always-truthy
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: 8496b3c85ef4ff781e3d25fb748f7a55e4dc6e55
commit: 1f07315f20ed156580b09c9a423a789c400d984b
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 650d990f42e32e808600bbb81f1ea350467cea4770aee36e28ba44ad18e95944
cli_bytes_before: 55153
cli_sha256_after: 5dc2944551764460327c06648af72002f94d1e83510d33744c8b6e09892bbc12
cli_bytes_after: 57227
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py -v` twice — 82/82 OK (8.871s / 8.907s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_8 mutation)

1. **For-body.** `for _ in [1]: def parse` is a list bind. Empty `for _ in ():` is not. for-else still runs after a completing loop (no break proof).
2. **Attribute.** `if (1).real:` list is live. `class T: x = 1; if T.x:` list is live (const class namespace).
3. **ListComp.** `if [x for x in [1]]:` list is live.
4. **GeneratorExp.** generator objects are always truthy; `if (x for x in []):` list is live.

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.

---

# MUTATE bindname 10 (applied 2026-09-02 18:52 JST)

From `destroyers/DESTROYER_bindname_9.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: genexp sentinel for For; SetComp/DictComp/filter ListComp; instance Call
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: 69fbdd6a42ecc37c668e639f777569016cfe2820
commit: 14790cb271d2af481f17c0f1f595308db44941aa
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 5dc2944551764460327c06648af72002f94d1e83510d33744c8b6e09892bbc12
cli_bytes_before: 57227
cli_sha256_after: 0bddedf8657f0dbc4eed4fe26f39676228bd31fc6ea2cb1be2a711d37c901570
cli_bytes_after: 59886
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py -v` twice — 86/86 OK (9.706s / 9.678s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_9 mutation)

1. **GeneratorExp as For-iter.** Generator objects are truthy *and* may be empty. `if (x for x in []):` still live. `for _ in (x for x in []): def parse` is not a list bind (honesty has no name). Mutate-9's `return True` leaked into For.
2. **SetComp / DictComp / filtered ListComp.** `if {x for x in [1]}` / `{x: 1 for x in [1]}` / `[x for x in [1, 0] if x]` list is live.
3. **Instance Call.** `class T: x = 1; t = T(); if t.x:` list is live (no-arg Call of a const class namespace). `if (lambda: 0):` is live. `if len([])` Call with args still both (declared: do not exec).

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.

---

# MUTATE bindname 11 (applied 2026-09-02 19:10 JST)

From `destroyers/DESTROYER_bindname_10.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: nonempty genexp rows; format-spec JoinedStr
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: b4f03d1155275eeb5bd0e25cb1ece8ede8ebf4e7
commit: 4d2fa1bca095f1b05db0fa43b312131e14a75f1c
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 0bddedf8657f0dbc4eed4fe26f39676228bd31fc6ea2cb1be2a711d37c901570
cli_bytes_before: 59886
cli_sha256_after: bf07a0ef52c21723b676558e313eba79e89cb3d35432800726b954b2f3be2c8f
cli_bytes_after: 60655
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py -v` twice — 90/90 OK (10.110s / 10.118s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_10 mutation)

1. **Nonempty genexp as sequence.** Const-evaluated generators stay always-truthy and iterate produced values (`_TruthyRows`). `for _ in (x for x in [1]): def parse` is a list bind. Empty genexp For is still not a bind. Mutate-10's always-empty sentinel missed nonempty For/comp/Starred.
2. **format-spec JoinedStr.** `if f'{1:d}':` list is live (`format(inner, spec)`).

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.

---

# MUTATE bindname 12 (applied 2026-09-02 19:27 JST)

From `destroyers/DESTROYER_bindname_11.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: post-class attr assign; multi-generator comps; conversion-then-spec
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: 76acbdaf1f19f197addd12918a0efa957a993bae
commit: c3280c10c685aab828956a87ac70173fdeb6d95d
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: bf07a0ef52c21723b676558e313eba79e89cb3d35432800726b954b2f3be2c8f
cli_bytes_before: 60655
cli_sha256_after: 8f019efdab17ab25c2d136adc84761b9f5051cac71bed8321c5c87879354ff15
cli_bytes_after: 62525
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py -v` twice — 94/94 OK (11.130s / 11.240s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_11 mutation)

1. **Post-class Attribute assign / AnnAssign / Delete.** `class T: x = 1; T.x = 0; if T.x:` list is dead-else. No-arg `T()` copies the namespace unless the class body defines `__init__` (then Call is unknown; do not exec `__init__`).
2. **Multi-generator comprehensions.** `if [x+y for x in [1] for y in [0]]:` list is live.
3. **JoinedStr conversion then spec.** `if f'{1!s:s}':` list is live. `f'{1!s:d}'` format of str with `d` is unknown (honesty ValueError).

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.

---

# MUTATE bindname 13 (applied 2026-09-02 19:49 JST)

From `destroyers/DESTROYER_bindname_12.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: instance follows class attrs; missing-attr If; class-body outer reads
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: 3728e24f3471418ccaf43db6ccea7af9be0ca5a8
commit: 16ed54d24c7d88cd16f53e7ab24ea424b5eb6d44
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 8f019efdab17ab25c2d136adc84761b9f5051cac71bed8321c5c87879354ff15
cli_bytes_before: 62525
cli_sha256_after: d0e4fff4285380107fbccdceb2a4f0325be724b9f6950ea011c57d4460a06643
cli_bytes_after: 64884
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py -v` twice — 98/98 OK (11.624s / 11.390s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_12 mutation)

1. **Instance follows class.** `t = T(); T.x = 0; if t.x:` list is dead-else (instance lookup reads the class namespace). Instance assign `t.x = 1` stays on the instance.
2. **Missing-attr If.** `del T.x; if T.x:` is not a list bind (honesty AttributeError).
3. **Class-body outer reads.** `flag = True; class T: x = flag; if T.x:` list is live. Writes stay on the class, not leaked as `T.flag`.

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.

---

# MUTATE bindname 14 (applied 2026-09-02 20:12 JST)

From `destroyers/DESTROYER_bindname_13.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: If fail polarity; del Name; class-body If assigns
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: c761d4fdc24f19cbc6209768ac88e638a72317eb
commit: 35fff7df4f63bb7ebfdd60490e1a1ad03c5af5a1
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: d0e4fff4285380107fbccdceb2a4f0325be724b9f6950ea011c57d4460a06643
cli_bytes_before: 64884
cli_sha256_after: 20f81016e90c9a15ea0251a56d143188fb67a834c8220af37b5f01b4b7c06224
cli_bytes_after: 65799
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py -v` twice — 102/102 OK (11.136s / 11.168s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_13 mutation)

1. **If fail polarity.** `_ATTR_MISSING` skips both body and orelse (honesty AttributeError). `del T.x; if T.x: … else:` is not a list bind.
2. **del Name.** `del x` stores a missing marker; `if x:` is fail, not both-branches last-wins.
3. **Class-body If.** `class T: if True: x = 1; else: x = 0` then `if T.x:` list is live.

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.

---

# MUTATE bindname 15 (applied 2026-09-02 20:48 JST)

From `destroyers/DESTROYER_bindname_14.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: class-body For/Match/walrus; _ATTR_MISSING through operators
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: 753034f24a6dd5a07e6c424ced074ea425003a43
commit: f341558de47cfebd6f7c2d6cc3738c606f0bf88c
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 20f81016e90c9a15ea0251a56d143188fb67a834c8220af37b5f01b4b7c06224
cli_bytes_before: 65799
cli_sha256_after: 9fbf4f6e466abcd39c6a9f64474c3574c64a8ade2cacf2f1f26f19f468c6d6e5
cli_bytes_after: 68040
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py -v` twice — 112/112 OK (14.840s / 12.998s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_14 mutation)

1. **Class-body const For / nested If / Match.** `class T: for _ in [1]: x = 1; if T.x` list is live. Nested `if True: if True: x = 1` and `match 1: case 1: x = 1` list are live. Empty For-else `for _ in []: x = 1; else: x = 0` list is dead. Walk const-known control for env only; do not yield class-body FunctionDef.
2. **If-test walrus / empty `_ChainEnv`.** `class T: if (x := 1): y = x; if T.y` list is live. `test_polarity` keeps an empty class env (`if env is None`) so NamedExpr writes stay on the class.
3. **`_ATTR_MISSING` through operators.** `del T.x; if not T.x: … else:` / `if T.x or True` / `del x; if not x: … else:` are not list binds (honesty AttributeError / NameError). Marker propagates through Not / BoolOp / Compare / BinOp / Subscript / IfExp; If is fail (skip both).

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.

---

# MUTATE bindname 16 (applied 2026-09-02 21:35 JST)

From `destroyers/DESTROYER_bindname_16.md` after MUTATE (not KILL). First KEEP/MUTATE is not protection.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-identity
  specimens: [specimen-013]
  mutation: BoolOp operand value; mixed assign; missing through collections; MatchSequence
  parent: candidate-bind
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname
branch: specimen-hdd/candidate-bind-bind
parent_commit: e0c4da8f89f4c9fe33f23b7222fd231142301615
commit: a0a6fecd978ebf6f35ea7d7347680ffa555b9174
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/
cli_sha256_before: 9fbf4f6e466abcd39c6a9f64474c3574c64a8ade2cacf2f1f26f19f468c6d6e5
cli_bytes_before: 68040
cli_sha256_after: c7d985ed9b0ebb42f775ff3bacefc3c27e9505ff37f25a03abdd82a18609755f
cli_bytes_after: 73327
```

Not merged to `main`. No `import_module`. leftover `ast.py` still helper.

`python3 tests/test_bindname.py` twice — 119/119 OK (14.111s / 14.508s).

`./demo.sh` ×2 byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

## Change (DESTROYER_bindname_16 mutation)

1. **BoolOp operand value.** `1 and 2` is `2`, not `True`. `if (1 and 2) == 2` list is live; `if (1 and 2) is True` list is dead.
2. **Mixed Name+Attribute Assign.** `T.x = y = 0; if T.x` list is dead. Each target binds the same const value.
3. **`_ATTR_MISSING` through collections.** `del T.x; if [T.x]: … else:` is not a list bind. Marker propagates through List/Tuple/Set/Dict/JoinedStr/Starred/comprehension/genexp.
4. **Const MatchSequence / Mapping / Star / MatchAs.** `match (1,): case (1,):` list is live. Class-body `case x: y = x` binds the capture.

If a later mutation cannot keep leftover `ast.py` as the leftover helper, or leftover `importlib.util` is `kind=def` while honesty cannot bind, or `import_module` against `sys.modules`, KILL.
