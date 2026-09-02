ACCEPT_R1

contrastiveness: high (never-moved current cache vs leftover cache after move+restore vs clean vs deleted-on-remove)
reproducibility: source-backed issue+PR + pinned parent/rebase-merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — same-name restored source and leftover cache JOIN; two greps cannot replace
ecosystem: gleam / compile cache
mechanism_family: leftover-compile-cache, same-name-module-after-move, cache-vs-source-identity

Packet is the failing world only. Do not assume a root cause.
