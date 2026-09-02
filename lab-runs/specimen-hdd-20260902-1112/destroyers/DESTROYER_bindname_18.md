# DESTROYER bindname 18

Date: 2026-09-02 21:51–21:55 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0662 worker=destroyer-bindname-18

Target (archive, post-MUTATE-16 / post-KEEP-17):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `c7d985ed9b0ebb42f775ff3bacefc3c27e9505ff37f25a03abdd82a18609755f` (73327 bytes). Matches `lineages/candidate-bind/MUTATE.md` after mutate-16 (`cli_sha256_after`, 119/119). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-bind-bind/bindname/bindname` is byte-identical (`cmp` rc=0). Worktree HEAD `c612e8a Record bindname mutate HEAD a0a6fec.` Archive `HEAD.txt` `c612e8a6a2c2acdc8b4c2b513c9f1878f12361c2`. Mutate-16 commit `a0a6fec`. Parent `main` is `432f954`; `git ls-tree` has no `bindname`. Host Python 3.14.5. No merge onto `main`. Worktree was not edited this pass.

`python3 tests/test_bindname.py` twice — 119/119 OK (14.034s / 14.262s). `./demo.sh` ×2 host-identical; archived `demo-1.log` / `demo-2.log` and both host logs byte-identical (`sha256` prefix `4d7df77f9d6709cf`). Wrapper exit 0.

First record: `DESTROYER_bindname.md` **MUTATE**. `_2`–`_14` **MUTATE**. `_15` **KEEP**. `_16` **MUTATE**. `_17` **KEEP**. First KEEP/MUTATE is not protection.

Honor KILL 1–10 host-executed. They do **not** fire (`HONOR_ANY False`). Mutate-16 leftover-identity still MATCH. New const-known probes this pass also MATCH: `T.x, y = 0, 0; if T.x` dead; `a = b = c = 0; if a` dead; `match 2: case 1 | 2:` live; `if (1 and 2 and 3) == 3` live; `if 1 is not True` live; `class T: x = 1; del x; if T.x` no bind (honesty AttributeError). Remaining list miss is still the declared nested-class object park plus FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While. Decision: **KEEP**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
```

Host-executed against the archive only. Attack log: `destroyers/_bindname18_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

| # | condition | fire? |
|---|-----------|-------|
| 1 | leftover `ast.py` Cellar / `lib/python` | no |
| 2 | `import_module` against `sys.modules` | no (`has_import_module False`) |
| 3 | `also` executes siblings | no |
| 4 | leftover `io.py` / `sys.py` `kind=def` | no |
| 5 | leftover `importlib.util` `kind=def` | no |
| 6 | leftover `importlib.py` / `importlib.abc` miss | no |
| 7 | `del T.x; if T.x: … else:` list `kind=def` | no |
| 8 | `del x; if x:` list `kind=def` | no |
| 9 | `t = T(); T.x = 0; if t.x` list live | no |
| 10 | THIN_WRAPPER of two greps | no |

---

## Mutate-16 + new probes MATCH

| fixture | honesty / query | list |
|---|---|---|
| `if (1 and 2) == 2` | `ae-live` | live |
| `if (1 and 2) is True` | `ait-dead` | dead |
| `T.x = y = 0; if T.x` | `mx-dead` | dead |
| `del T.x; if [T.x]` | AttributeError | no bind |
| `match (1,): case (1,):` | `msq-live` | live |
| `class T: match 1: case x: y = x; if T.y` | `mas-live` | live |
| `T.x, y = 0, 0; if T.x` | `mu-dead` | dead |
| `a = b = c = 0; if a` | `tn-dead` | dead |
| `match 2: case 1 \| 2:` | `mo-live` | live |
| `if (1 and 2 and 3) == 3` | `a3-live` | live |
| `if 1 is not True` | `int-live` | live |
| `class T: x = 1; del x; if T.x` | AttributeError | no bind |

`AST_STATIC_DIVERGES` is only `list_nestedcls` (declared nested-class object park). Attack fixture `multiset` syntax typo; `lambda_` is the declared lambda-bind park.

---

## Declared parks (not MUTATE)

- Nested class object: `class T: class U: y = 1; if T.U.y` query `'ncl-live'`; list miss. New `_Cls` object. `class T: class U: y = x` honesty NameError; already MATCH.
- FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While. Do not exec. Do not unroll For.
- Nested defs, FIFO `--file`, star/PEP562/exec as **list** binds, `--file` dynamic getattr / IfExp assign, AugAssign, Call in If tests, Try / assert / raise, match without static subject, MatchClass, Call For-iter, `T()` with `__init__`, format-error JoinedStr, `if __file__` / `if __name__`.

EXEC_PARK unchanged from DESTROYER_17.

---

## Primitive

Same as DESTROYER_17: leftover-vs-moved pairing plus leftover-stdlib isolate; const-known If/For/Match/BoolOp operand/mixed assign/collections-missing/MatchSequence. Nested class object / FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While stay last-wins or miss.

Nearest ordinary workflow remains `spec_from_file_location` + `inspect.getsource` + `grep def parse`. bindname's load-bearing delta is the join plus leftover `ast.py` not Homebrew. That is why this is not KILL and not THIN_WRAPPER.

---

## Mutation (what must change)

Nothing this cut. Remaining parks require executing user code or a new object. Do not exec. Do not store a nested `_Cls`. Keep leftover `ast.py` helper / leftover `importlib.util` miss / no `import_module`. If a later mutation answers Homebrew `ast.parse`, or leftover `importlib.util` is `kind=def`, or list-binds `del T.x; if T.x` / `del T.x; if [T.x]` while query has no name, KILL.

---

KEEP
