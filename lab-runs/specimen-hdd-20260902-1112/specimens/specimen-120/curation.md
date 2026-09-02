ACCEPT_R1

contrastiveness: high (first A/B overwrite vs leftover B filename reused as A vs single-arg hit vs wipe cache)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — env+name identity and arg-instantiation identity are different objects; leftover filename blocked cache
ecosystem: pixi / conda
mechanism_family: leftover-task-cache, omitted-arguments, filename-key

Packet is the failing world only. Do not assume a root cause.
