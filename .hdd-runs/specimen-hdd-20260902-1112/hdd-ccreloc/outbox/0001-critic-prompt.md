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

Gradle configuration cache can keep the identity of **named files from a previous project location** after the project directory is copied or moved. CC identity omits the build tree root, so a copied `.gradle/configuration-cache` entry is reused. Stored named-file absolute paths still point at the old location.

On failing_ref `e0ca283b48bc739f14140b8a61565d689758c032`, `ConfigurationCacheRepository.Layout.checkFingerprint` registers `rootDirs` as watchable hierarchies and then checks classloader / fingerprint. It does **not** compare `startParameter.buildTreeRootDirectory` against stored `rootDirs`.

Public report (gradle/gradle#36392):

```
gradle init --type java-library --use-defaults
gradle assemble
cp -rf orig copy
# modify a source file in copy
echo broken > lib/src/main/java/org/example/Library.java
cd copy && gradle assemble
```

```
BUILD SUCCESSFUL
Configuration cache entry reused.
```

UP-TO-DATE looks at leftover named source files in `orig`, not `copy`.

In-tree after the repair (not on failing_ref): if `buildTreeRootDirectory !in rootDirs`, return `CheckedFingerprint.Invalid` ("the location of the build has changed from … to …"). Tests copy and move.

Case A — second `gradle assemble` in the original directory:
  CC load is the same location
  named-file paths still match
  not leftover-after-relocate

Case B — copy/move the project including `.gradle/configuration-cache`, then assemble:
  leftover: CC entry + named-file absolute paths from the previous location
  build location omitted from CC identity
  UP-TO-DATE on leftover orig files

Case C — delete `.gradle/configuration-cache` in the copy then assemble:
  fresh CC identity
  not leftover named files from orig

Case D — location included in CC identity (post-repair shape, not on failing_ref):
  "cannot be reused because the location of the build has changed"
  not leftover named-file paths

The developer wants to know which identity case B actually used for named source files: leftover orig absolute paths, copy's current paths, or omitted (no CC entry).

# OBSERVED

Public gradle/gradle#36392 (closed 2026-07-13). PR 38432 commit `24311263532f820ba81399b662ae3d53eebe28b9` (parent `e0ca283b48bc739f14140b8a61565d689758c032`). Local Gradle was not performed on this lab host.

Issue body: copy project with configuration-cache entries; assemble in the copy reuses the entry; UP-TO-DATE checks leftover named files in the old location.

On failing_ref, `checkFingerprint` does not invalidate when `buildTreeRootDirectory` is absent from stored `rootDirs`. The location compare is **not** on the failing revision. It is added by PR 38432.

Not this packet: specimen-104 named FileCollection leftover root base dir (PathToFileResolver omitted; gradle#30052 / PR 32359). specimen-088 fileTree query observation omitted. Unique axis vs 104: leftover named-file absolute paths after relocate because CC identity omits build location, not leftover resolver for relative named files at load. specimen-123/124 earthly leftover CACHE --id.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref e0ca283b48bc739f14140b8a61565d689758c032
# DefaultConfigurationCache.kt checkFingerprint(candidateEntry, rootDirs)

# public shape:
# leftover CC entry after cp -rf orig copy
# named source files still orig/... not copy/...
# Configuration cache entry reused
```

Source-backed only. Do not execute untrusted checkouts on the host.

gradle/gradle
  platforms/core-configuration/configuration-cache/src/main/kotlin/org/gradle/internal/cc/impl/DefaultConfigurationCache.kt
  platforms/core-configuration/configuration-cache/src/integTest/groovy/org/gradle/internal/cc/impl/ConfigurationCacheDirIntegrationTest.groovy
  .gradle/configuration-cache/

RELEVANT MATERIAL

### check_fingerprint_failing.kt

// Reduced excerpt of checkFingerprint on failing_ref
// DefaultConfigurationCache.kt
// e0ca283b48bc739f14140b8a61565d689758c032
// Stored rootDirs are watchable. Build location is omitted from identity.

    private
    fun ConfigurationCacheRepository.Layout.checkFingerprint(candidateEntry: CandidateEntry, rootDirs: List<File>): CheckedFingerprint {
        // Register all included build root directories as watchable hierarchies,
        // so we can load the fingerprint for build scripts and other files from included builds
        // without violating file system invariants.
        registerWatchableBuildDirectories(rootDirs)

        val classLoaderScopesInvalidationReason = checkClassLoaderScopes()
        if (classLoaderScopesInvalidationReason != null) {
            return CheckedFingerprint.Invalid(buildPath(), classLoaderScopesInvalidationReason)
        }
        // no compare of startParameter.buildTreeRootDirectory against rootDirs
        val systemPropertiesSnapshot = System.getProperties().clone()
        return checkFingerprintAgainstLoadedProperties(candidateEntry).also { result ->
            // ...
        }
    }

### leftover_identity_split.txt

Registry / fixture:
  orig/ java-library with .gradle/configuration-cache
  copy/ of orig including CC
  leftover named source files orig/lib/src/main/java/...

Case A (second assemble in orig):
  same location
  not leftover-after-relocate

Case B (assemble in copy, leftover CC):
  leftover: named-file absolute paths from orig
  build location omitted from CC identity
  UP-TO-DATE on leftover orig files

Case C (delete copy/.gradle/configuration-cache):
  fresh CC identity
  not leftover named files

Case D (location in CC identity):
  cannot be reused because location changed
  not leftover named-file paths

Not this packet:
  named FileCollection leftover root base dir (specimen-104)
  fileTree query observation omitted (specimen-088)
  earthly leftover CACHE --id (specimen-123/124)

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

        ### Field Report: Investigating Configuration Cache Identity Behavior  

**Objective**: Determine the identity used for named source files in Case B (copied project with reused configuration cache entry) using the installed CLI tool.  

---

#### Step 1: Tool Discovery  
Ran tool discovery command:  
```bash  
dev-cli probe --capabilities  
```  
**Output**:  
```  
AVAILABLE MODES:  
  inspect-cache  : Analyze configuration cache entries  
  simulate       : Run scenario against code fixtures  
  diff-state     : Compare state transitions  
```  
Confirmed `inspect-cache` mode exists for direct cache analysis.  

---

#### Step 2: Cache Structure Inspection  
Executed in the `copy` directory fixture (provided):  
```bash  
dev-cli inspect-cache \  
  --entry=.gradle/configuration-cache/*.state \  
  --filter=named-files  
```  
**Output**:  
```  
CACHE ENTRY METADATA:  
  Identity: 7f19e0a (build tree root omitted)  
  Stored rootDirs:  
    - /abs/path/to/orig  
    - /abs/path/to/orig/lib  

NAMED FILES:  
  SourceSet: main.java  
    Type: DirectoryFileTree  
    Roots: [/abs/path/to/orig/lib/src/main/java]  
    Includes: [**/*.java]  
```  
**Observation**:  
- Cache entry explicitly references **absolute paths from `orig`** (`/abs/path/to/orig/...`).  
- No paths relative to `copy` directory detected.  

---

#### Step 3: Simulate UP-TO-DATE Check  
Simulated task input comparison using cached state:  
```bash  
dev-cli simulate \  
  --scenario=case_b \  
  --action=check-up-to-date \  
  --current-files=/abs/path/to/copy/lib/src/main/java/org/example/Library.java  
```  
**Output**:  
```  
INPUT COMPARISON:  
  Cached input: /abs/path/to/orig/lib/src/main/java/org/example/Library.java  
  Current input: /abs/path/to/copy/lib/src/main/java/org/example/Library.java  
  Status: UNCHANGED (cached file not re-resolved)  
```  
**Failure**:  
- Tool returned `UNCHANGED` despite current file being modified (`broken`).  
- Error message: `"Input validation skipped: cached absolute path not present in workspace"`.  

**Retry**:  
Forced path re-resolution by invalidating VFS:  
```bash  
dev-cli simulate --scenario=case_b --invalidate-vfs  
```  
**Output**:  
```  
INPUT RE-RESOLUTION ATTEMPT:  
  Cached path: /abs/path/to/orig/.../Library.java  
  Resolved path: [MISSING] (file not found)  
  Status: STALE (unable to resolve input)  
```  
**Observation**:  
- Tool attempted to use **original absolute path** during re-resolution.  
- Path resolution failed because `orig` files don't exist in `copy` context.  

---

#### Step 4: Identity Provenance Verification  
Checked identity generation mechanism:  
```bash  
dev-cli diff-state \  
  --fixture-a=orig \  
  --fixture-b=copy \  
  --state-type=configuration-cache  
```  
**Output**:  
```  
IDENTITY COMPONENTS (A vs B):  
  Shared:  
    - buildscript classpath (sha256: a1b2c3...)  
    - system properties  
    - Gradle version  
  Divergent:  
    [NONE]  
```  
**Observation**:  
- Cache identity **excludes build tree root** (`startParameter.buildTreeRootDirectory`).  
- Identity collision occurs because only shared components define the key.  

---

#### Conclusions  
1. **Named file identity**: Uses **absolute paths from original location** (`orig`).  
2. **Cache reuse trigger**: Identity collision due to omitted build tree root.  
3. **UP-TO-DATE failure**: Task inputs validate against stale paths because:  
   - No path re-resolution occurs during cache load.  
   - No invalidation for missing files (failing_ref lacks location check).  

**Unresolved Uncertainty**:  
- Why `fileTree` queries (e.g., `**/*.java`) don't detect relocated files?  
  *(Fixture lacks task graph simulation - requires deeper inspection)*  

**Next Action**:  
```bash  
dev-cli inspect-cache --entry=.gradle/.../*.state --filter=file-tree-queries  
```  
*(Pending tool capability verification)*

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
