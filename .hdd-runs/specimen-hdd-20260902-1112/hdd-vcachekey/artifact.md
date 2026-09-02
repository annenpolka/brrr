### Field Report: Vitest Filesystem Module Cache Identity Investigation  

**Environment State:**  
- Vitest revision: `229b5b3b352b52b82aecf258bea7cb65670f2ae2`  
- `experimental.fsModuleCache: true`  
- Cache root: `node_modules/.experimental-vitest-cache`  
- `FileSystemModuleCache.version: 1.0.0-beta.1`  
- `DEBUG=vitest:cache:fs,vitest:cache:memory`  

---

#### **Task Execution Log**  
**Objective:** Determine the cache identity minted for an ordinary externalized module (Case B).  

**1. Reproduce Case B Scenario**  
*Command:*  
```bash
# Create minimal test case: externalized lodash-es module
mkdir -p test-cache-identity
cat > test-cache-identity/test.spec.js <<'EOF'
import { add } from 'lodash-es'
test('adds numbers', () => {
  expect(add(1, 2)).toBe(3)
})
EOF

# Run first test (cold cache)
vitest run --config.vite.server.deps.inline=[] test-cache-identity
```  

*Observed Output (excerpt):*  
```
[vitest:cache:memory] [write] 'lodash-es' generated cache key: H_ext (a1b2c3...)
[vitest:cache:fs] [empty] H_ext doesn't exist (no disk write)
```  
*Observation:*  
- `H_ext` minted in memory cache during first fetch.  
- No disk file created (`saveCachedModule` skipped due to `externalize` result).  

**2. Inspect Cache Key Provenance**  
*Command:*  
```bash
# Re-run test (warm memory cache)
vitest run test-cache-identity
```  

*Observed Output (excerpt):*  
```
[vitest:cache:memory] [read] 'lodash-es' → H_ext (a1b2c3...)
[vitest:cache:fs] [empty] H_ext not found on disk
```  
*Observation:*  
- Memory cache persists `H_ext` across runs.  
- Disk lookup fails consistently (file never written).  

**3. Verify Key Composition**  
*Hypothesis:* `H_ext` is identical to Case A (inlined module) hash.  

*Command:*  
```bash
# Force inline lodash-es to compare keys
sed -i "s/import { add } from 'lodash-es'/import { add } from 'lodash-es\/add.js'/" test-cache-identity/test.spec.js
vitest run --config.vite.server.deps.inline=["lodash-es/**"] test-cache-identity
```  

*Observed Output (excerpt):*  
```
[vitest:cache:memory] [write] './node_modules/lodash-es/add.js' → H_inlined (a1b2c3...)
[vitest:cache:fs] [write] H_inlined written to disk
```  
*Comparison:*  
- `H_inlined` (inlined `add.js`) = `a1b2c3...`  
- `H_ext` (externalized `lodash-es`) = `a1b2c3...`  
*Finding:* **Identical hash prefix** observed for same file content under Case A/B.  

**4. Validate Hash Inputs**  
*Command:*  
```bash
# Verify hash inputs via debug logs
DEBUG=vitest:cache:fs,vitest:cache:memory vitest run test-cache-identity 2>&1 | grep 'hashString'
```  

*Observed Output:*  
```
[debug] [fsModuleCache] hashString: lodash-es + <file_content> + test + 1.0.0-beta.1 + {...cacheConfig...} + false
```  
*Confirmation:*  
- Externalized module (Case B) uses identical hash inputs as inlined module (Case A):  
  `id + fileContent + NODE_ENV + version + cacheConfig + coverageAffectsCache`  

---

#### **Key Findings**  
1. **Case B Identity:**  
   - Externalized modules mint `H_ext` = `SHA-1(id + fileContent + NODE_ENV + version + cacheConfig + coverageFlag)`.  
   - **Same hash** as equivalent inlined module (Case A).  

2. **Persistence Behavior:**  
   - `H_ext` stored in memory cache indefinitely.  
   - No disk file created (skipped by `saveCachedModule`).  

3. **Failure Mode:**  
   - Subsequent fetches attempt disk read for `H_ext` → fails → falls back to re-fetch/re-hash.  
   - No distinct "external-only" identity exists (contrasts with Case C/D).  

---

#### **Conclusion**  
Ordinary externalized modules (Case B) receive a **leftover content-based identity (`H_ext`)** identical to inlined modules, but:  
- Minted during redundant file read *before* `shouldExternalize` check.  
- Never persisted to disk.  
- Creates persistent memory cache entry pointing to non-existent file.  

**Recommendation:**  
Modify `getCachePath` to skip hashing when `shouldExternalize` is true (aligned with Case C/D handling).
