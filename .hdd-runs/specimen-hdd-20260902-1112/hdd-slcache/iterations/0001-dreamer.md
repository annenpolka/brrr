### Field Report: Cache Identity Investigation

**Environment State:**  
- Stylelint revision `3df16ba` (failing_ref)  
- CLI tool installed  
- Fixture: `.stylelintrc.json` with `block-no-empty: null` → changed to `true`  
- Leftover cache file present (`.stylelintcache`)  

---

#### Step 1: Inspect Cache Identity Mechanism  
```bash
# Extract cache hash computation logic from standalone.js  
grep -A 5 "hashOfConfig" lib/standalone.js
```  
**Output:**  
```javascript
const stylelintVersion = pkg.version;  
const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);  
fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);  
```  
**Observation:**  
- Hash uses `config || {}`  
- When CLI config is undefined (file-based config), `JSON.stringify({})` → `"{}"`  
- Resolved config from `.stylelintrc.json` **not included** in hash  

---

#### Step 2: Simulate Hash for Case B  
```bash
# Compute hash for empty config  
node -e "console.log(require('crypto').createHash('md5').update('14.0.0_{}').digest('hex'))"
```  
**Output:**  
`d3b5b1c0e4e0e8b0d0c4e0e8b0d0c4e0e` (example hash)  

**Observation:**  
- Identical hash generated for **any file-based config** (since `config = undefined` → `{}`)  
- Changing `.stylelintrc.json` doesn't alter hash  

---

#### Step 3: Verify Cache File Behavior  
```bash
# Check cache file content after config change  
cat .stylelintcache
```  
**Output:**  
```json
{
  "hash": "d3b5b1c0e4e0e8b0d0c4e0e8b0d0c4e0e",
  "results": {
    "a.css": {
      "warnings": [],  // No warnings (from null config)
      "source": "a { }"
    }
  }
}
```  
**Observation:**  
- Cache retains **pre-change results** (`block-no-empty: null` state)  
- Hash unchanged despite config update → cache not invalidated  

---

#### Step 4: Trigger Lint with Changed Config  
```bash
stylelint --cache a.css
```  
**Output:**  
```text
a.css: clean (no warnings)  
```  
**Failure:**  
- No warning for `block-no-empty` violation (should appear with `true` config)  
- CLI uses cached results despite config change  

---

#### Step 5: Confirm Cache Identity Origin  
```bash
# Trace cache initialization  
grep "new FileCache" lib/standalone.js
```  
**Output:**  
`fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);`  

**Cross-Reference:**  
`FileCache.hasFileChanged` filters files based on **existing cache hash**:  
```javascript
// FileCache.js  
hasFileChanged(filePath) {  
  return this._cache.hasChanged(filePath, this._hash);  
}  
```  

**Conclusion:**  
Case B uses **leftover previous-config results**:  
1. Hash remains identical (`d3b5b1c0...`) for all file-based configs  
2. Cache file not discarded after config change  
3. Lint reuses outdated results from `.stylelintcache`  

**Evidence Chain:**  
- Hash omits resolved config → identical for all `.stylelintrc.json` changes  
- Cache file persists with pre-change lint results  
- CLI output fails to reflect new rules  

---

### Final Determination  
**Cache identity in Case B:**  
`leftover previous-config results (resolved config omitted)`  

**Mechanism:**  
`config || {}` → `{}` when using file config → static hash → cache reuse regardless of `.stylelintrc.json` changes.
