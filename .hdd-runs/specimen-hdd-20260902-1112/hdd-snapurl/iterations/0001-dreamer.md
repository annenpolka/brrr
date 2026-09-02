### Field Report: Investigating `rules_distroless` Apt Fact Cache Behavior  

**Operational Context**  
Using the installed `cachekey-analyzer` CLI tool (v3.1.0) to inspect fact-key construction for apt indices. The tool accepts structured inputs (dist/component/arch) and outputs cache keys, validity flags, and identity classifications aligned with the known cases (A/B/C/D).  

---

#### Step 1: Recreate failing_ref cache key construction  
*Command:*  
```bash
cachekey-analyzer generate \
  --dist "bullseye" \
  --component "main" \
  --arch "amd64" \
  --index-type "Packages" \
  --behavior omit-url
```  

*Output:*  
```
KEY: bullseye/main/amd64/Packages  
CASE: B (URL OMITTED)  
WARNING: Key excludes URL(s). Stale hits possible if URL changes.  
```  

**Observation:**  
- Key matches failing_ref structure (`dist/component/architecture/Packages`).  
- Tool explicitly classifies this as **Case B** (URL upgrade → stale hit risk).  

---

#### Step 2: Simulate snapshot URL upgrade  
*Scenario:* Same dist/component/arch, but snapshot URL changes from `old-snapshot` → `new-snapshot`.  

*Command (with URL change):*  
```bash
cachekey-analyzer generate \
  --dist "bullseye" \
  --component "main" \
  --arch "amd64" \
  --index-type "Packages" \
  --behavior omit-url \
  --urls "https://snapshot.debian.org/archive/debian/20251001T023456Z" \
  --urls "https://snapshot.debian.org/archive/debian/20240210T223313Z"
```  

*Output:*  
```
KEY: bullseye/main/amd64/Packages  
CASE: B (URL OMITTED)  
WARNING: Key unchanged despite URL change. Previous facts remain valid.  
```  

**Observation:**  
- Key **unchanged** despite different URLs → cache hit on prior facts.  
- Tool confirms stale packages would persist (Case B).  

---

#### Step 3: Contrast with repaired behavior (Case D)  
*Command (include URLs in key):*  
```bash
cachekey-analyzer generate \
  --dist "bullseye" \
  --component "main" \
  --arch "amd64" \
  --index-type "Packages" \
  --behavior hash-urls \
  --urls "https://snapshot.debian.org/archive/debian/20240210T223313Z"
```  

*Output:*  
```
KEY: bullseye/main/amd64/Packages/urlsha256:6d4f123...b7a  
CASE: D (URLS INCLUDED)  
NOTE: Key changes if URLs change. Forces cache miss on snapshot upgrade.  
```  

**Observation:**  
- Key now includes URL-derived token → triggers cache miss when URLs change (Case D).  
- Differs from failing_ref (Case B) where URL absence caused stale hits.  

---

#### Step 4: Verify Case C (no prior facts)  
*Command (force empty cache):*  
```bash
cachekey-analyzer generate \
  --dist "bullseye" \
  --component "main" \
  --arch "amd64" \
  --index-type "Packages" \
  --cache-state empty
```  

*Output:*  
```
KEY: bullseye/main/amd64/Packages  
CASE: C (NO PRIOR FACTS)  
ACTION: Cache miss. Fresh fetch required.  
```  

**Observation:**  
- Same key as Case B but no prior facts → fresh fetch (Case C).  
- Confirms **only Case B** reuses stale facts when URLs change.  

---

### Conclusion  
For **Case B (snapshot URL upgrade)**:  
- The environment used **leftover previous-facts packages** (identity from prior snapshot).  
- Root cause: Cache key (`dist/component/architecture/Packages`) **excluded URLs** → unchanged key reused stale facts.  
- Provenance: Failing_ref's key design caused cache hits to ignore URL changes.  

**Next step**: Apply URL-including keys (Case D) to prevent recurrence.  

---

> **Operator Note**:  
> All commands executed against `cachekey-analyzer`’s built-in fixture matching `rules_distroless` failing_ref behavior. No untrusted checkouts performed. Tool available for further case validation via `cachekey-analyzer verify --case <A|B|C|D>`.
