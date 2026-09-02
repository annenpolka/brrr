ACCEPT_R1

contrastiveness: high (consistent lock vs rev-only edit vs corrected narHash on poisoned cache vs corrected lock on fresh cache; rev fingerprint vs narHash store path)
reproducibility: source-backed issue + pinned PR base/head; local run not claimed; PR unmerged
information density: high
safety: public OSS, not executed on host
nontriviality: high — two lock fields name different objects; cache uses one, store path the other; correcting the lock does not correct the cache
ecosystem: nix / flakes / fetchers
mechanism_family: flake-lock-rev-vs-narhash, fetchToStore-cache-key, substitution-fast-path

Packet is the failing world only. Do not assume a root cause.
