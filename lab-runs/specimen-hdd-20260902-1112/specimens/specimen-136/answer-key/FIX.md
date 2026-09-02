KNOWN FIX (sealed): pantsbuild/pants PR 17017 merge 510f1755680d23c3d6c68815ae77ad4a4f836021.

failing_ref is parent 02fa93e2947789cf1f9f8c025e7ceaca01169ef2.

VenvPexProcess for setuptools_scm was memoized with git hash omitted from the process cache identity, so leftover generated version after amend/commit kept previous git describe even though MaybeGitWorktree made the enclosing rule uncacheable.

PR repair: import ProcessCacheScope and set cache_scope=ProcessCacheScope.PER_SESSION on that VenvPexProcess.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
