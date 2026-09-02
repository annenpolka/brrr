KNOWN FIX (sealed): gradle/gradle#38668 merge 95dc4d2b06d40a234b72d8efdf328c2d2766312a.

BuildScopeInMemoryCachingScriptClassCompiler stored compiled scripts in a plain HashMap. With configuration-cache parallel, compile() runs on DefaultBuildOperationQueue worker threads; concurrent put corrupts bins (ClassCastException Node vs TreeNode, or a cyclic tree-bin hang).

Repair: ConcurrentHashMap. Keep get-then-put rather than computeIfAbsent because getOrCompile is long-running and can re-enter script compilation.

Regression: BuildScopeInMemoryCachingScriptClassCompilerConcurrencyTest — 8 threads, 100 rounds, 128 class names engineered to share String.hashCode() so one bucket treeifies.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
