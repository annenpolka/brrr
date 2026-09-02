# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public gradle/gradle#30052 (closed 2025-03-03). PR 32359 (alllex) merge `2f46ab737e15c67d3904602fa66c658258c32b66` (parents `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3` + `fa0e3417532e782cc892fcc6cbbf180fb5780038`). Milestone 8.14 RC1. Local Gradle execution was not performed on this lab host.

PR body: CC does not store the base directory for some file collection types. After load, a relative file is resolved against the leftover root-directory-of-the-build because CC injects the file collection factory service with that base. Named `ConfigurableFileCollection` / `ProviderBackedFileCollection` and `ConfigurableFileTree` can still accept relative paths at execution time.

On failing_ref, `ConfigurableFileCollectionCodec`:

```
encodePreservingIdentityOf(value) {
    codec.run { encodeContents(value) }
    writeBoolean(value.isFinalizing)
}
...
val fileCollection = fileCollectionFactory.configurableFiles()
fileCollection.from(contents)
```

No `write(value.resolver)`. `ProviderBackedFileCollectionSpec` is `val provider: ProviderInternal<*>` only. Decode: `is ProviderBackedFileCollectionSpec -> element.provider`.

`RelativePathFilesIntegrationTest` is **absent** on `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3`. The class is added by PR 32359.

Not this packet: specimen-088 (ConfigurableFileTree `.files` query omitted from CC fingerprint / Honor-KILL treeid). specimen-076 (unused system-property snapshot). specimen-042 (script class compiler HashMap race). specimen-051 (nested ValueSource deadlock).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
# ConfigurableFileCollectionCodec.kt encode/decode
# FileCollectionCodec.kt ProviderBackedFileCollectionSpec
# RelativePathFilesIntegrationTest.groovy (on the PR, not failing_ref)

# public shape (named files, relative provider, subproject):
# project.files(provider { "someFile.txt" })
# store: .../subproject/someFile.txt
# failing load: .../root/someFile.txt
```

Source-backed only. Do not execute untrusted checkouts on the host.

gradle/gradle
  platforms/core-configuration/core-serialization-codecs/src/main/kotlin/org/gradle/internal/serialize/codecs/core/ConfigurableFileCollectionCodec.kt
  platforms/core-configuration/core-serialization-codecs/src/main/kotlin/org/gradle/internal/serialize/codecs/core/FileCollectionCodec.kt
  platforms/core-configuration/file-collections/src/integTest/groovy/org/gradle/api/file/RelativePathFilesIntegrationTest.groovy

RELEVANT MATERIAL

### ConfigurableFileCollectionCodec_failing.kt

// Reduced excerpt of ConfigurableFileCollectionCodec on failing_ref
// 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
// Named collection contents are stored. Resolver / base directory is not.

    override suspend fun WriteContext.encode(value: ConfigurableFileCollection) {
        require(value is DefaultConfigurableFileCollection)
        encodePreservingIdentityOf(value) {
            codec.run {
                encodeContents(value)
            }
            writeBoolean(value.isFinalizing)
        }
    }

    override suspend fun ReadContext.decode(): ConfigurableFileCollection {
        return decodePreservingIdentity { id ->
            val contents = codec.run { decodeContents() }
            val fileCollection = fileCollectionFactory.configurableFiles()
            fileCollection.from(contents)
            if (readBoolean()) {
                fileCollection.finalizeValue()
            }
            isolate.identities.putInstance(id, fileCollection)
            fileCollection
        }
    }

### ProviderBackedFileCollectionSpec_failing.kt

// Reduced excerpt of FileCollectionCodec on failing_ref
// Provider-backed named collection stores the provider only.
// Decode uses leftover isolate fileCollectionFactory (root base dir).

private
class ProviderBackedFileCollectionSpec(val provider: ProviderInternal<*>)

                    is ProviderBackedFileCollectionSpec -> element.provider

            is ProviderBackedFileCollection -> {
                val provider = fileCollection.provider
                if (provider !is TaskProvider<*>) {
                    elements.add(ProviderBackedFileCollectionSpec(provider))
                    false
                } else {
                    true
                }
            }

### leftover_identity_split.txt

Registry / fixture:
  include("sub")
  named collection: project.files(provider { "someFile.txt" })
  CC store then load

Case A (absolute named files):
  path identity unchanged
  no leftover base dir

Case B (named provider relative in :sub, CC load):
  store: .../sub/someFile.txt
  failing_ref load: .../root/someFile.txt
  leftover: root-directory resolver omitted from the collection identity

Case C (fileTree("src").files queried, then src/file3):
  not this leftover (specimen-088 omitted WorkInputs)

Case D (named files("file1","file2"), rewrite file1 bytes):
  names stay; contents not this leftover axis

Not this packet:
  ConfigurableFileTree query observation omitted (specimen-088)
  unused system-property snapshot (specimen-076)
  script class compiler race (specimen-042)

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
