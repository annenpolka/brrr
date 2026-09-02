### Field Report: Cache Identity Analysis for EOLANG Transpilation

**Tool Used:** `cacheprobe` (unfamiliar CLI for cache behavior simulation)  
**Environment State:** Pre-loaded with `transpile_failing.java` and `leftover_identity_split.txt` fixtures. Cache registry emulation enabled.

---

#### Step 1: Inspect Cache Key Structure
```bash
cacheprobe inspect-key --source transpile_failing.java --method version
```
**Output:**  
```
CACHE KEY STRUCTURE DETECTED:
Format: "%s-%s-%b-%b-%s"
Components:
  [0] version: String (e.g., plugin version)
  [1] fingerprint: String (hash of XSLS+IMPORTS)
  [2] locations: boolean (trackLocations flag)
  [3] coverage: boolean
  [4] superclass: String
MISSING COMPONENTS: 
  steps() flag (detected in source but not included in key)
```

**Observation:**  
The cache key excludes `tracking.steps()` on failing_ref. Only `locations()`, `coverage`, and `superclass` are included alongside static artifacts.

---

#### Step 2: Simulate Case B (Leftover Cache Hit)
```bash
cacheprobe simulate \
  --key-version "1.5.0" \
  --key-fingerprint "a1b2c3d4" \
  --key-locations false \
  --key-coverage true \
  --key-superclass "Object" \
  --cache-state "leftover:no-steps" \
  --flag-trackSteps true
```
**Output:**  
```
CACHE RESULT: HIT (identity: 1.5.0-a1b2c3d4-false-true-Object)
OUTPUT ARTIFACTS: 
  main.xmir (hash: 9f86d081) 
INTERMEDIATE ARTIFACTS: 
  step-*.xmir: 0 files (cache hit skipped transform)
PROVENANCE: 
  Cache entry created at 2026-08-25T14:30:00Z (flags: trackSteps=false)
```

**Failure/Retry:**  
Attempted to force step-file generation by appending `--force-miss`:  
```bash
cacheprobe simulate [...] --force-miss
```
**Output:**  
```
ERROR: Cannot force miss with --force-miss: key matches existing entry. 
Override requires cache-key change (e.g., modified inputs).
```

**Observation:**  
The tool confirms the leftover artifact (built without `trackSteps`) is reused when the key matches. The `trackSteps=true` flag is ignored during cache lookup.

---

#### Step 3: Verify Key Sensitivity
Test if adding `steps()` to the key would break the hit:  
```bash
cacheprobe simulate \
  [...] \ # Same parameters as Step 2
  --key-steps true \ # Hypothetical inclusion
  --cache-state "leftover:no-steps"
```
**Output:**  
```
CACHE RESULT: MISS (key mismatch: '1.5.0-a1b2c3d4-false-true-Object-true' != '1.5.0-a1b2c3d4-false-true-Object')
OUTPUT ARTIFACTS: 
  main.xmir (hash: 7d3b9e5a) 
INTERMEDIATE ARTIFACTS: 
  step-*.xmir: 10 files generated
```

**Observation:**  
Including `steps()` in the key (as in post-repair) causes a cache miss, forcing fresh step-file generation. This matches Case D.

---

#### Step 4: Control Test (Case C - Private Cache)
```bash
cacheprobe simulate [...] --cache-state "empty"
```
**Output:**  
```
CACHE RESULT: MISS (no entry)
OUTPUT ARTIFACTS: 
  main.xmir (hash: 7d3b9e5a) 
INTERMEDIATE ARTIFACTS: 
  step-*.xmir: 10 files generated
```

**Observation:**  
With no prior cache, `trackSteps=true` triggers step-file generation as expected.

---

### Conclusion
**Case B Identity:**  
The transpile output uses the **leftover previous-cache result** (steps omitted). This is proven by:  
1. Cache key matching the prior entry (without `steps()`).  
2. Reused artifact's provenance showing original `trackSteps=false`.  
3. Failed retry to force step-file generation without key changes.  

**Root Cause:**  
The cache key's omission of `tracking.steps()` allowed a logically incompatible artifact (built without step tracking) to satisfy a request for step files. The fix (adding `steps()` to the key) corrects this by making the key reflect all relevant build parameters.  

**Recommendation:**  
Audit cache keys for all build flags affecting output artifacts. Flags that alter output structure (not just content) must be part of the key.  

**Final Tool Output:**  
```
SUMMARY:
  Case A: Key match → fresh artifact (irrelevant to leftover)
  Case B: Key match → leftover artifact (no steps)
  Case C: Key missing → fresh artifact (steps generated)
  Case D: Key mismatch → fresh artifact (steps generated)
```
