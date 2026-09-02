ACCEPT_R1

contrastiveness: high (never-built YN0007 vs leftover already-built skip vs yarn-remove prune of locators that left the tree; storedBuildState hash vs PnP packageLocation vs missing unplugged files; path-string hash vs content)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two stores disagree after unplugged remove; buildHash ignores folder contents; yarn remove of the package is a different prune
ecosystem: yarn / node / PnP
mechanism_family: leftover-build-state, unplugged-folder-remove, pnp-packageLocation-path-hash

Packet is the failing world only. Do not assume a root cause.
