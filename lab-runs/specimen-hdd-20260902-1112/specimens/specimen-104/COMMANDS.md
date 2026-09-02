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
