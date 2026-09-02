ACCEPT_R1

contrastiveness: high (unchanged plugin vs leftover cache after upgrade vs wipe vs meta in identity)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — plugin identity and serialized config identity are different objects; name@version omitted so leftover cache stayed current
ecosystem: eslint / js lint cache
mechanism_family: leftover-eslint-cache, omitted-plugin-meta, flat-config-serialization

Packet is the failing world only. Do not assume a root cause.
