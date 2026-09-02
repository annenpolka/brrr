ACCEPT_R1

contrastiveness: high (pytest 6 vs 7; rerun attempts vs later sibling method)
reproducibility: source-backed public issue + PR + pinned SHAs; local run not claimed
information density: high
safety: public OSS, no secrets, no network-only flake
nontriviality: high — fixture teardown prints on every attempt, yet `self` state accumulates
ecosystem: python
mechanism_family: leaked-instance-state, flaky-reruns

Packet is the failing world only. Do not assume a root cause.
