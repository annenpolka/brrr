# FIX (sealed)

Issue: https://github.com/astral-sh/uv/issues/21062
PR: https://github.com/astral-sh/uv/pull/21075
  title: Account for launcher overrides in interpreter cache keys
failing_ref: c5d8a25374a5b3c98178ebcb440c8c25f65b803e
  (reproduce + focused regression; cache key still paths-only)
fixed_ref: 405671a58e0b44ed2aa4ff734de3c206a5ce1ec9
  isolation landed in f0568414e23c3ab2c3f2ff12b1875fdd3a2447ef

Root cause: `InterpreterInfo` cache filename was
`cache_digest(&(absolute, canonical))` only. `PYTHONEXECUTABLE` and
`__PYVENV_LAUNCHER__` change the executable / virtualenv the interpreter
*reports* without changing those paths, so a query under a launcher
override reused metadata for a later query without the override.

Fix: include both env values in the digest:

```
cache_digest(&(&absolute, &canonical, &python_executable, &pyvenv_launcher))
```

After the fix, the second `uv python find` snapshot is
`[TEMP_DIR]/other/bin/python3`.
