ACCEPT_R1

contrastiveness: high (cfail1 tuple-struct Error vs cfail2 unit struct; typeck green vs type_of red; old-solver in_task read_index vs new-solver with_cached_task no read)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — first-run solver work is not an edge of typeck, so incremental reuse decodes a DefId that the second revision no longer has
ecosystem: rust / rustc
mechanism_family: query-dep-untracked, incremental-false-green, next-solver-anon-task

Packet is the failing world only. Do not assume a root cause.
