# CANDIDATE: mutation-01 — envfrom-json

```yaml
origin:
  method: hdd
  trial: hdd-env
  mutation: ordinary
  parent: candidate-05__envfrom
```

## Primitive

Name a variable. See whether its effective value is inherited from the process environment, assigned at a dotenv `file:path:line`, or unset. Empty file assignments (`KEY=`) are reported as empty overrides, including the inherited process value they would wipe.

Ordinary mutation of candidate-05: `--json` emits an array of `{key, value, source, empty_override, inherited}` without changing default text blocks. `empty_override` is a boolean. `inherited` is the process string or JSON `null`.

## Why it might not exist

`env` and `printenv` show the current map, not which file emptied a key. `jq` can wrap `env` dumps but has no file:line. Parent `envfrom` is grepable blocks; a script that wants empty-override vs inherited as data still has to parse `VALUE=` / `INHERITED: (unset)`. `--json` is the same provenance record as a document.

## How to run

```bash
./demo.sh
python3 -m unittest tests.test_envfrom
python3 ./envfrom --dir fixtures/empty-override LIBRARY_PATH
python3 ./envfrom --json --dir fixtures/empty-override LIBRARY_PATH APP_ENV
python3 ./envfrom --json --dir fixtures/quoted-export PREFIX GREETING NAME COLOR EMPTY_QUOTED HASH_IN_QUOTES
```

## Pre-implementation Reality assessment

Copied from the harvest, before the parent implementation existed (still in force):

- Read process env and dotenv-like files.
- For each requested key, report value and source.
- Optionally wrap a command (print provenance then exec).
- CLI `envfrom [KEY...]` and `envfrom --run CMD`.
- Existing tools are not enough: `env` prints values, not which file emptied them.

Removed magic: auto-edit repair, checksums, live metrics.

This mutation adds a JSON encoding of that record. It does not add interpolation, `KEY+=`, or a source chain.

## Empirical transcript

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-01-envfrom-json`

```text
$ python3 -m unittest tests.test_envfrom -v
test_env_local_wins ... ok
test_fail_empty_blocks_exec ... ok
test_file_empty_when_process_unset ... ok
test_run_includes_extra_key_args ... ok
test_run_load_applies_empty_override ... ok
test_run_without_load_keeps_inherited ... ok
test_usage_errors ... ok
test_fail_empty_exits_2 ... ok
test_fail_empty_ok_when_not_empty_override ... ok
test_file_empty_override_vs_inherited ... ok
test_inherited_env_when_not_in_file ... ok
test_json_does_not_change_default_text ... ok
test_json_empty_override_array ... ok
test_json_fail_empty_still_exits_2 ... ok
test_double_quote_escapes ... ok
test_export_prefix_quotes_and_inline_comments ... ok
test_json_double_quote_escapes_round_trip ... ok
test_json_quoted_export_round_trip ... ok
test_load_quoted_and_export_into_child ... ok
Ran 19 tests in 0.676s
OK
```

`./demo.sh` exit 0. Process `LIBRARY_PATH=/usr/local/lib:/usr/lib`, `APP_ENV=from-shell`. Text mode unchanged from parent. JSON section (pretty-printed here; the CLI emits one line):

```json
[
  {
    "key": "LIBRARY_PATH",
    "value": "",
    "source": "file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-01-envfrom-json/fixtures/empty-override/.env:2",
    "empty_override": true,
    "inherited": "/usr/local/lib:/usr/lib"
  },
  {
    "key": "APP_ENV",
    "value": "dev",
    "source": "file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-01-envfrom-json/fixtures/empty-override/.env:3",
    "empty_override": false,
    "inherited": "from-shell"
  },
  {
    "key": "NOT_A_REAL_VAR",
    "value": "",
    "source": "unset",
    "empty_override": false,
    "inherited": null
  }
]
```

`--fail-empty LIBRARY_PATH` still exit 2. `--run` without `--load` child keeps inherited LIBRARY_PATH; `--run --load` child `LIBRARY_PATH=''` and `APP_ENV=dev`.

## Dogfood

Fed `fixtures/quoted-export/.env` to `--json`. That file uses `export PREFIX=app`, `"hello world"`, `'Ada Lovelace'`, `COLOR=red # inline comment`, `EMPTY_QUOTED=""`, and `HASH_IN_QUOTES="# not a comment"`.

