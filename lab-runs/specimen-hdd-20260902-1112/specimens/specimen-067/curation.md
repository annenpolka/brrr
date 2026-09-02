ACCEPT_R1

contrastiveness: high (str|Unknown vs str|sentinel; ALIAS rejected as Sentinel; enum members already keep class identity)
reproducibility: source-backed issue + PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — a sentinel's only identity is the attached literal, and generic substitution throws that literal away
ecosystem: python / mypy
mechanism_family: identity-loss, generic-substitution, sentinel-literal

Packet is the failing world only. Do not assume a root cause.
