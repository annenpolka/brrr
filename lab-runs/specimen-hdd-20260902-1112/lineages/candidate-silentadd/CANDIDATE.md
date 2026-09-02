# silentadd

origin.method: specimen-hdd
origin.trial: hdd-silent-add
specimens: [specimen-014, specimen-017]

classification: USEFUL_COMPOSITION

## Core operation

Report an insert that returned ok while a file/dir collision remained,
including scan start.

## Observable delta

One query treats exit 0 plus remaining collision as the object, not a
successful add, and names the scan cursor. Printing the list plus the
process exit still looks like success.

## Reality mapping

Ordered path strings plus a name. Directory collision: an entry is `name/`
or `name/...`. File collision: an entry equals a parent of `name`, or the
same path without a trailing slash. Directory-prefix scan walks forward from
a cursor and breaks on the first non-prefix entry.

## Research boundary

Does not rebuild libgit2 or parse a real git index. The list is the world.
specimen-017 is extras/requires, not a path index: the tool must not invent
a file/dir collision there.

## Removed

git rebuild, index dumpers, known C patch.

## Smallest artifact

Python 3 stdlib CLI `silentadd`.

## Baseline

`printf '%s\n' aaa blobtree/ zzz` plus remembering that add exited 0. The
candidate names `add ok`, `remain blobtree/`, `scan_start 0`, `hide aaa`,
`scan0 miss` / `scan_pos hit`, `silent yes`.

## Empirical

specimen-014 list `aaa blobtree/ zzz`, name `blobtree`, scan 0:

```
add	ok
collision	present
remain	blobtree/	dir
hide	aaa
scan0	miss
scan_pos	hit
silent	yes
```

Same list, `--scan pos`: `add fail`, `silent no`, `hide none`.

Only `blobtree/` (insert_pos 0): `scan0 hit`, `add fail` — the single-prior
entry case that never exposes the miss.

specimen-017 extra name `B` with index `B`: `collision absent`, `silent no`.

Unseen `pkg` into `000 README pkg/__init__.py tests/test.py`: `silent yes`,
`remain pkg/__init__.py`, `hide 000`.

## Dogfood

First run needed two invocations (`--scan 0` and `--scan pos`) to see cursor
dependence. One query now prints `scan0`, `scan_pos`, the hiding sibling
(`hide`), and whether the list is `ordered`.

## Known failures

- Unsorted lists: prefix-break is not a range scan; `ordered no` is the
  honest flag, not a repair.
- Does not read `.git/index` or git stages.
- Does not apply or simulate `ok_to_replace`.
- specimen-017 extras remainder is a different primitive; silentadd reports
  `collision absent` for extra names with no `/`.

## Suggested mutations

- Parse a real git index (stages, replace).
- Name the sufficient scan start that would have found the remainder.
- Refuse to answer `add` when `ordered` is `no`.
