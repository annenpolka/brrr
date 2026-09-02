KNOWN FIX (sealed): pytest-dev/pytest PR 12168 merge 5acc3f86ac1713aea6775f04dcae35a2f0848437.

failing_ref is merge first parent 4e3dd21506a9e543c04c63ebff966a9b604d2b9e.

Cache.set treated leftover directory existence as initialized-cache identity and skipped supporting files. mkdir never wrote them.

PR repair: _ensure_cache_dir_and_supporting_files builds README/.gitignore/CACHEDIR.TAG in a TemporaryDirectory then rename onto _cachedir; early-return only if _cachedir.is_dir(); mkdir and set both go through _mkdir.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
