# OBSERVED

Public gradle/gradle#36392 (closed 2026-07-13). PR 38432 commit `24311263532f820ba81399b662ae3d53eebe28b9` (parent `e0ca283b48bc739f14140b8a61565d689758c032`). Local Gradle was not performed on this lab host.

Issue body: copy project with configuration-cache entries; assemble in the copy reuses the entry; UP-TO-DATE checks leftover named files in the old location.

On failing_ref, `checkFingerprint` does not invalidate when `buildTreeRootDirectory` is absent from stored `rootDirs`. The location compare is **not** on the failing revision. It is added by PR 38432.

Not this packet: specimen-104 named FileCollection leftover root base dir (PathToFileResolver omitted; gradle#30052 / PR 32359). specimen-088 fileTree query observation omitted. Unique axis vs 104: leftover named-file absolute paths after relocate because CC identity omits build location, not leftover resolver for relative named files at load. specimen-123/124 earthly leftover CACHE --id.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
