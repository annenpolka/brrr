ACCEPT_R1

contrastiveness: high (clean CARGO_HOME one path vs `..` two spellings of one git checkout vs true two-directory same-name clash vs local path dep with no git checkout; git PackageId vs PathBuf identity; GitSource fingerprint is oid)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — git+https SourceId is one object; RecursivePathSource still keys discovery on unsmoothed PathBuf; nested path= already collapsed
ecosystem: rust / cargo
mechanism_family: git-https-path-identity, cargo-home-dotdot, duplicate-package-warning

Packet is the failing world only. Do not assume a root cause.
