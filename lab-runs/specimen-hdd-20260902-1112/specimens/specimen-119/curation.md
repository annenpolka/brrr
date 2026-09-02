ACCEPT_R1

contrastiveness: high (first A.txt cache vs leftover env+name reused as B.txt vs differently named task unique vs delete cache)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — computation_hash already includes file hashes; leftover identity is the *filename* omitting args
ecosystem: pixi / rust
mechanism_family: leftover-cache-filename, omitted-task-arguments

Packet is the failing world only. Do not assume a root cause.
