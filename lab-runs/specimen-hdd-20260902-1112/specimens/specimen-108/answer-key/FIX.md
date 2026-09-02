KNOWN FIX (sealed): npm/cli PR 9632 squash 981e2498589c83859b3c9e8b92a2cc67562dc06b.

failing_ref is squash parent 696801574984ad19ffaa9a7200d7e752920a018d.

Linked uninstall's actual-tree diff never emitted a drop for the bin shim. #cleanOrphanedStoreEntries skipped .bin as a dot-entry. Leftover rimraf shim identity remained after store+top-level cleanup.

PR repair: binsByDir from still-linked package.bin; #cleanStaleBinLinks removes .bin names not provided by survivors (and dangling symlinks), keeping surviving shims including Windows .cmd/.ps1.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
