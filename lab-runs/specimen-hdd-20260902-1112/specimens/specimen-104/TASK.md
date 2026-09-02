# TASK

A **named** `FileCollection` of relative paths (not a directory `fileTree`) can keep the identity of the **root project's base directory** after configuration-cache load, even when the collection was created in a subproject.

Public report (gradle/gradle#30052, subproject `build.gradle.kts`):

```
val files = project.files(provider { "someFile.txt" })
println("config phase:")
files.forEach { println(it) }
doLast {
    println("execution phase:")
    files.forEach { println(it) }
}
```

With configuration cache, config phase prints `.../subproject/someFile.txt`. Execution phase after load prints `.../root/someFile.txt`.

On failing_ref `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3`, `ConfigurableFileCollectionCodec.decode` rebuilds with `fileCollectionFactory.configurableFiles()` and does **not** encode `PathToFileResolver`. `ProviderBackedFileCollectionSpec` stores only the `ProviderInternal`. Decode maps that spec to `element.provider` and `fileCollectionFactory.resolving(...)` using the CC isolate factory whose leftover base directory is the root of the build.

In-tree after the repair (not on failing_ref): `RelativePathFilesIntegrationTest` `"provider-backed relative files are resolved relative to their owner"`. Subproject task:

```
incoming.from(project.files(provider { "subFile.txt" }))
incoming.from(project(":other").isolated.projectDirectory.files(provider { "otherFile.txt" }))
incoming.from(layout.settingsDirectory.files(provider { "settingsFile.txt" }))
```

Expected files: `sub/subFile.txt`, `other/otherFile.txt`, `settingsFile.txt`.

Case A — named `files("/abs/sub/someFile.txt")` (already absolute):
  load path equals store path
  no leftover base directory

Case B — named `project.files(provider { "someFile.txt" })` in `:sub` under configuration cache:
  store (config) resolves against `:sub`
  failing_ref load (execution) resolves against leftover root directory
  leftover identity: root-dir FileCollection vs subproject FileCollection

Case C — `fileTree("src").files` queried at configuration time, then `src/file3` is added:
  not this leftover (that is specimen-088 omitted WorkInputs fingerprint)

Case D — named `files("file1", "file2")` then rewrite `file1` contents:
  names stay `[file1, file2]`; contents are not this leftover axis
  same named-files contrast used in specimen-088 case B, not a leftover root dir

The developer wants to know which identity case B actually stored for the named collection after CC load: leftover root-directory resolver (so `root/someFile.txt`), the creating project's resolver (`sub/someFile.txt`), or omitted (no collection restored).
