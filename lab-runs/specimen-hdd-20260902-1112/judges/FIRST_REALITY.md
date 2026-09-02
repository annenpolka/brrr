# First Selection — Reality-Stripped

Judge: Reality-Stripped. Date: 2026-09-02.

Scope: shipped CLIs under `lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envlayers`, `candidate-ordleak`, `candidate-bind`. Names, branding, and architecture are ignored. The question is what operation remains if the label is peeled off.

Method: read README.md and CANDIDATE.md; inspect the shipped file; run `./demo.sh` and the unittest suite in each lineage directory. Ordinary-workflow replacements were run on the same fixtures in this session. Did not read `EVOLUTION_REPORT.md`, `lab/`, previous lineages, previous judge reports, `.hdd/` transcripts, or specimen `answer-key/` files.

Empirical rule: scores on Empirical credibility and Cross-specimen transfer are taken from this run, not from README claims. All three demos exited 0. All three test suites exited 0.

| Candidate | Demo | Tests | Observed in this run |
| --- | --- | --- | --- |
| envlayers | `./demo.sh` exit 0 | 9 OK | Fixture loader: skip_empty `'/x'` `'2'`, assign `''` `'2'`, process unset. CLI KEY: inherited `'/x'`, file `''`, skip_empty `'/x'`, assign `''`, process `None`. CLI OTHER: inherited `'1'`, file `'2'`, skip_empty `'2'`, assign `'2'`. Extra probe: file without KEY → file `None`, assign `'/x'` (not `''`). Process `KEY=` → process `''`; process unset → process `None`. |
| ordleak | `./demo.sh` exit 0 | 6 OK | Fixture orders: `test_a` then `test_b` → PASS/FAIL `['a']`; reverse → PASS/PASS. CLI names `exposing_order	test_a test_b` and `leaked	acc	into	test_b	[]	['a']	via	test_a`. Hidden pair (append, then no-assert): exposing_order `none`, leaked `acc` into `test_c` `[]` vs `['a']`. Independent pair: exposing_order `none`, leaked `none`. specimen-012 `test_order.py` is byte-identical to specimen-009. |
| bindname | `./demo.sh` exit 0 | 11 OK | `grep def parse` hits both files. Fixture: util `('legacy', '  z  ')`, parse `('moved', 'z')`, `same_function False`. `--from pkg_util parse`: kind `def`, runs `pkg_util.parse`, `also pkg_parse.parse`, `same_function False`, source is `return ('legacy', x)`. `--from pkg_parse`: runs moved `x.strip()` body. `--file test_parse_identity.py`: count 2, same_function False, both binds. Owned reexport fixture: kind `reexport`, runs `pkg_parse.parse`, same_function True, no `also`. |

Multiple KEEP is required. This report keeps three. Kill would be for a missing remainder, not for lack of polish. No candidate is merged onto `main`.

---

## candidate-envlayers — one key, five labeled values, empty assignment ≠ unset

Shipped file: `envlayers`.

### 1. Operation that remains

Name one environment key. Print its value at five layers, with Python `repr` so `''` and `None` stay distinct:

- **inherited** — starting map (copy of this process env unless `--no-process-env`, plus `--inherited NAME=VALUE` overlays);
- **file** — last `KEY=VALUE` in a dotenv-style file; `''` if the file assigns empty; `None` if the file has no `KEY=`;
- **skip_empty** — loader that copies inherited and assigns only truthy file values;
- **assign** — loader that copies inherited and assigns every file value, including empty;
- **process** — `os.environ` of this CLI process, not of some other process.

The cut is: empty file assignment is a present value, not unset, and the two loaders then disagree. The CLI does not attach, trace, or infer which policy a third-party tool used.

Honesty limit, part of the remainder: the file parser is `partition("=")` on each line. In this run `export KEY=` left file `None` (key parsed as `export KEY`). `KEY=""` stored file `'""'` and skip_empty assigned `'""'` rather than keeping inherited. Those are not dotenv. The claimed specimen shape is unquoted `KEY=`.

