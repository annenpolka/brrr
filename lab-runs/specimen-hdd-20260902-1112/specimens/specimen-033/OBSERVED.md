# OBSERVED

npm/cli#9876, npm 11.15.0, Node v24.15.0.

Current behavior: empty cache, `npm install vite` into an empty project installs 10 packages but fetches full packuments for optional peers that do not appear in the install.

```
1. mkdir repro && cd repro && npm init -y
2. npm install vite --cache ./.cache
3. grep -rl playwright .cache/_cacache/index-v5
4. the cache contains a 16.6MB playwright packument (and many others) for packages that were never installed
```

Expected (reporter): nothing fetched unless something else in the tree actually installs the package.

`Arborist.#loadPeerSet` at this revision:

```javascript
    const peerEdges = [...node.edgesOut.values()]
      // we typically only install non-optional peers, but we have to
      // factor them into the peerSet so that we can avoid conflicts
      .filter(e => e.peer && !(e.valid && e.to))
      .sort(({ name: a }, { name: b }) => localeCompare(a, b))

    for (const edge of peerEdges) {
      ...
      if (!edge.to) {
        if (!parentEdge) {
          // easy, just put the thing there
          await this.#nodeFromEdge(edge, node.parent, null, required)
          continue
```

`edge.peer` is true for both required peers and `peerOptional`. Unmet edges with no parent edge still call `#nodeFromEdge`, which loads a packument.

Reporter's before/after counts on the later PR (for orientation of scale, not as a local measurement here): registry requests 86 → 54; cached registry data ~121MB → ~72MB.
