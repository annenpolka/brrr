KNOWN FIX (sealed): npm/cli PR 8089 squash merge b9225e524074239bd8db9a27f3e9ab72f2b5c09e.

failing_ref is squash-merge parent e345cc58ecad0e1e18eefc00638d7fa32966c2b7.

addEdgeIn assigned `this.overrides = edge.overrides` and did not walk edgesOut. Edge.detach / reload removed the incoming edge with `edgesIn.delete` and left the target OverrideSet in place, so nested override identity leaked onto later installs from the leftover lockfile / node_modules graph (public: json-server nested package-json@7.0.0 honored only on first empty-store install; subsequent npm install restored the original package-json identity and 5 audit hits).

Repair: Node.deleteEdgeIn calls updateOverridesEdgeInRemoved (recompute from remaining edgesIn, then recalculateOutEdgesOverrides). addEdgeIn / updateOverridesEdgeInAdded pick the more specific OverrideSet via OverrideSet.findSpecificOverrideSet instead of last-write. Edge.reload propagates a changed override set to the target even when `newTo === this.#to`. node.overridden now requires an incoming edge whose override value equals this.version and is not equal to edge.from.overrides. Tests added in workspaces/arborist/test/node.js cover EdgeInRemoved / EdgeInAdded / reload propagation.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
