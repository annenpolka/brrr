# poslayer

origin.method: hdd
origin.trial: hdd-ctr019
specimens: [specimen-019]

classification: USEFUL_COMPOSITION

## Primitive

Name which layer expanded a template token versus leftover CLI args that
never entered it.

## Why this might not exist

The file-backed spelling and the CLI override spelling can be identical.
One argv contains leftover paths. The other ends with the characters
`{posargs}`. Exit 0 still looks like the intended command ran. Printing
both argvs leaves the join as a hand comparison.

## Core operation

Take a file-backed template, a CLI override template, leftover args, and a
token. Print which layer expanded, which leftover never entered the override
substitution pass, and what the override ran against.

## Observable delta

One query names expansion layer versus leftover args. Ordinary print of
argv plus the template file does not.

## Reality mapping

File layer: `template.replace(token, " ".join(leftover)).split()`.
Override layer: `override.split()` with no replace unless `--subst-override`.
Owned fixture `override_subst.py` is the world.

## Research boundary

Does not run tox, pytest, or a shell. Does not parse tox.ini.

## Removed

tox, live pytest, invented workspace listings.

## Smallest artifact

Python 3 stdlib CLI `poslayer`.

## Pre-implementation Reality assessment

See `REALITY.md`. Classification USEFUL_COMPOSITION. Nearest existing
operation: print argv and the template file. Constraint: ground on
`override_subst.py`.

## How to run

From this directory:

```
python3 tests/test_poslayer.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. `./demo.sh` twice; `demo-1.log` and `demo-2.log`
are byte-identical.

Owned fixture `specimens/specimen-019/files/override_subst.py`:

```
file_argv ['pytest', 'tests', 'src']
override_argv ['pytest', '{posargs}']
cli_leftover ['tests', 'src']
override_exit 0
override_ran_against {posargs}
```

`poslayer --file fixtures/019-file.txt -- tests src`:

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

Unseen `{packages}` leftover `pkg`: `file expanded pytest pkg`,
`override literal pytest {packages}`, `missed pkg`, `ran_against {packages}`,
`silent yes`.

Coincidental override word `pytest tests {posargs}` leftover `tests src`:
`in_override tests`, `missed tests src`, `entered file`. `tests` is in the
override argv as a template word and still missed as leftover.

`--subst-override` leftover `tests src`: both layers `expanded`,
`entered file override`, `missed -`, `ran_against src`, `silent no`.

## Dogfood

First working commit treated leftover as missed when it was absent from
override argv. `pytest tests {posargs}` leftover `tests src` then reported
`missed src` only, because `tests` was already a template word.

Now `missed` is leftover that did not enter via override substitution.
`in_override` still names coincidental argv words. `--subst-override` is
the repaired pass: both layers expand, leftover is not missed, `silent no`.

## Known failures

- Does not run the command.
- Naive `.split()`, not quoting.
- Leftover never appends after `--`; it only replaces the token.
- Empty leftover plus a token still “expands” to a hole filled with `""`.
- `--exit` is reported, not measured from a child process.

## Suggested mutations

- Parse a real tox override / `{posargs}` config.
- shlex quoting instead of `.split()`.
- Append leftover when the override has no token, matching `--` forwarding.
