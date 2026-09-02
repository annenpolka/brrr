# FIRST_SKEPTIC — first blind selection

Role: Skeptic.
Stance: a tool should not exist until evidence proves otherwise.
Date: 2026-09-02 12:07 JST.
Host: python 3.14.5.
Seal: prior brrr reports, answer-keys, `hdd-origins/`, and `lab-hdd/` were not read.
This judge did not merge anything onto `main`. Product code stays in lineages.

Judged embodiments only:

| candidate | binary | path |
| --- | --- | --- |
| candidate-envlayers | `envlayers` | `lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envlayers/` |
| candidate-ordleak | `ordleak` | `lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/` |
| candidate-bind | `bindname` | `lab-runs/specimen-hdd-20260902-1112/lineages/candidate-bind/` |

Axes scored 0–5. 3 is “a question exists.” 4+ empirical requires an observable that ordinary tools lose *and* a case that is not the owned toy. Scores are this judge’s; do not average with other judges.

Dreamer text is not evidence. README is not evidence. Tests that replay the specimen are weak evidence. Demos I ran, plus replacements I ran, are evidence.

---

## Verdicts

| candidate | binary | verdict | first-selection survivor? | install tomorrow? |
| --- | --- | --- | --- | --- |
| candidate-envlayers | envlayers | **KILL** | no | no |
| candidate-ordleak | ordleak | **PARK** | no | no |
| candidate-bind | bindname | **KILL** | no | no |

Skeptic survivor list: **empty**.

Tomorrow-test PATH list: **empty**.

PARK is not KEEP. `ordleak` names one real join (module-global start state that changed when only order changed, including when both tests PASS). That is not enough to mint a binary, and the embodiment misses the leak shapes that actually happen. Remember the object; do not install it; do not treat it as a grounded primitive yet.

---

## Axes (skeptic, not averaged)

| axis | envlayers | ordleak | bindname |
| --- | ---: | ---: | ---: |
| Novelty | 1 | 2 | 1 |
| Utility | 1 | 2 | 2 |
| Primitive strength | 2 | 3 | 2 |
| Composability | 2 | 2 | 3 |
| Empirical credibility | 2 | 2 | 2 |
| Evolution potential | 2 | 3 | 2 |
| Reality-Stripped Strength | 1 | 2 | 1 |
| Cross-specimen transfer | 1 | 0 | 1 |

Empirical stays at 2 for all three: official demos and unit tests passed on this host, then off-fixture probes showed the claimed delta is either a specimen replay or a 2–8 line ordinary workflow.

---

## Method

Ran, this session, on this host:

1. Official `demo.sh` for each candidate (exit 0). Transcripts: `/tmp/first-skeptic-1112/{envlayers,ordleak,bindname}-demo.out`.
2. Official unit tests (envlayers 9 OK, ordleak 6 OK, bindname 11 OK).
3. Ordinary replacements that a developer would type instead.
4. Off-fixture probes the READMEs do not advertise.

Did not read `answer-key/`, `hdd-origins/`, previous-run judges, or `lab-hdd/`.
Did use owned fixture files and `OBSERVED.md` because the demos load those files. That is the problem world, not an answer key.

---

## candidate-envlayers / `envlayers` — KILL

### Claim

For one environment key, print inherited / file (including empty) / skip-empty loader / assign-all loader / this process, so empty assignment is not unset.

### Execution (required)

```
bash lineages/candidate-envlayers/demo.sh   # exit 0
python3 lineages/candidate-envlayers/tests/test_envlayers.py -v   # 9 OK
```

Demo on specimen-010 (`KEY=` in file, inherited `KEY=/x`, process unset):

```
key          KEY
inherited    '/x'
file         ''
skip_empty   '/x'
assign       ''
process      None
```

Absent-key control (`OTHER=2` only): `file None`, `skip_empty '/x'`, `assign '/x'`. Empty vs absent is distinct in the table. That much is real.

The CLI is the specimen. `files/loader.py` defines `load_skip_empty` / `load_assign` with `if v:`. The CLI defines the same two functions. I supplied `--inherited KEY=/x` and `--file`. The binary then reprints the fixture’s two policies.

### Ordinary replacement (ran)

```
file_has True ''
skip '/x'
assign ''
process False None
```

from a 15-line reader of the same file plus the same two merges. `cat file.env` already shows `KEY=`. `printenv` already distinguishes process empty vs unset:

```
env -u KEY printenv KEY ; echo rc:$?    # rc 1, no line
KEY= printenv KEY ; echo rc:$?          # rc 0, empty line
```

Once a skip-empty loader has already stuffed `/x` into the process, `printenv` cannot see the file’s `KEY=`. True. The recovery is to open the file, not to re-simulate two canned loaders in a third process.

`process` is `os.environ` of *this CLI*. It does not attach. So the row cannot answer “why does my app have an empty KEY.”

### Off-fixture (ran)

