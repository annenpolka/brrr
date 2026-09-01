# envfrom

Show where effective environment variables come from: process env, a dotenv file:line, or unset.

`env` prints values. `envfrom` prints the source. A `.env` line `LIBRARY_PATH=` is a file empty override even when the process already has `LIBRARY_PATH` — that is the whole point.

`--dir DIR` reads dotenv files from DIR, not from the current working directory. A missing or non-directory DIR is an error (exit 1), not a silent `SOURCE: env`.

```yaml
origin:
  method: hdd
  trial: hdd-env
  mutation: fix
  parent: mutation-01__envfrom-json
```

## Install

Python 3 stdlib only. The shipped CLI is `./envfrom`.

```bash
chmod +x envfrom
```

## Usage

```text
envfrom [--dir DIR] [--json] KEY [KEY...]
envfrom [--dir DIR] [--json] [--fail-empty] KEY [KEY...]
envfrom [--dir DIR] [--json] --run [--load] [KEY...] -- CMD
```

Default files in DIR (cwd if `--dir` is omitted): `.env`, then `.env.local` if present. Later files win.

Honest rule:

- process env = inherited
- `.env` / `.env.local` = file override that *would* apply if a loader ran
- `--load` actually applies those assignments onto the child of `--run`
- missing DIR / DIR that is a file / `.env` that exists but is not a file → exit 1
- invalid UTF-8 `.env` → exit 1, no traceback
- a UTF-8 BOM on the first key is stripped, not treated as part of the name

## Output

```text
LIBRARY_PATH
VALUE=
SOURCE: file:fixtures/empty-override/.env:2
EMPTY_OVERRIDE: yes
INHERITED: /usr/local/lib:/usr/lib
```

`SOURCE` is `env`, `file:<path>:<line>`, or `unset`.

`--json` prints one JSON array of objects `{key, value, source, empty_override, inherited}` instead of the text blocks. `empty_override` is a boolean. `inherited` is the process value or JSON `null` (not the text-mode `(unset)` token). Default text mode is unchanged.

`--fail-empty` exits 2 if a reported key is empty-overridden by a file.

Dotenv lines accept `export KEY=value`, `"double"` / `'single'` quotes, full-line `#` comments, and unquoted inline comments (`KEY=red # comment`). A quoted empty `KEY=""` is still an empty override.

## Demo

```bash
./demo.sh
python3 -m unittest tests.test_envfrom
```
