# FIRST_TOOLSMITH

Role: Toolsmith. Question: **what would a developer use tomorrow?**

Sealed first selection. Judged only the real CLIs under `lab-runs/specimen-hdd-20260902-1112/lineages/candidate-{envlayers,ordleak,bind}/`. Did not read prior-run reports, origins, Dreamer transcripts, or answer keys.

A toolsmith keeps a verb that collapses a recurring loop into one command. Strange is allowed if it already paid rent. Polish, LOC, and README size are not scores. Multiple KEEP. Empty PATH slots are allowed.

Ran `./demo.sh` and the bundled tests myself, then extra cases a person would actually type.

| candidate | demo | tests | KEEP/KILL | tomorrow PATH |
| --- | --- | --- | --- | --- |
| `ordleak` | pass | 6/6 | **KEEP** | **install** |
| `bindname` | pass | 11/11 | **KEEP** | **install** |
| `envlayers` | pass | 9/9 | **KEEP** | remember, do not install yet |

---

## Tomorrow Test

Binaries a human should actually install and try tomorrow:

1. `ordleak` — suspected pair, both orders, name the leaked binding.
2. `bindname` — after a move, which body does this import run?

Not on PATH tomorrow: `envlayers`. The empty-vs-unset table is a real question. The file parser lies on `export KEY=`, comments, and quoted empty, so I would not trust it on a real `.env`.

---

## `ordleak` — KEEP, install

**Verb:** run two named tests in both orders; print which module binding differed when only order changed, and which order is enough to expose it.

### Execution

- `./demo.sh` exit 0 on specimen-009. `test_a test_b` FAIL with `['a']`; reverse PASS. `exposing_order	test_a test_b`. `leaked	acc	into	test_b	[]	['a']	via	test_a`.
- `python3 tests/test_ordleak.py -v`: 6/6 OK.
- Transfer: same pair on specimen-012, same leak row.
- Hidden leak (no failing assert): `exposing_order	none` and still `leaked	box	into	test_c	{'n': 0}	{'n': 1}	via	test_a`. That is rent.
- `FILE::LEFT FILE::RIGHT` nodeids work.

### Extra dogfood (not in demo)

- Class methods / `unittest.TestCase` methods: `no test callable 'test_a'`. Honest boundary, and it will miss a lot of real suites.
- Leak in an imported helper: both orders FAIL, `exposing_order	none`, `leaked	none`. `helper` stays in `sys.modules`, so order two is not isolated. Documented “two orders do not share state” is false for imports, env, and files.
- `os.environ` / filesystem leaks: statuses can fail, leak row stays `none`. Process-global state is not snapshotted and is not reset between orders.
- Always-fail pair: `none`/`none`, correct.

### Scores

| axis | score | why |
| --- | --- | --- |
| Novelty | 4 | Pytest will run two nodeids. It will not name the leaked binding or the sufficient exposing order. Random-order plugins say “flaky”; this says `acc`. |
| Utility | 4 | I would type this tomorrow on a suspected pair. I would not type it as a suite scanner, and I cannot type it on class-based tests. That is still weekly work. |
| Primitive strength | 5 | One query, two facts: *what leaked* and *which order exposes it*. Pair-not-suite is the right cut, not a missing feature. Hidden leak without a fail is the same primitive, not a second tool. |
| Composability | 4 | Tab-separated, `repr` values, nodeid form, exit 0 on a diagnostic report (not a test runner). Usage errors are 2. |
| Empirical credibility | 5 | Demo, tests, specimen-012, hidden-leak control all observed here. |
| Evolution potential | 4 | Fresh import of helpers, class/unittest callables, maybe env/tmp as a later layer. Do not grow into a whole-suite permuter. |
| Reality-Stripped Strength | 4 | Operation left: load the file twice, run A then B and B then A, snapshot non-callable module globals before each call, diff. Nearest workflow: `pytest t1 t2; pytest t2 t1` plus print. Lost if replaced: the join that names `acc` and `test_a test_b` as one answer, including when both tests pass. |
| Cross-specimen transfer | 4 | 009 and 012 (same mechanism), plus a hidden-leak fixture that is not the original assert. Does not transfer to class/unittest/import-module leaks. |