### 2. Nearest ordinary workflow

`printenv KEY`; `grep KEY file.env`; `env KEY=/x cmd`; two short Python loops (`if value:` vs always assign); or just run the loader you already have.

### 3. What is lost if that workflow replaces this tool

`printenv` sees one map, after a loader has already chosen. In this run, process unset printed nothing (exit 1); `env KEY=/x printenv KEY` printed `/x`; `grep` printed `KEY=`. None of those three says that skip-empty would keep `'/x'` while assign would store `''`, and none distinguishes file empty from file absent.

That last split was observed: same inherited `KEY=/x`, file `KEY=` → file `''`, skip_empty `'/x'`, assign `''`; file `OTHER=2` only → file `None`, skip_empty `'/x'`, assign `'/x'`. After replacement, that is two mental simulations, not one query. Process `KEY=` vs unset (`''` vs `None`) is also lost if you only `printenv`, which cannot spell unset.

What is *not* lost, and must not be claimed: watching another process. The skip/assign columns are what-if policies, not a trace.

### Scores

- **Novelty 2.** Dumping env and grepping `KEY=` are ordinary. Treating empty assignment as a different event from unset, and printing skip-empty vs assign-all as named layers, is a small cut, not a new object type.
- **Utility 4.** “Why is KEY still `/x` after the file said `KEY=`?” is a real, expensive debug. The empty-vs-unset fork is not hypothetical; the demo fixture is that case. Naive `export` / quoted-empty parsing limits how far the same query travels.
- **Primitive strength 3.** One key, five named cells, empty ≠ unset. The two loader policies are hardcoded rather than discovered; that is an honest boundary and also a thinner atom than “observe what the loader did.” No interpolation, no `+=`, no attach.
- **Composability 4.** One KEY argument, TSV rows, `repr` values, `--file` / `--inherited` / `--no-process-env`. Easy to ask one key at a time. Success is always exit 0; there is no fail-empty gate.
- **Empirical credibility 5.** This run: demo exit 0; 9/9 tests; empty vs absent file; process `''` vs `None`; inherited overlay distinct from process. Extra dotenv shapes were probed here and did not match a real parser; that is a documented remainder, not a hidden demo.
- **Evolution potential 3.** Last-wins across several files, and treating `KEY=""` as empty, stay inside the same question. Process attach or “guess the third-party policy” would destroy the primitive.
- **Reality-Stripped Strength 3.** Peel the name off and this is still not `printenv`: a five-cell what-if table whose interesting cell is empty-assignment vs unset. It is also close to shell glue plus two loops. Keep as a composition, not as a flagship.
- **Cross-specimen transfer 2.** Claimed specimen is one empty-assignment file. Owned extra cases (absent key, process empty string) transferred. No second distinct specimen was exercised; `export KEY=` / `KEY=""` did not transfer.

**KEEP** — USEFUL_COMPOSITION. Not a thin wrapper of `printenv`. Borderline wrapper of “run the two loaders,” except the file-empty vs file-absent split is a real extra observable.

---

## candidate-ordleak — pair of tests, both orders, name the start-state leak

Shipped file: `ordleak`.

### 1. Operation that remains

Name a file and two test callables. Import the file twice (once per order). Within an order, the two tests share module state; the two orders do not. Snapshot non-callable, non-class, non-underscore module bindings before each test. Report:

- PASS/FAIL/ERROR per test in each order;
- **exposing_order** — sequence where a test fails that passed in the other order, or `none`;
- **leaked** — binding whose value at the start of `into` differed when that test ran first versus after `via`, or `none`.

The pair is explicit. Not a suite permutation. Not pytest. Not other modules, env, or filesystem.

### 2. Nearest ordinary workflow

Run the two tests in both orders (`python` import, or a test runner with a chosen nodeid order) and read the PASS/FAIL lines. Optionally print the suspect global by hand.

