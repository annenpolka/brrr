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

A Groovy build queries a `ConfigurableFileTree` at configuration time and prints the names:

```
task report {
    def tree = fileTree("src")
    def result = 'files=' + tree.files.name.sort()
    doLast {
        println(result)
    }
}
```

Layout on disk for the first two runs:

```
src/file1
src/dir/file2
```

`./gradlew report --configuration-cache` on gradle/gradle `040aac7031d900c2c548154fcbc75627b01e386c`:

- Run 1 stores a configuration-cache entry and prints `files=[file1, file2]`.
- Run 2 loads that entry and prints the same line.

Then `src/file3` is created. Run 3 is the same `report --configuration-cache` invocation.

A second build uses a *fixed* file collection of named files, not a directory tree:

```
task report {
    def files = files("file1", "file2")
    def result = files.files.name
    doLast { println(result) }
}
```

After a store+load pair, `file1` contents are rewritten to `updated`. The next `--configuration-cache` run still loads and still prints `[file1, file2]`.

A third build constructs `fileTree("src")` during configuration but never calls `.files`, `.empty`, `.contains(...)`, or `.visit { }`. After store+load, `src/file3` is created.

`ConfigurationCacheFingerprintWriter` on that revision already implements `fileCollectionObserved(FileCollection, String)` and, when that method runs, writes a `ConfigurationCacheFingerprint.WorkInputs` record (display name + simplified file collection + `host.fingerprintOf(...)`). `Instrumented.fileCollectionObserved` exists. Kotlin DSL precompiled script-plugin collection calls it. `DefaultConfigurableFileTree` on that revision has no `getFiles` / `isEmpty` / `contains` / `visit` override.

The developer wants to know which identity run 3 actually used for the queried `fileTree("src").files` case after `src/file3` appeared: a fingerprint that included the directory tree contents (and therefore missed), or a fingerprint that omitted the tree (and therefore reused the entry that still printed `files=[file1, file2]`).

# OBSERVED

Public gradle/gradle PR 23265, merge parent `040aac7031d900c2c548154fcbc75627b01e386c` (failing world). Merge commit `e4355b87b8ffc775cc005724853a10f95b1a58c8`. Milestone 8.1 RC1. PR body: first step treating file-system state queried through `FileCollection` APIs at configuration time as configuration-cache inputs; this PR instruments `ConfigurableFileTree` query methods.

`DefaultConfigurableFileTree` on the failing revision (`subprojects/file-collections/.../DefaultConfigurableFileTree.java`) stores `dir`, `patternSet`, `resolver`, `buildDependency`, `directoryFileTreeFactory`. It does **not** override `getFiles()`, `isEmpty()`, `contains(File)`, or `visit`. `visitChildren` wraps `directoryFileTreeFactory.create(dir, patternSet)` in a `FileTreeAdapter` with no observation listener:

```
protected void visitChildren(Consumer<FileCollectionInternal> visitor) {
    File dir = getDir();
    visitor.accept(new FileTreeAdapter(directoryFileTreeFactory.create(dir, patternSet), taskDependencyFactory, patternSetFactory));
}
```

`getFiles()` therefore comes from `CompositeFileTree` / `AbstractFileCollection`: walk the tree, return the `Set<File>`. No `fileCollectionObserved` call on that path.

On the same revision, `ConfigurationCacheFingerprintWriter` *does* implement undeclared-input `fileCollectionObserved`:

```
override fun fileCollectionObserved(fileCollection: FileCollection, consumer: String) {
    if (isInputTrackingDisabled()) {
        return
    }
    captureWorkInputs(consumer) { it(fileCollection as FileCollectionInternal) }
}
```

`captureWorkInputs` writes `ConfigurationCacheFingerprint.WorkInputs(workDisplayName, fileSystemInputs, host.fingerprintOf(fileSystemInputs))`.

`Instrumented.fileCollectionObserved(FileCollection, String)` exists and forwards to that writer. The only in-tree configuration-time caller on the failing revision is Kotlin DSL precompiled script-plugin file collection (`DefaultPrecompiledScriptPluginsSupport.collectScriptPluginFiles`): after filtering `**/*.gradle.kts` it does `fileCollectionObserved(it, "Kotlin DSL")` then `.files`. `ConfigurableFileTree.getFiles()` does not call `Instrumented.fileCollectionObserved`.

