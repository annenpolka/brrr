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
