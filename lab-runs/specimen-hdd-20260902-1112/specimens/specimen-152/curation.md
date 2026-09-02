ACCEPT_R1

contrastiveness: high (unchanged snapshot vs leftover facts after URL upgrade vs empty facts vs URL in key)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — dist/component/arch and snapshot URL are different identities; leftover facts stayed current
ecosystem: bazel-distroless / apt facts cache
mechanism_family: leftover-apt-facts, omitted-snapshot-url-from-fact-key, stale-packages-after-snapshot-upgrade

Packet is the failing world only. Do not assume a root cause.
