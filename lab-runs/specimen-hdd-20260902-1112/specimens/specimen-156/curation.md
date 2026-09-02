ACCEPT_R1

contrastiveness: high (same define vs leftover substitution after define change vs empty cache vs define_hash in key)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — source bytes and define table are different identities; leftover substituted JS stayed current
ecosystem: bun / runtime transpiler cache
mechanism_family: leftover-transpiler-cache, omitted-define-from-features-hash, bunfig-define-stale-output

Packet is the failing world only. Do not assume a root cause.
