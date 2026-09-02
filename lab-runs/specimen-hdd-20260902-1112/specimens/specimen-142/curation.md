ACCEPT_R1

contrastiveness: high (no flush vs leftover inventory after --flush-cache vs delete cache dir vs cache=False)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — facts flush and inventory cache are different identities; leftover inventory stayed current
ecosystem: ansible / inventory cache
mechanism_family: leftover-inventory-cache, omitted-flush-inventory, facts-only-flush

Packet is the failing world only. Do not assume a root cause.
