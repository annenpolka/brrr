# TASK

Spack `concretizer:concretization_cache` can keep the identity of a **previous spec hash** after a `package.py` change should have been a different dag_hash. The cache stores fully-finalized specs (hashes baked in). On a cache hit, `_finalize_concretization` / package-hash post-processing is omitted, so leftover `mo2ogtq` is reused after commenting `install()` in bzip2.

On failing_ref `194e0da658190ae0219bd9576bd7ce1099ce1e0b`:

```
cache_key = self._make_cache_key(problem, control_file_paths)
if conc_cache_enabled and self._conc_cache:
    result, concretization_stats = self._conc_cache.fetch(cache_key)
if not result:
    result = self._run_clingo(...)
    self._conc_cache.store(cache_key, result, self.control.statistics)
# later, on the stored Result:
root._finalize_concretization()
```

`_make_cache_key` hashes ASP problem + control files. Cached `Result.to_dict()` already has concrete hashes. Cache hit skips re-finalization.

Public report (spack/spack#51553). `spack spec -l bzip2` with cache on; edit package.py; leftover previous hash until cache disabled.

In-tree after the repair (not on failing_ref): cache write immediately after solve, before finalization; cache hits re-run `post_process_concretization_result()`.

Case A — second `spack spec` with unchanged package.py:
  cache identity is current
  not leftover-after-package-change

Case B — package.py flipped, leftover concretizer cache:
  leftover: previous dag_hash / fully-finalized spec
  package-hash recompute omitted on cache hit
  same `mo2ogtq`

Case C — cache disabled / `spack clean -m`:
  fresh hash identity
  not leftover previous spec

Case D — cache stores pre-finalization, re-finalize on hit (post-repair shape, not on failing_ref):
  cache miss / new hash after package.py change
  not leftover previous dag_hash

The developer wants to know which identity case B actually used for the spec hash after the package.py change: leftover previous-finalized results (re-finalization omitted), current package identity, or omitted (no cache).
