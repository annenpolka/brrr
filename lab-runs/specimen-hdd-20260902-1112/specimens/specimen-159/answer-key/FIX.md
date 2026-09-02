KNOWN FIX (sealed): gleam-lang/gleam PR 4325 rebase-merge b3e1ceb15118c3b4abb0909ef1f2baca6abacd37.

failing_ref is parent of first rebased PR commit: 3767575d05372e4b823c132afacb28e52fbe3aa1.

Removed modules were marked stale; cache files stayed. Restored same-name source with matching fingerprint took leftover previous compile of `a` after `b` changed.

PR repair: delete cache files when the source is gone; restoring `a` is a new compile.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
