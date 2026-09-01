# Candidate: stated

origin.method: hdd
origin.trial: hdd-debug
Reality: USEFUL_COMPOSITION

## Primitive

Given a configuration key, scan config-like files for declaration sites (`KEY:`, `KEY=`) and source files for assignments of the same identifier. When both sides look like scalars, compare the literals. The result is a **disagreement pair** (declaration site vs contradicting site), not a hit list. If only one side exists, or the values agree, print the sites and exit 0. If a value is not statically comparable, say so instead of guessing.

Composition of existing moves:

1. walk a tree and classify files as config vs source
2. regex-match `KEY` with `:` / `=` / `:=`
3. parse a trailing token as a scalar or as unknown
4. pair declaration values against assignment values

Nearest existing: `rg KEY` across config and source, then read both. `stated` removes the read-and-diff step for the comparable-literal case.

## Why it might not exist

`rg`, IDE find-references, and `git grep` already surface every occurrence. Comparing a YAML scalar to a Python assignment is a tiny extra that people do by eye during "it only broke after I changed the timeout" debugging. The composition is useful and small; it is easy to dismiss as "just grep." That is why a dedicated disagreement-pair CLI may not exist even though the primitive is real.

It also refuses work that looks adjacent but is a different product: no deploy trackers, no hotfix IDs, no live runtime metrics, no auto-repair.

## How to run

```bash
python3 stated timeout fixtures/disagree
python3 stated --json timeout fixtures/agree
./demo.sh
python3 -m unittest tests.test_stated
```

Requires Python 3 stdlib only.

Exit codes: 0 agree / one-sided / unknown / none; 1 usage; 2 comparable disagreement.

## Empirical transcript

First working commit `4e39dac`, 2026-09-01, shipped `./stated` (not a mock).

Command: `./demo.sh`

```
======== disagree (config.yaml timeout: 5 vs app.py timeout = 10) ========
status: DISAGREE
disagreement:
  declared     5	config.yaml:1	timeout: 5	value=5
  contradicted 10	app.py:3	timeout = 10	value=10
exit: 2

======== agree (both 5) ========
status: AGREE
value: 5
exit: 0

======== config only ========
status: DECLARED_ONLY
value: 5
exit: 0

======== unknown (interpolation vs getenv) ========
status: UNKNOWN
note: sites found, none statically comparable
declarations:
  config.yaml:1	timeout: ${WAIT}	value=${WAIT} (not comparable: interpolation)
assignments:
  app.py:3	timeout = os.getenv("WAIT")	value=os.getenv("WAIT") (not comparable: call)
exit: 0
```

`python3 -m unittest tests.test_stated` after first commit: 12 tests, OK.

## Dogfood

After first commit, ran the shipped CLI on a new fixture where the same key appears in comments and in a real assignment.

Fixture:

- `config.yaml` — `timeout: 5` and `# timeout: 99`
- `app.py` — module docstring contains `timeout = 99`; real code `timeout = 5`; `# timeout = 99`
- `legacy.c` — `/* timeout = 99; */` then `int timeout = 5;`

**Before** (commit `4e39dac`):

```
$ python3 stated timeout fixtures/comments
status: DISAGREE
disagreement 1:
  declared     5	config.yaml:1	timeout: 5
  contradicted 99	app.py:4	timeout = 99
disagreement 2:
  declared     5	config.yaml:1	timeout: 5
  contradicted 99	legacy.c:3	timeout = 99;
exit: 2
```

False disagreement: docstring and C block-comment literals were treated as assignments. Whole-line `# timeout: 99` in YAML did not match (start-anchored regex), so hash comments were already silent rather than labeled. Also, the real `int timeout = 5;` in `legacy.c` was not seen, because the first scanner required the key at column-0.

**Change:** classify `#` / `//` / `/* */` / Python triple-quoted docstrings as comments; still report those KEY hits, but ignore them for comparison. Allow a type/qualifier prefix so `int timeout = 5` counts as an assignment.

**After:**

```
$ python3 stated timeout fixtures/comments
status: AGREE
value: 5
declarations:
  config.yaml:1	timeout: 5	value=5
assignments:
  app.py:7	timeout = 5	value=5
  legacy.c:6	int timeout = 5;	value=5
comments (ignored for comparison):
  config.yaml:2	# timeout: 99	value=99
  app.py:4	timeout = 99	value=99
  app.py:9	# timeout = 99	value=99
  legacy.c:3	timeout = 99;	value=99
exit: 0
```

`python3 -m unittest tests.test_stated` after the change: 14 tests, OK.

## Surprises

- `timeout:` in YAML and `timeout =` in Python compare as scalars without a parser per language. Enough for the demo fixtures.
- `${WAIT}` vs `os.getenv("WAIT")` correctly refused comparison instead of pretending they match.
- Dogfood: a C typed declaration (`int timeout = 5`) is a real assignment the first regex dropped. Fixing comments without that prefix would have reported DECLARED_ONLY plus a missed site.
- Hash-comments were *not* the failing case on v1; docstrings and `/* */` interiors were, because those lines look like bare `KEY = value`.

## Failures

- Nested keys are only visible as a line token (`timeout:`), not as `server.timeout`.
- No runtime evaluation. Interpolated / computed values stay UNKNOWN.
- Comment tracker is line-level, not a lexer: `/* x */ int timeout = 5;` on one line can be misclassified; strings that are not docstrings but span lines with `"""` can be treated as comments.
- Format coverage is partial (listed extensions only).
- Case-sensitive: `timeout` does not match `TIMEOUT`.

## Mutations

Possible next cuts, not implemented unless dogfood forces them:

- nested keys (`server.timeout`) as a path, not a line token
- case-insensitive env keys (`timeout` vs `TIMEOUT`)
- richer language parsers (so `timeout: int = 5` in Python is a typed assignment, not `value=int`)
- more languages / `KEY: value` in markdown docs
