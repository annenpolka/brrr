KNOWN FIX (sealed): spack/spack PR 51931 merge 525775aa9b3e9500f661508456902c7634c23655.

failing_ref is parent 194e0da658190ae0219bd9576bd7ce1099ce1e0b.

Concretization cache stored fully-finalized specs and omitted re-running _finalize_concretization on cache hit, so leftover dag_hash after package.py change stayed current.

PR repair: store immediately after solve, before finalization; re-run post_process_concretization_result on cache hits.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
