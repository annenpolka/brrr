# TASK

pytest's cache directory can keep the identity of an **already-initialized cache dir** after a write that only created the directory, even when the supporting files that mark that identity (`.gitignore`, `CACHEDIR.TAG`, `README.md`) were never written.

On failing_ref `4e3dd21506a9e543c04c63ebff966a9b604d2b9e`, `Cache.set` (`src/_pytest/cacheprovider.py`) decides whether to call `_ensure_supporting_files` with:

```
if path.parent.is_dir():
    cache_dir_exists_already = True
else:
    cache_dir_exists_already = self._cachedir.exists()
    path.parent.mkdir(exist_ok=True, parents=True)
if not cache_dir_exists_already:
    self._ensure_supporting_files()
```

`Cache.mkdir` creates `_cachedir/d/<name>` with `parents=True` and never calls `_ensure_supporting_files`. `_ensure_supporting_files` writes `README.md`, `.gitignore` (`# Created by pytest automatically.` plus `*`), and `CACHEDIR.TAG`.

Public report (pytest-dev/pytest#12167): the earlier check from PR 3982 is not robust. If a cache write is interrupted after the directory exists and is non-empty, `.pytest_cache` is present without `.gitignore`. Because `_cachedir.exists()` is then true, later `set` calls never write the supporting files.

Case A — first `Cache.set("cache/lastfailed", ...)` on an absent `.pytest_cache`:
  `path.parent` (`v/`) is not a dir
  `_cachedir.exists()` is false
  supporting files are written
  no leftover uninitialized dir identity

Case B — interrupt after `.pytest_cache/` (and maybe `v/`) exists, before supporting files:
  leftover: dir identity is "already initialized"
  `.gitignore` / `CACHEDIR.TAG` omitted
  later `set` sees exists() and skips `_ensure_supporting_files`

Case C — `Cache.mkdir("plugin-dump")` then `Cache.set(...)` with no interrupt:
  mkdir created `_cachedir` via `parents=True`
  set sees `_cachedir.exists()` true
  leftover: same omitted supporting-file identity as B, without a crash

Case D — `--cache-clear` then `set` on a missing dir:
  `clear_cache` removes the leftover dir
  not this leftover (fresh identity)

The developer wants to know which identity case B (and C) actually left for `.pytest_cache`: leftover "already initialized" dir (supporting files omitted), supporting-file identity present (`.gitignore` + `CACHEDIR.TAG`), or omitted (no cache dir at all).
