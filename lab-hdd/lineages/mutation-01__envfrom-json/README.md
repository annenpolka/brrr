# envfrom

Show where effective environment variables come from: process env, a dotenv file:line, or unset.

`env` prints values. `envfrom` prints the source. A `.env` line `LIBRARY_PATH=` is a file empty override even when the process already has `LIBRARY_PATH` — that is the whole point.

```yaml
origin:
  method: hdd
  trial: hdd-env
  mutation: ordinary
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

Default files in DIR (cwd if omitted): `.env`, then `.env.local` if present. Later files win.

Honest rule:

- process env = inherited
- `.env` / `.env.local` = file override that *would* apply if a loader ran
- `--load` actually applies those assignments onto the child of `--run`

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
