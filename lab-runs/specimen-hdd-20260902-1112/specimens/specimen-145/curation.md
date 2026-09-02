ACCEPT_R1

contrastiveness: high (unchanged source vs leftover dest after ref/files change vs cache wipe vs copy-manifest Clean)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — cache-path identity and source version/query are different; leftover previous copy stayed current
ecosystem: terragrunt / source cache
mechanism_family: leftover-source-copy, omitted-ref-from-cache-path, no-copy-manifest

Packet is the failing world only. Do not assume a root cause.
