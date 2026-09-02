ACCEPT_R1

contrastiveness: high (keepGitDir false same-key identical trees vs keepGitDir true SHA-only leftover vs SHA identifier with no named ref vs two different commits)
reproducibility: source-backed PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — pin (commit) and cache key are different objects; keep-git-dir snapshot identity included .git bytes that name refs the key omitted
ecosystem: go / buildkit / git source
mechanism_family: omitted-ref-from-cache-key, keep-git-dir-snapshot, two-refs-one-sha

Packet is the failing world only. Do not assume a root cause.
