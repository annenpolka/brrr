# CANDIDATE: gen3-04 — effect-compact

```yaml
origin:
  method: hdd
  kind: hybrid
  generation: 3
  mutation: effect-compact
  parent: hybrid-01__effect
  destroyer: DESTROYER_CONFIG
```

## Primitive

Name a configuration key. Emit **one record** with four fields:

- **DECLARED** — config-file sites (`KEY:` / `KEY=`) excluding dotenv
- **ASSIGNED** — source-file assignment sites
- **ENV_SOURCE** — process/dotenv provenance of KEY, of its case variant, and of names those sites defer to (`${WAIT}`, `os.getenv("WAIT")`, `os.environ.get("WAIT")`, `process.env.WAIT`)
- **EFFECTIVE** — a comparable scalar if the layers statically agree; otherwise `unknown` with a reason

Exit 2 if a declared literal disagrees with an assigned literal. Env provenance is still printed.

This is not `stated KEY && envfrom KEY`. Concatenation would put `.env TIMEOUT=30` in stated's declaration list (or miss it), look up only the string `timeout` in envfrom, and never join `${WAIT}` / `os.getenv("WAIT")` to WAIT's empty override. The object is the join: dotenv is env-layer not declaration; getenv/interpolation names ride in the same record; EFFECTIVE refuses to pick a winner.

Generation-3 FIX of DESTROYER_CONFIG 3.2: hybrid-01's `config_key_re` is still the pre-mutation stated pattern (start-of-line indent/export only). Compact `{"timeout": 5}` is invisible, so EFFECTIVE becomes a false assigned-only 10. mutation-05 already closed that hole on stated; this cut copies those leaders onto the joint record.

## Why it might not exist

People already `rg timeout` then `cat .env`. stated answers declaration vs assignment. envfrom answers where a named env var would come from. The remaining question is *what would this key actually be, given those three layers*, and that question is unanswerable from either CLI's stdout. A wrapper that prints both reports is a mashup. A four-field record with a deferred-name env join is the hybrid.

Discarded as concatenation: shelling out to stated then envfrom; treating `.env` as another config declaration; looking up only KEY in the environment.

## How to run

```bash
python3 effect timeout fixtures/disagree
python3 effect --json timeout fixtures/deferred
python3 effect timeout fixtures/compact_json
./demo.sh
python3 -m unittest tests.test_effect
```

Python 3 stdlib only.

Exit codes: 0 no declared-vs-assigned literal disagreement; 1 usage; 2 comparable declared vs assigned disagreement.

## Pre-implementation Reality assessment

Parents were classified USEFUL_COMPOSITION (stated / envfrom). The hybrid is the join, not a new primitive. DESTROYER_CONFIG: keep the four-field record; FIX compact JSON miss that lies about EFFECTIVE.

## Empirical transcript

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/gen3-04-effect-compact`

Copied `./effect` from `hybrid-01__effect` (not a mock). Parent tests unchanged. Compact JSON object members are still missed.

Command: `python3 -m unittest tests.test_effect`

```
Ran 16 tests in 0.443s
OK
```

Compact `{"timeout": 5}` vs `timeout = 10` still reports DECLARED (none), EFFECTIVE 10, disagree false. False assigned-only.

## Dogfood

After first commit `b9c0385`, ran the shipped CLI on a one-line JSON object next to a hardcoded assignment — the hole mutation-05 closed for stated and DESTROYER_CONFIG 3.2 named for effect.

Fixture:

- `config.json` — `{"timeout": 5, "host": "localhost"}`
- `app.py` — `timeout = 10`

**Before** (commit `b9c0385`):

```
$ python3 effect timeout fixtures/compact_json
DECLARED:
  (none)
ASSIGNED:
  app.py:1	timeout = 10	value=10
EFFECTIVE:
  10
# rc=0, disagree=false
```

The declaration exists. EFFECTIVE is a **false assigned-only 10**. Hybrid dropped the compact-JSON cut its stated parent just grew.

**Change:** copy mutation-05 ignorable `{` / `[` / `,` leaders and the first-member token cut, but only on compact object/array declaration lines so `${WAIT}` and `os.getenv("TIMEOUT", "5")` stay whole.

**After:**

```
$ python3 effect timeout fixtures/compact_json
DECLARED:
  config.json:1	{"timeout": 5, "host": "localhost"}	value=5
ASSIGNED:
  app.py:1	timeout = 10	value=10
EFFECTIVE:
  unknown	declared 5 vs assigned 10
# rc=2
```

`--json` has `"declared": [{..., "raw_value": "5"}]`, `"effective": {"status":"unknown",...}`, `"disagree": true`.

`python3 -m unittest tests.test_effect` after the change: 18 tests, OK. `./demo.sh` exit 0.

## Surprises

- `.env TIMEOUT=30` stays in ENV_SOURCE, never DECLARED.
- Deferred WAIT still joins `${WAIT}` / `os.getenv("WAIT")` to file WAIT=10.
- Dogfood: compact `{"timeout": 5}` vs `timeout = 10` was EFFECTIVE 10 with declared none. After the leaders, exit 2 and EFFECTIVE unknown.

## Failures

- Nested keys are line tokens (`timeout:`), not `server.timeout`.
- No runtime evaluation of getenv defaults (`os.getenv("TIMEOUT", "5")` is a call).
- Silent 2MiB source skip still lies about EFFECTIVE (DESTROYER_CONFIG 3.4; not this cut).
- First-token cut is not a JSON parser: a value that is itself an object/array on the same line stays non-scalar.

## Suggested mutations

- never emit EFFECTIVE value after a silent file skip
- dotenv decode policy from envfrom FIX pack
- `os.getenv("X", "5")` static default

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

Keep if the four-field record is the product. Kill if a judge can replace it with `stated KEY; envfrom KEY` and lose nothing. DESTROYER_CONFIG: the deferred fixture still fails that kill test. Do not kill. FIX the compact JSON miss.
