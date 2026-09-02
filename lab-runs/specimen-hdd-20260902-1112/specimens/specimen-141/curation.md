ACCEPT_R1

contrastiveness: high (unchanged package.py vs leftover cache after edit vs cache off vs re-finalize on hit)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — ASP problem key and package.py hash are different identities; leftover finalized hashes stayed current
ecosystem: spack / concretizer cache
mechanism_family: leftover-concretizer-cache, omitted-package-hash-recompute, post-finalization-store

Packet is the failing world only. Do not assume a root cause.
