ACCEPT_R1

contrastiveness: high (parent write {path,hash} vs 223b9b2 write hash-only vs 223b9b2 read of leftover object vs omitted; not CRLF byte-hash #4961; not merger drop #8366; not bun leftover packages; not 085 yaml fixture; not 086 cargo rustc fingerprint)
reproducibility: source-backed PR + pinned format-change and migrate commits; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — writer and type dropped path, reader still spread leftover objects; tests only cover fresh writes
ecosystem: pnpm / node
mechanism_family: leftover-path-field, patchedDependencies-hash-only, lockfile-format-migrate

Packet is the failing world only. Do not assume a root cause.
