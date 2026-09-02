# DESTROYER bindname 2

Date: 2026-09-02 15:39–15:44 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0373 worker=destroyer-bindname-2

Target (archive, post-MUTATE isolate):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `a1ba68cde9550dd15893e4a83ffd5e46c796f45660dfc446a772697a0b830575` (30927 bytes). Matches `lineages/candidate-bind/MUTATE.md` after (`cli_sha256_after`, 30/30). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (HEAD `9eec707` on `specimen-hdd/candidate-bind-bind`, `Record bindname mutate HEAD 5f53561.`). Parent `main` is `432f954`; `git ls-files` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_bindname.py -v` → 30/30 OK. `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` byte-identical.

First record: `destroyers/DESTROYER_bindname.md` **MUTATE**. First-selection KEEP (Unix/Toolsmith/Heretic/Reality; Skeptic dissent). Isolate mutate claimed: queried import via `spec_from_file_location` under unique `_bindname_N_*`; leftover `ast.py` reports leftover body; `also` static; no `importlib.import_module` of the query against `sys.modules`.

Honor KILL if still `import_module` against `sys.modules` / leftover `ast.py` reports stdlib / `also` executes siblings. Those three were host-executed. They do **not** fire. Decision is not KILL. Remaining isolate identity is unique `__name__`. Decision: **MUTATE**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
SPEC013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
```

Host-executed against the archive only. Attack log: `destroyers/_bindname2_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer.

---

## Honor KILL (did not fire)

`rg import_module` on the CLI: no matches. Load path is `importlib.util.spec_from_file_location` + unique name.

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

No `Cellar`, no `lib/python`. `--import 'from ast import parse'` is the same. List mode `count 2` leftover + moved. Leftover `inspect.py` / `json.py` same shape (`leftover-inspect` / `leftover-json`, not stdlib).

In-process: `load_query` returns unique `_bindname_1_ast`, `mod.parse('z')` is `('leftover-ast', 'z')`, `sys.modules['ast']` is **not** that unique module during load (stdlib `ast` was dropped; leftover is registered only under the unique key). After `isolated_import`, `sys.modules['ast']` is the original Homebrew 3.14 `ast.py`. `binding_from_import` remaps `runs` to `ast.parse`, `kind=def`, `file ast.py`. Isolate claim holds for the ungated fixture.

### `also` does not execute siblings

`keep.py` leftover def, `killer.py` `sys.exit(9)` plus `def parse`, `side.py` writes `SIDE`. `--from keep parse` rc=0, body `'kept'`, `also killer.parse` / `also side.parse`, `SIDE` does not exist. `os._exit(11)` sibling does not take the process down. `aaa_patch.py` (sorts first, patches `pkg_util.parse`) does not rewrite `--from pkg_util`: `kind=def`, `runs=pkg_util.parse`, source still `legacy`.

Honor KILL conditions are closed. First-selection pairing still runs. Attacks below are the isolate method's leftover, not a re-run of tree-wide `import_module`.

---

## What still works

Specimen-013: `--from pkg_util parse` is `kind=def`, `runs=pkg_util.parse`, body `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. `--from pkg_parse` is the moved `strip` body. List `count 2 same_function False`. Demo matches.

Reexport `from pkg_parse import parse` still `kind=reexport`, `runs=pkg_parse.parse`, `same_function True`. Package relative `from .moved import parse` under unique query name still reexports (`pkg.util` → `pkg.moved.parse`). Namespace package `ns/keep.py` without `__init__.py` binds. Annotation-only is not `kind=def`. `boom.py` raise after a local def is `import failed`, not last-wins reexport. Non-UTF-8 sibling is a `miss` row, queried leftover still prints. Symlink / hardlink pairs `count 2 same_function False`. Symlink `loop -> root` does not hang. Queried `print` is not mixed into the TSV (`query\t` first). Specimen-010 `loader.py` stdout pollution is gone. Empty / missing / star `--import` / NAME mismatch / `--from`+`--file`: nonzero rc, no fake TSV.

`if __name__ == '__main__'` leftover `ast.py` takes the else-branch leftover body (unique name is not `__main__`; honesty the same). That common gate is not the hole.

That is the isolate mutate. It is real. Unique `__name__` is not honesty `__name__`.

---

## Implementation

### 1. Unique module name is not the leftover's `__name__`

`load_query` always execs under `_bindname_N_<logical>`. Honesty `from ast import parse` execs leftover as `__name__ == 'ast'`. The origin leftover that **gates on that name** diverges.

