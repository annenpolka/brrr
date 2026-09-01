# CANDIDATE: gen3-02 — envfrom-dir

```yaml
origin:
  method: hdd
  trial: hdd-env
  mutation: fix
  generation: 3
  parent: mutation-01__envfrom-json
  destroyer: DESTROYER_CONFIG
```

## Primitive

Name a variable. See whether its effective value is inherited from the process environment, assigned at a dotenv `file:path:line`, or unset. Empty file assignments (`KEY=`) are reported as empty overrides, including the inherited process value they would wipe.

Fix mutation of mutation-01 (DESTROYER_CONFIG). `--dir DIR` reads dotenv from DIR, not cwd. A missing or non-directory DIR is exit 1, not a silent `SOURCE: env`. Invalid UTF-8 `.env` is exit 1 without a traceback. A UTF-8 BOM on the first key is stripped, not folded into the name.

## Why it might not exist

`env` and `printenv` show the current map, not which file emptied a key. Parent `envfrom --json` is the provenance record. The remaining lie is treating a missing tree as "no dotenv, inherit everything". stated and effect already exit 1 on a missing directory. This cut matches that.

## How to run

```bash
./demo.sh
python3 -m unittest tests.test_envfrom
python3 ./envfrom --dir fixtures/empty-override LIBRARY_PATH
python3 ./envfrom --json --dir fixtures/empty-override LIBRARY_PATH APP_ENV
```

## Pre-implementation Reality assessment

Copied from the harvest, before the parent implementation existed (still in force):

- Read process env and dotenv-like files.
- For each requested key, report value and source.
- Optionally wrap a command (print provenance then exec).
- CLI `envfrom [KEY...]` and `envfrom --run CMD`.
- Existing tools are not enough: `env` prints values, not which file emptied them.

Removed magic: auto-edit repair, checksums, live metrics.

This mutation does not add interpolation, `KEY+=`, a source chain, or a JSON/text newline encoder.

## Empirical transcript

Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/gen3-02-envfrom-dir`

```text
$ python3 -m unittest tests.test_envfrom
...............................
----------------------------------------------------------------------
Ran 31 tests in 1.100s
OK
```

`./demo.sh` exit 0. Empty-override / `--json` / quoted-export unchanged from mutation-01. New sections:

```text
=== --dir reads that tree, not cwd ===
FOO
VALUE=from-here
SOURCE: file:.env:1
INHERITED: (unset)
FOO
VALUE=from-there
SOURCE: file:…/there/.env:1
INHERITED: (unset)

=== missing --dir (expect exit 1, not SOURCE: env) ===
envfrom: directory not found: /no/such/envfrom-dir
exit=1

=== UTF-8 BOM keeps FOO; invalid UTF-8 exits 1 without traceback ===
FOO
VALUE=bom
SOURCE: file:…/.env:1
INHERITED: (unset)

BAR
VALUE=
SOURCE: unset

BAZ
VALUE=ok
SOURCE: file:…/.env:3
INHERITED: (unset)
envfrom: cannot read …/.env: 'utf-8' codec can't decode byte 0xff in position 11: invalid start byte
exit=1
```

`--fail-empty LIBRARY_PATH` still exit 2. `--run` without `--load` child keeps inherited LIBRARY_PATH; `--run --load` child `LIBRARY_PATH=''`.

## Dogfood

Fed the DESTROYER_CONFIG BOM / binary / missing-DIR probes to parent mutation-01, then this CLI.

Before (mutation-01, real run):

```text
$ python3 mutation-01__envfrom-json/envfrom --dir /no/such/envfrom-dir PATH
PATH
VALUE=/Users/annenpolka/.grok/bin:…
SOURCE: env
# rc=0

$ printf '\xef\xbb\xbfFOO=bom\r\nexport BAR\r\nBAZ=ok\r\n' > DIR/.env
$ python3 mutation-01__envfrom-json/envfrom --dir DIR FOO BAR BAZ
FOO
VALUE=
SOURCE: unset
BAR
VALUE=
SOURCE: unset
BAZ
VALUE=ok
SOURCE: file:…/.env:3
# rc=0  — BOM glued to the first key; FOO dropped

$ printf 'FOO=ok\nBAR=\xff\xfe\x00notutf8\nBAZ=1\n' > DIR/.env
$ python3 mutation-01__envfrom-json/envfrom --dir DIR FOO
Traceback (most recent call last):
  …
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 11: invalid start byte
# rc=1
```

After (this CLI, real `./demo.sh`):

```text
envfrom: directory not found: /no/such/envfrom-dir
exit=1

FOO
VALUE=bom
SOURCE: file:…/.env:1
BAR
VALUE=
SOURCE: unset    # export BAR with no '=' still skipped; honest
BAZ
VALUE=ok
SOURCE: file:…/.env:3

envfrom: cannot read …/.env: 'utf-8' codec can't decode byte 0xff in position 11: invalid start byte
exit=1
# no Traceback
```

`--dir` pointing at a regular file or `/dev/null` is `not a directory`, rc=1. A directory named `.env` or a self-symlink `.env` is `not a file`, rc=1. Unittest count after dogfood: 31 tests, OK.

## Surprises

- Omitting `--dir` while cwd has no `.env` and another tree does still reports `SOURCE: env`. That is cwd-default, not the missing-DIR bug. The bug is `--dir /no/such/dir` printing inherited PATH.
- `--dir /dev/null` and `--dir` pointing at a regular file are the same class of lie as a missing path.
- `utf-8-sig` strips the BOM; the decode error for binary still names the `utf-8` codec. The object is "no traceback", not the codec label.
- `export BAR` (no `=`) remains skipped. DESTROYER already called that honest.

## Failures

- Still: no `${OTHER}` interpolation, no `KEY+=`.
- Still: `--json --run` concatenates the JSON document and the child on the same stdout.
- Still: no source chain when `.env` and `.env.local` both set the same key (last-wins only).
- Still: quoted `\n` in text `VALUE=` is a multi-line block (`--json` already round-trips).

## Suggested mutations

- Report a source chain when `.env` and `.env.local` both set the same key.
- Parse `KEY+=` / interpolation, or emit `source: skipped` for dropped lines.
- Encode newlines in text `VALUE=` (or refuse).
- `--json --run` with child stdout on fd 3, or provenance on stderr, so jq can consume stdout.
