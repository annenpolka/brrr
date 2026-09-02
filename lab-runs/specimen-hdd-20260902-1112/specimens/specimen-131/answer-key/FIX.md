KNOWN FIX (sealed): ninja-build/ninja PR 2680 merge 88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68.

failing_ref is merge first parent 77d328f5f679bfef14b1f67f3cd431b729bc786f.

RecomputeNodeDirty loaded leftover deps-log before dirty was known; LoadDepsFromLog omitted dirty/command identity.

PR repair: only load depsfile if the producing edge is not dirty; RecomputeOutputsDirtyCache follow-up after deps load.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
