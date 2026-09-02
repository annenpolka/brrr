# OBSERVED

Public ninja-build/ninja#2666 (closed 2026-07-19). PR 2680 merge `88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68` (first parent `77d328f5f679bfef14b1f67f3cd431b729bc786f`). Local ninja was not performed on this lab host.

Issue comment (root-cause rewrite): Ninja loads an old deps-log dependency even though the target will be regenerated; leftover obsolete deps cause cycle detection. Ninja should only load a deps file if the target producing it is not dirty.

On failing_ref, `LoadDeps` runs in `RecomputeNodeDirty` before the dirty walk finishes. `LoadDepsFromLog` validity is output mtime vs stored deps mtime. Dirty/command identity is omitted.

Not this packet: specimen-075 rustc incremental fingerprint. specimen-086 cargo rustc extra-filename. Distinct leftover: ninja deps-log identity loaded while the producing edge is dirty.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
