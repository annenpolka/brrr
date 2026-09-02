ACCEPT_R1

contrastiveness: high (pip 25.0.1 PASS vs 25.3 FAIL; empty user value vs missing key vs non-empty)
reproducibility: source-backed issue + PR + pinned SHAs; local run not claimed
information density: high
safety: public OSS
nontriviality: high — empty is not the same as unset, and layering changed after filename variants
ecosystem: python
mechanism_family: env-empty-vs-unset, config-precedence

Packet is the failing world only. Do not assume a root cause.
