# Reduced excerpt of PyclingoDriver solve cache on failing_ref
# lib/spack/spack/solver/asp.py
# 194e0da658190ae0219bd9576bd7ce1099ce1e0b
# Stores Result after clingo; later _finalize_concretization bakes hashes.
# Cache hit reuses leftover finalized hashes. package.py recompute omitted.

cache_key = self._make_cache_key(problem, control_file_paths)
result, concretization_stats = None, None
if conc_cache_enabled and self._conc_cache:
    result, concretization_stats = self._conc_cache.fetch(cache_key)
if not result:
    result = self._run_clingo(specs, setup, problem_repr, control_file_paths, timer)
    self._conc_cache.store(cache_key, result, self.control.statistics)
# later on Result specs:
#   root._finalize_concretization()
# cache hit skips that recompute
