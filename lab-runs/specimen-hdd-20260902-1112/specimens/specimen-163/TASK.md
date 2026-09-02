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
