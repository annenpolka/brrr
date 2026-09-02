# OBSERVED

Public spack/spack#51553 (closed 2026-06-16). PR 51931 merge `525775aa9b3e9500f661508456902c7634c23655` (parent `194e0da658190ae0219bd9576bd7ce1099ce1e0b`). Local spack was not performed on this lab host.

Issue body: concretizer cache returns previous bzip2 hash after package.py install() comment; disabling the cache yields a new hash.

On failing_ref, cache stores the Result after the solve and later finalizes hashes into that object. Cache hits reuse leftover finalized hashes. PR 51931 moves the store before finalization and re-runs post-processing on hits.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-140 rush leftover downstream phase vs operation graph.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
