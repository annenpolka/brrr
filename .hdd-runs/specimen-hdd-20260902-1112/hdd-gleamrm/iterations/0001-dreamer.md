### Field Report: Gleam Cache Identity Investigation  

**Operational Context**:  
- Investigating Gleam compiler cache behavior (failing_ref `3767575d05372e4b823c132afacb28e52fbe3aa1`).  
- Focus: Module `a` cache identity after source removal/restoration (Case B scenario).  
- Constraints: No local execution (untrusted checkouts prohibited). Reliance on provided code excerpts and public issue #4320.  

---

### Step 1: Reproduce Cache Behavior via Code Inspection  
**Command**: Analyze `PackageLoader` and `ModuleLoader` logic from provided excerpts.  

**Observation**:  
- `PackageLoader::run` marks removed modules stale **without deleting cache files** (`package_loader_failing.rs`):  
  ```rust
  for cache_file in gleam_cache_files(...) {
      if !inputs.contains_key(&module) {
          self.stale_modules.add(module); // ← Stale marker added
      }
  }
  ```  
- `ModuleLoader::load` prioritizes **fingerprint matching** over mtime (`module_loader_failing.rs`):  
  ```rust
  if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
      return Ok(Input::New(...)); // ← New compile if fingerprint mismatch
  } 
  // Else: use cached artefact (Input::Cached)
  ```  

**Conclusion**:  
- Cache files persist after source removal (no deletion).  
- Restored `a.gleam` with identical bytes triggers fingerprint match → **leftover cache reused**.  

---

### Step 2: Verify Case B Identity  
**Scenario**:  
1. Initial state: `a` calls `b.f` → cache generated.  
2. `a.gleam` moved out → marked stale (cache remains).  
3. `b.f` changed → `b` recompiled.  
4. `a.gleam` restored (unchanged) → rebuild attempted.  

**Hypothesis**:  
Module `a` should use **leftover cache** (previous compile with old `b.f`).  

**Validation via Code Paths**:  
- ✅ **Fingerprint match**: Restored `a.gleam` has same bytes → `Input::Cached` returned.  
- ✅ **Stale marker ignored**: `stale_modules` tracks removal but doesn’t invalidate cache on restoration.  
- ❌ **No mtime fallback**: Cache reused despite newer `b.f` (mtime check only triggers fingerprint comparison).  

**Output Simulation**:  
```  
// Expected after restore (Case B):  
ModuleLoader::load("a") →  
  Source fingerprint matches →  
  Returns Input::Cached (old artefact) →  
  Runtime error: "function b.f did not exist"  
```  

**Conflict Check**:  
- Prior assumption ("cache should invalidate on dependency change") conflicts with fingerprint-centric design.  
- Investigation confirms: **No dependency tracking** in `ModuleLoader::load`. Cache identity purely source-content-driven.  

---

### Step 3: Contrast Identity Cases  
| Case | Trigger                     | `a` Cache Identity       |  
|------|-----------------------------|---------------------------|  
| A    | No removal, `b` unchanged  | Current cache (expected)  |  
| **B**  | **`a` removed/restored, `b` changed** | **Leftover previous cache** |  
| C    | `gleam clean` post-restore  | New compile (no cache)    |  
| D    | Cache deleted on removal (post-fix) | New compile          |  

**Key Evidence**:  
- Case B confirmed via:  
  1. Undeleted cache files post-removal (`PackageLoader`).  
  2. Fingerprint match bypasses recompile (`ModuleLoader`).  
- Absence of dependency hash in cache metadata → **no invalidation** when `b` changes.  

---

### Final Status  
**Identity Resolution**:  
Module `a` in Case B uses **leftover previous cache** (failing_ref `3767575d05372e4b823c132afacb28e52fbe3aa1`).  

**Root Cause**:  
- Cache retention policy + source-fingerprint prioritization over dependency changes.  

**Recommendation**:  
- Patch: Delete cache files during `stale_modules` marking (implemented in PR #4325).  
- Workaround: `gleam clean` after source restoration (forces Case C).  

**Uncertainties**:  
- Edge cases with clock skew affecting mtime not validated (no host execution).  
- Impact on LSP mode (`incomplete_modules` path) not explored.  

**Operator Note**:  
> "Cache stayed put, source came back same as before – compiler grabbed the old artefact like nothing changed. Dependencies be damned."
