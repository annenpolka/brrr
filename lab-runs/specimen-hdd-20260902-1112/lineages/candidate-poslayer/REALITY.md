# Reality assessment (pre-implementation)

classification: USEFUL_COMPOSITION

## Core operation

Show which layer expanded a template token and which leftover args never
entered it.

## Nearest existing operation

Print argv and the template file.

## Observable delta

One query names the expansion layer versus leftover args. Printing both
argvs still leaves “file expanded, override kept `{posargs}` literal, leftover
`tests src` unused, exit 0” as a hand join. Exit 0 on a literal token hides
the missed substitution.

## Reality mapping

Two command constructions from the same spelling `pytest {posargs}` plus
leftover `tests src`:

- file-backed: replace `{posargs}` with the leftover join, then split
- CLI override: split the override string with no replacement; leftover stays
  beside it

The owned fixture `override_subst.py` is the world. tox is not executed.

## Research boundary

Does not run tox, pytest, or a shell. Does not parse tox.ini. Does not claim
which tests a real process executed beyond the override argv it would have
used. Naive `.split()` matches the fixture, not shell quoting.

## Removed

tox, live pytest, invented workspace listings.

## Smallest artifact

Python 3 stdlib CLI `poslayer`.

## Why existing tools are not enough

`print(argv)` plus reading the template still looks like success when the
override argv ends with `{posargs}` and the process exits 0.
