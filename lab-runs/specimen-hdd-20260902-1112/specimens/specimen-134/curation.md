ACCEPT_R1

contrastiveness: high (unchanged .env vs leftover cache after flip vs wipe vs gitignored file hashed)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — env var values and env-file identity are different objects; gitignore skip omitted .env so leftover cache stayed current
ecosystem: moon / task cache
mechanism_family: leftover-task-cache, omitted-env-file-input, gitignored-hash-skip

Packet is the failing world only. Do not assume a root cause.
