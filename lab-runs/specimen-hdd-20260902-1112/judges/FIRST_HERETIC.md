# FIRST_HERETIC — first blind selection

Role: Heretic. Value genuinely unfamiliar interactions, not useful tables.

Sealed: no prior-run reports, no answer keys, no origin steering, no previous-run tool names. Lineage origin fields in `CANDIDATE.md` were ignored. Judged from runnable artifacts, demos, tests, and off-axis probes only.

No merge. No product code onto `main`.

Score real embodiments only. Strong empirical scores require execution evidence. Do not rank by code volume, polish, or README length. Do not average disagreement with other judges; this packet is one vote.

Scale: 0–5. 5 = a new object of inquiry (“why is this not already a verb?”). 1 = renamed ordinary workflow. 0 = demo theater.

---

## What was executed

All three candidate directories under `lineages/`. Fresh `./demo.sh` and `python3 tests/test_*.py -v` in each. Then adversarial probes that the demos do not show.

| candidate | demo | tests | heretic probes |
| --- | --- | --- | --- |
| `candidate-envlayers` (`envlayers`) | exit 0, specimen-010 fixture | 9/9 OK | messy dotenv, `export KEY=`, quoted empty, process `KEY=`, INI `proxy =` |
| `candidate-ordleak` (`ordleak`) | exit 0, specimen-009 pair | 6/6 OK | imported-module leak, class-attr leak, filesystem leak, env leak, two bindings, nested dict, both-fail, TestClass methods |
| `candidate-bind` (`bindname`) | exit 0, specimen-013 leftover/move | 11/11 OK | leftover vs reexport, nested/class, `import as`, star import, top-level side effect |

Tabs in CLI output are real TSV (verified by substituting `|` for `\t`). Terminal capture in this environment collapses tabs; do not treat collapsed logs as missing fields.

---

## Ranking (heretic)

1. **bindname** — different object of inquiry: *bound identity*, not *textual name*.
2. **ordleak** — different object of inquiry: *order-induced leak*, not *test failure*. Embodiment is narrower, and sometimes silent, than the question.
3. **envlayers** — real distinction (empty ≠ unset) trapped inside a specimen-shaped what-if table. Not a new verb.

**Advance:** `bindname`.
**Advance for mutation, not as a finished primitive:** `ordleak`.
**Do not advance as an unfamiliar interaction:** `envlayers`.

A Toolsmith may keep all three. This vote does not.

---

## candidate-bind / bindname

### The interaction

Ask a name how it binds:

```text
bindname -C DIR NAME
bindname -C DIR --from MODULE NAME
bindname -C DIR --import 'from MODULE import NAME'
bindname -C DIR --file PATH NAME
```

Observed on the leftover-vs-moved fixture (demo, exit 0):

```text
grep def parse  →  both pkg_util.py and pkg_parse.py

bindname --from pkg_util parse
  query   from pkg_util import parse
  bind    pkg_util.parse
  runs    pkg_util.parse
  kind    def
  source  return ('legacy', x)
  also    pkg_parse.parse
  same_function  False
```

`grep` hits both defs. The query that is actually asked — *which body would `from pkg_util import parse` run, and is there another independent body this import did not bind* — is one shot.

Reexport (tests, not the demo fixture): `kind=reexport`, `bind=pkg_util.parse`, `runs=pkg_parse.parse`, `same_function True`. That is the other half of the same question: leftover helper versus moved definition that left a reexport behind.

### Why this is unfamiliar

Ordinary nearest workflow:

```text
grep -n "def parse"
python -c "from pkg_util import parse; import inspect; print(inspect.getsource(parse))"
```

That is two tools, two objects: *definitions that mention the string* and *the one object this process imported*. Neither reports the other independent def, nor labels leftover versus reexport, nor answers `same_function`.

Reality-stripped remainder: import the module, print `inspect.getsource`, AST-scan other modules for the same name, join on object identity. Ingredients are familiar. The **object of inquiry is not**. Name-as-text versus name-as-binding is a recurring multi-step investigation collapsed into one explicit question.

This is the only candidate that made “why is this not already first-class?” feel earned.

### Cracks (do not kill the primitive)

- Nested defs and class methods are not import bindings. Advertised. Honest.
- Importing runs top-level code. Observed: a module that `print("SIDE_EFFECT")` printed it. Advertised. Still a cost.
- `--file user.py p` on `from pkg_parse import parse as p` reported `no uses of p`. The alias local name is the thing a stale test would call. Implementation crack, not a reason to deny the bind/runs split.
- List mode does not see `from pkg_parse import *` until you `--from` the importing module (runtime). AST-first list is incomplete for star imports.
- Python-only. That is a research boundary, not a costume.

### Scores

