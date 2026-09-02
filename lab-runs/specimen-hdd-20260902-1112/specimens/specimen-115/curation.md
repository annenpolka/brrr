ACCEPT_R1

contrastiveness: high (first foo checksum vs leftover foo reused as bar vs non-wildcard unique vs delete checksum)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — template-name identity and MATCH instantiation identity are different objects; leftover checksum blocked bar
ecosystem: go / task
mechanism_family: leftover-fingerprint, omitted-wildcard, checksum-key

Packet is the failing world only. Do not assume a root cause.
