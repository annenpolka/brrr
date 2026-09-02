ACCEPT_R1

contrastiveness: high (unchanged inputs vs leftover Found Remotely after edit vs cache off vs digest-equal found)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — input hash and remote tag are different identities; leftover tag digest stayed current
ecosystem: skaffold / artifact cache
mechanism_family: leftover-remote-artifact, omitted-digest-compare, tag-reuse-cache-hit

Packet is the failing world only. Do not assume a root cause.
