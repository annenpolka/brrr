ACCEPT_R1

contrastiveness: high (first matching deps vs leftover deps-log after flip vs wipe .ninja_deps vs mtime-stale reject)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — current command identity and leftover deps-log identity are different objects; leftover edges caused cycle
ecosystem: ninja / deps-log
mechanism_family: leftover-deps-log, omitted-dirty, previous-depfile-identity

Packet is the failing world only. Do not assume a root cause.
