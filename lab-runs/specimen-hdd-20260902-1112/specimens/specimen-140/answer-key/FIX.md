KNOWN FIX (sealed): microsoft/rushstack PR 4476 merge 3530cb21a03927ec8b06072ee89a91466dc6beb3.

failing_ref is parent 300fcd107dea176ef503ffa073776bff47ee17a1.

_getCacheIdAsync walked npm dependencyProjects and omitted the runtime operation graph, so leftover downstream phase cache after upstream CLI/env/file change stayed current.

PR repair: compute cache hashes in CacheableOperationPlugin beforeExecuteOperations from the operation graph.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
