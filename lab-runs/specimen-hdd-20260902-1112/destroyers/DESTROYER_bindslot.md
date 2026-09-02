# DESTROYER bindslot

Date: 2026-09-02 12:58 JST

Target (harvested jump): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/jump-bind-nopath/bindslot`

sha256 `241c990ab5468ec37cfd84e46d5579971710d2125021075c70c6c91e4da57a5a` (8485 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/jump-bind-nopath-nopath/bindslot/bindslot` is byte-identical. Tests 17/17 pass. `demo-1.log` / `demo-2.log` byte-identical.

Origin claim (`CANDIDATE.md` / `JUMP.md`): for a name in one module, print every binding slot and the body that would run, after path identity is gone. Concatenated leftover vs moved must still be two slots. Parent `bindname` last-wins per path and reports one identity. This process does not import the blob.

Happy path is real. Specimen-013 concatenated is leftover `('legacy', x)` then runs `('moved', x.strip())`, `same_function False`, no `file` field. Isolation is real: `sys.exit(9)` and `print` in the blob do not hijack the query. That is not enough. `role=runs` is last source-order slot, not the bind that would run, and several module-namespace binds are not slots at all.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/jump-bind-nopath/bindslot
S013=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013/files
PARENT=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
```

No merge onto `main`. No merge of this jump back into `bindname`. This object is leftover vs moved inside one blob; it is not a tree-wide import of every same-name hit.

---

## What still works

Concatenated specimen-013, `--code` of that blob, and pathless stdin. Two `def parse`, last is moved, earlier is leftover.

```bash
python3 "$CLI" parse --concat "$S013/pkg_util.py" --concat "$S013/pkg_parse.py"
```

```text
name	parse
slots	2
runs_slot	1
same_function	False

slot	0
role	leftover
kind	def
line	1
source	"def parse(x):\n    return ('legacy', x)"

slot	1
role	runs
kind	def
line	4
source	"def parse(x):\n    return ('moved', x.strip())"
```

Honesty `exec` of the cat'd blob with no `__file__`: `parse('  z  ')` is `('moved', 'z')`. Parent `bindname -C concat_dir parse`: `count 1`, `same_function True`, only the moved body, `file concat.py`.

Leftover def then `from pkg_parse import parse`: last slot `kind=import`, leftover `kind=def`. Annotation-only `parse: Callable` is `no slots` rc=1. Syntax error and non-UTF-8 are visible `bindslot:` errors. Nested `def parse` inside a function or class is not a module slot (`grep def parse` still hits it). Unicode names (`解析`) work. FIFO, `/dev/stdin`, `-s -`, `--concat -` then a file, space in filename, symlink, hardlink: rc=0, no `file` field. TTY with no source: `source required` rc=2. Conflicting `-s` / `--concat` / `--code`: rc=2. Empty NAME: rc=2.

That is the whole useful delta. Attacks below break the “body that would run” claim around it, or show the primitive cannot see ordinary module binds that are not `def` / `assign` / `import` statements.

---

## Implementation

### 1. `role=runs` is last source slot, not the bind that would run

CANDIDATE.md: “Last slot is what would run if the module finished.” README: `runs_slot` is “the body that would run if the module finished.” Tests walk `If` bodies on purpose (`test_if_body_def_is_a_slot`). The printer then labels the last collected node `runs`.

**Dead branch last.** Honesty still binds leftover.

```bash
python3 "$CLI" parse --code "def parse(x):
    return ('legacy', x)
if False:
    def parse(x):
        return ('moved', x.strip())