The specimen’s own `run_orders.py` already does the first half: it prints PASS/FAIL and `acc_after`.

### 3. What is lost if that workflow replaces this tool

The join. Two orders tell you *that* order matters. They do not name *what* the second test saw at start. In this run, a plain two-order import printed PASS/FAIL `['a']` and stopped. The CLI added `leaked acc into test_b [] ['a'] via test_a` and `exposing_order test_a test_b`.

The stronger remainder is leak without a failing assert. This run: `test_a` appends, `test_c` is `pass` → both orders PASS, exposing_order `none`, leaked `acc` into `test_c` `[]` vs `['a']`. Replacement with a test runner reports green and never mentions `acc`. Independent tests: leaked `none`.

What is *not* lost: discovering that `test_a` then `test_b` fails. The fixture runner already showed that. What replacement will not emit unless someone writes it every time: the start-state binding diff for an explicit pair.

### Scores

- **Novelty 3.** Order-dependent tests are a known pain; rerunning two nodeids is ordinary. The remaining cut is “name the module binding whose start value changed when only order changed,” including when statuses agree. That is not a new test runner.
- **Utility 4.** Flaky-by-order module state is a daily debug. Naming `acc` is the expensive part. Pair-only is a real limit (you must already suspect the two names) and also what keeps the operation small.
- **Primitive strength 4.** The primitive is coherent: two named tests, two isolated imports, start snapshots, leak row and exposing order as separate facts. Hidden leak without fail is the same atom, not a second product. Deepcopy failure falls back to `repr`; other modules are out of scope.
- **Composability 4.** `FILE LEFT RIGHT` or `FILE::LEFT FILE::RIGHT`. TSV. Exit 0 on a successful report even when a test FAILs — the product is the contrast, not a runner status. A script can grep `leaked` / `exposing_order`.
- **Empirical credibility 5.** Demo exit 0; 6/6 tests; specimen pair; nodeid form; hidden leak; no-leak control. Numbers in this run are `[]` vs `['a']`, not a README claim.
- **Evolution potential 4.** Same-file extra names, or reporting which test *wrote* the binding, stay inside the pair. Whole-suite permutation, pytest plugin inference, or tracing env/fs would turn this into a scanner and kill the atom.
- **Reality-Stripped Strength 4.** Peel the name off and the remainder is still not “run tests twice.” It is a start-state leak record for an explicit pair, including leaks that never fail. That is the strongest remainder in this batch.
- **Cross-specimen transfer 2.** specimen-012 produced the same leak row, but `test_order.py` there is byte-identical to specimen-009, so that is a copy, not a new shape. The hidden no-assert pair is a real second shape and is owned, not a second specimen.

**KEEP** — USEFUL_COMPOSITION with a sharp remainder. The exposing-order bit is ordinary; the named start-state leak is not.

---

## candidate-bind (bindname) — this import binds this body; other same-name defs exist

Shipped file: `bindname` (directory `candidate-bind`).

### 1. Operation that remains

Name a name, optionally with the import that binds it (`--from MODULE`, `--import 'from MODULE import NAME'`, `MODULE.NAME`, or `--file PATH` for uses in that file). Walk a directory for module-level defs/assignments/imports of that name, import those modules, and report:

- **import / bind** — the import path;
- **runs** — defining identity of the object that would run;
- **kind** — `def` if this module defines it, `reexport` if it aliases another module’s object;
- **file / line / source** — the body that would run (`source` in `repr`);
- **also** — other independent defs of the same name (query mode);
- **same_function** — whether the listed binds are the same object.

Does not execute the bound function. Importing a module runs its top-level code. Nested defs are not import bindings. No git-move reconstruction.

### 2. Nearest ordinary workflow

`grep -n 'def parse'`; then `python -c 'from pkg_util import parse; import inspect; print(parse.__module__, inspect.getsource(parse))'`; then `parse is other_parse` if you already imported both.

### 3. What is lost if that workflow replaces this tool

