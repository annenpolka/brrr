ACCEPT_R1

contrastiveness: high (first CACHE vs leftover mount after ARG change vs constant --id vs wipe cache)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — unexpanded ARG token identity and expanded ARG value identity are different objects; leftover mount blocked cache
ecosystem: earthly / buildkit cache mounts
mechanism_family: leftover-cache-id, omitted-expanded-arg, unexpanded-token

Packet is the failing world only. Do not assume a root cause.
