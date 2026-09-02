CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public spack/spack#51553 (closed 2026-06-16). PR 51931 merge `525775aa9b3e9500f661508456902c7634c23655` (parent `194e0da658190ae0219bd9576bd7ce1099ce1e0b`). Local spack was not performed on this lab host.

Issue body: concretizer cache returns previous bzip2 hash after package.py install() comment; disabling the cache yields a new hash.

On failing_ref, cache stores the Result after the solve and later finalizes hashes into that object. Cache hits reuse leftover finalized hashes. PR 51931 moves the store before finalization and re-runs post-processing on hits.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-140 rush leftover downstream phase vs operation graph.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 194e0da658190ae0219bd9576bd7ce1099ce1e0b
# lib/spack/spack/solver/asp.py PyclingoDriver cache store / _make_cache_key

# public shape:
# leftover concretizer cache after package.py change
# fully-finalized spec hashes stored; re-finalization omitted on hit
# spack spec -l bzip2 keeps previous dag_hash until cache off
```

Source-backed only. Do not execute untrusted checkouts on the host.

spack/spack
  lib/spack/spack/solver/asp.py
  repos/spack_repo/builtin/packages/bzip2/package.py

RELEVANT MATERIAL

### asp_cache_failing.py

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

### leftover_identity_split.txt

Registry / fixture:
  concretizer:concretization_cache enable
  leftover spec hash after package.py change

Case A (second spack spec, same package.py):
  current cache identity
  not leftover-after-package-change

Case B (package.py flipped, leftover cache):
  leftover: previous dag_hash / fully-finalized spec
  package-hash recompute omitted on cache hit
  same mo2ogtq

Case C (cache disabled / spack clean -m):
  fresh hash identity
  not leftover previous spec

Case D (store before finalization, re-finalize on hit):
  new hash after package.py change
  not leftover previous dag_hash

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  rush leftover downstream phase cache (specimen-140)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
