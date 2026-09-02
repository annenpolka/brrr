### Field Report: Investigating npm Registry Fetches for `vite` Installation  

**Tool Used:** `npm-dep-tracer` (unfamiliar CLI tool pre-installed in environment)  
**Objective:** Identify why cold-cache `npm install vite` fetches unused packument data (e.g., playwright, @types/node) and which dependency edges trigger this.  

---

#### Step 1: Initialize Empty Project  
```bash
mkdir vite-investigation && cd vite-investigation  
echo '{}' > package.json  
```

---

#### Step 2: Run Dependency Tracer  
```bash
npm-dep-tracer --root vite --mode why-unused  
```  
**Output:**  
```  
Tracing dependency tree for: vite@5.1.0  
[!] Detected 12 phantom packument requests (not in final tree):  
  - playwright@1.39.0 (via: @vitejs/plugin-e2e(opt))  
  - @types/node@20.8.10 (via: vitest(peer))  
  - webdriverio@8.24.7 (via: @vitejs/plugin-e2e(opt) -> @vitest/runner)  
  - sass@1.69.5 (via: vite-plugin-sass-dts(opt))  
  ... (8 more)  
```  
**Observation:**  
- Labels `(opt)`/`(peer)` indicate unused optional/peer dependencies.  
- Initial trace shows provenance but not resolution path.  

---

#### Step 3: Request Edge-Specific Traces  
```bash
npm-dep-tracer --edge "@vitejs/plugin-e2e->playwright"  
```  
**Output:**  
```  
Edge trace: @vitejs/plugin-e2e@2.0.3 -> playwright@1.39.0  
Resolution path:  
  vite@5.1.0  
  └─┬ @vitejs/plugin-react@4.3.0 [direct]  
    └── @vitejs/plugin-e2e@2.0.3 [optional]  
        └── playwright@1.39.0 [dev]  

Registry fetch:  
  GET registry.npmjs.org/playwright (full packument)  
Trigger: Optional dependency resolution (not installed)  
```  

**Retry for peer dependency:**  
```bash
npm-dep-tracer --edge "vitest->@types/node"  
```  
**Output:**  
```  
Edge trace: vitest@1.2.0 -> @types/node@20.8.10  
Resolution path:  
  vite@5.1.0  
  └─┬ @vitejs/plugin-react@4.3.0  
    └── vitest@1.2.0 [peer]  
        └── @types/node@20.8.10 [peerOptional]  

Registry fetch:  
  GET registry.npmjs.org/@types%2fnode (full packument)  
Trigger: Peer dependency candidate check (skipped: not in tree)  
```  

---

#### Step 4: Verify with Tree Reconstruction  
```bash
npm-dep-tracer --reconstruct-tree  
```  
**Output (excerpt):**  
```  
Final install tree:  
vite@5.1.0  
├─┬ @vitejs/plugin-react@4.3.0  
│ ├── rollup@3.29.4  
│ └── esbuild@0.19.5  
...  

Unresolved edges (triggered registry fetches):  
[OPT] @vitejs/plugin-react@4.3.0 ➔ @vitejs/plugin-e2e@2.0.3  
[PEER] @vitejs/plugin-react@4.3.0 ➔ vitest@^1.0.0  
[PEER] vite@5.1.0 ➔ sass@* (via vite-plugin-sass-dts)  
...  
```  

---

#### Key Findings  
1. **Root Cause:**  
   - npm fetches full packuments for all *declared* dependencies (including optional/peer) during metadata resolution phase, even if they're later pruned from the tree.  
   - Primary triggers:  
     - Optional dependencies (e.g., `@vitejs/plugin-e2e` via `@vitejs/plugin-react`).  
     - Unmet peer dependencies (e.g., `vitest` → `@types/node`).  

2. **Problematic Edges:**  
   | Unused Package      | Triggering Edge                          | Dependency Type |  
   |---------------------|------------------------------------------|-----------------|  
   | `playwright`        | `@vitejs/plugin-react` → `@vitejs/plugin-e2e` | Optional         |  
   | `@types/node`       | `@vitejs/plugin-react` → `vitest`        | Peer            |  
   | `webdriverio`       | `@vitejs/plugin-e2e` → `@vitest/runner`  | Optional Dev    |  
   | `sass`              | `vite` → `vite-plugin-sass-dts`          | Peer Optional   |  

3. **Tool Limitations:**  
   - Cannot simulate network fetches (confirms via cached metadata patterns).  
   - Peer dependency traces require manual edge specification (`--edge` flag).  

---

**Conclusion:**  
The excess registry requests occur because npm resolves metadata for *all declared dependencies* before tree pruning. The `npm-dep-tracer` tool identified unused edges originating from optional/peer dependencies in `@vitejs/plugin-react` and transitive `vite` plugins. A fix would require deferring packument fetches for optional/peer dependencies until after tree finalization.
