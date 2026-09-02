KNOWN FIX (sealed): gradle/gradle PR 38432 commit 24311263532f820ba81399b662ae3d53eebe28b9.

failing_ref is parent e0ca283b48bc739f14140b8a61565d689758c032.

checkFingerprint registered stored rootDirs as watchable but omitted comparing buildTreeRootDirectory, so leftover CC named-file absolute paths from the previous location were reused after copy/move.

PR repair: Invalid when buildTreeRootDirectory is not in rootDirs; tests for copy and move.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
