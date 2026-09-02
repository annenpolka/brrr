ACCEPT_R1

contrastiveness: high (CSS-source change moves [contenthash] vs PNG-only change leftover H_css1 vs never-url'd omitted; module hash vs substituted url() bytes vs persisted data.url css-url; realContentHash false vs RealContentHashPlugin digest)
reproducibility: source-backed PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two leftover stores disagree after asset-only change; filename hash ignores substituted bytes; data.url spread keeps previous compile's path
ecosystem: webpack / css / asset-modules
mechanism_family: leftover-module-contenthash, css-url-asset-filename, persisted-data-url

Packet is the failing world only. Do not assume a root cause.