Before (first mutation commit, real run). Values were already unquoted; `inherited` leaked the text-mode token:

```text
[{"key": "PREFIX", "value": "app", "source": "file:fixtures/quoted-export/.env:2", "empty_override": false, "inherited": "(unset)"}, {"key": "GREETING", "value": "hello world", "source": "file:fixtures/quoted-export/.env:3", "empty_override": false, "inherited": "(unset)"}, {"key": "NAME", "value": "Ada Lovelace", "source": "file:fixtures/quoted-export/.env:4", "empty_override": false, "inherited": "(unset)"}, {"key": "COLOR", "value": "red", "source": "file:fixtures/quoted-export/.env:5", "empty_override": false, "inherited": "(unset)"}, {"key": "EMPTY_QUOTED", "value": "", "source": "file:fixtures/quoted-export/.env:6", "empty_override": true, "inherited": "(unset)"}, {"key": "HASH_IN_QUOTES", "value": "# not a comment", "source": "file:fixtures/quoted-export/.env:7", "empty_override": false, "inherited": "(unset)"}, {"key": "PATH_FRAGMENT", "value": "/usr/bin:/opt/app/bin", "source": "file:fixtures/quoted-export/.env:8", "empty_override": false, "inherited": "(unset)"}]
```

`json.loads` succeeded. PREFIX/GREETING/NAME/COLOR/EMPTY_QUOTED/HASH_IN_QUOTES values were correct (`app`, `hello world`, `Ada Lovelace`, `red`, empty+empty_override, `# not a comment`). Every `inherited` was the string `"(unset)"`.

After (real `./demo.sh` `--json quoted-export` section; pretty-printed here):

```json
[
  {"key": "PREFIX", "value": "app", "source": "file:.../quoted-export/.env:2", "empty_override": false, "inherited": null},
  {"key": "GREETING", "value": "hello world", "source": "file:.../quoted-export/.env:3", "empty_override": false, "inherited": null},
  {"key": "NAME", "value": "Ada Lovelace", "source": "file:.../quoted-export/.env:4", "empty_override": false, "inherited": null},
  {"key": "COLOR", "value": "red", "source": "file:.../quoted-export/.env:5", "empty_override": false, "inherited": null},
  {"key": "EMPTY_QUOTED", "value": "", "source": "file:.../quoted-export/.env:6", "empty_override": true, "inherited": null},
  {"key": "HASH_IN_QUOTES", "value": "# not a comment", "source": "file:.../quoted-export/.env:7", "empty_override": false, "inherited": null}
]
```

A quoted inner-quote line `MSG="say \"hi\"\tnow"` round-trips as JSON value `say "hi"\tnow`. Unittest count after dogfood: 19 tests, OK. Text mode still prints `INHERITED: (unset)`.

## Surprises

- The interesting JSON bug was not quotes on GREETING. Parent already unquotes. The leak was copying the text token `(unset)` into a field that should be `null`.
- `EMPTY_QUOTED=""` is `value: ""` plus `empty_override: true` in JSON, same primitive as `KEY=`.
- `HASH_IN_QUOTES` value `# not a comment` is legal JSON; it only looks comment-like in dotenv.
- Reporting `PATH` remains honest and noisy in text mode. JSON of PATH is the whole inherited string with `source: "env"` and `inherited` equal to `value`.
- `--run` without `--load` still prints would-apply provenance (text or JSON) then the child keeps inherited values.

## Failures

- First JSON encoder: missing inherited was `"(unset)"` (see dogfood before).
- Still: no `${OTHER}` interpolation, no `KEY+=`.
- Still: `--json --run` prints the JSON document, then the child writes to the same stdout. That is the parent composition, not a parser.
- Still: no source chain when `.env` and `.env.local` both set the same key (last-wins only).

## Suggested mutations

- Report a source chain when `.env` and `.env.local` both set the same key.
- Parse `KEY+=` / interpolation.
- Compare against a recorded child `env` dump.
- Relative SOURCE paths when `--dir` is under cwd.
- `--json --run` with child stdout on fd 3, or provenance on stderr, so jq can consume stdout.
