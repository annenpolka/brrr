### Field Report: Investigating Minimal Cache Behavior with Output Artifacts  
**Operational Context:**  
Using the provided fixture with a minimal cache that keys solely on input hash and ignores requested outputs. Only observable evidence: build status messages and file presence in `target/`.  

---

#### Step 1: Initial build without SBOM  
```bash
cargo build
```  
```  
   Compiling my_crate v0.1.0 (/crate)  
    Finished dev [unoptimized + debuginfo] target(s) in 0.12s  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  
```  
**Observation:**  
Build completes successfully. No `sbom-precursor.json` present.  

---

#### Step 2: Request SBOM artifact (same inputs)  
```bash
CARGO_BUILD_SBOM=true cargo build -Zsbom  
```  
```  
    Finished dev [unoptimized + debuginfo] target(s) in 0.01s  # Status: FRESH  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  
```  
**Observation:**  
Cache reports `FRESH`. `sbom-precursor.json` **not generated**.  

---

#### Step 3: Force cache miss by altering input  
```bash
echo "// modify" >> src/lib.rs  # Change input hash  
CARGO_BUILD_SBOM=true cargo build -Zsbom  
```  
```  
   Compiling my_crate v0.1.0 (/crate)  # Status: REBUILD  
    Finished dev [unoptimized + debuginfo] target(s) in 0.11s  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  sbom-precursor.json  
```  
**Observation:**  
Rebuild triggered. `sbom-precursor.json` **now present**.  

---

#### Step 4: Verify cache persistence of extra artifact  
```bash
CARGO_BUILD_SBOM=true cargo build -Zsbom  # Same inputs as Step 3  
```  
```  
    Finished dev [unoptimized + debuginfo] target(s) in 0.01s  # FRESH  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  sbom-precursor.json  
```  
**Observation:**  
Cache hit preserves all artifacts from Step 3, including SBOM precursor.  

---

#### Step 5: Test artifact leakage without SBOM request  
```bash
cargo build  # No SBOM flags, same inputs  
```  
```  
    Finished dev [unoptimized + debuginfo] target(s) in 0.01s  # FRESH  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  sbom-precursor.json  
```  
**Observation:**  
Cache serves **all previously built artifacts** regardless of current request. SBOM precursor persists even when unrequested.  

---

### Findings  
1. **Cache identity flaw confirmed:**  
   - Freshness determined **solely by input hash**  
   - Requested outputs **do not affect** cache hit/miss decisions  
   - Artifact requirements (`-Zsbom`, `CARGO_BUILD_SBOM`) ignored in key  

2. **Artifact handling behavior:**  
   ```mermaid  
   graph LR  
   A[Build] --> B{Cache Key Match?}  
   B -->|Yes| C[Restore ALL cached artifacts]  
   B -->|No| D[Rebuild with current parameters]  
   D --> E[Cache new artifact set]  
   ```  
   - Cache stores/replays **complete artifact sets** from first build per input hash  
   - No capability to:  
     - Add new artifacts to existing cache entries  
     - Filter artifacts based on current request  

3. **Failure modes:**  
   - **False negative**: New artifact request → cache hit → missing artifact  
   - **False positive**: Artifacts from prior configuration persist when unrequested  

**Root Cause:**  
Cache treats artifact sets as immutable byproducts of input hashes. Output requirements exist outside cache identity.  

**Recommendation:**  
Modify cache key to include:  
- `requested_artifacts` bitmask  
- Unstable flags (`-Z` features)  
- Environment variables controlling output generation  

**Verification Path:**  
After fix implementation:  
1. Repeat Step 2 → should report `COMPILING` (not `FRESH`)  
2. `sbom-precursor.json` appears in `target/` post-build  

---  
**Operational Note:**  
All conclusions derived from build status strings and file system observations. No cache introspection used.
