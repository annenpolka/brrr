# Reduced excerpt of Defaults.analysisStore + zinc staticCachedStore on failing_ref
# sbt main/src/main/scala/sbt/Defaults.scala
# c491f035f832a62843d69364b55237dc29c99e7d
# Last-write Analysis identity is the cache. File size/mtime are omitted.

  private inline def analysisStore(inline analysisFile: TaskKey[File]): AnalysisStore =
    MixedAnalyzingCompiler.staticCachedStore(
      analysisFile = analysisFile.value.toPath,
      useTextAnalysis = false,
    )

# zinc MixedAnalyzingCompiler.scala two-arg overload (cacheLast = true):

  def staticCachedStore(analysisFile: Path, useTextAnalysis: Boolean): AnalysisStore =
    staticCachedStore(
      analysisFile = analysisFile,
      useTextAnalysis = useTextAnalysis,
      useConsistent = false,
      cacheLast = true,
      mappers = ReadWriteMappers.getEmptyMappers(),
      reproducible = true,
      parallelism = Runtime.getRuntime.availableProcessors(),
    )

    val store1 =
      if cacheLast then AnalysisStore.getCachedStore(fileStore)
      else fileStore
    staticCache(analysisFile, AnalysisStore.getThreadSafeStore(store1))
