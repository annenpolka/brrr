# FIRST_UNIX — first blind selection

Judge: Unix
Run: specimen-hdd-20260902-1112
When: 2026-09-02
Archives scored (only these):

- `lineages/candidate-envlayers/` (`envlayers`)
- `lineages/candidate-ordleak/` (`ordleak`)
- `lineages/candidate-bind/` (`bindname`)

Sealed and unread: prior-run lineages/judges, hdd-origins, answer-key, evolution reports.
Lineage origin in `CANDIDATE.md` was not used as a grade. Creator self-labels (`USEFUL_COMPOSITION`) ignored.
This judge does not average with other judges and does not merge to `main`.

Scale: integer 0–5 per axis. Strong empirical scores require execution in this session.
Unix lens: one object of inquiry, tiny orthogonal verbs, text in/out, exit status, composition with ordinary filters. Not ranked by LOC, polish, UI, or README length.

---

## Execution (this session)

All three `demo.sh` ran exit 0. Unit tests:

| archive | tests | result |
| --- | --- | --- |
| envlayers | `python3 tests/test_envlayers.py -v` | 9/9 OK |
| ordleak | `python3 tests/test_ordleak.py -v` | 6/6 OK |
| bindname | `python3 tests/test_bindname.py -v` | 11/11 OK |

Additional probes (stdin, isolation, parser, class tests, other-module/env/fs leaks, INI transfer, owned fixtures) are cited under each candidate. Tabs in TSV are real; some logs below show fields separated by spaces only because the transcript collapsed `\t`.

---

## candidate-bind — `bindname`

**Object.** For one name, print the import path that binds it and the body that would run. Leftover same-name helper vs moved definition vs reexport.

**Demo (specimen-013).** `grep def parse` hits both files. Fixture prints `legacy` vs `moved`, `same_function False`. `bindname -C files parse` lists two `kind=def` binds. `--from pkg_util parse` → `runs=pkg_util.parse`, `also pkg_parse.parse`, `same_function False`. `--import 'from pkg_parse import parse'` → moved body with `strip`. `--file test_parse_identity.py parse` lists both attribute uses.

This is the Unix verb in the batch: `which`/`type` for an import binding. Grep names spellings. `inspect.getsource` names one object you already imported. bindname names *which body this import selects*, and whether another independent def exists.

### Axes

| axis | score | note |
| --- | ---: | --- |
| Novelty | 4 | Same-name leftover after a move is a real question existing search does not answer in one shot. Not a new cosmology; a missing locator. |
| Utility | 4 | I would run this tomorrow on a stale `from util import parse`. Whole-tree import and stdout side-effects keep it off a 5. |
| Primitive strength | 4 | `bind` vs `runs` vs `kind=def|reexport` vs `same_function` is one object. Extra flags (`--from`, `--import`, `--file`, `MODULE.NAME`) are mouths, not extra products. |
| Composability | 3 | TSV; `-C DIR` like make/git; `awk -F'\t' '$1=="runs"'` works. Not a stdin filter. Importing a module dumps its prints onto stdout and breaks the table. Querying one name still imports every module that defines it. |
| Empirical credibility | 4 | Demo + 11 tests. Owned leftover/moved and true-reexport fixtures pass. Relative import `from .core import parse` reports `kind=reexport` `runs=rel.core.parse`. Packages work. Failures below are real, not theoretical. |
| Evolution potential | 4 | Isolate import stdout/stderr; import only the queried module; keep assignment source; stop calling `int.parse` a reexport. Static-only mode would be a sibling, not a mashup. |
| Reality-Stripped Strength | 4 | Strip the name: resolve an import to the defining object and list other defs of that name. Nearest ordinary workflow: grep + `python -c inspect`. Lost if replaced: leftover vs reexport and identity across a tree without calling the function. |
| Cross-specimen transfer | 3 | Owned two-def and reexport trees (not the demo fixture) recover the same object. specimen-055 `helper`: finds `proj.conftest.helper` as `kind=reexport` `runs=str.helper` with empty source — pytest injection is not an import bind; `--file tests/test_item.py helper` exits 1 (bare name, no import). specimen-034 `test` only locates the test function, not the interesting identity. |

**Empirical dings (executed).**

- `parse = 2` reported `kind=reexport` `runs=int.parse` `source=''`. Assignment of a non-function is not a reexport.
- Top-level `print` in an unrelated `side.py` appeared on stdout while resolving `front.py` / listing `parse` — the walker imports the whole tree.
- `--from pkg parse` in a dirty tree lists `also` every other def of that name, including leftovers from earlier probes in the same tmpdir. Useful for the leftover-helper question; noisy as a default.
- Nested `def parse` inside `outer` is ignored (honest: not an import binding).
- Star import rejected with exit 2 (honest).

**Verdict: KEEP.** PATH-candidate. Smallest mutation is hygiene (import isolation, assignment kind), not a new product.

---

## candidate-ordleak — `ordleak`

**Object.** Run two named tests in both orders. Report the exposing order and the module-level binding whose *start* value changed when only order changed.

