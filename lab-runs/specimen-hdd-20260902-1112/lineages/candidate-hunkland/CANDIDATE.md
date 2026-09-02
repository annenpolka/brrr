# hunkland

origin.method: specimen-hdd
origin.trial: hdd-emptyrange
specimens: [specimen-020]

classification: USEFUL_COMPOSITION

## Primitive

Compare where a patch insert landed with the line the hunk header named.

## Why this might not exist

An apply that exits 0 is reported as success. The miss is an insert on the
wrong line. Reading the `@@` header plus `cat` of the result still leaves
the join — exit 0, named new-file line, actual insert line — as a hand
comparison.

## Core operation

Given original text, a result (or an `apply_hunk` applier), and a hunk
header, print `land` versus `header`. Exit 0 does not mean they match.

## Observable delta

One query names mis-indexed success rather than a clean apply. On the owned
fixture, `header` is 3 (`second`) and `land` is 2 (`inserted`) while
`apply_exit` is 0.

## Reality mapping

Owned fixture `specimen-020/files/patch_insert.py`: orig
`first\nsecond\nthird\n`, hunk `@@ -2,0 +3 @@` / `+inserted`, result
`first\ninserted\nsecond\nthird\n`, apply_exit 0. `header` is the `+N` in
the hunk. `land` is the first inserted line in the result.

## Research boundary

Does not rebuild pnpm or git apply. Does not fix the applier. Does not treat
frozen-lockfile install success as evidence.

## Removed

pnpm rebuild, installer hooks, frozen-lockfile lore.

## Smallest artifact

Python 3 stdlib CLI `hunkland`.

## Pre-implementation Reality assessment

See `REALITY.md`. Classification USEFUL_COMPOSITION. Nearest existing
operation: read the diff and the result file. Observable delta: names
mis-indexed success rather than a clean apply.

## How to run

From this directory:

```
python3 tests/test_hunkland.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. `./demo.sh` (after --applier / line-text dogfood):

```
== fixture .../specimen-020/files/patch_insert.py ==
orig 'first\nsecond\nthird\n'
hunk @@ -2,0 +3 @@ +inserted
result 'first\ninserted\nsecond\nthird\n'
apply_exit 0
frozen_lockfile_install success

== hunkland --applier (owned apply_hunk) vs @@ -2,0 +3 ==
header	3
header_line	second
land	2
land_line	inserted
apply_exit	0
match	no
verdict	mis-indexed
```

`cat` of orig/result plus the hunk still looks like a successful insert.
`hunkland` names `header 3` vs `land 2` under `apply_exit 0`.

Aligned result `first\nsecond\ninserted\nthird\n`: `land 3`, `match yes`,
`verdict aligned`.

Unseen `--applier` `@@ -3,0 +4 @@` + `mid` on `alpha\nbeta\ngamma\ndelta\n`:
`header 4` (`gamma`), `land 3` (`mid`), `verdict mis-indexed`.

Tests: 14 OK (`python3 tests/test_hunkland.py`).

## Dogfood

First run required a hand-built result file and a `cat` of that file to see
that line 2 was `inserted` while line 3 was `second`. One query now loads
the owned `apply_hunk` (`--applier`) and prints `header_line` / `land_line`
plus `verdict mis-indexed`.

## Surprises

`old_start=0` is `idx = -1`. Python `list.insert(-1, …)` inserts before the
last line, not at line 1 and not at EOF. `@@ -0,0 +1 @@` on the three-line
fixture lands at 3 (`inserted`) while `header` is 1 (`first`).

The fixture's `frozen_lockfile_install success` line is extra lore; hunkland
does not print it.

## Failures

Does not apply unified diffs with context lines or deletions. `--applier`
must expose `apply_hunk(text, old_start, old_count, insert)`. Does not
repair the applier. `land` is the first inserted or replaced line only.

## Suggested mutations

- `--check` exit 1 on `mis-indexed`
- Name the 0-based index the applier used (`old_start-1`) next to `header`
- Multiple inserted lines as a range
- Refuse `verdict aligned` when `old_count` is not 0

## Kill / keep

Keep: specimen-020 names `land 2` vs `header 3` under `apply_exit 0` and
`verdict mis-indexed`. An insert that actually occupies the header line is
`aligned`.
