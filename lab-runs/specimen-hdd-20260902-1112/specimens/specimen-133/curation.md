ACCEPT_R1

contrastiveness: high (unchanged file config vs leftover cache after flip vs wipe vs resolved-config hash)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — CLI config object and cosmiconfig-resolved file config are different identities; empty {} hash omitted the file so leftover cache stayed current
ecosystem: stylelint / css lint cache
mechanism_family: leftover-stylelint-cache, omitted-resolved-config, hashed-empty-cli-config

Packet is the failing world only. Do not assume a root cause.