**Reality-stripped:** ignore the name. Remaining operation is “contrast two run orders and diff module bindings at test start.” Ordinary replacement is two pytest invocations and a human diff. The lost capability is the named leak and the exposing order. That is why it is not a wrapper.

**KEEP.** First PATH slot.

---

## `bindname` — KEEP, install

**Verb:** for a name, show the import path and the body that would run. Leftover same-name helper vs moved definition vs reexport.

### Execution

- `./demo.sh` exit 0 on specimen-013. `grep def parse` hits both files. `--from pkg_util parse` → `kind	def`, `runs	pkg_util.parse`, leftover `legacy` body, `also	pkg_parse.parse`, `same_function	False`. `--from pkg_parse` / `--import 'from pkg_parse import parse'` → moved `strip` body. `--file test_parse_identity.py parse` lists both binds, `same_function	False`.
- `python3 tests/test_bindname.py -v`: 11/11 OK, including a true reexport (`kind	reexport`, `runs	pkg_parse.parse`, `same_function	True`).

### Extra dogfood

- True reexport: `bind	pkg_util.parse` / `runs	pkg_parse.parse` / `kind	reexport`. This is the other half of the primitive; leftover vs moved is not just “grep two defs.”
- Package leftover + `__init__` reexport: works. `runs	pack.parse.parse` is ugly and true.
- Assignment alias `parse = other`: `runs	alias.other` and the body of `other`. Correct “what would run.”
- Nested `parse` assigned at module level: reports the nested body that would run.
- Importing runs top-level code: `print("SIDE_EFFECT")` lands on **stdout** and contaminates TSV. Documented, still a pipe-breaker.
- Query mode `also` is tree-wide. `--from pack.util parse` also lists unrelated `pkg_parse.parse` in the same temp tree. On a real repo `bindname parse` will drown.
- `--file` on `from pkg_util import parse as p` with query `p`: `no uses of p`. Query `parse` works. Tomorrow people ask about the local name.

### Scores

| axis | score | why |
| --- | --- | --- |
| Novelty | 3 | `python -c 'import inspect; print(inspect.getsource(parse))'` exists. Jedi/go-to-def exist. The CLI that answers leftover-vs-reexport and names the other def is the gap. |
| Utility | 4 | After a move, I would type `bindname --from pkg_util parse`. That is the loop of grep + import + getsource + “is this the same object.” Tree-wide `bindname parse` I would not trust as a search. |
| Primitive strength | 4 | Import path vs body that runs, `def` vs `reexport`, `same_function`. Strong. `also` is the right extra fact with the wrong default scope. |
| Composability | 3 | TSV and flags (`--from`, `--import`, `--file`, `MODULE.NAME`) compose. Side-effect prints on stdout do not. `--file` is cwd-relative, not `-C`-relative. |
| Empirical credibility | 5 | Demo, 11 tests, leftover/reexport/package/alias observed here. |
| Evolution potential | 4 | Scope `also` to the queried package; capture/redirect import stdout; bind local aliases (`as p`). Do not add git-blame reconstruction. |
| Reality-Stripped Strength | 4 | Operation left: AST-scan defs/imports, import the modules, inspect the bound object. Nearest workflow: grep + `python -c` + `is`. Lost: leftover vs reexport in one table, `also`, `same_function`. |
| Cross-specimen transfer | 3 | Owned fixture is 013. Synthetic leftover, reexport, and package trees transferred. No second identity specimen run. |

**Reality-stripped:** ignore the name. Remaining operation is “resolve this import to a source body, and mention other defs of that name.” Ordinary replacement is editor go-to-definition, which often follows the name you meant, not the leftover helper you actually imported. That miss is the rent.

**KEEP.** Second PATH slot.

---

## `envlayers` — KEEP, do not install yet

**Verb:** for one environment key, print inherited / file / skip-empty / assign / process, with empty distinct from unset.

### Execution

- `./demo.sh` exit 0 on specimen-010. Inherited `KEY=/x`, file `KEY=`, process unset: `file	''`, `skip_empty	'/x'`, `assign	''`, `process	None`. `OTHER` is `'2'` on file/skip/assign. TSV is real (awk `-F'\t'` extracted `file` as empty).
- `python3 tests/test_envlayers.py -v`: 9/9 OK. Empty file assignment ≠ absent key. Process empty string `''` ≠ process `None`.

