ACCEPT_R1

contrastiveness: high (parent git db vs nested submodule checkout-only vs two parents sharing submodule URL vs already-at-head skip)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — git/db ident is the cache identity; checkout is a copy; submodule used a third path
ecosystem: rust / cargo / git
mechanism_family: git-submodule-db-cache, leftover-checkout-only-submodule

Packet is the failing world only. Do not assume a root cause.
