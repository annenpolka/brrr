# OBSERVED

Public pytest-dev/pytest#12167 (closed 2024-04-06). PR 12168 (tamird) merge `5acc3f86ac1713aea6775f04dcae35a2f0848437` (parents `4e3dd21506a9e543c04c63ebff966a9b604d2b9e` + `2e65f4e3ac81dd5e294839441262b8b112ba18bd`). Local pytest was not performed on this lab host.

Issue body: PR 3982's supporting-file write is gated on the cache directory not already existing. An interrupted cache write can leave `.pytest_cache` non-empty without `.gitignore`. The exists-already check then never creates `.gitignore`.

On failing_ref, `Cache.set` uses `path.parent.is_dir()` / `_cachedir.exists()` as the initialized-dir identity. `Cache.mkdir` does not call `_ensure_supporting_files`. `_ensure_supporting_files` is the only writer of `.gitignore` / `CACHEDIR.TAG` / `README.md`.

Atomic tempdir+rename of supporting files is **not** on the failing revision. It is added by PR 12168 (`_ensure_cache_dir_and_supporting_files`).

Not this packet: specimen-001 (assertion display evaluation order). specimen-002 (collection-identity / config-scope). specimen-003 (object-identity / fixture-closure). specimen-055 (derived rootdir collect). specimen-094 (vitest cache key). pytest#5702 / #3968 / #10002 / #14935 remain open (no merged fixed_ref).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
