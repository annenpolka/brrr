ACCEPT_R1

contrastiveness: high (unchanged rustfmt.toml vs leftover cache after flip vs clear-cache vs resolved config hashed)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — raw dprint.jsonc plugin map and plugin-resolved cache_key are different identities; cacheKeyFiles contents omitted so leftover cache stayed current
ecosystem: dprint / incremental cache
mechanism_family: leftover-incremental-cache, omitted-resolved-plugin-config, cachekeyfiles-hash-omitted

Packet is the failing world only. Do not assume a root cause.
