# CANDIDATE: capdiff

```yaml
origin:
  method: hdd
  trial: hdd-ci
```

## Primitive

Named captures of a directory: parsed `.env` plus sha256 of relative file paths. Diff two names as ENV vs FILES. Replay by overlaying captured env vars and exec'ing a command in a directory.

The compared object is the **labeled capture**, not an ad-hoc pair of dumps.

## Why it might not exist

`diff -ru` compares trees. `env` prints or prefixes a process environment. `direnv` loads an `.envrc` into a shell. None of them keep a named pair `{env map, file hashes}` you can diff later and then `exec` with. The composition is small enough that people glue it by hand and then forget which dump was local vs remote.

## Pre-implementation Reality assessment

Copied before implementation:

> Serialize cwd env files (.env) and a file list/hashes. Diff two captures. For replay: export captured env and exec a command in a directory.

Removed magic: tarball import, vaults, auto-started daemons.

Classification: USEFUL_COMPOSITION. Nearest: `diff -ru`; `env`; `direnv`.

## How to run

```bash
./demo.sh
python3 -m unittest discover -s tests -v
```

Python 3 stdlib. Store: `.capdiff/NAME/{.env,manifest.json}` in cwd.

## Empirical transcript

Real run, 2026-09-01. Worktree `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-04-capdiff`.

```text
$ python3 -m unittest discover -s tests -v
test_bad_name ... ok
test_capture_diff_shows_api_key_and_extra_file ... ok
test_files_flag_writes_dotenv ... ok
test_help ... ok
test_identical_captures_exit_0 ... ok
test_missing_capture_diff ... ok
test_missing_env_is_error ... ok
test_no_args_is_usage ... ok
test_replay_does_not_require_host_env ... ok
test_replay_env_only_prints_api_key ... ok
test_replay_remote_key ... ok
Ran 11 tests in 0.985s
OK
```

```text
$ ./demo.sh
== capture a (local) ==
captured a -> .capdiff/a (2 files, 1 env vars)
== capture b (remote) ==
captured b -> .capdiff/b (3 files, 1 env vars)
== diff a b (expect exit 2) ==
ENV modified:
  API_KEY
    A: local-ci-key
    B: remote-ci-key
ENV extra:
  (none)
ENV missing:
  (none)
FILES modified:
  .env
    A: 1f7a9a2f63027fbc9c8c175fd741638d7ccec817ee7fdd6133b6acd1f6a3a306
    B: cec6ea94dca1d4594c66a30a65ad3de3750c1f3353f41a0b970d6ef3dc6fab86
FILES extra:
  extra.txt
FILES missing:
  (none)
diff exit: 2
== replay a (env-only) ==
local-ci-key
== replay b (env-only) ==
remote-ci-key
demo ok
```

Replay used `fixtures/print_key.py` (`print(os.environ["API_KEY"])`) with env-only overlay. No file tree restore.

## Dogfood

First working commit **required** a `.env`. Pointing `capture` at a checkout that only had `readme.txt` exited 1 (`missing .env`). That is the usual shape of a repo that ships `.env.example` and no secrets.

Second commit: missing `.env` is an empty env map. File hashes still record. Diff against a capture that had `API_KEY` reports `ENV missing: API_KEY=local-ci-key` instead of crashing.

Before (commit 1, unittest):

```text
test_missing_env_is_error ... ok   # capture exit 1, stderr "missing .env"
```

After (this commit, real `./demo.sh` tail):

```text
== capture none (no .env) ==
captured none -> .capdiff/none (1 files, 0 env vars)
== diff a none (expect exit 2, API_KEY missing on none) ==
ENV modified:
  (none)
ENV extra:
  (none)
ENV missing:
  API_KEY=local-ci-key
FILES modified:
  (none)
FILES extra:
  readme.txt
FILES missing:
  .env
  app.txt
diff exit: 2
```

## Surprises

- ENV and FILES both report `.env` changes. Parsed `API_KEY` is an env delta; the `.env` bytes (including comments `# local CI` vs `# remote CI`) are a file delta. That split is the point, not a bug.
- `app.txt` hashes matched across fixtures (`be2d377d…`), so the file section stayed quiet except `extra.txt` and `.env`.
- Env-only replay works in an empty directory that has no `.env` at all. The capture, not the live tree, supplies `API_KEY`.

## Failures

- `--files` restores only the captured `.env`, not hashed file bodies. Honest: capture never stored bodies. Replay of a no-`.env` capture with `--files` warns and continues.
- File walk caps at 5000 files (`truncated: true` in the manifest). Huge trees are hashed until the cap, not dumped.
- Overlay replay does not *unset* host variables absent from the capture. Empty env map means "add nothing".

## Suggested mutations

- Capture a listed subset of env vars from `os.environ` in addition to `.env`.
- `capdiff diff --env-only` / `--files-only`.
- Optional include/exclude globs so `node_modules` is not the only skip list.
- Unset host keys missing from the capture (`env -i` style) as an explicit flag.
