# OBSERVED

Public JetBrains/kotlin#6654 (merged 2026-07-14). Squash `0a61a56593a0d6270e6e5f66d0fd31c2209429ed` (parent `a05299825cbf5d5e19df97bd7f8ec00a98716871`). Local kotlin-native was not performed on this lab host.

PR title: Incremental compilation: fixed stale external caches problem. There was no check if an external library was changed (only existence of its cache). Rollback to an already-cached version reused leftover IC.

On failing_ref, stale detection compared `compilerFingerprint` only. `CacheMetadata` had no `dependenciesFingerprint`. Dirty-file analysis compared source IR hashes.

Not this packet: specimen-104 gradle incremental. specimen-075 rust incremental leftover. specimen-103 go work-sync leftover replace.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
