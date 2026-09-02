ACCEPT_R1

contrastiveness: high (never-overridden original identity vs first-install 7.0.0 vs subsequent leftover original vs npm-update re-apply vs top-level override that does not leftover vs in-tree leftover OverrideSet after edge detach)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two stores (package.json nested override vs lockfile/node_modules identity) disagree after a no-op second install; leftover is the OverrideSet on the node after the carrying edge is gone, not a missing first-install
ecosystem: npm / node
mechanism_family: leftover-override-set, nested-override-lockfile-identity, edge-detach-skips-override-update

Packet is the failing world only. Do not assume a root cause.
