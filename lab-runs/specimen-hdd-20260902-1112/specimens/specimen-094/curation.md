ACCEPT_R1

contrastiveness: high (inlined H_inlined used vs ordinary-external leftover H_ext unused vs data:/client/network omitted vs glob bail-null vs cache-off omitted)
reproducibility: source-backed PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two externalize paths disagree; leftover memory identity names a path that was never written; file bytes still hashed though shouldExternalize is not a key input
ecosystem: vitest / vite-node / fs-module-cache
mechanism_family: leftover-cache-key, externalize-after-hash, fs-module-cache-identity

Packet is the failing world only. Do not assume a root cause.
