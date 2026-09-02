ACCEPT_R1

contrastiveness: high (honest in-log Lookup vs leftover extension hash vs GONOSUMDB skip vs fork ErrSecurity vs cmd/go sumdbMismatch/sumdbAbsent; signed-but-unlogged tree-note extra line vs tile-authenticated record text)
reproducibility: source-backed issue + pinned Gerrit parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — note signatures cover the tree-head extension, ParseTree ignores extra lines, checkRecord authenticates only ParseRecord text, Lookup identity scan walks a wider cache payload
ecosystem: go modules / sumdb
mechanism_family: sumdb-lookup-leftover, unauthenticated-tree-extension, go-sum-identity

Packet is the failing world only. Do not assume a root cause.