**Demo (specimen-009).** Fixture runner: `test_a` then `test_b` FAIL `['a']`; reverse PASS. `ordleak FILE test_a test_b` names `exposing_order test_a test_b` and `leaked acc into test_b [] ['a'] via test_a`. Tests also cover hidden leak without a failing assert (`acc` still named, `exposing_order none`) and a no-leak control (`leaked none`).

This is a real Unix contrast: not “run the suite twice”, but `cmp` of start-state across a pair permutation. The pair is explicit, like `diff`. That is a feature.

### Axes

| axis | score | note |
| --- | ---: | --- |
| Novelty | 4 | Order-dependent tests are old. Naming the leaked binding, including when both orders PASS, is not what a second pytest invocation gives you. |
| Utility | 4 | I would use it on a suspected pair. I would not use it as a suite permuter (and it refuses to be one). |
| Primitive strength | 4 | Two operations that belong together: status delta across orders, and snapshot-diff of non-callable module globals at each test start. Orthogonal to pytest. |
| Composability | 3 | TSV rows. No stdin. Exit 0 even when a leak is named — `diff` would be 1. Pair cannot be streamed. `leaked … into … via …` is parseable but wordy. |
| Empirical credibility | 3 | Happy path is solid (demo, 6 tests, dict-mutate hidden leak). Isolation and naming holes below are execution failures, not README caveats. |
| Evolution potential | 4 | Subprocess (or at least env/modules/cwd) isolation per order; exit 1 on leak or exposing order; class/method targets; maybe stdin `FILE LEFT RIGHT`. Do not grow a whole-suite scanner. |
| Reality-Stripped Strength | 4 | Remaining op: A then B vs B then A; diff module globals at start. Nearest workflow: two pytest nodeid orders and a human. Lost if replaced: named leak and silent leaks. |
| Cross-specimen transfer | 3 | Owned hidden-leak and `state` dict fixtures transfer. specimen-012 `test_order.py` is **byte-identical** to specimen-009 (`shasum` match) — clone, not transfer. specimen-030 class tests: `No module named 'pytest'` (and class methods are not module callables anyway). |

**Empirical dings (executed).**

- Declared “two orders do not share state.” False for process globals:
  - `os.environ` mutation: CLI order `test_a test_b` reports `exposing_order none` (second order contaminated). CLI order `test_b test_a` reports `exposing_order test_a test_b`. **The report depends on argument order.**
  - Imported `pkg.mod.val` with `PYTHONPATH=.`: both orders fail `test_b`, `leaked none` — dependency modules stay in `sys.modules`.
  - Filesystem side file: same contamination, `exposing_order none`.
- Class methods: `no test callable 'test_a'` / `'T.test_a'`.
- Mutable default on module-level `f(x=[])`: exposing_order correct, `leaked none` (functions skipped; default lives on the function object).
- Closure `acc` (the shape of the specimen’s *other* file `run_orders.py`): exposing_order correct, `leaked none`.
- Local package import without `PYTHONPATH`: `No module named 'pkg'` (sys.path is the CLI’s directory, not cwd).
- No `-` stdin.

Boundary is honest (only that file’s module globals). Status rows still claim isolated orders. That is the Unix problem: the tool prints PASS/FAIL as if the second import were a fresh process.

**Verdict: KEEP the verb, MUTATE the embodiment.** First-selection survivor. Do not ship until one order cannot poison the other and a leak is a non-zero exit.

---

## candidate-envlayers — `envlayers`

**Object.** For one environment key, print inherited, file assignment (empty vs absent), skip-empty loader, assign-all loader, and this process env.

**Demo (specimen-010).** Fixture `loader.py`: skip_empty keeps `'/x'`, assign stores `''`. `envlayers` on `KEY=` with inherited `KEY=/x`:

```
key	KEY
inherited	'/x'
file	''
skip_empty	'/x'
assign	''
process	None
```

`OTHER` is assigned `'2'` in both loaders. `file ''` vs `file None` is the empty-vs-unset distinction `printenv` loses after a loader has already chosen.

The *question* is Unix: empty assignment is not unset. The *embodiment* is a five-row dashboard that *simulates* two hardcoded Python policies (`if v:` vs always assign) instead of observing a loader or exposing parse and merge as filters.

### Axes

