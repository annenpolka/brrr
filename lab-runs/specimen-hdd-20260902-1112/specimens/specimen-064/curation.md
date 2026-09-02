ACCEPT_R1

contrastiveness: high (same rev, two narHashes; warning names master; lock record gains a ref field)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — a fully pinned git revision still consults HEAD, then a guessed branch name changes the hashed tree
ecosystem: nix
mechanism_family: detached-HEAD, ref-fallback, identity-vs-rev

Packet is the failing world only. Do not assume a root cause.
