ACCEPT_R1

contrastiveness: high (same checksum vs leftover tarball after republish vs rm cache vs mismatch refetch)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — package-version path and registry checksum are different identities; leftover tarball stayed current
ecosystem: hex / tarball cache
mechanism_family: leftover-tarball-cache, omitted-checksum-mismatch-refetch, package-version-path-identity

Packet is the failing world only. Do not assume a root cause.
