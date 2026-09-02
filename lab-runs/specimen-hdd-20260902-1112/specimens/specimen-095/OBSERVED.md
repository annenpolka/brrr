# OBSERVED

Public npm/cli#5850 (lukekarrys, 2022-11-12) / PR 8089. Failing world: npm@8.19.2 and later 9.x/10.x reports; pinned checkout `e345cc58ecad0e1e18eefc00638d7fa32966c2b7` (merge parent of the squash).

Issue reproduction (nested override only honored on a cold first install):

```
# package.json as in TASK (json-server ^0.17.0, nested package-json 7.0.0)
npm install                         # 0 vulnerabilities
npm install                         # 5 vulnerabilities
npm update                          # 0 vulnerabilities
rm -rf node_modules && npm install  # 5 vulnerabilities
rm package-lock.json && npm install # 5 vulnerabilities
rm -rf node_modules package-lock.json && npm install  # 0 vulnerabilities
```

Expected after every `npm install` while the nested override remains in package.json: lockfile identity of `package-json` stays `7.0.0`; audit stays at 0.

Saw: only the empty-store first install and `npm update` apply the nested rule. Any later `npm install` that can read the existing lockfile or `node_modules` returns the original `package-json` identity. Collaborator note (bnbdr): the same tree with a **top-level** `"package-json": "7.0.0"` override does apply on subsequent installs.

In-tree leftover on the failing revision (`workspaces/arborist/lib/node.js` `addEdgeIn`):

```
  addEdgeIn (edge) {
    if (edge.overrides) {
      this.overrides = edge.overrides
    }

    this.edgesIn.add(edge)
    ...
  }
```

That assignment overwrites `this.overrides` with the incoming edge's set. It does not walk `this.edgesOut`. `get overridden` is `!!(this.overrides && this.overrides.value && this.overrides.name === this.name)` — a leftover set still reports overridden.

`Edge.reload` / `detach` on the failing revision (`workspaces/arborist/lib/edge.js`):

```
    if (newTo !== this.#to) {
      if (this.#to) {
        this.#to.edgesIn.delete(this)
      }
      ...
    }
...
  detach () {
    ...
    if (this.#to) {
      this.#to.edgesIn.delete(this)
    }
    this.#from.edgesOut.delete(this.#name)
    ...
  }
```

`edgesIn.delete` does not recompute the target's OverrideSet from remaining incoming edges. After the override-carrying edge is gone, the leftover set on the node and its out-edges is unchanged.

Parent attach on the failing revision still copies `parent.overrides.getNodeRule(this)` onto the child when a parent is set. That is a different copy path from the incoming-edge leftover.

PR 8089 later added `workspaces/arborist/test/node.js` cases `updateOverridesEdgeInRemoved uses findSpecificOverrideSet for multiple edgesIn` and `should propagate the new override set to the target node`. Those names are not on the failing revision.

This packet is not optional-peer packument fetch of unmet peers (npm/cli#9876), not bun.lock leftover `packages` vs `optionalPeers` mention after `bun remove`, and not leftover overridden versions after deleting the `overrides` field from package.json (#8986, still open).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
