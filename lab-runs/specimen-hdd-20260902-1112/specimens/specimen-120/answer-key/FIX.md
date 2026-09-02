KNOWN FIX (sealed): prefix-dev/pixi PR 3782 squash 804d2360157ca9c3d9197a4519ea803d28220e59.

failing_ref is squash parent 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05.

cache_name was run-environment + task-name. Two ArgValues instantiations of one task shared leftover cache file; the later hash overwrote the earlier.

PR repair: NameHash of rendered inputs/outputs is part of the filename; can_skip/save_cache call TaskHash::task_args_hash.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
