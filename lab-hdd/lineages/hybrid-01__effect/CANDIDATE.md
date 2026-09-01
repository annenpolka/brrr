# Candidate: effect

```yaml
origin:
  method: hdd
  kind: hybrid
  parents: [stated, envfrom]
```

## Primitive

Name a configuration key. Emit **one record** with four fields:

- **DECLARED** — config-file sites (`KEY:` / `KEY=`) excluding dotenv
- **ASSIGNED** — source-file assignment sites
- **ENV_SOURCE** — process/dotenv provenance of KEY, of its case variant, and of names those sites defer to (`${WAIT}`, `os.getenv("WAIT")`, `os.environ.get("WAIT")`, `process.env.WAIT`)
- **EFFECTIVE** — a comparable scalar if the layers statically agree; otherwise `unknown` with a reason

Exit 2 if a declared literal disagrees with an assigned literal. Env provenance is still printed.

This is not `stated KEY && envfrom KEY`. Concatenation would put `.env TIMEOUT=30` in stated's declaration list (or miss it), look up only the string `timeout` in envfrom, and never join `${WAIT}` / `os.getenv("WAIT")` to WAIT's empty override. The object is the join: dotenv is env-layer not declaration; getenv/interpolation names ride in the same record; EFFECTIVE refuses to pick a winner.

## Why it might not exist

People already `rg timeout` then `cat .env`. stated answers declaration vs assignment. envfrom answers where a named env var would come from. The remaining question is *what would this key actually be, given those three layers*, and that question is unanswerable from either CLI's stdout. A wrapper that prints both reports is a mashup. A four-field record with a deferred-name env join is the hybrid.

Discarded as concatenation: shelling out to stated then envfrom; treating `.env` as another config declaration; looking up only KEY in the environment.

## How to run

```bash
python3 effect timeout fixtures/disagree
python3 effect --json timeout fixtures/deferred
./demo.sh
python3 -m unittest tests.test_effect
```

Python 3 stdlib only.

Exit codes: 0 no declared-vs-assigned literal disagreement; 1 usage; 2 comparable declared vs assigned disagreement.

## Empirical transcript

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-01-effect`

First working commit `2d33a98`. `python3 -m unittest tests.test_effect -v`: 14 tests, OK. After dogfood: 16 tests, OK.

`./demo.sh` exit 0. Observed (abridged):

```
======== disagree (config 5 vs source 10; .env TIMEOUT=30 still in ENV_SOURCE) ========
KEY: timeout
DECLARED:
  config.yaml:1	timeout: 5	value=5
ASSIGNED:
  app.py:3	timeout = 10	value=10
ENV_SOURCE:
  timeout	unset	why=key
  TIMEOUT	file:.env:2	value=30	INHERITED: (unset)	why=case-variant
EFFECTIVE:
  unknown	declared 5 vs assigned 10
exit: 2
```

`.env` is not under DECLARED. Exit 2 still prints TIMEOUT's file provenance.

```
======== empty override (declared 5, getenv TIMEOUT, file TIMEOUT=) ========
DECLARED:
  config.yaml:1	timeout: 5	value=5
ASSIGNED:
  app.py:3	timeout = os.getenv("TIMEOUT", "5")	value=os.getenv("TIMEOUT", "5") (not comparable: call)
ENV_SOURCE:
  timeout	unset	why=key
  TIMEOUT	file:.env:2	value=(empty)	EMPTY_OVERRIDE: yes	INHERITED: /already/set	why=deferred
EFFECTIVE:
  unknown	literal 5 vs env (empty)
exit: 0
```

```
======== deferred WAIT (config ${WAIT} and os.getenv WAIT; file WAIT=10) ========
DECLARED:
  config.yaml:1	timeout: ${WAIT}	value=${WAIT} (not comparable: interpolation)
ASSIGNED:
  app.py:3	timeout = os.getenv("WAIT")	value=os.getenv("WAIT") (not comparable: call)
ENV_SOURCE:
  timeout	unset	why=key
  WAIT	file:.env:1	value=10	INHERITED: from-shell	why=deferred
EFFECTIVE:
  10
exit: 0
```

`--json` on disagree is one object with `declared`, `assigned`, `env_source`, `effective`, `disagree: true`. Not two payloads.

## Dogfood

After first commit `2d33a98`, ran the shipped CLI on a fixture whose assignment is not `os.getenv`:

- `config.yaml` — `timeout: 5`
- `app.py` — `timeout = os.environ.get("WAIT")` and `timeout = os.environ["WAIT"]`
- `client.js` — `const timeout = process.env.WAIT`
- `.env` — `export WAIT="10" # seconds`
- process `WAIT=from-shell`

