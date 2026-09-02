# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Kotlin/Native incremental compilation can keep the identity of a **previous per-file cache** after an external dependency is rolled back to a version whose cache already exists, because `CacheMetadata` stored `compilerFingerprint` / `runtimeFingerprint` and omitted a combined fingerprint of auto-cached external libraries. The dirty-file check only compared IR content hashes of source files. Existence of the old cache was enough.

On failing_ref `a05299825cbf5d5e19df97bd7f8ec00a98716871`:

```
class CacheMetadata(
    val target: KonanTarget,
    val compilerFingerprint: String,
    val runtimeFingerprint: String?,
)

val staleCompilerCacheLibraries = icedLibraries.filter { library ->
    val cache = caches[library] as? CachedLibraries.Cache.PerFile ?: return@filter false
    val anyCachedFile = File(cache.path).listFiles.firstOrNull()?.name ?: return@filter false
    (cache.getMetadata(anyCachedFile).compilerFingerprint != currentCompilerFingerprint)
}
```

Rollback of an external library to an already-cached version does not change the compiler fingerprint and does not dirty the user's source IR hashes. Leftover previous IC cache is reused; linkage/runtime see the old dependency identity.

Public report (JetBrains/kotlin#6654 / KT-87194). Change a dependency to an earlier version whose cache was already built. Expected: full rebuild of dependable caches. Actual: leftover previous cache.

In-tree after the repair (not on failing_ref): `dependenciesFingerprint` is stored and compared; mismatch forces a full rebuild. Caches without metadata (older than 2.2.20) also rebuild.

Case A — same external deps, same compiler, source unchanged:
  cache identity is current
  not leftover-after-rollback

Case B — external dep rolled back to already-cached version, leftover IC:
  leftover: previous per-file cache built against the newer dep
  dependencies fingerprint omitted
  compiler fingerprint still matches

Case C — `clean` / missing cache directory:
  fresh cache
  not leftover previous dep

Case D — dependenciesFingerprint compared (post-repair shape, not on failing_ref):
  full rebuild after rollback
  not leftover previous cache

The developer wants to know which identity case B actually used for the IC'ed library after the rollback: leftover previous-cache (deps fingerprint omitted), current dep graph, or omitted (no cache).

# OBSERVED

Public JetBrains/kotlin#6654 (merged 2026-07-14). Squash `0a61a56593a0d6270e6e5f66d0fd31c2209429ed` (parent `a05299825cbf5d5e19df97bd7f8ec00a98716871`). Local kotlin-native was not performed on this lab host.

PR title: Incremental compilation: fixed stale external caches problem. There was no check if an external library was changed (only existence of its cache). Rollback to an already-cached version reused leftover IC.

On failing_ref, stale detection compared `compilerFingerprint` only. `CacheMetadata` had no `dependenciesFingerprint`. Dirty-file analysis compared source IR hashes.

Not this packet: specimen-104 gradle incremental. specimen-075 rust incremental leftover. specimen-103 go work-sync leftover replace.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref a05299825cbf5d5e19df97bd7f8ec00a98716871
# kotlin-native/.../CacheBuilder.kt staleCompilerCacheLibraries
# kotlin-native/.../CacheSerializationSupport.kt CacheMetadata

# public shape:
# leftover Native IC cache after external dep rollback
# metadata stores compiler fingerprint; deps fingerprint omitted
# clean / miss writes a new cache
```

Source-backed only. Do not execute untrusted checkouts on the host.

JetBrains/kotlin
  kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CacheBuilder.kt
  kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/serialization/CacheSerializationSupport.kt
  kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CachedLibraries.kt

RELEVANT MATERIAL

### CacheBuilder_failing.kt

// Reduced excerpt of stale cache detection on failing_ref
// kotlin-native/.../CacheBuilder.kt
// only compilerFingerprint is compared.

val currentCompilerFingerprint = config.distribution.compilerFingerprint
val staleCompilerCacheLibraries = icedLibraries.filter { library ->
    val cache = caches[library] as? CachedLibraries.Cache.PerFile ?: return@filter false
    val anyCachedFile = File(cache.path).listFiles.firstOrNull()?.name ?: return@filter false
    (cache.getMetadata(anyCachedFile).compilerFingerprint != currentCompilerFingerprint)
}

### CacheMetadata_failing.kt

// Reduced excerpt of CacheMetadata on failing_ref
// kotlin-native/.../CacheSerializationSupport.kt
// a05299825cbf5d5e19df97bd7f8ec00a98716871
// dependenciesFingerprint omitted.

class CacheMetadata(
    val target: KonanTarget,
    val compilerFingerprint: String,
    val runtimeFingerprint: String?,
)

### leftover_identity_split.txt

Registry / fixture:
  Kotlin/Native CacheBuilder / CacheMetadata
  leftover IC cache after external dep rollback

Case A (same deps, same compiler, source unchanged):
  current cache identity
  not leftover-after-rollback

Case B (dep rolled back to already-cached version, leftover IC):
  leftover: previous per-file cache built against the newer dep
  dependencies fingerprint omitted

Case C (clean / missing cache directory):
  fresh cache
  not leftover previous dep

Case D (dependenciesFingerprint compared):
  full rebuild after rollback
  not leftover previous cache

Not this packet:
  gradle incremental (specimen-104)
  rust incremental leftover (specimen-075)
  go work-sync leftover replace (specimen-103)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
