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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
