ACCEPT_R1

contrastiveness: high (10 installed packages vs large optional-peer packument fetches; npm vs yarn/pnpm)
reproducibility: source-backed issue + PR + pinned SHAs; local run not claimed
information density: high
safety: public OSS; do not run install with host secrets
nontriviality: high — optional peers are already “not installed”, yet they still perturb resolution I/O and can change hoist shape
ecosystem: node
mechanism_family: optional-peer, install-graph

Packet is the failing world only. Do not assume a root cause.
