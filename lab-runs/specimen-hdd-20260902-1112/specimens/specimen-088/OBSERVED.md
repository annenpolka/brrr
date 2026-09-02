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
