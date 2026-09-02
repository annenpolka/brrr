ACCEPT_R1

contrastiveness: high (single-project stale lock vs sibling leftover pin vs prune already-true vs shared lock path)
reproducibility: source-backed PR + pinned parent/merge + e2e added by the PR; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — lock pin and install identity are different tables; upgrade keep-set used resolve-without-lock globally
ecosystem: mise / lockfile
mechanism_family: leftover-lock-pin, tracked-config, upgrade-cleanup

Packet is the failing world only. Do not assume a root cause.
