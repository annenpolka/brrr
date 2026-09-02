```
# not executed on this lab host
# failing_ref c77093e228ff21a93638b42356aa0a4d2713aa17
# src/black/files.py find_project_root @lru_cache

# public shape:
# leftover project root after black --code from a different CWD
# cache key omits resolved CWD when srcs is empty
# wrong pyproject.toml [tool.black]
```

Source-backed only. Do not execute untrusted checkouts on the host.
