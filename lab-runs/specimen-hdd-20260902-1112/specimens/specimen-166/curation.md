ACCEPT_R1

contrastiveness: high (still-open current vs leftover parse after close vs never-opened vs db_remove_file)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — path-keyed parse JOINs previous close; two greps cannot replace
ecosystem: biome / LSP workspace db
mechanism_family: leftover-parsed-source, omitted-close-eviction, workspace-db-file-map

Packet is the failing world only. Do not assume a root cause.
