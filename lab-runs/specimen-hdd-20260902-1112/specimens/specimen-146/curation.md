ACCEPT_R1

contrastiveness: high (unchanged file vs leftover key after rotation vs new process vs mtime in memoize key)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — file path and on-disk key material are different identities; leftover memoize object stayed current
ecosystem: salt / crypt RSA cache
mechanism_family: leftover-rsa-key, omitted-mtime-from-memoize-key, process-cache-after-rotation

Packet is the failing world only. Do not assume a root cause.