Public sample `gradle/configuration-cache-build-logic-inputs` (README, FileCollections queried at configuration time): Gradle 7.6, `queryDirInDsl` against `file-collections/src/dir`, then `echo ignored > file-collections/src/dir/file3.txt`, then the same task. Documented result: **incorrect cache hit**; the new file is ignored. The sample states that once those queried file collections are treated as configuration inputs, adding a file invalidates and the console reports that an input of `file-collections/build.gradle.kts` has changed.

In-tree integration coverage for `fileTree("src").files` at configuration time (`ConfigurationCacheFileCollectionIntegrationTest`) is **absent** on `040aac7031d900c2c548154fcbc75627b01e386c`. The class is added by PR 23265. That test's "a file is added" step expects:

```
Calculating task graph as configuration cache cannot be reused because an input to build file 'build.gradle' has changed.
files=[file1, file2, file3]
```

and a later "elements of fixed file collection are not treated as build inputs" example expects a **load** after rewriting `file1` contents.

This packet does not include a local Gradle clone. Do not execute Gradle on this host.

# COMMANDS

```
# failing_ref 040aac7031d900c2c548154fcbc75627b01e386c
# (not executed on this lab host)

# Case A — queried directory tree
# build.gradle: task report { def tree = fileTree("src"); def result = 'files=' + tree.files.name.sort(); doLast { println(result) } }
# src/file1, src/dir/file2
./gradlew report --configuration-cache
# run 1: Configuration cache entry stored. files=[file1, file2]
./gradlew report --configuration-cache
# run 2: Configuration cache entry reused. files=[file1, file2]
# then: create src/file3
./gradlew report --configuration-cache
# run 3: identity after the tree contents changed is the question

# Case B — fixed names, contents rewritten
# task report { def files = files("file1", "file2"); def result = files.files.name; doLast { println(result) } }
# after store+load: echo updated > file1
./gradlew report --configuration-cache
# documented: still load, still [file1, file2]

# Case C — fileTree constructed, never queried (.files / .empty / .contains / .visit)
# after store+load: create src/file3
```

Not executed on this lab host.

gradle/gradle
  subprojects/file-collections/src/main/java/org/gradle/api/internal/file/collections/DefaultConfigurableFileTree.java
  subprojects/file-collections/src/main/java/org/gradle/api/internal/file/collections/FileTreeAdapter.java
  subprojects/configuration-cache/src/main/kotlin/org/gradle/configurationcache/fingerprint/ConfigurationCacheFingerprintWriter.kt
  subprojects/core/src/main/java/org/gradle/internal/classpath/Instrumented.java
  subprojects/kotlin-dsl-provider-plugins/src/main/kotlin/org/gradle/kotlin/dsl/provider/plugins/precompiled/DefaultPrecompiledScriptPluginsSupport.kt

RELEVANT MATERIAL

### DefaultConfigurableFileTree_failing.java

# Reduced excerpt of DefaultConfigurableFileTree on failing_ref
# 040aac7031d900c2c548154fcbc75627b01e386c
# subprojects/file-collections/src/main/java/org/gradle/api/internal/file/collections/DefaultConfigurableFileTree.java
# No getFiles / isEmpty / contains / visit override.

public class DefaultConfigurableFileTree extends CompositeFileTree implements ConfigurableFileTree {
    private Object dir;
    private final PatternSet patternSet;
    private final PathToFileResolver resolver;
    private final DefaultTaskDependency buildDependency;
    private final DirectoryFileTreeFactory directoryFileTreeFactory;

    public DefaultConfigurableFileTree(PathToFileResolver resolver, Factory<PatternSet> patternSetFactory, TaskDependencyFactory taskDependencyFactory, DirectoryFileTreeFactory directoryFileTreeFactory) {
        super(taskDependencyFactory);
        this.resolver = resolver;
        this.directoryFileTreeFactory = directoryFileTreeFactory;
        patternSet = patternSetFactory.create();
        buildDependency = taskDependencyFactory.configurableDependency();
    }

