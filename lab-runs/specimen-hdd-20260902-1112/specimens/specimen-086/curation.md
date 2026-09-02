ACCEPT_R1

contrastiveness: high (two Fedora rustc 1.82 at same path and clamped mtime vs rustup-env arm that also hashes toolchain mtime vs cache disabled; fingerprint equal/reuse vs unequal/new cache vs no cache)
reproducibility: source-backed PR + pinned bors parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — compiler identity for .rustc_info.json is filesystem path+mtime of the rustc binary, not rustc -vV; a cache hit never re-reads the Fedora suffix that later appears in E0514
ecosystem: rust / cargo
mechanism_family: rustc-fingerprint-metadata, compiler-identity, clamped-mtime

Packet is the failing world only. Do not assume a root cause.
