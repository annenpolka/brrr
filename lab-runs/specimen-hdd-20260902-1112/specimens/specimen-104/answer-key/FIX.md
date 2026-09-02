KNOWN FIX (sealed): gradle/gradle PR 32359 merge 2f46ab737e15c67d3904602fa66c658258c32b66.

failing_ref is merge first parent 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3.

Named ConfigurableFileCollectionCodec decoded via factory.configurableFiles() with no resolver. ProviderBackedFileCollectionSpec stored only the provider. Load resolved relative names against leftover root-directory-of-the-build.

PR repair: PathToFileResolverCodec; encode value.resolver; withResolver(resolver).configurableFiles(); ProviderBackedFileCollectionSpec(resolver, provider). RelativePathFilesIntegrationTest owner-relative named files.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