**Before** (commit `2d33a98`):

```
$ env WAIT=from-shell python3 effect timeout fixtures/environ-get
KEY: timeout
DECLARED:
  config.yaml:1	timeout: 5	value=5
ASSIGNED:
  client.js:1	const timeout = process.env.WAIT;	value=process.env.WAIT (not comparable: identifier)
  app.py:3	timeout = os.environ.get("WAIT")	value=os.environ.get("WAIT") (not comparable: call)
ENV_SOURCE:
  timeout	unset	why=key
EFFECTIVE:
  unknown	assignment not statically comparable
```

WAIT=10 in `.env` was invisible. Concatenation `envfrom timeout` would also miss it. The joint record did not join.

**Change:** treat `os.environ.get`, `os.environ[]`, `process.env.NAME`, `process.env["NAME"]`, and `env::var` as deferrals. Classify `os.environ["WAIT"]` as a subscript, not unparsed leftover.

**After:**

```
$ env WAIT=from-shell python3 effect timeout fixtures/environ-get
KEY: timeout
DECLARED:
  config.yaml:1	timeout: 5	value=5
ASSIGNED:
  client.js:1	const timeout = process.env.WAIT;	value=process.env.WAIT (not comparable: identifier)
  app.py:3	timeout = os.environ.get("WAIT")	value=os.environ.get("WAIT") (not comparable: call)
  app.py:7	    timeout = os.environ["WAIT"]	value=os.environ["WAIT"] (not comparable: subscript)
ENV_SOURCE:
  timeout	unset	why=key
  WAIT	file:.env:1	value=10	INHERITED: from-shell	why=deferred
EFFECTIVE:
  unknown	literal 5 vs env 10
```

Quoted `export WAIT="10" # seconds` unquoted to 10. EFFECTIVE is honest unknown (declared 5 vs env-resolved assignment 10) instead of a silent miss.

`python3 -m unittest tests.test_effect` after the change: 16 tests, OK.

## Surprises

- `export WAIT=10` in dotenv is a deferred env source, not a YAML declaration. stated would have classified `.env` as config and still missed WAIT when KEY is `timeout`.
- Case-variant TIMEOUT is reported when the file has it, but it does not become EFFECTIVE unless a site defers to it. disagree's TIMEOUT=30 stays a third claim, not a tie-break.
- Empty file override of a deferred name is comparable as empty; EFFECTIVE stays unknown when a declared literal is 5.
- Dogfood: `os.environ.get("WAIT")` is a call and `process.env.WAIT` is an identifier; v1 extracted neither, so `.env WAIT=10` vanished. Following those forms made EFFECTIVE `literal 5 vs env 10`.

## Failures

- v1 followed `${NAME}` and `os.getenv("NAME")` only; WAIT from `os.environ.get` / `process.env` was missed (see dogfood).
- Nested keys are line tokens (`timeout:`), not `server.timeout`.
- No runtime evaluation of getenv defaults (`os.getenv("TIMEOUT", "5")` is a call).
- Comment tracker is line-level, not a lexer.
- `std::env::var_os`, `os.environ.get(name)` with a non-literal, and `process.env[key]` computed keys stay unfollowed.

## Suggested mutations

- Source chain when `.env` and `.env.local` both set the deferred name.
- Nested config paths.
- Follow computed env keys (`os.environ.get(name)`).

## Flipped assumption: bought and lost

Parent **stated** assumed the interesting pair is config-file vs source-file literals, and `.env` is a config file. Parent **envfrom** assumed you already know the env var's name.

**Bought**

- Dotenv is ENV_SOURCE, never DECLARED.
- Names that sites defer to (`WAIT` from `${WAIT}` / `os.getenv("WAIT")`) are in the same record as the key.
- EFFECTIVE is unknown when layers are not statically comparable. Exit 2 is only declared-literal vs assigned-literal.

**Lost**

- You cannot get stated's disagreement pair without also seeing env provenance.
- `envfrom timeout` would miss WAIT and (often) TIMEOUT.

## Kill / keep

Keep if the four-field record is the product. Kill if a judge can replace it with `stated KEY; envfrom KEY` and lose nothing.