| input | result |
| --- | --- |
| `export KEY=quoted` | query `KEY` → `file None`. The assignment is stored under the key `export KEY`. |
| `  KEY4=spaced` | query `KEY4` → `file None`. Stored under `  KEY4`. |
| `# KEY=nope` | stored as key `# KEY`. |
| `KEY2="double"` | file value is `'"double"'` including quotes. |
| last of `KEY=first` / `KEY=` / `KEY=third` | last wins (`'third'`). |
| default inherited, process has `KEY=/from-process` | `inherited` copies the CLI process, which is not the app. |

No `python-dotenv` on this host, so I could not even compare to a real loader. The binary does not invoke one.

### What operation remains?

Print one key from a `KEY=VALUE` file, then apply two hardcoded merge rules copied from `loader.py`.

Nearest workflow: `cat` / `grep '^KEY='` / `printenv` / read the loader.

Lost by replacement: a labeled five-row table. Not a fact.

### Why KILL

Empty vs unset is a real distinction. This binary does not discover which layer emptied a live variable. It restages the specimen and labels the restage. A developer who already knows inherited `KEY=/x` and has the file does not need `envlayers`. A developer who does not know those things cannot get them from this CLI.

Do not install. Do not breed this embodiment. If someone later probes a *real* loader (dotenv, systemd `EnvironmentFile`, docker `--env-file`) and reports what that loader did to `KEY=`, that is a different candidate.

---

## candidate-ordleak / `ordleak` — PARK

### Claim

Run a named pair in both orders. Name the leaked module-level binding and the exposing order.

### Execution (required)

```
bash lineages/candidate-ordleak/demo.sh   # exit 0
python3 lineages/candidate-ordleak/tests/test_ordleak.py -v   # 6 OK
```

Demo on specimen-009:

```
order     test_a test_b
status    test_a  PASS
status    test_b  FAIL  ['a']
order     test_b test_a
status    test_b  PASS
status    test_a  PASS
exposing_order    test_a test_b
leaked    acc  into  test_b  []  ['a']  via  test_a
```

That output is real. The leak row names `acc`.

### Ordinary replacement (ran)

The specimen already ships `files/run_orders.py`. Same two orders, same PASS/FAIL, and it prints `acc_after ['a']`. The assertion is `assert acc == [], acc`, so the FAIL line already names the value.

pytest is not installed on this host (`No module named pytest`). Two-order contrast does not require pytest; the owned runner already does it.

Claimed second specimen: `specimens/specimen-012/files/test_order.py` is **byte-identical** to specimen-009 (`sha256 5867c684ecf7`). That is not transfer.

### What is actually extra

Hidden leak, no failing assert (replayed):

```
# acc=[]; test_a appends; test_c pass
exposing_order    none
leaked    acc  into  test_c  []  ['a']  via  test_a
```

Both tests PASS in both orders; the start-state of `acc` still moved. Two-order pytest would stay green. That join is the only reason this is not KILL.

You still have to name the pair. Finding the pair is the job. This CLI refuses to search.

### Off-fixture (ran)

| leak shape | exposing_order | leaked | notes |
| --- | --- | --- | --- |
| module list `acc` (toy) | named | `acc` | specimen |
| hidden module list, no assert | none | `acc` | the one extra |
| class attribute `Box.items` | named | **none** | classes are not “bindings”; FAIL detail still `['a']` |
| `test_b.seen = True` on a function | named | **none** | functions skipped |
| imported `helper_mod.bucket` | — | — | **exit 1** `No module named 'helper_mod'` |
| `os.environ["LEAK"]` | **none** | **none** | order 2 is poisoned by order 1’s process env; `test_b` FAIL in *both* orders |
| filesystem side file | **none** | **none** | same self-poison |
| pair `test_a,test_c` in a three-test file | none | `acc` both ways | only works if you already named a mutating pair |

So: the leak row is true for a module-level list in the same file, false-silent for class/function/env/fs, and crash for a neighboring module. Isolation of the two orders is not isolation of process env or the filesystem.

### What operation remains?

Import a file twice. Call two named functions in both orders. Diff non-callable, non-class module globals at each test’s start.

Nearest workflow: run the pair both ways; print the global you already suspect.

Lost by replacement: automatic name of that global when you already named the pair, including the hidden-PASS case.

### Why PARK, not KEEP, not KILL

KEEP would mean I believe a human should type `ordleak` tomorrow or that this is a primitive worth breeding as-is. I do not. You must bring the pair. The pair is the mystery. The implementation then looks only at the least common leak (module `acc = []`).

KILL would mean the object is fake. It is not fake. Start-state-across-orders is a real question. Preserve it as an extinct interaction. Do not mint. Mutation that (1) finds pairs without being told, (2) snapshots more than module globals, (3) isolates env/fs, would be a different candidate.

---

## candidate-bind / `bindname` — KILL

### Claim

For a name, show the import path and the body that would run. Distinguish leftover same-name helper from a moved definition.

### Execution (required)

```
bash lineages/candidate-bind/demo.sh   # exit 0
python3 lineages/candidate-bind/tests/test_bindname.py -v   # 11 OK
```

