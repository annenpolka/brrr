# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
