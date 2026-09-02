# Reality assessment (pre-implementation)

classification: USEFUL_COMPOSITION

## Core operation

Compare where a patch insert landed with the line the hunk header named.

## Nearest existing operation

Read the `@@` header and the result file, then count lines by hand.

## Observable delta

One query names `land` versus `header`. Apply exit 0 is still `match no`
when the insert sits on the wrong line. Ordinary apply success still looks
like a clean apply.

## Reality mapping

The world is original text, result text, and a unified-diff hunk header
`@@ -old,oldcount +new @@`. `header` is the new-file line the header named.
`land` is the 1-based line of the first inserted line in the result. Empty
old-range (`oldcount=0`) is an insert; treating it as a 1-based index
(`old-1`) lands one line early on the owned fixture.

Owned fixture `specimen-020/files/patch_insert.py`: orig
`first\nsecond\nthird\n`, hunk `@@ -2,0 +3 @@` / `+inserted`, result
`first\ninserted\nsecond\nthird\n`, apply_exit 0. Header names 3; land is 2.

## Research boundary

Does not rebuild pnpm, git apply, or a package installer. Does not fix the
applier. Does not treat frozen-lockfile install success as evidence.

## Removed

pnpm rebuild, installer hooks, frozen-lockfile lore.

## Smallest artifact

Python 3 stdlib CLI `hunkland`.

## Why existing tools are not enough

`diff` plus `echo $?` still presents a successful apply. The join (exit 0,
header line, land line) is a hand comparison.
