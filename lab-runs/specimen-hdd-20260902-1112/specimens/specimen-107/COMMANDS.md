```
# not executed on this lab host
# failing_ref 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
# src/_pytest/cacheprovider.py Cache.set / Cache.mkdir / _ensure_supporting_files

# public shape:
# Cache.mkdir or interrupted Cache.set leaves .pytest_cache existing
# later Cache.set: cache_dir_exists_already True
# leftover: .gitignore / CACHEDIR.TAG omitted
```

Source-backed only. Do not execute untrusted checkouts on the host.
