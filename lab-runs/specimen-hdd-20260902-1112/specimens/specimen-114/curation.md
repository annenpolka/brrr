ACCEPT_R1

contrastiveness: high (clean+ignore vs leftover cache after nested change vs --no-cache vs reclean)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — nested pyproject identity and leftover cache identity are different objects; directory route miss kept ignored-F821
ecosystem: python / ruff
mechanism_family: leftover-cache, nested-config, omitted-directory-route

Packet is the failing world only. Do not assume a root cause.