```python
# ast.py
if __name__ == 'ast':
    def parse(x):
        return ('name-gated-leftover', x)
```

Honesty, same tree: `('name-gated-leftover', 'z')`. bindname `--from ast parse` rc=1, empty stdout:

```text
bindname: ast has no name parse
```

The leftover helper exists. Unique `__name__` hid it. This is the stdlib-shadow case the first destroyer existed to catch.

Opposite branch:

```python
if __name__ != 'ast':
    def parse(x):
        return ('unique-only', x)
else:
    def parse(x):
        return ('honesty-leftover', x)
```

Honesty: `('honesty-leftover', 'z')`. bindname reports `unique-only`, `kind=def`, `same_function True`. Unsupported certainty: it is not the body that import would bind.

`drop_foreign_cache` already removes Homebrew `ast` when leftover `ast.py` is the query file. Unique names were to avoid `sys.modules['ast']`. After that drop, `spec_from_file_location("ast", leftover_path)` is the honesty identity. FIX.md loaded under the real name for that reason; MUTATE switched to unique ids because DESTROYER_bindname item 1 named them, then remapped `runs` so the TSV would not show `_bindname_1_ast`. The TSV remap does not restore `__name__`.

### 2. `from pkg import parse` when `parse` is a submodule

```text
pkg/__init__.py   (empty)
pkg/parse.py      def parse(x): return ('submodule', x)
```

Honesty: `from pkg import parse` binds a **module** (`type=module`, `value='mod'`). bindname `--from pkg parse` rc=1 `pkg has no name parse`. `getattr` after loading `pkg/__init__.py` does not auto-import the submodule; `from pkg import parse` does. List mode `count 1 same_function True` on `pkg.parse.parse` (the function inside the submodule), not the bound submodule. First destroyer §7 named this split. Mutation remaining listed exec / PEP 562 / star, not this.

### 3. Static `also` / list still name defs that never bind

`if False: def parse` / `if TYPE_CHECKING: def parse`: honesty `hasattr` is False. `--from` that module: `has no name parse` (query load is honest). List mode still `count`s them as binds. `--from pkg_parse parse` lists `also dead.parse` / `also typed.parse`. Mutation asked If/Try bodies in static `also`. That made `also` a mention index, not “other defs this import did not bind” in the runtime sense. `same_function False` on a leftover that is not importable is the old silent-miss family, inverted: the ghost is extra, not dropped.

### 4. Coding cookie vs utf-8 scan: queried file `miss`es itself

`latin.py` with `# -*- coding: latin-1 -*-` and `return 'café'`. Honesty prints `café`. `--from latin parse` prints the leftover body **and**:

```text
miss	latin.py	UnicodeDecodeError
same_function	False
```

`static_scan` is `path.read_text(encoding="utf-8")`. `exec_module` honors the cookie. Query succeeds; the miss row is the queried file. BOM leftover: query succeeds, `miss bom.py SyntaxError`. Mutation caught UnicodeDecodeError so a *sibling* would not dump a traceback. It did not make the queried encoding the scan encoding.

### 5. `kind` / `runs` noise the first destroyer already named

`parse = functools.partial(_p, 'pre')`: `kind=reexport`, `runs=functools.parse`. Decorator without `wraps`: `runs=decer.inner`, `source` is the wrapper. `import pkg_parse as parse`: `runs=pkg_parse.pkg_parse`. `also` on those queries still lists every other def/class in the tree (`cls.parse`, `decer.parse`). Mutation 1–7 did not touch this. Not Honor KILL; still a ceiling on the pairing columns.

Star import / PEP 562 / `exec("def parse...")` **query** can succeed because the queried module still runs (star → `pkg_parse.parse`; pep → nested source via `inspect`; exec → `file <string>` empty `source`). List mode still `count 1` on the moved def only. Declared remaining. Query of a module that `import`s `killer` still dies (`SystemExit(9)` wrapped as `import failed`) — dependency, not `also`.

### 6. Stderr is not the TSV; `--file` FIFO still `not a file`

Queried `print('ERR', file=sys.stderr)` leaks `ERR` on stderr next to a clean stdout TSV. Mutation 6 redirected stdout only. `--file` FIFO / `/dev/stdin` still `not a file` (`Path.is_file()`). Declared. Huge 200 kB body still dumped (`stdout` 200208 bytes, starts `query\t`). Nested specimen-012 `test_a` is still the module-level leftover, not the identity that ran inside `run()` — declared boundary.

