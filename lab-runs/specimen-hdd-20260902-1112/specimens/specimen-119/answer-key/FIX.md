KNOWN FIX (sealed): prefix-dev/pixi PR 3782 squash 804d2360157ca9c3d9197a4519ea803d28220e59.

failing_ref is squash parent 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05.

Cache filename was run-environment + task-name. Two parametrized invocations of the same task shared leftover cache identity; the second overwrote the first.

PR repair: TaskHash::task_args_hash hashes rendered inputs/outputs (not glob expansion). cache_name takes Optional NameHash and formats env-name-<args-hash>.json. can_skip/save_cache use that name. Old cache files are not found (breaking cache-key change).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
