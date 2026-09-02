ACCEPT_R1

contrastiveness: high (hoisted uninstall drops shim vs linked leftover dangling shim vs first install vs wipe+reinstall)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — store/top-level link identity and .bin shim identity are different objects; linked diff never saw the leftover shim
ecosystem: npm / arborist linked
mechanism_family: leftover-bin-shim, linked-strategy, omitted-dot-sweep

Packet is the failing world only. Do not assume a root cause.
