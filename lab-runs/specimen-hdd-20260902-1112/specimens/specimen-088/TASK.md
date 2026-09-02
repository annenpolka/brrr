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
