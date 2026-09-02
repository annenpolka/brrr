# FIX (sealed)

HypothesisWorks/hypothesis PR 3371 / issue 3370.

Merge commit: f0b8c229060dbf63e8ebca3a2c2e45a40c39959e
Title: Remove sorting of dictionaries in pretty.printer. #3370

Python 3.7+ dict iteration is insertion-ordered. Sorting keys in the vendor pretty-printer made falsifying-example text a different dict from the one that failed.

Repair: `_dict_pprinter_factory` enumerates `obj` as stored, without `sorted(keys)`. RELEASE notes: pretty-printer no longer sorts dictionary keys because iteration order is stable and can affect reproducing examples.

Added assertion: `pretty.pretty({1: 1, 0: 0}) == "{1: 1, 0: 0}"`.

Do not expose this file to Dreamers, initial Red Pen, or initial Grounders.