| axis | score | note |
| --- | ---: | --- |
| Novelty | 4 | Binding identity, not another “find definition”. |
| Utility | 4 | Move/split leftovers; Python import graphs. |
| Primitive strength | 4 | `bind` / `runs` / `kind` / `also` / `same_function` is one primitive. |
| Composability | 4 | TSV; `--from` / `--import` / `--file` are three doors to the same question. |
| Empirical credibility | 4 | Demo + 11 tests, including leftover, reexport, and `--file`. Heretic probes mostly agree. |
| Evolution potential | 4 | Other languages, assignment aliases, `import as` — without reconstructing git blame (correctly refused). |
| Reality-Stripped Strength | 4 | Join remains after deleting the name `bindname`. |
| Cross-specimen transfer | 2 | Owned leftover/move fixture plus a synthetic reexport. No unseen foreign tree in this packet. |

**Verdict: ADVANCE.** Keep. Mutate the alias/`--file` miss. Do not grow a tracer daemon.

---

## candidate-ordleak / ordleak

### The interaction

Run an explicit pair in both orders. Name what differed when only order changed.

```text
ordleak FILE LEFT RIGHT
```

Observed on the shared-`acc` pair (demo, exit 0):

```text
order   test_a test_b
status  test_a PASS
status  test_b FAIL  ['a']
order   test_b test_a
status  test_b PASS
status  test_a PASS
exposing_order  test_a test_b
leaked  acc  into  test_b  []  ['a']  via  test_a
```

Tests also include a hidden leak: both orders PASS, `exposing_order none`, still `leaked acc`. That row is the heretical part. Ordinary “rerun pytest in two orders” cannot say that, because there is no failure to bisect.

### Why this is somewhat unfamiliar

Ordinary nearest workflow: run the pair twice, compare traces by eye. pytest order plugins tell you *that* order matters. They do not name the leaked binding, and they do not report a leak that never failed an assertion.

Reality-stripped remainder: load the file twice, call two functions, deepcopy non-callable module globals, diff start snapshots. Familiar machinery. The **question** — *what leaked when only order changed* — is a debugging object existing runners do not expose as a verb.

Two leaked names and in-place nested-dict mutation both named the bindings. That is not demo-only.

### Why the embodiment is not yet the question

Isolation is the test file’s module object in this process. That is not “two orders.” It is “two imports of one file, sharing the rest of the process.”

| probe | order contrast | named leak | what actually happened |
| --- | --- | --- | --- |
| module global `acc` in the same file | yes | `acc` | claimed behavior |
| two module globals | yes | `acc` and `flag` | claimed behavior |
| class attribute `Box.items` | yes (FAIL/PASS) | `leaked none` | classes are skipped; the tool sees the order bug and refuses to name the leak |
| `from pkg.state import acc` (with `PYTHONPATH`) | `exposing_order none` (both orders FAIL `test_b`) | inverted: `acc into test_a via test_b` | imported module is process-global; second “order” is dirty |
| `os.environ` write | both orders FAIL | `leaked none` | env is outside the snapshot |
| filesystem write | `exposing_order none` | `leaked none` | file persists across the two imports |
| pytest `class TestT` methods | cannot run | — | `no test callable 'test_a'` |

The class-attribute case is the damaging one for the claimed primitive: the report still says `leaked none` while `test_b` failed only after `test_a`. That is not a documented research boundary in the output. It is a false “nothing leaked.”

specimen-012’s `test_order.py` is the same pair as specimen-009. That is not transfer.

### Scores

| axis | score | note |
| --- | ---: | --- |
| Novelty | 3 | Question is 4. Embodiment is “diff two module dicts.” |
| Utility | 3 | High on same-file module globals; cliff elsewhere. |
| Primitive strength | 3 | Pair-contrast is real; “name what leaked” is only true for a narrow binding class. |
| Composability | 3 | Explicit pair is Unix-honest. Not a suite scanner (good). TSV is pipeable. |
| Empirical credibility | 3 | Demo+tests are honest on the fixture. Off-axis isolation failures are also empirical. |
| Evolution potential | 4 | Isolation holes are mutation fuel if the question is kept. |
| Reality-Stripped Strength | 3 | Hidden-leak row survives stripping. Class-attr silence does not. |
| Cross-specimen transfer | 1 | Second listed specimen is a duplicate file. |

**Verdict: ADVANCE FOR MUTATION.** Do not freeze this isolation model. Do not kill the question. A later embodiment that still prints `leaked none` on a class-level list should be killed.

---

## candidate-envlayers / envlayers

### The interaction

One environment key, five labeled rows:

```text
inherited / file / skip_empty / assign / process
```

Observed on the owned empty-assignment fixture (demo, exit 0):

```text
key         KEY
inherited   '/x'
file        ''
skip_empty  '/x'
assign      ''
process     None
```

Empty file assignment is not unset. `skip_empty` keeps `'/x'`. `assign` stores `''`. `process` is `None` while inherited overlay is `'/x'`. That table is what the demo is for, and it works.

### Why this is not an unfamiliar interaction

Ordinary nearest workflow, once you already know the two loader policies:

```text
cat file.env
printenv KEY
# mentally apply: if v: assign  versus  always assign
```

Reality-stripped remainder: parse `KEY=VALUE` lines, overlay on a dict, apply `if v:` versus always-assign, print `repr` so `''` and `None` stay distinct.

`skip_empty` and `assign` are not observed layers of a running program. They are **two hardcoded policies copied from the fixture**. The README says the tool will not infer which policy a third-party loader used. So the CLI cannot answer the actual developer question (“what did *this* loader do with `KEY=`?”). It answers a hypothetical the author already knew.

