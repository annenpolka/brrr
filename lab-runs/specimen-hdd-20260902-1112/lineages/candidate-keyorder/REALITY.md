# Reality assessment (pre-implementation)

classification: USEFUL_COMPOSITION

## Core operation

Show which printed mapping is sorted-keys and which preserves insertion
order, when those views disagree.

## Nearest existing operation

`print(d)` versus `print(list(d))`. One is a mapping display in insertion
order; the other is a key list. Neither names a second mapping printer as
the one that reordered keys.

## Observable delta

One query names each displayed mapping as `sorted-keys` or
`insertion-order` and names the printer that reordered keys.

## Reality mapping

The world is an owned dict `{1: 0, 0: 0}` (insertion order `1` then `0`)
and two printers of that same object: one enumerates `sorted(keys)`, one
enumerates the dict as stored. Hypothesis/pytest are not required. The
displayed text is a Python mapping literal; key order in that literal is
the displayed order.

## Research boundary

Does not check out Hypothesis, run pytest, or port a vendor pretty-printer.
Does not reconstruct a failing `@given` test. Unsortable keys cannot be
classified as sorted-keys.

## Removed

Hypothesis checkout, pytest dump scraping, pretty-printer port.

## Smallest artifact

Python 3 stdlib CLI `keyorder`.

## Why existing tools are not enough

`print(d)` and `print(list(d))` still leave the join — which mapping
display was sorted, which preserved insertion, which printer reordered —
as a hand comparison of three forms of one dict.