### Extra dogfood

- Docker-style `KEY=` (no `export`) matches the demo. Last-assignment-wins works. Missing file: exit 1.
- `export KEY=` in a real-looking dotenv: `file	None`, skip and assign stay inherited `/x`. The empty assignment is invisible. Tomorrow’s `.env` often has `export`.
- Comment line `# comment KEY=should-not-count` becomes a key named `# comment KEY`.
- `KEY=""` is file `'""'` (quoted characters), so skip-empty treats it as present and truthy. Quoted empty ≠ empty.
- `KEY_SPACE = spaced` is a different key (`KEY_SPACE `). Lookup `KEY_SPACE` is unset.
- No `--file`: file layer `None`, skip/assign equal inherited. Fine.
- Process `KEY=`: inherited and process are `''`. Overlay `--inherited` does not pretend to be process env. Fine.

### Scores

| axis | score | why |
| --- | --- | --- |
| Novelty | 3 | Empty vs unset is an old wound. `printenv` cannot see a file `KEY=` after a skip-empty loader left `/x`. The labeled two-policy table is the new question. It is not a new physics. |
| Utility | 3 | The loop “I wrote `KEY=` and it is still `/x`” is real. I would not type this tomorrow on a repo `.env` after watching `export KEY=` vanish. A tool that lies is worse than `cat -e`. |
| Primitive strength | 4 | “Empty is not unset; show one key at every layer” is a small hard primitive. The two loaders (`if v:` vs always assign) are specimen-shaped, but they are real policies, not decoration. |
| Composability | 4 | One key, TSV, Python `repr` so `''` and `None` stay distinct, awk-able, no stdout junk on the happy path. |
| Empirical credibility | 5 | Demo, tests, and extra probes all observed here. The parser failures are also observed, not inferred. |
| Evolution potential | 4 | Comments, `export`, quotes, then maybe named policies (`dotenv`, `compose`, `direnv`) as rows. Attach was correctly not built. |
| Reality-Stripped Strength | 3 | Operation left: parse `KEY=` lines, apply two assignment policies, print a table. Nearest workflow: `cat -e .env` + `printenv` + a six-line Python dump. Lost: one labeled contrast of skip-empty vs assign with empty≠unset. Real, thin until the parser is honest. |
| Cross-specimen transfer | 2 | Claimed specimen is 010 only. Transfers to other raw `KEY=` files. Does not transfer to `export`/quoted dotenv. No second env specimen exercised. |

**Reality-stripped:** ignore the name. Remaining operation is “show this key as inherited, as written in a file, under skip-empty, under assign-all, and in this process.” Ordinary replacement is reading the file with `repr` and printing `os.environ`. What you lose is the policy contrast. What you must not lose is empty≠unset. What this embodiment still loses on contact with a real dotenv is the file layer itself.

**KEEP** the lineage. **Not** a tomorrow PATH entry until comments/`export`/quotes stop lying.

---

## What I would type tomorrow

```text
ordleak tests/test_order.py test_a test_b
bindname -C src --from pkg.util parse
```

Not:

```text
envlayers --file .env DATABASE_URL
```

until the file layer matches the file I actually have.

---

## KEEP / KILL

| candidate | decision | reason |
| --- | --- | --- |
| `ordleak` | KEEP | Collapses the order-flake loop to one command. Paid rent on the demo, on 012, and on a hidden leak. |
| `bindname` | KEEP | Collapses leftover-vs-moved to one command. Paid rent on 013 and on reexport. |
| `envlayers` | KEEP | The layer table is a real verb. Embodiment is not yet something I would install. |

No KILL. None of these is a polished clone of an ordinary workflow. `envlayers` is the closest to a thin table, and it is also the one I will not put on PATH.

Do not merge any of them onto `main`.

---

## Notes for later judges (not a ranking)

- Do not average these scores. A Unix judge may like `envlayers` more than I did because the table is tiny and orthogonal. A skeptic may KILL it because it does not attach and the parser is a toy. Both can be right.
- `ordleak`’s isolation hole (imported modules / env / files) is the first destroyer target, not a reason to drop the verb.
- `bindname`’s stdout side effects and tree-wide `also` are the first destroyer targets, not a reason to drop leftover-vs-reexport.
