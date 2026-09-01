# CANDIDATE: mutation-05 — stated-jsonobj

```yaml
origin:
  method: hdd
  trial: hdd-debug
  mutation: ordinary
  parent: candidate-02__stated
```

## Primitive

Given a configuration key, scan config-like files for declaration sites (`KEY:`, `KEY=`) and source files for assignments of the same identifier. When both sides look like scalars, compare the literals. The result is a **disagreement pair** (declaration site vs contradicting site), not a hit list. If only one side exists, or the values agree, print the sites and exit 0. If a value is not statically comparable, say so instead of guessing.

Ordinary mutation of candidate-02 (the original stated, not the clean-room). Compact one-line JSON objects (`{"KEY": 5}`) count as declarations. Pretty-printed JSON already matched; the hole was the start-anchored line token.

## Why it might not exist

`rg`, IDE find-references, and `git grep` already surface every occurrence. Comparing a YAML scalar to a Python assignment is a tiny extra that people do by eye during "it only broke after I changed the timeout" debugging. The composition is useful and small; it is easy to dismiss as "just grep." That is why a dedicated disagreement-pair CLI may not exist even though the primitive is real.

It also refuses work that looks adjacent but is a different product: no deploy trackers, no hotfix IDs, no live runtime metrics, no auto-repair.

## How to run

```bash
python3 stated timeout fixtures/disagree
python3 stated --json timeout fixtures/agree
python3 stated timeout fixtures/compact_json
./demo.sh
python3 -m unittest tests.test_stated
```

Requires Python 3 stdlib only.

Exit codes: 0 agree / one-sided / unknown / none; 1 usage; 2 comparable disagreement.

## Pre-implementation Reality assessment

Copied from `lab-hdd/hdd-origins/hdd-debug.md` before the parent implementation existed (still in force):

- Classification: USEFUL_COMPOSITION
- Nearest: `rg` the key across config and source, then read both hits
- Delta: the result is the disagreement pair, not a list of search hits
- Mapping: scan config-like files and source for a key/identifier; compare literal values; report mismatches; honest "unknown" when values cannot be compared statically
- Removed magic: deploy/hotfix trackers, protocol version oracles, live runtime metrics, auto-repair
- Research boundary: will not recover runtime-only values; will not understand every config DSL; partial file-format coverage is acceptable

This mutation does not add nested paths, case folding, or a JSON parser. `{` / `[` / `,` are ignorable leaders; the first value token is cut so `5, "host": ...}` compares as `5`.

## Empirical transcript

First mutation commit `369b481`, 2026-09-02, worktree `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-05-stated-jsonobj`. Copied `./stated` from `candidate-02__stated` (not a mock, not the clean-room file).

Command: `python3 -m unittest tests.test_stated`

```
Ran 14 tests in 0.355s
OK
```

Command: `./demo.sh` (first commit; compact JSON fixture not yet present)

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
exit: 0
```

After the dogfood commit, `python3 -m unittest tests.test_stated -v`: 16 tests, OK. `./demo.sh` exit 0 (stated itself exits 2 on disagree fixtures).

## Dogfood

After first commit, ran the shipped CLI on a one-line JSON object (the shape `package.json` / small service configs actually take), next to a hardcoded assignment.

Fixture:

- `config.json` — `{"timeout": 5, "host": "localhost"}`
- `app.py` — `timeout = 10`

**Before** (commit `369b481`):

```
$ python3 stated timeout fixtures/compact_json
status: ASSIGNED_ONLY
value: 10
assignments:
  app.py:1	timeout = 10	value=10
exit: 0
```

False one-sided result: the declaration exists, but a start-anchored line token does not see `"timeout"` after `{`. Pretty-printed JSON (`  "timeout": 5`) already matched; compact form did not.

**Change:** treat `{` / `[` / `,` as ignorable leaders so an object member is still a declaration. Cut the first value token so `5, "host": ...}` compares as `5`, not as an expression. Implemented on the original scanner; not a paste of the clean-room file.

**After:**

```
$ python3 stated timeout fixtures/compact_json
status: DISAGREE
disagreement:
  declared     5	config.json:1	{"timeout": 5, "host": "localhost"}	value=5
  contradicted 10	app.py:1	timeout = 10	value=10
exit: 2
```

`python3 -m unittest tests.test_stated` after the change: 16 tests, OK.

## Surprises

- `timeout:` in YAML and `timeout =` in Python compare as scalars without a parser per language.
- `${WAIT}` vs `os.getenv("WAIT")` correctly refused comparison instead of pretending they match.
- Hash comments, `/* */` interiors, and Python triple-quoted spans are labeled and ignored for pairing; `int timeout = 5` still counts because of identifier prefixes.
- Compact JSON was the hole a line-token scanner hides: pretty JSON agreed with the tests, one-line JSON silently dropped the declaration.
- Cutting on any comma would turn a source tuple `timeout = 5, 6` into scalar `5`. Sibling cut only fires on a closer or `, "next"`.

## Failures

- Nested keys are only visible as a line token (`timeout:`), not as `server.timeout`.
- No runtime evaluation. Interpolated / computed values stay UNKNOWN.
- Comment tracker is line-level, not a lexer: `/* x */ int timeout = 5;` on one line can be misclassified; strings that are not docstrings but span lines with `"""` can be treated as comments.
- Format coverage is partial (listed extensions only).
- Case-sensitive: `timeout` does not match `TIMEOUT`.
- First-token cut is not a JSON parser: a value that is itself an object/array on the same line stays non-scalar / unparsed.
- Later members on the same line still need `{` / `[` / `,` as the only characters before the key. `{"host": "x", "timeout": 5}` is not seen; timeout has to sit after ignorable leaders.

## Suggested mutations

- nested keys (`server.timeout`) as a path, not a line token
- case-insensitive env keys (`timeout` vs `TIMEOUT`)
- richer language parsers (so `timeout: int = 5` in Python is a typed assignment, not `value=int`)
- more languages / `KEY: value` in markdown docs
- skip a previous `"other": value` on the same compact line so a non-first member still declares