"
```

```text
slots	2
runs_slot	1
role leftover  source legacy
role runs      source moved
rc=0
```

Honesty: `parse('  z  ')` is `('legacy', '  z  ')`. Same lie for `if 0:`, `while False:`, `from typing import TYPE_CHECKING` / `if TYPE_CHECKING:`, and an unmatched `match 0: case 1: def parse`.

`if False: ... else: def parse` happens to agree with honesty (else ran). The tool did not know that; it printed the last node.

**`for parse in []`:** last slot is the `for`, `role=runs`. Honesty: leftover function still bound (loop never assigned). `for parse in ['moved']:` honesty is `'moved'` — now the last slot did bind. Same AST shape, opposite runtime.

**`except ValueError as parse` / `except*`:** last slot `kind=assign`, `role=runs`. Python 3 clears the name at the end of the handler. Honesty: unbound. The “runs” body is a name that does not exist after the module finished.

**`del parse` is not a slot.** Two defs then `del parse`: `slots 2`, last leftover-vs-moved pair, `role=runs` on moved. Honesty: unbound. Def then `del parse` only: `slots 1`, `same_function True`, `role=runs` on the leftover. Honesty: unbound. The module finished. Nothing runs.

**Raise before last def** (stated research boundary, still printed as certainty):

```text
slots	2
role leftover  legacy
role runs      moved
rc=0
```

Honesty: `RuntimeError: die`, leftover still bound, moved never executed.

**Failed last import.** Leftover then `from no_such_mod import parse`: last slot `kind=import`, `from no_such_mod`, `role=runs`. Honesty: `ModuleNotFoundError`, leftover still bound, leftover still callable.

`iter_module_stmts` yields every `If`/`For`/`While`/`Try`/`Match`/`With` arm, then `slot_from_node` treats `For` targets, `With` as-names, and `ExceptHandler` names as assigns. Dead arms and non-persisting names become `runs`. That is unsupported certainty, not a leftover/moved report.

### 2. Module-namespace binds that are not slots (`same_function True` on the leftover)

One leftover `def parse`, then a later bind the scanner does not see: `slots 1`, `runs_slot 0`, `same_function True`. The header reads as one identity. Honesty is a different object.

| later bind | bindslot | honesty |
| --- | --- | --- |
| `(parse := lambda x: ('walrus', x))` | leftover `role=runs` | walrus lambda |
| `if (parse := lambda ...):` | leftover | walrus |
| `assert (parse := lambda ...)` | leftover | walrus |
| `match (parse := 'subj'):` | leftover | `'subj'` |
| `[parse := x for x in [('walrus-comp', 1)]]` | leftover | `('walrus-comp', 1)` |
| `match 1: case parse:` | leftover | `1` |
| `match ['moved']: case [parse]:` | leftover | `'moved'` |
| `match 1: case x as parse:` | leftover | `1` |
| `type parse = int` | leftover | `TypeAliasType` |
| `exec("def parse(x): return ('execed', x)")` | leftover | `('execed', ...)` |
| leftover then `from moved import *` (`moved.parse` exists) | leftover `same_function True` | `('star-moved', 'z')` |

Walrus-only / type-only / match-capture-only (no leftover def): `no slots for parse` rc=1. Honesty binds the name. The jump world (pathless blob) uses exactly these forms.

`from … import *` is an explicit `continue`. A true move that left a star import in the concatenated leftover file is reported as “one identity, leftover runs.”

PEP 562: `__getattr__` that returns `parse` is `no slots` rc=1. `parse` is not in `mod.__dict__`; `getattr(mod, 'parse')('z')` is `('getattr', 'z')`. Stated nested-def boundary is not this. Attribute access is how a pathless loader would bind the name.

`ast.Delete`, `ast.NamedExpr`, `ast.TypeAlias`, and match patterns are never `slot_from_node` cases. `If.test` / `Assert` / `Expr` are walked only as statements, not for named expressions inside them.

### 3. `--concat` is not `cat`; owned demo already disagrees on `line`

Both specimen-013 files end in `\n`. `cat pkg_util.py pkg_parse.py` has the moved def at line 3. `load_source` does `"\n".join(parts)`, which inserts an extra blank. `--concat` reports `line 4`. Stdin of the cat'd blob reports `line 3`. `demo-1.log` already prints both.

```text
== bindslot --concat ... ==
line	4

