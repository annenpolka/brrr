# Host 実機 pytest#14613

Not Dreamer-facing. HOLD feature. No View.

Requested env `PYTEST_CACHE_DIR_BASE` does not exist.
`-o cache_dir=DIR` with cacheprovider enabled on pytest 9.1.1 writes separate cache trees (`CACHEDIR.TAG`) per project. `-p no:cacheprovider` makes `cache_dir` an unknown option.

`os.environ.get("PYTEST_CACHE_DIR_BASE")` is None on this host.
`pytest --help` documents ini `cache_dir` and `-o cache_dir=cache` (8.4.1 and 9.1.1). It does **not** mention `PYTEST_CACHE_DIR_BASE`.

pytest 9.0.1 `-o cache_dir=...` on `p1`: rc=0; writes `v/cache/nodeids` (no top-level `CACHEDIR.TAG` in this tree).
pytest 9.0.3/9.1.0 `-o cache_dir` on `p1`: rc=0.

Existing `-o cache_dir` is not the requested env. No View/export.

Leftover `-p no:cacheprovider -o cache_dir=...`: 8.4.1 **2 passed**; pytest 9 **2 passed, 1 warning** `Unknown config option: cache_dir`. Leftover cacheprovider on `-o cache_dir`: 2 passed 8.4.1–9.1.1. Unknown-option is a warning, not rc=4, when cacheprovider is off.

Leftover `--setup-show -o cache_dir=... p1 p2` (cacheprovider on): **2 passed** on 8.4.1–9.1.1. `--setup-show` does not change per-project caches. No View.

Leftover `--cache-show -o cache_dir=/tmp/hdd-20260909-1730-cache-14613-show p1`: rc=0, `cache is empty`, no tests ran, 8.4.1–9.1.1. `--cache-show` does not execute tests so it does not write per-project nodeids. No View.

Leftover run `p1` then `--cache-show -o cache_dir=...`: `--cache-show` lists `cache/nodeids` `['p1/test_a.py::test_a']` on 8.4.1–9.1.1. Show-after-run writes nodeids; show-without-run was empty. No View.
