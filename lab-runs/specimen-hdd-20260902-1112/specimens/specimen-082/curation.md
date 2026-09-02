ACCEPT_R1

contrastiveness: high (never-installed optional peer vs leftover after add/remove vs still-reachable via hard dep; bun.lock packages identity vs optionalPeers metadata substring; bun remove vs package.json edit + bun install)
reproducibility: source-backed PR + pinned squash parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — optional-peer resolution slots are skipped on fresh enqueue but carried through lockfile clone once hoist has filled them
ecosystem: bun / node
mechanism_family: optional-peer-leftover, lockfile-resolution-slot, clone-carries-optional-peer

Packet is the failing world only. Do not assume a root cause.
