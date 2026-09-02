ACCEPT_R1

contrastiveness: high (unchanged HEAD vs leftover process cache after amend/commit vs cache dir deleted vs PER_SESSION)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — uncacheable enclosing rule and memoized child process are different identities; git hash omitted so leftover setuptools_scm stdout stayed current
ecosystem: pants / vcs_version process cache
mechanism_family: leftover-process-cache, omitted-git-hash-identity, vcs-version-setuptools-scm

Packet is the failing world only. Do not assume a root cause.
