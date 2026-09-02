ACCEPT_R1

contrastiveness: high (incremental false clean vs leftover stale error vs first compile vs delete tsbuildinfo)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — d.ts text identity and d.ts diagnostic identity are different objects; leftover text-hash blocked importer recheck
ecosystem: typescript / incremental builder
mechanism_family: leftover-tsbuildinfo, omitted-dts-diagnostics, stale-error-identity

Packet is the failing world only. Do not assume a root cause.
