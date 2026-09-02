# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
