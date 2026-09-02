ACCEPT_R1

contrastiveness: high (unset defaults vs leftover cwd after :: vs empty string vs trailing-colon append vs EINVAL)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — unset, empty, trailing colon, and empty :: component are different identities; leftover cwd stayed a search path
ecosystem: systemd / path-lookup
mechanism_family: leftover-empty-vs-unset, empty-path-component-as-cwd, search-path-identity

Packet is the failing world only. Do not assume a root cause.
