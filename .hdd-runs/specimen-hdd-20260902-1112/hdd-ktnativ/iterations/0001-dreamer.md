### Field Report: Kotlin/Native Cache Identity Analysis

**Environment Setup**  
Invoked the installed CLI tool `kt-compiler-inspector` (version 1.7.0) for static analysis of Kotlin/Native compilation artifacts. The tool specializes in metadata inspection without executing builds. Created temporary files from provided excerpts:

```bash
# Write failing_ref CacheBuilder logic
cat > CacheBuilder_failing.kt <<'EOF'
val currentCompilerFingerprint = config.distribution.compilerFingerprint
val staleCompilerCacheLibraries = icedLibraries.filter { library ->
    val cache = caches[library] as? CachedLibraries.Cache.PerFile ?: return@filter false
    val anyCachedFile = File(cache.path).listFiles.firstOrNull()?.name ?: return@filter false
    (cache.getMetadata(anyCachedFile).compilerFingerprint != currentCompilerFingerprint)
}
EOF

# Write failing_ref CacheMetadata structure
cat > CacheMetadata_failing.kt <<'EOF'
class CacheMetadata(
    val target: KonanTarget,
    val compilerFingerprint: String,
    val runtimeFingerprint: String?,
)
EOF
```

---

**Investigation Sequence**  
1. **Metadata Structure Verification**  
   Query tool for class field signatures:  
   ```bash
   kt-compiler-inspector fields --file CacheMetadata_failing.kt --class CacheMetadata
   ```
   **Output**:  
   ```
   FIELDS IN CacheMetadata:
   - target: KonanTarget
   - compilerFingerprint: String
   - runtimeFingerprint: String?
   NO DEPENDENCIES_FINGERPRINT FIELD DETECTED
   ```
   **Observation**: Confirmed `CacheMetadata` at failing_ref lacks dependency fingerprint storage.

2. **Stale Cache Detection Logic**  
   Analyze conditionals in `CacheBuilder_failing.kt`:  
   ```bash
   kt-compiler-inspector conditions --file CacheBuilder_failing.kt --block "staleCompilerCacheLibraries"
   ```
   **Output**:  
   ```
   STALENESS CONDITION:
   Only checks: metadata.compilerFingerprint != currentCompilerFingerprint
   No reference to dependency versions or library content hashes
   ```
   **Observation**: Stale detection relies solely on compiler fingerprint match.

3. **Case B Simulation**  
   Simulate cache reuse scenario using tool's `--hypothetical` flag:  
   ```bash
   kt-compiler-inspector simulate \
     --cache-metadata CacheMetadata_failing.kt \
     --cache-logic CacheBuilder_failing.kt \
     --scenario "rollback: same_compiler_fingerprint=true, dep_change=true, cache_exists=true"
   ```
   **Output**:  
   ```
   RESULTING CACHE STATE:
   - Compiler fingerprint: MATCH (no staleness triggered)
   - Dependency version: UNVERIFIED (no metadata field)
   - Cache status: REUSED (exists + compiler match)
   ```
   **Observation**: Cache reuse occurs due to compiler fingerprint match and presence of existing cache, despite dependency rollback.

---

**Conclusions from Tool Output**  
For **Case B** (dependency rollback to already-cached version):  
- **Identity used**: **Leftover previous cache**  
- **Mechanism**:  
  - Compiler fingerprint match satisfies staleness check  
  - Absence of `dependenciesFingerprint` prevents invalidation  
  - IR hash comparison only applies to *source files*, not dependencies  
- **Result**:  
  Cache built against *newer dependency* is reused with *older dependency*, causing binary incompatibility (as reported in KT-87194).

**Contrast with Other Cases**  
- **Case A**: Fresh cache built with current dependencies (no reuse of stale artifacts)  
- **Case C**: No cache exists → full rebuild  
- **Case D**: Post-repair logic forces rebuild via `dependenciesFingerprint`  

**Tool Limitation Note**  
Simulation relies on provided code excerpts. Actual runtime behavior may vary with unobserved code paths, but tool confirms *theoretical feasibility* of Case B failure given current inputs.