| axis | score | note |
| --- | ---: | --- |
| Novelty | 3 | `KEY=` vs unset is POSIX folklore. Labeling skip-empty vs assign for one key is a small new question, not a new verb family. |
| Utility | 2 | I would not install this. On the specimen it reprints `loader.py`. It does not attach to another process (honest). Real dotenv/INI files are misparsed. |
| Primitive strength | 3 | Empty vs absent is a primitive. Bundling inherited + file + skip_empty + assign + process is a report, not an orthogonal verb. The two loaders are not available as composable filters. |
| Composability | 3 | TSV; `awk -F'\t' '$1=="skip_empty"'` returned `'/x'`. `--file -` fails; `--file /dev/stdin` works. No merge filter to pipe into. `--inherited` is a fake env, not `env`. |
| Empirical credibility | 4 | Demo + 9 tests match the specimen. Process empty string vs unset distinguished. Parser and transfer failures below are measured, so empirical stays high for the claimed fixture and drops on generality — that drop is scored on transfer/utility, not by ignoring the passing tests. |
| Evolution potential | 3 | Peel into `envparse` (empty vs absent, stdin) and `envmerge --skip-empty|--assign`. Or observe a real process. Do not add more named layers. |
| Reality-Stripped Strength | 3 | Remaining op: simulate two dotenv merges for one key. Nearest workflow: `cat` the file and `printenv`. Lost if replaced: one-query labeled empty vs skip vs assign. If you already know the two policies, replacement loses almost nothing. |
| Cross-specimen transfer | 2 | Nearest corpus neighbour is specimen-031 (user `proxy =` empty vs global proxy). As-is, `proxy` is `file None` — INI `proxy =` parses as key `'proxy '` with a trailing space. Querying `'proxy '` sees empty vs value but inherited overlay on `proxy` does not join. A hand-rewritten dotenv analogue *does* replay the object (`skip_empty` keeps global, `assign` stores `''`). Object transfers by re-encoding; the CLI does not transfer to the real file. |

**Empirical dings (executed).**

- `# KEY=hidden` / `export KEY=` / `KEY = spaced`: not dotenv. Comment line with `=` becomes a weird key; `export KEY=` is key `export KEY`; spaced `=` does not bind `KEY`.
- `KEY=""` stores literal `'""'`.
- Overlay `KEY = /x` binds key `'KEY '`, so `KEY` is `None` (exit 0, silent miss).
- Missing file exit 1; bad overlay exit 2 — fine.
- `process` is this CLI, not a target process.

**Verdict: MUTATE the object, do not KEEP this binary.** Empty≠unset deserves a parse primitive. This table is specimen-010 with extra print. Not a PATH slot. Not a KILL of the question.

---

## Scoreboard

| candidate | Nov | Util | Prim | Comp | Emp | Evo | RSS | Xfer | total | decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| bindname | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 3 | 30 | KEEP |
| ordleak | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 3 | 29 | KEEP verb / MUTATE isolation+exit |
| envlayers | 3 | 2 | 3 | 3 | 4 | 3 | 3 | 2 | 23 | MUTATE (peel); do not install |

Totals are a record, not a vote. Unix ranking below is by object and composition, not by sum.

---

## Unix ranking

1. **bindname** — one name, which body runs. Maps onto `which`/`type`. TSV. The leftover-vs-reexport split is the reason it exists. Hygiene mutations, not a rewrite.
2. **ordleak** — one pair, both orders, name what leaked. Maps onto `diff`/`cmp` of test start-state. Stronger novelty than bindname; weaker Unix citizenship (exit 0, process isolation lie). Survivor if mutated.
3. **envlayers** — one key, five simulated layers. Maps onto `printenv` only after you pretend two loaders. The interesting bit is empty vs absent; the rest is a dashboard. Peel or park.

None of the three is a stdin→stdout filter yet. bindname is closest to a query tool you actually type. ordleak is closest to a debugging primitive that should have been a verb already. envlayers is closest to a fixture pretty-printer.

---

## Survivors (Unix, this cut)

Keep as real embodiments worth evolving:

- **bindname** (KEEP, install-try)
- **ordleak** (KEEP the question; mutate before PATH)

Do not install:

- **envlayers** (remember empty≠unset; current CLI is not the verb)

Empty PATH slots are allowed. This judge would try **bindname** tomorrow, **ordleak** after isolation/exit, **envlayers** never in this shape.

---

## Mutations this judge wants (not implemented here)

**bindname**

- Import with stdout/stderr redirected; do not exec the whole tree for `--from`/`--file`.
- `kind=assign` for `NAME = literal`; never `int.parse`.
- Keep `also` as an explicit flag, not the default noise floor.

**ordleak**

- Fresh process (or saved/restored `os.environ` + imported-module wipe) per order.
- Exit 1 if `exposing_order` or `leaked` is not `none`; 0 if clean; 2 on usage.
- Leave class/pytest out until the module-global verb is honest.

**envlayers**

- Split: parse file → `KEY\tvalue|empty|absent`; merge policy as a second filter.
- Accept stdin (`-` and `/dev/stdin`).
- Drop the five-row specimen table as the product. If layers stay, they must be observed, not hardcoded `if v:` vs assign.

---

## What ordinary tools already do (reality-stripped, no prior-run names)

- envlayers: `cat` + `printenv` + reading `if v:`. Lost: labeled empty-vs-unset vs skip vs assign in one query, and only when the file is `KEY=` with no spaces.
- ordleak: two pytest orders. Lost: named module binding and silent leaks. Not lost: env/fs/other-module leaks (this tool misses them too, and misreports status).
- bindname: grep `def parse` + `inspect.getsource`. Lost: which import binds which body, reexport vs leftover, `same_function`.

---

## Independence

No other judge file was read. Destroyer notes were not used. Scores are from the binaries, tests, demos, and probes above.
