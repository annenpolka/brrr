ACCEPT_R1

contrastiveness: high (unchanged world vs leftover cache after new LXC vs cache off vs persist-on-refresh)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — inventory file path and remote host-set are different identities; leftover jsonfile stayed current
ecosystem: ansible / proxmox inventory cache
mechanism_family: leftover-inventory-cache, cache-keyed-by-file-path, refresh-omits-cache-persist

Packet is the failing world only. Do not assume a root cause.
