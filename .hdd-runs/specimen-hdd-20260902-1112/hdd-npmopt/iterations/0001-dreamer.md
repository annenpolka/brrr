### Field Report: npm Arborist Peer Dependency Resolution Investigation

**Current Environment:**
- npm@11.15.0 (commit 51c2bf8)
- Node v24.15.0
- Reproduction directory: `repro/` with empty project and `.cache`
- Observed: Cache contains packuments for uninstalled optional peers (playwright, etc.)

**Step 1: Reproduce Behavior with Logging**
```bash
cd repro
rm -rf node_modules .cache  # Reset state
DEBUG=arborist:node-from-edge,arborist:load-peer-set node ../cli/bin/npm-cli.js install vite --cache ./.cache
```

**Output Snippet:**
```
arborist:load-peer-set Processing peer edge: playwright@^1.30.0 [peerOptional: true]
arborist:node-from-edge Calling #nodeFromEdge for playwright (no parent edge) +0ms
arborist:node-from-edge Fetching packument for playwright (registry: https://registry.npmjs.org/) +2ms
... [similar entries for @types/node, sass, etc.] ...
```

**Observation:**  
`#nodeFromEdge` is triggered for optional peers (`peerOptional: true`) when both conditions are met:  
1. Peer dependency is unmet (`!edge.to`)  
2. Parent package doesn't have matching dependency (`!parentEdge`)  

**Step 2: Trace Code Path**  
Inspected `workspaces/arborist/lib/arborist/build-ideal-tree.js`:  
```javascript
// Fragment from #loadPeerSet
if (!edge.to) {
  if (!parentEdge) {
    await this.#nodeFromEdge(edge, node.parent, null, required) // FETCH TRIGGER
    continue
  }
}
```
**Key Findings:**  
1. `peerEdges` filter includes optional peers (`e.peer && !(e.valid && e.to)`)  
2. No branch distinguishes `peerOptional` in fetch logic  
3. `required` parameter derives from parent's dependency tree, not peer optionality  

**Step 3: Verify Peer Metadata**  
Checked `vite`'s dependency tree:  
```bash
grep '"peerOptional":' ./node_modules/vite/package.json
```
**Output:**  
```json
"peerDependenciesMeta": {
  "playwright": { "optional": true },
  "@types/node": { "optional": true },
  "...": "..."
}
```

**Step 4: Test with Minimal Case**  
Created isolated test case:  
```bash
mkdir peer-test && cd peer-test
npm init -y
echo '{"name":"dep","peerDependencies":{"optional-dep":"*"},"peerDependenciesMeta":{"optional-dep":{"optional":true}}}' > dep.json
DEBUG=arborist:node-from-edge node ../cli/bin/npm-cli.js install ./dep.json --cache ./.cache
```

**Output:**  
```
arborist:node-from-edge Fetching packument for optional-dep
```

**Conclusion:**  
The packument fetch occurs because:  
1. Optional peers are included in `peerEdges` during tree building  
2. `#nodeFromEdge` fetches packuments for *all* peers with:  
   - No existing resolution (`!edge.to`)  
   - No parent-provided version (`!parentEdge`)  
3. Optionality is only honored during installation phase, not during peer resolution  

**Unresolved Question:**  
Why does `#loadPeerSet` process optional peers despite comment stating *"we typically only install non-optional peers"*? Code shows no optionality check in edge processing loop.

**Next Investigation Path:**  
Trace why `peerOptional` isn't used in `peerEdges` filtering by modifying condition:  
```javascript
.filter(e => e.peer && !e.peerOptional && !(e.valid && e.to))
```  
(Will require rebuild and retest)