== bindslot stdin (pathless) ==
line	3
```

Slot index is the same. The only remaining location field (`line`, there is no `file`) does not name a line in the blob you would `exec`.

First file without a trailing newline: `--concat` still splits (join inserts `\n`), two slots, rc=0. Raw `cat` of those bytes is `return ('legacy', x)def parse(x):` and bindslot stdin of that cat is `syntax error` rc=1. `--concat` is neither cat nor a documented extra-newline rule.

Second file non-UTF-8, first file has the leftover: `not utf-8: …/b.py` rc=1, leftover not reported. Second file syntax error: `syntax error` on the joined blob, leftover not reported. UTF-8 BOM on an otherwise valid leftover+moved file: `invalid non-printable character U+FEFF` rc=1, both slots gone. One-module concat makes a join error a blob error; it also means `--concat` of two files is not “show leftover in file 1 even if file 2 is dirty.”

Backslash continuation as the last line of file 1 plus `def parse` in file 2: concat succeeds (`x = 1\` + newline + def), one slot, leftover identity never at issue. Fine as one blob; not `cat`.

### 4. `from` drops relative level; `from . import parse` has no `from` field

```text
from .pkg_parse import parse   →  from	pkg_parse
from ..pkg_parse import parse  →  from	pkg_parse
from . import parse            →  (no from row)
import pkg_parse as parse      →  from	pkg_parse
```

`slot_from_node` stores `node.module` / `alias.name` and never `node.level`. Absolute `from pkg_parse import parse` and relative `from ..pkg_parse import parse` print the same `from` field. `from . import parse` has `module is None`, so the optional row is omitted while `role=runs` still claims that import.

`import ast.parse` queried as `parse`: `no slots` (local name is `ast`). Queried as `ast`: one import slot, `from	ast.parse`. That is ordinary import semantics. The relative-level collapse is not.

### 5. Decorator source is the undecorated def; runtime body is the wrapper

```python
def deco(f):
    def wrap(x):
        return ('wrap', x)
    return wrap
@deco
def parse(x):
    return ('legacy', x)
