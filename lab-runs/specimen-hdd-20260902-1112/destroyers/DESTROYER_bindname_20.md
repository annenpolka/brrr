# DESTROYER bindname 20

Date: 2026-09-02 22:02–22:03 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0674 worker=destroyer-bindname-20

Target (archive, post-MUTATE-16 / KEEP-17 / KEEP-18 / KEEP-19):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname`

CLI sha256 `c7d985ed9b0ebb42f775ff3bacefc3c27e9505ff37f25a03abdd82a18609755f` (73327 bytes). Matches mutate-16 (119/119). Worktree byte-identical. Worktree HEAD `c612e8a`. Parent `main` `432f954`; no `bindname` on `main`. Host Python 3.14.5. No merge. Worktree not edited.

`python3 tests/test_bindname.py` twice — 119/119 OK. `./demo.sh` ×2 host-identical (`sha256` prefix `4d7df77f9d6709cf`).

`DESTROYER_bindname.md` **MUTATE**. `_2`–`_14` **MUTATE**. `_15` **KEEP**. `_16` **MUTATE**. `_17` **KEEP**. `_18` **KEEP**. `_19` **KEEP**. This is the **fourth KEEP** after mutate-16. First KEEP/MUTATE is not protection; four KEEP passes close the same declared parks.

Honor KILL 1–10 did **not** fire (`HONOR_ANY False`). Mutate-16 leftover-identity MATCH. Remaining list miss is declared nested-class object park plus FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While. `AST_STATIC_DIVERGES` is only `list_nestedcls` (declared). Decision: **KEEP**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/bindname
```

Host-executed against the archive only. Attack log: `destroyers/_bindname20_scratch/attack.log`. Do not merge onto `main`. Do not grow an import tracer. Do not send THIN_WRAPPER back to R1.

---

## Honor KILL (did not fire)

Same ten as DESTROYER_19. leftover `ast.py` helper, no `import_module`, `also` static, leftover `io.py`/`sys.py` miss, leftover `importlib.util` miss, leftover `importlib.py` helper, `del T.x; if T.x` skip both, `del x; if x` skip both, `t=T(); T.x=0; if t.x` dead, not two greps.

---

## Declared parks (not MUTATE)

Nested class object (`class T: class U: y = 1; if T.U.y` query live, list miss — new `_Cls`). FunctionDef sentinel / Name-bases / exec `__init__` / Subscript assign / While. Do not exec. Do not unroll For.

---

## Mutation (what must change)

Nothing this cut. Four KEEP after mutate-16. Remaining parks require executing user code or a new object. If a later mutation answers Homebrew `ast.parse`, leftover `importlib.util` is `kind=def`, or list-binds `del T.x; if T.x` / `del T.x; if [T.x]` while query has no name, KILL.

---

KEEP
