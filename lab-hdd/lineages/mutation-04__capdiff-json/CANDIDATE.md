# CANDIDATE: mutation-04 — capdiff-json

```yaml
origin:
  method: hdd
  trial: hdd-ci
  mutation: ordinary
  parent: candidate-04__capdiff
```

## Primitive

Named captures of a directory: parsed `.env` plus sha256 of relative file paths. Diff two names as ENV vs FILES. Replay by overlaying captured env vars and exec'ing a command in a directory.

The compared object is the **labeled capture**, not an ad-hoc pair of dumps.

Ordinary mutation of candidate-04: `capdiff diff A B --json` emits `{a, b, env, files}`. `env` and `files` each have `modified` / `extra` / `missing` as arrays of objects. Default text blocks and exit codes (0 identical, 2 delta, 1 error) are unchanged.

## Why it might not exist

`diff -ru` compares trees. `env` prints or prefixes a process environment. `direnv` loads an `.envrc` into a shell. None of them keep a named pair `{env map, file hashes}` you can diff later and then `exec` with. Parent `capdiff` is grepable sections; a script that wants extra vs missing as data still has to parse `  extra.txt` and `  API_KEY=local-ci-key`. `--json` is the same six buckets as a document.

## Pre-implementation Reality assessment

Copied from the harvest, before the parent implementation existed (still in force):

> Serialize cwd env files (.env) and a file list/hashes. Diff two captures. For replay: export captured env and exec a command in a directory.

Removed magic: tarball import, vaults, auto-started daemons.

Classification: USEFUL_COMPOSITION. Nearest: `diff -ru`; `env`; `direnv`.

This mutation adds a JSON encoding of that record. It does not add `--env-only` / `--files-only`, glob filters, or env-from-process capture.

## How to run

```bash
./demo.sh
python3 -m unittest discover -s tests -v
./capdiff capture a fixtures/env-a
./capdiff capture b fixtures/env-b
./capdiff diff a b
./capdiff diff a b --json
```

Python 3 stdlib. Store: `.capdiff/NAME/{.env,manifest.json}` in cwd.

## Empirical transcript

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-04-capdiff-json`

```text
$ python3 -m unittest discover -s tests -v
test_bad_name ... ok
test_capture_diff_shows_api_key_and_extra_file ... ok
test_files_flag_writes_dotenv ... ok
test_help ... ok
test_identical_captures_exit_0 ... ok
test_json_diff_a_b_objects ... ok
test_json_does_not_change_default_text ... ok
test_json_env_extra_value_keeps_embedded_equals ... ok
test_json_identical_empty_arrays_exit_0 ... ok
test_json_missing_capture_still_exits_1 ... ok
test_json_missing_env_is_object_not_text_line ... ok
test_missing_capture_diff ... ok
test_missing_env_is_empty_not_crash ... ok
test_no_args_is_usage ... ok
test_replay_does_not_require_host_env ... ok
test_replay_env_only_prints_api_key ... ok
test_replay_remote_key ... ok
Ran 17 tests in 0.979s
OK
```

`./demo.sh` exit 0. Default text for `diff a b` is unchanged from the parent (ENV `API_KEY` local vs remote, FILES extra `extra.txt`, exit 2). JSON section (pretty-printed here; the CLI emits one line):

```json
{
  "a": "a",
  "b": "b",
  "env": {
    "extra": [],
    "missing": [],
    "modified": [{"a": "local-ci-key", "b": "remote-ci-key", "key": "API_KEY"}]
  },
  "files": {
    "extra": [{"hash": "67985e4bbe56ba7c83837e3fdc1bfa0ece762b040f19f68d091cf5402251cb98", "path": "extra.txt"}],
    "missing": [],
    "modified": [
      {
        "a": "1f7a9a2f63027fbc9c8c175fd741638d7ccec817ee7fdd6133b6acd1f6a3a306",
        "b": "cec6ea94dca1d4594c66a30a65ad3de3750c1f3353f41a0b970d6ef3dc6fab86",
        "path": ".env"
      }
    ]
  }
}
```

`diff a none --json` exit 2. `diff a a --json` empty arrays plus `"a":"a","b":"a"`, exit 0. Missing capture with `--json` still exit 1, empty stdout. Text mode still prints `API_KEY=local-ci-key`.

## Dogfood

Fed `diff a none --json` (capture with `API_KEY` vs capture of a tree with no `.env`). Text mode reports `ENV missing: API_KEY=local-ci-key` and `FILES extra: readme.txt`.

Before (first mutation commit, real run). Extra/missing leaked the text-mode lines:

```text
{"env": {"extra": [], "missing": ["API_KEY=local-ci-key"], "modified": []}, "files": {"extra": ["readme.txt"], "missing": [".env", "app.txt"], "modified": []}}
```

`json.loads` succeeded. `API_KEY` was joined with `=`. File extra was a path string with no hash. Capture names were absent.

After (real `./demo.sh` `--json` `a none` section; pretty-printed here):

```json
{
  "a": "a",
  "b": "none",
  "env": {
    "extra": [],
    "missing": [{"key": "API_KEY", "value": "local-ci-key"}],
    "modified": []
  },
  "files": {
    "extra": [{"hash": "23c54a5ec19281dc438187204a7de0703402d42eb1a916e501429e9bae83d7b3", "path": "readme.txt"}],
    "missing": [
      {"hash": "1f7a9a2f63027fbc9c8c175fd741638d7ccec817ee7fdd6133b6acd1f6a3a306", "path": ".env"},
      {"hash": "be2d377d8d8b117822739d072afed71c19487f7236d8bfbd5a02d6769d55d1aa", "path": "app.txt"}
    ],
    "modified": []
  }
}
```

A value with an embedded `=` (`DSN=postgres://x=y` extra on B) round-trips as JSON `{key: "DSN", value: "postgres://x=y"}`. Text mode still prints `DSN=postgres://x=y`. Unittest count after dogfood: 17 tests, OK.

## Surprises

- The interesting JSON bug was not quotes on `API_KEY`. Parent already parses `.env`. The leak was copying the text line `KEY=value` / bare path into a field that should be an object.
- Empty buckets are `[]`, not the text token `(none)`. Identical JSON is six empty arrays, exit 0.
- ENV and FILES both report `.env` changes in JSON the same way as text: parsed `API_KEY` is an env delta; the `.env` bytes are a file delta. That split is the point, not a bug.
- `extra.txt` hash `67985e4b…` is the bytes of `remote-only artifact\n`. JSON extra now carries that hash; text still prints only the path.
- `--json` after names (`diff a b --json`) and before names (`diff --json a b`) both work.

## Failures

- First JSON encoder: extra/missing were text-mode strings (see dogfood before).
- Still: `--files` restores only the captured `.env`, not hashed file bodies. Honest: capture never stored bodies.
- Still: overlay replay does not unset host variables absent from the capture. Empty env map means "add nothing".
- File walk still caps at 5000 files (`truncated: true` in the manifest).

## Suggested mutations

- `capdiff diff --env-only` / `--files-only`.
- Optional include/exclude globs so `node_modules` is not the only skip list.
- Capture a listed subset of env vars from `os.environ` in addition to `.env`.
- Unset host keys missing from the capture (`env -i` style) as an explicit flag.
- `--json` pretty-print flag; default stays one line.