```

```text
slots	1
same_function	True
role	runs
kind	def
line	7
source	"def parse(x):\n    return ('legacy', x)"
```

Honesty: `parse('  z  ')` is `('wrap', '  z  ')`. `ast.get_source_segment` on `FunctionDef` starts at `def`, not the decorator (`lineno` 7, decorator lineno 1). The printed “body that would run” is the function that did not run. Leftover-then-moved still classifies slots correctly; a decorated *runs* slot is a wrong body.

### 6. `same_function` is source-string equality; one slot is tautologically True

Two identical leftover copies: `slots 2`, `same_function True`. Runtime `is` is False (two function objects). The field means “source of every slot equals source of last,” which README states, and which a pipe will still read as “not a leftover/moved pair.”

One leftover plus an unseen later bind (§2): `same_function True` because the later bind was never a slot.

CRLF blob: leftover vs moved still `False`, but `source` embeds `\r\n`. Mixed LF leftover + CRLF moved would compare unequal even if the text otherwise matched.

200 kB body: rc=0 in 0.03s, stdout 200133 bytes (`source` is `repr` of the whole def). 80 defs: `slots 80`, `runs_slot 79`, 79 leftover rows, no cap. Not fatal; not a pipe component.

---

## Primitive

Reality-stripped operation: `ast.parse` one blob; walk module-namespace statements including compound wrappers; collect `FunctionDef`/`ClassDef`/`Assign`/`AnnAssign`/`AugAssign`/`Import`/`ImportFrom`/`For`/`With`/`ExceptHandler` whose target is NAME; last collected node is `runs`; earlier are `leftover`; `same_function` is source-string equality.

Nearest ordinary workflow:

```bash
cat pkg_util.py pkg_parse.py | grep -n "def parse"
python3 -c "mod=types.ModuleType('b'); exec(open('concat.py').read(), mod.__dict__); print(mod.parse('  z  '))"
```

On specimen-013 that pair is leftover line + moved line + last-wins exec. bindslot’s load-bearing delta is printing both slots in one TSV, marking last vs earlier, `kind` def/import/assign, skipping nested defs and annotation-only, and **not executing**. Parent `bindname` cannot ask this once path identity is gone, and it executes every same-name module to fill `also`.

That delta is why this is not KILL. The pairing survives concatenation and stdin. Isolation is the jump DESTROYER_bindname asked for.

The ceiling is already written into the walker, and it is too small for “body that would run”:

- last source slot ≠ runtime bind on dead branches, empty `for`, `except as`, `del`, raise, failed import
- walrus, match capture, `type` aliases, `exec`, `import *`, PEP 562 are not slots
- `--concat` line numbers are not the cat'd blob’s line numbers
- `from` is not a relative import
- decorator `source` is not the wrapper that runs
- `same_function True` at `slots 1` after a silent miss reads as one identity

Do not grow a tree-wide `import_module` to escape this. That is the parent, and it is a different object. Do not merge bindslot into bindname.

---

## Mutation (what must change)

Keep the object: for one name in one blob, leftover same-name helpers versus the slot that last-wins in source, with no path identity and no import of the blob.

Do not keep a printer that labels last-AST-hit `runs` while dead branches, `del`, and walrus disagree with exec.

1. **`role=runs` is a runtime claim or it is not printed.** Source-order last slot is `last` (or `source_last`). `runs` only if the tool executed, which this jump refuses. Dead `if False` / `TYPE_CHECKING` / unmatched `match` / empty `for` must not read as the body that would run. If the mutation still prints `role=runs` on `if False:` last def, a later destroyer should KILL.

2. **Unbind is a slot.** `del NAME` is a slot (`kind=del`) or a stated refusal that forces `role` off `runs` for a previous def. `except E as NAME` / `except*` must not be `runs` after Python 3 clears the name; either omit non-persisting handler names or mark them `cleared`.

3. **Module-namespace binds the walker skips are slots or a visible miss.** `NamedExpr` (`parse := …` in `Expr`/`If.test`/`Assert`/`match` subject/comprehension leak), match capture / `as` / sequence capture, `type NAME = …` (`ast.TypeAlias`), and `from … import *` (unknown names: `kind=import_star`, not leftover-as-runs). PEP 562 remains out of scope only if declared; `no slots` while `getattr` would bind is a miss, not a finished report. `exec("def parse")` stays a stated dynamic hole; then `same_function True` on the leftover is forbidden — emit `dynamic_bind_possible` or refuse certainty.

4. **`--concat` is cat bytes, or line numbers name the joined blob and README says so.** Files that already end in `\n` must not gain a blank line. `--concat` and `python3 bindslot NAME < cat.blob` must agree on `line`. Join errors (BOM, non-UTF-8, syntax) stay visible; do not claim leftover from file 1 after a failed join unless the tool stops calling the input one module.

5. **`from` includes relative level.** `from .pkg_parse import parse` is not `from pkg_parse`. `from . import parse` still has a `from` row (`.` / level). Absolute and relative must not collapse.

6. **Decorator `source` includes the decorator lines** (or `kind=def` plus a `wrapped` row). A sole `@deco def parse` must not print the undecorated body as `role=runs`.

7. **Tests the current suite cannot see.** `if False` last def vs honesty leftover; `for NAME in []`; `except as NAME` cleared; `del NAME`; walrus-only and leftover-then-walrus; `match` capture; `type NAME = int`; leftover then `from moved import *`; `--concat` vs cat line numbers on specimen-013; relative `from .pkg import NAME`; decorated sole bind; UTF-8 BOM.

If the mutation cannot do (1)+(3), the object is still `grep def NAME` plus last-wins AST with a `runs` sticker, and a later destroyer should KILL.

---

MUTATE
