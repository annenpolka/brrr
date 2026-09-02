# FIX (sealed)

npm/cli PR 9877 / issue 9876.

Merge commit: dc43591e6e08e9857c787116b1ed12f074e68c3c
Title: fix(arborist): don't fetch packuments for uninstallable optional peer deps

`#loadPeerSet` resolved unmet optional peer edges into the virtual root even though they would be pruned. That fetched packuments (playwright, vitest, …) and could let an optional peer win a top-level slot over a required chain.

Repair: if `edge.type === 'peerOptional'` and there is no parent edge, look at `node.parent.sourceReference.resolve(edge.name)`. Skip the fetch when nothing is currently providing it, or when the current provider already satisfies the edge. An incompatible provider still has to be resolved so the optional set nests instead of displacing required peers.

Tests added in workspaces/arborist/test/arborist/build-ideal-tree.js cover “do not fetch”, “resolved by another dependent”, and “satisfied by the actual tree”.

Do not expose this file to Dreamers, initial Red Pen, or initial Grounders.
