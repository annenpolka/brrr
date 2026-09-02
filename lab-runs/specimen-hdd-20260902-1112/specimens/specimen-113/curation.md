ACCEPT_R1

contrastiveness: high (cold clean vs warm introduce-error vs leftover replay after fix vs delete-tsbuildinfo)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — JSON content-hash identity and leftover diagnostic identity are different objects; fileInfos updated while semanticDiagnosticsPerFile replayed
ecosystem: typescript / incremental
mechanism_family: leftover-tsbuildinfo, omitted-shape-invalidation, json-module

Packet is the failing world only. Do not assume a root cause.
