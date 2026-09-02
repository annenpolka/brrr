ACCEPT_R1

contrastiveness: high (same CWD vs leftover root after CWD flip vs new process vs CWD in cache key)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — CWD and srcs tuple are different identities; empty srcs omitted CWD so leftover pyproject stayed current
ecosystem: black / project-root cache
mechanism_family: leftover-lru-cache, omitted-cwd-cache-key, pyproject-root-identity

Packet is the failing world only. Do not assume a root cause.
