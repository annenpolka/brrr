ACCEPT_R1

contrastiveness: high (same lock file, different missing inputs each run; exit 0; done set keyed by pointer to a bind copy)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — dedup looks correct if you think &node is the lock-graph node; it is the address of a temporary
ecosystem: nix
mechanism_family: pointer-identity, bind-temporary, silent-skip

Packet is the failing world only. Do not assume a root cause.
