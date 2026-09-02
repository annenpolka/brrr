KNOWN FIX (sealed): Homebrew/brew PR 23597 merge b62af44bc2d4173d113d07648eb78a9facb73fcf.

failing_ref is merge first parent 4f6e4df964fa22f12591ca4b27e9b52df34b9494.

no_diff? keyed only formula.path; local patch files omitted; leftover bottle reused after patch change.

PR repair: relative_paths includes formula.path plus formula.patchlist.grep(LocalPatch) map file; regression test rejects a bottle when a local patch has changed.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
