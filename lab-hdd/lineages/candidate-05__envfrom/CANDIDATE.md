# CANDIDATE: envfrom

```yaml
origin:
  method: hdd
  trial: hdd-env
```

## Primitive

Name a variable. See whether its effective value is inherited from the process environment, assigned at a dotenv `file:path:line`, or unset. Empty file assignments (`KEY=`) are reported as empty overrides, including the inherited process value they would wipe.

## Why it might not exist

`env` and `printenv` show the current map, not which file emptied a key. `bash -x` and `direnv status` show loading activity, not per-variable provenance. People paste `.env` files next to inherited `LIBRARY_PATH` / `PYTHONPATH` and then cannot tell why a child is empty.

## How to run

```bash
./demo.sh
python3 -m unittest tests.test_envfrom
python3 ./envfrom --dir fixtures/empty-override LIBRARY_PATH
```

## Pre-implementation Reality assessment

Copied from the harvest, before this implementation existed:

- Read process env and dotenv-like files.
- For each requested key, report value and source.
- Optionally wrap a command (print provenance then exec).
- CLI `envfrom [KEY...]` and `envfrom --run CMD`.
- Existing tools are not enough: `env` prints values, not which file emptied them.

Removed magic: auto-edit repair, checksums, live metrics.

## Empirical transcript

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom`

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
Ran 11 tests in 0.409s
OK
```

`./demo.sh` (process `LIBRARY_PATH=/usr/local/lib:/usr/lib`, `APP_ENV=from-shell`, fixture `.env` has `LIBRARY_PATH=` on line 2). PATH VALUE is the real login PATH from that run:

```text
=== envfrom LIBRARY_PATH APP_ENV PATH NOT_A_REAL_VAR ===
LIBRARY_PATH
VALUE=
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/empty-override/.env:2
EMPTY_OVERRIDE: yes
INHERITED: /usr/local/lib:/usr/lib

APP_ENV
VALUE=dev
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/empty-override/.env:3
INHERITED: from-shell

PATH
VALUE=/Users/annenpolka/.grok/bin:/Users/annenpolka/.local/bin:/Users/annenpolka/.opencode/bin:/Users/annenpolka/.moon/bin:/Users/annenpolka/.bun/bin:/Users/annenpolka/.antigravity/antigravity/bin:/opt/homebrew/opt/libpq/bin:/Users/annenpolka/.local/share/mise/installs/ruby/3/bin:/Users/annenpolka/.volta/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/Users/annenpolka/.ghcup/bin:/Users/annenpolka/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu/bin/:/Users/annenpolka/.cargo/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/pkg/env/global/bin:/Library/Apple/usr/bin:/usr/local/share/dotnet:~/.dotnet/tools:/Users/annenpolka/.deno/bin:/Applications/Ghostty.app/Contents/MacOS:/Users/annenpolka/.orbstack/bin:/Applications/Obsidian.app/Contents/MacOS:/Users/annenpolka/go/bin:/Users/annenpolka/Library/pnpm/bin:/Users/annenpolka/.cache/lm-studio/bin
SOURCE: env

NOT_A_REAL_VAR
VALUE=
SOURCE: unset

=== --fail-empty LIBRARY_PATH (expect exit 2) ===
LIBRARY_PATH
VALUE=
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/empty-override/.env:2
EMPTY_OVERRIDE: yes
INHERITED: /usr/local/lib:/usr/lib
exit=2

=== --run without --load: child keeps inherited LIBRARY_PATH ===
LIBRARY_PATH
VALUE=
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/empty-override/.env:2
EMPTY_OVERRIDE: yes
INHERITED: /usr/local/lib:/usr/lib

APP_ENV
VALUE=dev
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/empty-override/.env:3
INHERITED: from-shell
child LIBRARY_PATH=/usr/local/lib:/usr/lib

=== --run --load: child sees file empty override ===
LIBRARY_PATH
VALUE=
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/empty-override/.env:2
EMPTY_OVERRIDE: yes
INHERITED: /usr/local/lib:/usr/lib

APP_ENV
VALUE=dev
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/empty-override/.env:3
INHERITED: from-shell
child LIBRARY_PATH=''
child APP_ENV=dev
```

## Dogfood

Fed `fixtures/quoted-export/.env` to the first working CLI. That file uses `export PREFIX=app`, `"hello world"`, `'Ada Lovelace'`, `COLOR=red # inline comment`, and `EMPTY_QUOTED=""`.

Before (first commit, real run):

```text
PREFIX
VALUE=
SOURCE: unset

GREETING
VALUE="hello world"
SOURCE: file:fixtures/quoted-export/.env:3
INHERITED: (unset)

NAME
VALUE=
SOURCE: unset

COLOR
VALUE=red # inline comment
SOURCE: file:fixtures/quoted-export/.env:5
INHERITED: (unset)

EMPTY_QUOTED
VALUE=""
SOURCE: file:fixtures/quoted-export/.env:6
INHERITED: (unset)

HASH_IN_QUOTES
VALUE="# not a comment"
SOURCE: file:fixtures/quoted-export/.env:7
INHERITED: (unset)
```

`export PREFIX` and `export NAME` vanished (invalid keys). Quotes stuck to values. Inline comments became part of the value. `""` was not an empty override.

After parser change (real `./demo.sh` section):

```text
=== quoted values, inline comments, export PREFIX ===
PREFIX
VALUE=app
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/quoted-export/.env:2
INHERITED: (unset)

GREETING
VALUE=hello world
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/quoted-export/.env:3
INHERITED: (unset)

NAME
VALUE=Ada Lovelace
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/quoted-export/.env:4
INHERITED: (unset)

COLOR
VALUE=red
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/quoted-export/.env:5
INHERITED: (unset)

EMPTY_QUOTED
VALUE=
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/quoted-export/.env:6
EMPTY_OVERRIDE: yes
INHERITED: (unset)

HASH_IN_QUOTES
VALUE=# not a comment
SOURCE: file:/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-05-envfrom/fixtures/quoted-export/.env:7
INHERITED: (unset)
```

Unittest count after dogfood: 14 tests, OK.

## Surprises

- Reporting `PATH` is honest and noisy: `SOURCE: env` plus the entire inherited string. The interesting delta is next to it (`LIBRARY_PATH` empty-overridden at `.env:2`).
- `--run` without `--load` prints the *would-apply* empty override and then the child still has the inherited value. That split is the honest rule, not a bug.
- Full-line `#` comments already worked in the first parser. Inline comments did not.
- Quoted `# not a comment` must stay a value; the same character starts a comment when unquoted and preceded by whitespace.
- `KEY=""` is an empty override, same as `KEY=`. That only became true after unquoting.

## Failures

- First parser: `export KEY=value` dropped, quotes retained, inline comments retained (see dogfood before).
- Still: a quoted value containing a newline would break the one-line `VALUE=` block format. Not parsed into the demo; escaped `\n` is supported in double quotes but not pretty-printed.
- Still: no `${OTHER}` interpolation, no `KEY+=`.

## Suggested mutations

- Report a source chain when `.env` and `.env.local` both set the same key.
- Parse `KEY+=` / interpolation.
- Compare against a recorded child `env` dump.
- Relative SOURCE paths when `--dir` is under cwd (absolute paths are correct, ugly in transcripts).
- Encode newlines in VALUE so quoted multiline dotenv does not smash the block format.

