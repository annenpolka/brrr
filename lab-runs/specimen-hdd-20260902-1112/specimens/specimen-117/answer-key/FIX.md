KNOWN FIX (sealed): sbt/sbt PR 9207 merge 49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef.

failing_ref is merge first parent c491f035f832a62843d69364b55237dc29c99e7d.

analysisStore used MixedAnalyzingCompiler.staticCachedStore two-arg overload (cacheLast=true). Zinc getCachedStore kept leftover extra Analysis identity after sbt 2.x switched the gz under the same path.

PR repair: BuildDef.cachedAnalysisStore keys caffeine cache on VirtualFileRef + lastModified + sizeBytes; zinc staticCachedStore(..., cacheLast=false). previousCompile / compileTask / early analysis all go through that store.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