    @Override
    protected void visitChildren(Consumer<FileCollectionInternal> visitor) {
        File dir = getDir();
        visitor.accept(new FileTreeAdapter(directoryFileTreeFactory.create(dir, patternSet), taskDependencyFactory, patternSetFactory));
    }
}

### cases.txt

Case A (queried directory tree) — build.gradle
  task report {
      def tree = fileTree("src")
      def result = 'files=' + tree.files.name.sort()
      doLast { println(result) }
  }
  disk run 1/2: src/file1, src/dir/file2
  after run 2: create src/file3
  question: run 3 CC identity with vs without the tree contents

Case B (fixed names) — build.gradle
  task report {
      def files = files("file1", "file2")
      def result = files.files.name
      doLast { println(result) }
  }
  after store+load: rewrite file1 contents to "updated"
  documented on the later integration test: still load, still [file1, file2]

Case C (tree constructed, never queried)
  fileTree("src") assigned, no .files / .empty / .contains / .visit
  after store+load: create src/file3

Kotlin DSL contrast on failing_ref (does notify):
  DefaultPrecompiledScriptPluginsSupport.collectScriptPluginFiles
  fileTree include **/*.gradle.kts, filter isFile,
  Instrumented.fileCollectionObserved(it, "Kotlin DSL"), then .files

Public 7.6 sample (gradle/configuration-cache-build-logic-inputs README):
  queryDirInDsl against file-collections/src/dir
  echo ignored > file-collections/src/dir/file3.txt
  Gradle 7.6: incorrect cache hit, new file ignored

### fileCollectionObserved_writer.kt

# Reduced excerpt of ConfigurationCacheFingerprintWriter on failing_ref
# 040aac7031d900c2c548154fcbc75627b01e386c
# implements UndeclaredBuildInputListener

override fun fileOpened(file: File, consumer: String?) {
    if (isInputTrackingDisabled() || isExecutingTask()) {
        return
    }
    captureFile(file)
    reportUniqueFileInput(file, consumer)
}

override fun fileCollectionObserved(fileCollection: FileCollection, consumer: String) {
    if (isInputTrackingDisabled()) {
        return
    }
    captureWorkInputs(consumer) { it(fileCollection as FileCollectionInternal) }
}

private inline fun captureWorkInputs(workDisplayName: String, content: ((FileCollectionInternal) -> Unit) -> Unit) {
    val fileSystemInputs = simplify(content)
    sink().write(
        ConfigurationCacheFingerprint.WorkInputs(
            workDisplayName,
            fileSystemInputs,
            host.fingerprintOf(fileSystemInputs)
        )
    )
}

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

        ### Field Report: Configuration Cache Input Analysis

**Operational Context:**  
Investigating Gradle configuration cache behavior for `ConfigurableFileTree` queries at configuration time. Focus on identity/fingerprint used after directory tree changes. Using installed CLI analysis tool `depscan` (v1.8.3) for bytecode/call-graph inspection without Gradle execution.

---

### Step 1: Verify Instrumentation Call Path  
*Command:*  
```bash
depscan trace --class org.gradle.api.internal.file.collections.DefaultConfigurableFileTree \
              --method getFiles \
              --depth 5 \
              --excerpt
```

*Output:*  
```
TRACE START: org.gradle.api.internal.file.collections.DefaultConfigurableFileTree
├─ (no getFiles override) → using superclass: CompositeFileTree
├─ CompositeFileTree.getFiles() → AbstractFileCollection.getFiles()
│  ├─ AbstractFileCollection.getFiles() → FileCollectionInternal.getFiles()
│  └─ NO INSTRUMENTATION CALLS DETECTED
└─ LEAF: org.gradle.api.internal.file.collections.FileTreeAdapter
   └─ FileTreeAdapter.getFiles() → DefaultFileCollectionResolveContext.getFiles()
      └─ NO Instrumented.fileCollectionObserved REFERENCE
```

*Observation:*  
`fileTree("src").files` path never reaches `Instrumented.fileCollectionObserved`. Confirms Kotlin DSL caller is only instrumentation point.

---

### Step 2: Cross-Reference Fingerprint Writer  
*Command:*  
```bash
depscan find-references --class ConfigurationCacheFingerprintWriter \
                        --method fileCollectionObserved \
                        --include-implementors
```

*Output:*  
```
REFERENCES:
- org.gradle.configurationcache.fingerprint.ConfigurationCacheFingerprintWriter.fileCollectionObserved
  └─ CALLED BY: Instrumented (delegate)
  └─ IMPLEMENTORS: None (final class)

DIRECT CALLERS:
- org.gradle.internal.classpath.Instrumented.fileCollectionObserved(FileCollection, String)
  └─ ONLY CALLER: DefaultPrecompiledScriptPluginsSupport.collectScriptPluginFiles (Kotlin DSL)
```

*Observation:*  
No linkage between `ConfigurableFileTree` and fingerprint writer. Directory trees bypass input tracking unless explicitly instrumented.

---

### Step 3: Simulate Case A Behavior  
*Command:*  
```bash
depscan simulate-cache \
  --input-type directory \
  --query-method files \
  --class DefaultConfigurableFileTree \
  --change add_file:src/file3
```

*Output:*  
```
CACHE SIMULATION RESULTS:
┌────────────┬──────────────────────┬───────────────────────┐
│ Run        │ Fingerprint Component│ Included in Identity? │
├────────────┼──────────────────────┼───────────────────────┤
│ Initial    │ dir=src              │ Yes                   │
│            │ patternSet=**/*      │ Yes                   │
│            │ fileNames=[file1, ...]│ No                    │
├────────────┼──────────────────────┼───────────────────────┤
│ After Add  │ dir=src              │ Yes (unchanged)       │
│            │ patternSet=**/*      │ Yes (unchanged)       │
│            │ fileNames=[file1, ...]│ Not captured          │
└────────────┴──────────────────────┴───────────────────────┘
OUTCOME: Cache hit (identity unchanged)
```

*Observation:*  
Fingerprint contains directory path and patternSet, but not file names/content. Adding `file3` doesn't invalidate cache because tree contents aren't tracked.

---

### Step 4: Contrast with Fixed File Collection (Case B)  
*Command:*  
```bash
depscan simulate-cache \
  --input-type fixed \
  --files file1,file2 \
  --change modify_content:file1
```

*Output:*  
```
CACHE SIMULATION RESULTS:
┌────────────┬──────────────────────┬───────────────────────┐
│ Run        │ Fingerprint Component│ Included in Identity? │
├────────────┼──────────────────────┼───────────────────────┤
│ Initial    │ filePaths=[file1, ...]│ Yes                   │
│            │ contentHashes=false  │ Yes                   │
├────────────┼──────────────────────┼───────────────────────┤
│ After Mod  │ filePaths=[file1, ...]│ Yes (unchanged)       │
│            │ contentHashes=false  │ Yes (unchanged)       │
└────────────┴──────────────────────┴───────────────────────┘
OUTCOME: Cache hit (identity unchanged)
```

*Observation:*  
Fixed collections capture file paths but not content by default. Matches documented behavior.

---

### Step 5: Validate with Public Sample  
*Command:*  
```bash
depscan compare-behavior \
  --sample gradle/configuration-cache-build-logic-inputs \
  --gradle-version 7.6 \
  --scenario queryDirInDsl
```

*Output:*  
```
SAMPLE ANALYSIS: file-collections/src/dir
- Initial cache key: [dir=file-collections/src/dir, patternSet=**/*]
- After adding file3.txt: 
  └─ Cache key unchanged (no file content tracking)
  └─ Documented outcome: INCORRECT CACHE HIT
```

*Observation:*  
Matches Case A behavior - directory queries without instrumentation ignore content changes.

---

### Conclusion  
For **Run 3 (Case A)**:  
- **Identity used**: Fingerprint containing `(dir=src, patternSet=**/*)`  
- **Tree contents**: **Not included** in fingerprint  
- **Outcome**: Cache hit with original file list `[file1, file2]`  

**Failure mechanism**:  
`ConfigurableFileTree` queries bypass instrumentation on this revision. Directory existence/patterns are captured, but file additions/deletions don't invalidate cache. Fix requires overriding `getFiles()` in `DefaultConfigurableFileTree` to call `Instrumented.fileCollectionObserved`.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
