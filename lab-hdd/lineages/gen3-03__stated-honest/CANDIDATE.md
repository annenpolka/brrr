# CANDIDATE: gen3-03 — stated-honest

```yaml
origin:
  method: hdd
  trial: hdd-debug
  generation: 3
  mutation: stated-honest
  parent: mutation-05__stated-jsonobj
  destroyer: DESTROYER_CONFIG
```

## Primitive

Given a configuration key, scan config-like files for declaration sites (`KEY:`, `KEY=`) and source files for assignments of the same identifier. When both sides look like scalars, compare the literals. The result is a **disagreement pair** (declaration site vs contradicting site), not a hit list. If only one side exists, or the values agree, print the sites and exit 0. If a value is not statically comparable, say so instead of guessing.

Generation-3 honesty cut of mutation-05 (compact-JSON stated, not the clean-room). Compact `{"timeout": 5}` stays a declaration. Dotenv is **not** a declaration: `.env TIMEOUT=30` is env-layer, the same flipped assumption effect already made.

## Why it might not exist

`rg`, IDE find-references, and `git grep` already surface every occurrence. Comparing a YAML scalar to a Python assignment is a tiny extra that people do by eye. Treating `.env` as just another config file is the obvious grep-shaped move; the honest pair keeps dotenv out so the disagreement is config vs source, not config vs env.

It also refuses work that looks adjacent but is a different product: no deploy trackers, no hotfix IDs, no live runtime metrics, no auto-repair.

## How to run

```bash
python3 stated timeout fixtures/disagree
python3 stated --json timeout fixtures/agree
python3 stated timeout fixtures/compact_json
python3 stated timeout fixtures/dotenv_not_decl
python3 stated TIMEOUT fixtures/dotenv_not_decl
python3 stated timeout fixtures/strlit
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

DESTROYER_CONFIG (05:00) named `.env`-as-declaration as a stated hole (effect already excludes dotenv). Compact JSON is already closed in mutation-05; this cut does not re-open it.

## Empirical transcript

First mutation commit on worktree `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/gen3-03-stated-honest`. Copied `./stated` from `mutation-05__stated-jsonobj` (not a mock, not the clean-room file). Dotenv files are no longer config.

Command: `python3 -m unittest tests.test_stated`

```
Ran 19 tests in 0.483s
OK
```

Compact JSON still DISAGREEs. `stated timeout fixtures/dotenv_not_decl` DISAGREEs yaml 5 vs py 10 and does not mention `.env`. `stated TIMEOUT` on the same tree is NONE, not DECLARED_ONLY 30.

## Dogfood

After first commit, ran the shipped CLI on a source line that *mentions* the key inside a string rather than assigning it.

Fixture:

- `config.yaml` — `timeout: 5`
- `app.py` — `msg = "timeout = 99 is wrong"`

**Before** (commit `ea05d9b`):

```
$ python3 stated timeout fixtures/strlit
status: UNKNOWN
note: both sides exist; at least one value is not statically comparable
declarations:
  config.yaml:1	timeout: 5	value=5
assignments:
  app.py:1	msg = "timeout = 99 is wrong"	value=99 is wrong" (not comparable: unparsed)
exit: 0
```

False assignment site: `.*?timeout` matches inside the quotes and flips DECLARED_ONLY → UNKNOWN. DESTROYER_CONFIG 2.5. reimpl-01 never saw the string (start-anchored).

**Change:** mask quoted spans before the assignment scan so KEY inside `'...'` / `"..."` is not an assignment. Rest is still sliced from the original line, so `timeout = "10"` stays a quoted scalar.

**After:**

```
$ python3 stated timeout fixtures/strlit
status: DECLARED_ONLY
value: 5
declarations:
  config.yaml:1	timeout: 5	value=5
exit: 0
```

A real `timeout = 10` on the next line still DISAGREEs 5 vs 10; the string mention is skipped.

`python3 -m unittest tests.test_stated` after the change: 22 tests, OK. `./demo.sh` exit 0.

## Surprises

- Compact JSON from mutation-05 still DISAGREEs `{"timeout": 5}` vs `timeout = 10`.
- `.env timeout=99` next to `timeout: 5` used to produce a second disagreement pair. After the cut, only yaml vs py remains.
- `stated TIMEOUT` on a tree whose only TIMEOUT site is `.env TIMEOUT=30` is NONE, not DECLARED_ONLY.
- Dogfood: `msg = "timeout = 99 is wrong"` was an unparsed assignment. Masking quotes restored DECLARED_ONLY.

## Failures

- Nested keys are only visible as a line token (`timeout:`), not as `server.timeout`.
- No runtime evaluation. Interpolated / computed values stay UNKNOWN.
- Comment tracker is line-level, not a lexer.
- Case-sensitive: `timeout` does not match `TIMEOUT`.
- Quote mask is `'...'` / `"..."` only; a KEY split across concatenated strings can still hide.

## Suggested mutations

- nested keys (`server.timeout`) as a path, not a line token
- case-insensitive env keys (`timeout` vs `TIMEOUT`)
- announce MAX_FILE_BYTES skips instead of silently dropping the assignment side
