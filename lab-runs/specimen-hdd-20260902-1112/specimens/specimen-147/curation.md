ACCEPT_R1

contrastiveness: high (unchanged file vs leftover fingerprint after rewrite vs cache bypass vs full mtime key)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — inode/size/truncated-mtime and file bytes are different identities; leftover sha256 stayed current
ecosystem: aws-cdk / asset fingerprint cache
mechanism_family: leftover-fingerprint, truncated-mtime-cache-key, large-file-fingerprint-cache

Packet is the failing world only. Do not assume a root cause.