Demo on specimen-013: grep hits both `def parse`; `from pkg_util import parse` is leftover `('legacy', x)`; `from pkg_parse import parse` is moved `strip`; `same_function False`. Isolated leftover vs reexport also matched the README (`kind=def` leftover, `kind=reexport` + `runs=pkg_parse.parse` + `same_function True` for a true alias).

### Ordinary replacement (ran)

```
python3 -c 'import sys,inspect,pkg_util,pkg_parse
sys.path.insert(0, "specimens/specimen-013/files")
print(pkg_util.parse.__module__, pkg_parse.parse.__module__)
print(pkg_util.parse is pkg_parse.parse)
print(inspect.getsource(pkg_util.parse))
print(inspect.getsource(pkg_parse.parse))'
```

Output:

```
pkg_util pkg_parse
False
def parse(x):
    return ('legacy', x)
def parse(x):
    return ('moved', x.strip())
```

Leftover vs moved is `__module__` plus `inspect.getsource` plus `is`. Grep already listed both defs (the demo runs grep first).

`--file test_parse_identity.py parse` reprints the two attribute uses in that test. Reading the test does the same.

### Off-fixture (ran, isolated trees)

| case | result |
| --- | --- |
| leftover helper | `kind=def runs=pkg_util.parse also=pkg_parse.parse same_function=False` |
| `from pkg_parse import parse` reexport | `kind=reexport runs=pkg_parse.parse same_function=True` |
| `parse = pkg_parse.parse` assignment alias | treated as reexport (runtime object identity). Fine. |
| `@wrap` decorator | `runs=deco.inner`, source is the wrapper, original `parse` body omitted |
| nested def assigned to module `parse` | reports nested source as `kind=def` |
| star import | runtime getattr works (`kind=reexport`); `--import` parser rejects stars |
| `-C DIR` list mode | scans the whole tree; unrelated `parse` names in the same dir show up as `also` |

Importing a module runs its top-level code. That is disclosed. It is also why this is not a safe “just look” query.

### What operation remains?

AST-find the name, import the module, `inspect.getsource` / `__module__` / `id`.

Nearest workflow: `rg 'def parse'` and `python3 -c 'import …, inspect'`.

Lost by replacement: one TSV blob that joins those facts and prints `also`. Not a new object of inquiry.

### Why KILL

“Which body does this import bind?” is a real moment. Existing tools already answer it. This CLI is a polite join of grep and inspect. The leftover/reexport table is the specimen’s two files. I would not put `bindname` on PATH. I would not breed this as a primitive. A later candidate that answered the question *without importing* (pure binding graph, no top-level execution) might be interesting. This one is not that.

---

## Tomorrow test

Which binaries should a human actually install and try tomorrow?

**None.**

Empty slots are allowed. Abundance is not a virtue. Passing your own demo is not a reason to exist.

If a later judge KEEP-s one of these, that disagreement should stand. This judge still will not install.

---

## What would change my mind

- **envlayers:** point it at an actual loader (or a running process) and report which layer emptied `KEY` without being told the two policies. `export KEY=`, comments, and indented keys must parse as the loader under test parses them.
- **ordleak:** find an unknown pair in a file of many tests; name a class-attr / imported-module / fixture leak; stop poisoning order 2 with order 1’s env and files. Then I might PARK→KEEP the object, still maybe not the name.
- **bindname:** show a binding that `inspect.getsource` + `__module__` + `rg` does not already show, without executing module top-level. Until then, no.

---

## Evidence index

Host runs, 2026-09-02:

| what | result |
| --- | --- |
| `bash candidate-envlayers/demo.sh` | exit 0 |
| `bash candidate-ordleak/demo.sh` | exit 0 |
| `bash candidate-bind/demo.sh` | exit 0 |
| `python3 tests/test_envlayers.py -v` | 9 tests OK |
| `python3 tests/test_ordleak.py -v` | 6 tests OK |
| `python3 tests/test_bindname.py -v` | 11 tests OK |
| envlayers ordinary 15-line reader | same facts as CLI on `KEY=` |
| `printenv` empty vs unset | rc 1 vs rc 0 |
| envlayers `export KEY=` / indent / comments | wrong keys |
| ordleak vs `run_orders.py` | same PASS/FAIL; CLI adds leak row |
| specimen-009 vs specimen-012 `test_order.py` | identical |
| ordleak class / fnattr / env / fs / import | leak row empty or crash |
| ordleak hidden PASS leak | names `acc` |
| bindname vs `inspect.getsource` | same leftover vs moved |
| bindname decorator | wrapper body, not wrapped |

Raw demo transcripts: `/tmp/first-skeptic-1112/*-demo.out` (tabs preserved). Probe dump: `/tmp/first-skeptic-1112/probes.json`.

Binaries this session:

```
envlayers  150 lines  sha256 701f7cd737c8
ordleak    243 lines  sha256 79552164dc8d
bindname   589 lines  sha256 35160e389926
```

Code volume was not used as a ranking signal.

---

## Non-survivors, restated

First blind selection, Skeptic only:

```
KEEP:    (none)
PARK:    ordleak   # object: start-state diff across a named pair; do not install
KILL:    envlayers, bindname
PATH:    (empty)
```