`--file dyn.py` last binding `parse = m.parse` after `importlib.import_module('pkg_parse')` is `kind=assign`, source the assignment, not the moved body. `--from dyn` **does** follow to `pkg_parse.parse` because the query executes. MUTATE.md parked `import_module` inside `--file`. The split is list/file static vs query live.

---

## Primitive

Reality-stripped operation: AST-scan module-level `def` / assign / `from … import` for NAME (If/Try/With/Match bodies included); load **only** the queried file via `spec_from_file_location` under `_bindname_N_*` after dropping foreign `sys.modules` entries whose files are not that tree; `inspect.getsource` that object; print other static last-hit `def`s as `also`.

Nearest ordinary workflow:

```bash
python3 -c "import importlib.util, inspect, sys; spec=importlib.util.spec_from_file_location('m', 'pkg_util.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(inspect.getsource(m.parse))"
grep -n "def parse" -r .
```

On specimen-013 that pair is leftover body + the other `def parse`. bindname's load-bearing delta is still combining them in one query, plus `kind` reexport vs def, plus leftover `ast.py` not Homebrew. Mutation made that isolate real for ungated leftovers and stopped executing siblings. That is why this is not KILL.

Hardcoded unique-name exec is the new ceiling:

- Honesty leftover `ast.py` has `__name__ == 'ast'`. bindname leftover has `__name__ == '_bindname_1_ast'`. Name-gated leftovers are misses or unique-only bodies.
- `from pkg import parse` submodule is a Python bind `getattr` does not see.
- `also` is static last-def including `if False` / `TYPE_CHECKING`.
- utf-8 scan vs cookie exec: the queried file can `miss` itself.
- `runs=functools.parse` / wrapper source remain inspect artifacts.
- Nested defs, FIFO `--file`, huge `source`, query top-level (stderr, stdin, `os._exit` of the query, parent `__init__` `sys.exit`) stay as declared.

Observable capability lost if bindname vanishes: the pairing plus leftover-stdlib isolate for ungated helpers. Isolated `spec_from_file_location` + `inspect.getsource` + grep still do the rest. Unique names were the mutation's instrument; they are now the identity lie.

---

## Mutation (what must change)

Keep the object: for one import, the body that would run, versus other same-name defs that this import did not bind. Keep isolate (do not import the tree for `also`). Keep leftover `ast.py` as the leftover helper.

Do not keep a calculator that execs the leftover under a synthetic `__name__` and then remaps the TSV.

1. **Load the queried module under its logical name** via `spec_from_file_location` after `drop_foreign_cache`, not `_bindname_N_*`. Leftover `if __name__ == 'ast': def parse` must report the leftover body. `if __name__ != 'ast'` must report honesty-leftover, not unique-only. Restore stdlib after. Unique ids were to avoid `sys.modules`; the drop already does that. `runs` stays `ast.parse`. If logical-name load reintroduces Homebrew `ast.parse` as `kind=def` for leftover `ast.py`, that is a regression — a later destroyer should KILL.
2. **`from PKG import NAME` when NAME is a submodule.** Report the bound module (kind that is not `def parse` inside it), or a stated miss. Do not print `has no name` while honesty binds. List mode must not claim `same_function True` on the inner function as if it were the package bind.
3. **Static `also` / list last-binding are live binds, or say they are mentions.** `if False` / `TYPE_CHECKING` defs are not `also`. Query already refuses them; list/`also` must not resurrect them. If/Try that can run stay.
4. **Scan encoding matches exec.** Honor coding cookies / BOM so a latin-1 leftover does not `miss` itself. Sibling decode failures stay visible `miss` rows.
5. **`runs` / `kind` for partial, unwrapped decorator, `import mod as NAME`.** Do not invent `functools.parse`. Wrapper source is not the decorated def unless `wraps` says so. `also` is other independent defs, not every class/lambda in the tree.
6. **Stderr of the queried module is not the record.** Redirect like stdout, or static source only. FIFO `--file` remains out of scope only if declared (still `not a file`).
7. **Tests the current suite cannot see.** `__name__ == 'ast'` leftover; `__name__` unique-only branch; `from pkg import parse` submodule; latin-1 self-miss; TYPE_CHECKING / `if False` not in `also`; `functools.partial` `runs`.

Keep declared boundaries: nested defs (specimen-012), `importlib.import_module` inside `--file`, exec / PEP 562 / star as a **list** bind, query still runs that module's top-level (captured off stdout), huge `source` dump.

If a later mutation cannot do (1) without answering leftover `ast.py` as Homebrew `ast.parse`, or does (1) by `import_module` against `sys.modules` again, or fills `also` by executing siblings, KILL.

---

MUTATE
