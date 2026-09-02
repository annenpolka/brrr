ACCEPT_R1

contrastiveness: high (same-deps current vs leftover after rollback vs clean vs fingerprint-compared)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — existence of old cache JOINs previous dep identity; two greps cannot replace
ecosystem: kotlin-native / incremental cache
mechanism_family: leftover-native-ic-cache, omitted-dependencies-fingerprint, external-dep-rollback

Packet is the failing world only. Do not assume a root cause.