The only remainder that is even slightly first-class: **empty is a present assignment**, printed next to unset as `''` vs `None`. That is a real collapsed distinction (`printenv` after a skip-empty loader has already thrown it away). It is not five layers. It is one boolean wearing a table.

### Off-axis (same process, same binary)

- `export KEY=` is a different key. File layer for `KEY` is `None`.
- `KEY=''` in the file is a truthy string of quotes; `skip_empty` assigns it.
- `KEY=0` and `KEY=false` are truthy (Python string truthiness, not shell/dotenv).
- Process `KEY=` with `--no-process-env`: `process ''`, `inherited None`. The empty-vs-unset split works *inside this process*.
- Unseen-ish INI empty assignment (`proxy =` in specimen-031 user pip.conf): query `proxy` → all `None`. Parser stored the key as `'proxy '` (trailing space). Query `'proxy '` to see `file ''`. The empty-assignment primitive did not transfer across a space-padded `=`.

This is a dotenv-line table for one specimen’s two functions. Useful composition, if that is the job. It is not a new observation of environment.

### Scores

| axis | score | note |
| --- | ---: | --- |
| Novelty | 2 | Empty≠unset is a real query object. The five-row table is costume. |
| Utility | 2 | Immediate on the fixture. Brittle parser; no attach; no policy discovery. |
| Primitive strength | 2 | Fixed layer list, two policies baked in. |
| Composability | 3 | One key, TSV, overlays. Unix-shaped. Still a table, not a verb. |
| Empirical credibility | 3 | Demo+9 tests match specimen-010. Off-axis parser/format misses are also evidence. |
| Evolution potential | 2 | Becomes interesting only if hardcoded policies die and empty-vs-unset becomes the whole tool. |
| Reality-Stripped Strength | 2 | `cat` + two `if`s. |
| Cross-specimen transfer | 1 | INI empty assignment did not query as the same key. |

**Verdict: DO NOT ADVANCE as an unfamiliar interaction.** Remember the collapsed distinction (empty assignment vs unset). Do not PATH-install a two-policy simulator. A Unix/Toolsmith keep is expected; this vote is no.

---

## Axis table (heretic weights)

Novelty, Reality-Stripped Strength, and Primitive strength dominate. Utility without a new question does not save a candidate here.

| axis | bindname | ordleak | envlayers |
| --- | ---: | ---: | ---: |
| Novelty | 4 | 3 | 2 |
| Utility | 4 | 3 | 2 |
| Primitive strength | 4 | 3 | 2 |
| Composability | 4 | 3 | 3 |
| Empirical credibility | 4 | 3 | 3 |
| Evolution potential | 4 | 4 | 2 |
| Reality-Stripped Strength | 4 | 3 | 2 |
| Cross-specimen transfer | 2 | 1 | 1 |

Do not average these into a single score. The ranking is the ranking.

---

## Selection

| candidate | heretic decision | why |
| --- | --- | --- |
| `candidate-bind` / `bindname` | **SURVIVE** | Bound identity vs textual name. Leftover vs reexport is a real join. |
| `candidate-ordleak` / `ordleak` | **SURVIVE-TO-MUTATE** | Keep “what leaked when only order changed.” Do not keep “module globals of this file, and `leaked none` when it was a class.” |
| `candidate-envlayers` / `envlayers` | **NO** | Empty≠unset is a note. The embodiment is a labeled replay of two known loaders. |

Multiple real embodiments exist. This judge names **one** interaction that should survive as a primitive (`bindname`) and **one** question that should survive as a mutation target (`ordleak`). That is not a three-way keep.

---

## Tomorrow Test (heretic)

Which binary should a human actually install and try tomorrow?

- **Install:** `bindname`. Point it at a tree where a name moved and a helper stayed. Ask `--from` the stale module.
- **Drawer, not PATH:** `ordleak`, only after isolation is the pair of *orders*, not two imports sharing `sys.modules` / env / cwd.
- **Empty slot:** `envlayers`. The sentence “empty assignment is not unset” is enough to remember. The CLI is not.

Empty slots are allowed. Abundance is not a virtue.

---

## Expected disagreement (do not collapse)

- **Unix** will like all three for TSV, one-key/one-pair, small stdlib CLIs. Heretic grants the shape and still rejects `envlayers` as a renamed `cat`+`repr`.
- **Toolsmith** will argue `envlayers` is the one a person would actually run tomorrow on a dotenv incident. Possibly true. Usefulness is not the heretic axis.
- **Skeptic** may try to kill `bindname` as `inspect.getsource` plus grep. The `also`/`same_function` join is the answer to that kill. If a skeptic shows an ordinary one-liner that reports leftover versus reexport as one query, this vote should be revisited.
- **Reality-stripped** should agree that `envlayers` shrinks to two policy functions, and that `bindname` still has a remainder.

---

## Notes for later, not used here

Origins, answer keys, and prior-run names remain sealed for this packet. Transfer scores are low because this judge would not unseal them to inflate them.

No candidate product was merged.