Grep hits both files and does not say which body `from pkg_util import parse` binds. In this run grep printed two `def parse` lines; the leftover query printed `runs pkg_util.parse`, source `return ('legacy', x)`, `also pkg_parse.parse`, `same_function False`. The moved query printed the `x.strip()` body. After replacement, getting the bound body is one `inspect.getsource` if you already know the import; discovering that another independent def exists is a second grep you must remember to join.

The leftover vs reexport split is the other remainder. This run, owned reexport (`pkg_util` does `from pkg_parse import parse`): kind `reexport`, runs `pkg_parse.parse`, same_function True, no `also`. Ordinary `inspect.getsource` on that import already shows the moved body and `__module__ == pkg_parse`. What grep+inspect will not emit unless composed by hand: “this import reexports; there is no second independent def” versus “this import is a leftover helper; a second def exists.”

`--file` on the stale test listed both binds and `same_function False`. Grep on the test file does not print those bodies.

### Scores

- **Novelty 2.** Go-to-definition and `inspect.getsource` are ordinary. The remaining cut is leftover-def vs reexport plus “also these other defs of the same name,” as one report. Not a new linker.
- **Utility 4.** After a move, two functions sharing a name is a real stale-test failure. The demo fixture is that case: `from pkg_util import parse` still runs `('legacy', x)`. People who already know to import and `inspect` get less; people who stop at grep get the wrong body.
- **Primitive strength 3.** The atom is “import path → object identity → source, plus other defs.” AST scan plus live import is a composition, not one irreducible mechanism. Nested functions and git history are honestly out.
- **Composability 4.** Several query forms, `-C DIR`, TSV, exit 1 on no bindings, exit 2 on usage. List mode vs query mode. `--file` is a second entrance to the same object, not a second product.
- **Empirical credibility 5.** Demo exit 0; 11/11 tests; leftover, moved, reexport, `--file`, dotted name, missing name, specimen-013. Reexport was owned in tests and re-run here.
- **Evolution potential 3.** Attribute-use graphs inside one file, or refusing to import (static-only) as an explicit mode, stay nearby. Bytecode signatures or a tracer daemon would leave the primitive.
- **Reality-Stripped Strength 3.** Peel the name off and this is grep-plus-import-plus-inspect, with a leftover/reexport bit and an also-other-def join. Ordinary tools can approximate each piece; they do not emit the bound report by default. Enough to keep; not a new universe.
- **Cross-specimen transfer 3.** Only one claimed specimen. Leftover vs reexport vs `--file` are three shapes and all ran. That is owned-shape transfer, not a second specimen tree.

**KEEP** — USEFUL_COMPOSITION. Kill would require that `inspect.getsource` already be the whole interaction; the also-other-def / leftover-vs-reexport report is the part grep does not do.

---

## Verdict

| Candidate | Remainder (name ignored) | RSS | Transfer | Decision |
| --- | --- | --- | --- | --- |
| envlayers | Five-cell what-if for one key; empty file assignment ≠ unset; skip-empty vs assign | 3 | 2 | KEEP |
| ordleak | Explicit pair, both orders, named start-state leak (including no-fail leaks) | 4 | 2 | KEEP |
| bindname | Import path → body that would run; leftover def vs reexport; other same-name defs | 3 | 3 | KEEP |

KEEP: envlayers, ordleak, bindname.

KILL: none.

The strongest remainder after branding is removed is ordleak (start-state leak record for a pair). envlayers and bindname are useful compositions whose nearest workflows are obvious; each still loses a bound observable if replaced (`file ''` vs `None` plus skip vs assign; leftover vs reexport plus `also`). None is a polished clone with only syntax left.

Do not average these scores with other judges. Disagreement is expected on envlayers (composition vs two hardcoded loaders) and bindname (report vs `inspect.getsource`). ordleak should survive Reality-Stripped even if another role calls it a tiny test runner: the runner half is ordinary; the leak row is not.

No merge. This file is the Reality-Stripped ballot only.
