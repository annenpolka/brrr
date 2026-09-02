ACCEPT_R1

contrastiveness: high (first filename store vs leftover stale AST on second body vs content-keyed miss vs different path)
reproducibility: source-backed PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — filename identity and patch-content identity are different objects; leftover AST crashed the second render
ecosystem: typescript / coder diffs
mechanism_family: leftover-highlight-cache, omitted-content-key, filename-default

Packet is the failing world only. Do not assume a root cause.
