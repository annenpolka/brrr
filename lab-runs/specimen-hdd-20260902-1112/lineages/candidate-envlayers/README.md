# envlayers

Show one environment key at every layer that can disagree when a dotenv-subset
file contains an empty assignment (`KEY=` or `KEY=""`).

Empty is not unset. A skip-empty loader keeps the inherited value (or an
earlier non-empty file value); an assign loader stores the empty string.
`printenv` and `env | grep` cannot tell those apart once a loader has already
chosen.

This process environment is read in-process unless `--process NAME=VALUE`
injects a snapshot. There is no attach, trace, or guess about what a
third-party tool did.

## Usage

```
envlayers [--file PATH] [--inherited NAME=VALUE] [--process NAME=VALUE] KEY
```

| flag | meaning |
| --- | --- |
| `KEY` | the single key to inspect (POSIX name) |
| `--file PATH` | dotenv-subset file (`KEY=` / `KEY=""` is empty, absent key is unset) |
| `--inherited NAME=VALUE` | caller-supplied inherited map (repeatable). `--inherit` is an alias |
| `--from-process-env` | copy this process env into inherited (opt-in; default is empty) |
| `--no-process-env` | inherited starts empty (the default; kept for older invocations) |
| `--process NAME=VALUE` | injected process map; otherwise process is this CLI `os.environ` |

Inherited does **not** clone `os.environ` by default. Default mode does not
make `inherited == process`.

## File grammar

Declared subset, not silent `partition("=")`:

- UTF-8; leading BOM stripped
- blank lines and `#` comments skipped
- optional `export ` prefix
- `KEY = value` (spaces around `=`) binds `KEY`
- `KEY=""` and `KEY=''` are empty assignments
- other non-assignment lines: `envlayers: not an assignment` (rc=1)

## Output

Tab-separated rows. Column 2 is Python `repr` so `''` and `None` stay
distinct. Column 3 is presence. Column 4 is source. Display values longer
than 256 characters are truncated with `…`.

```
key	KEY	query
inherited	'/x'	present	caller
file	''	empty-assignment	text
skip_empty	'/x'	present	inherited
assign	''	empty	file-empty
process	None	unset	os.environ
file_n	1	assignments
policies_disagree	true
```

| layer | what it is |
| --- | --- |
| `inherited` | caller map (empty unless `--inherited` / `--from-process-env`) |
| `file` | last assignment: `omitted` / `absent` / `empty-assignment` / `value` |
| `skip_empty` | last non-empty file assignment; empty does not unset an earlier file value |
| `assign` | last assignment, including empty string |
| `process` | injected map, or `os.environ` of this CLI process |

`skip_empty` source is `file` when a non-empty file assignment exists, even
if the last file line is empty. It is `inherited` only when no non-empty
file assignment exists.

## Duplicate keys

`file` is last-assignment (empty counts). `skip_empty` is last-non-empty.
A later `KEY=` does not erase an earlier `KEY=fromfile`, and does not fall
back to inherited while a non-empty file assignment exists.

```
# file: KEY=fromfile then KEY= ; inherited KEY=/x
file	''	empty-assignment	text
skip_empty	'fromfile'	present	file
assign	''	empty	file-empty
file_n	2	assignments
```

Last-wins-then-skip (collapse the file to a map, then skip empty → inherited)
is not this policy.

## Errors

Missing `--file` path: `envlayers: file not found: PATH` (rc=1). No
`[Errno 2]`, no traceback. A directory is `envlayers: is a directory: PATH`.
Invalid UTF-8 is `envlayers: not utf-8: PATH`. Omitted `--file` is a
successful run with `file	None	omitted`; an empty file is
`file	None	absent`. Empty names and non-POSIX query keys are refused.

## Example (specimen-010)

Inherited `KEY=/x`, file `KEY=`, this process has no `KEY`:

```
env -u KEY ./envlayers --inherited KEY=/x --file file.env KEY
```

`skip_empty` stays `'/x'`. `assign` becomes `''`. `file` is empty-assignment.
`process` is unset.
