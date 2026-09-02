# poslayer

Show which layer expanded a template token and which leftover CLI args never
entered it.

A file-backed command template `pytest {posargs}` replaces the token with
leftover args `tests src`. A CLI override of the same spelling keeps
`{posargs}` as an argv element. Leftover stays beside the override. The
process can still exit 0. Printing both argvs does not name that split.

This is a template-plus-leftover fixture, not tox.

## Usage

```
poslayer --file PATH [--override TEXT] [--token TOKEN] [--subst-override] [-- leftover...]
poslayer --file-template TEXT [--override TEXT] [--token TOKEN] [--subst-override] [-- leftover...]
```

| argument | meaning |
| --- | --- |
| `--file PATH` | file-backed template (trailing newline stripped) |
| `--file-template TEXT` | file-backed template as a string |
| `--override TEXT` | CLI override spelling; default is the file-backed template |
| `--token TOKEN` | substitution token (default `{posargs}`) |
| leftover | CLI args that would replace the token on a substituting layer |
| `--subst-override` | also replace the token on the override layer |
| `--exit N` | reported override exit code (default 0) |

File-backed construction replaces `TOKEN` with leftover joined by space, then
splits. Override construction splits the override string with no replacement
unless `--subst-override`.

## Output

Tab-separated rows.

```
token	{posargs}
leftover	tests	src
file	expanded	pytest	tests	src
override	literal	pytest	{posargs}
entered	file
in_override	-
missed	tests	src
ran_against	{posargs}
exit	0
silent	yes
```

| row | meaning |
| --- | --- |
| `file` / `override` | layer state (`expanded` / `literal` / `absent`) then argv |
| `entered` | layers whose substitution pass consumed leftover |
| `in_override` | leftover items that appear as override argv words (may be coincidental) |
| `missed` | leftover that did not enter via override substitution |
| `ran_against` | last override argv element |
| `exit` | reported override exit (not a real pytest run) |
| `silent` | `yes` when override left the token literal and exit is 0 |

`in_override` can list a leftover word that was already in the override
template. That is not entry. `missed` is the substitution question.

## Example (specimen-019)

```
poslayer --file-template 'pytest {posargs}' -- tests src
```

`file` is `expanded` with argv `pytest tests src`. `override` is `literal`
with argv `pytest {posargs}`. `entered` is `file`. `missed` is `tests src`.
`ran_against` is `{posargs}`. `silent` is `yes`.

```
poslayer --file-template 'pytest {posargs}' --subst-override -- tests src
```

Both layers `expanded`. `entered` is `file,override`. `missed` is `-`.
`silent` is `no`. `ran_against` is `src`.

## Boundary

Does not run tox or pytest. Naive `.split()`, not shell quoting. Leftover
enters only as a token replacement, never as an appended `--` tail.
