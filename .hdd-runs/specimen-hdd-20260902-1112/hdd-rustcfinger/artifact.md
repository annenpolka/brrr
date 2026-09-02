### Field Report: Investigative Session on Rustc Info Cache Behavior

#### Operational Environment
- **Tool**: Cargo build system (rust-lang/cargo@`40d6078baf`)
- **Context**: Fedora-distributed rustc 1.82.0 with clamped mtimes
- **Focus**: `rustc_fingerprint` cache behavior in shared workspace (`target/.rustc_info.json`)
- **Investigation Method**: Source analysis of cache logic at failing revision

---

### Step 1: Reproduce Cache Decision Path
**Command**: Simulate `Cache::load` for Case A (Fedora compilers X/Y)  
**Input**:  
- `rustc_path`: `/usr/bin/rustc` (identical for X/Y)  
- `mtime`: `2024-10-17 00:00:00` (clamped, identical)  
- `rustc_wrapper`: `None`  
- `rustc_workspace_wrapper`: `None`  
- `RUSTUP_HOME`/`RUSTUP_TOOLCHAIN`: Unset (non-rustup case)  

**Code Execution Path**:  
1. `hash_exe` invoked for `/usr/bin/rustc`:  
   ```rust
   path = Path::resolve_executable("/usr/bin/rustc")?; // -> /usr/bin/rustc  
   path.hash(hasher);  // Hashes "/usr/bin/rustc"  
   mtime(&path)?.hash(hasher);  // Hashes clamped mtime (0)  
   ```  
2. No wrappers → skip additional hashing  
3. Rustup check:  
   ```rust
   (maybe_rustup, RUSTUP_HOME, RUSTUP_TOOLCHAIN) = (false, _, _)  
   // Skips rustup branch → final fingerprint = hash("/usr/bin/rustc" + 0)  
   ```  

**Observation**:  
- **Fingerprint output**: Identical `u64` for X and Y  
  (Path + mtime identical → same hash)  

---

### Step 2: Cache Load Simulation  
**Command**: Simulate `Cache::load` with existing `.rustc_info.json` from Compiler X  
**Cache State**:  
```json
{
  "rustc_fingerprint": 0xAABBCCDD, // Fingerprint from X
  "outputs": { ... } // Cached -vV from X
}
```  

**Logic**:  
```rust
if current_fingerprint == cache_fingerprint { // 0xAABBCCDD == 0xAABBCCDD
  debug!("reusing existing rustc info cache");
  reuse_cache = true;
} else {
  debug!("different compiler, creating new rustc info cache");
}
```  

**Observation**:  
- **Debug log**: `"reusing existing rustc info cache"`  
- **`rustc -vV` command**: Not executed (uses cached output from X: `(Fedora 1.82.0-1.fc42)`)  
- **Actual compiler**: Y (`Fedora 1.82.0-1.fc40`)  

---

### Step 3: Impact on Build  
**Command**: Simulate crate reuse with cached compiler info  
**Result**:  
- Cargo assumes rustc identity matches cache (X)  
- Does not invalidate existing `libautocfg-*.rlib` (built with X)  
- Compiler Y links against rlib from X → **E0514 error**  
  ```
  error[E0514]: found crate `autocfg` compiled by an incompatible version of rustc
    = note: crate compiled by rustc 1.82.0 (Fedora 1.82.0-1.fc42)
    = help: recompile with current compiler (Fedora 1.82.0-1.fc40)
  ```  

**Failure Analysis**:  
- Root cause: Fingerprint collision due to:  
  1. Path/mtime-only hashing  
  2. Fedora mtime clamping  
- Cache reuse masks compiler mismatch → stale artifacts not cleaned  

---

### Case Variations  
| Case | Path | Mtime | Size | Birth Time | Fingerprint Match | Cache Reused |  
|------|------|-------|------|------------|-------------------|--------------|  
| **A** | Same | Same | - | - | ✅ | ✅ |  
| **B** | Same | Same | Diff | - | ✅ | ✅ |  
| **C** | Same | Same | Same | Diff | ✅ | ✅ |  

**Key Insight**:  
- Fingerprint **ignores size/birth time** → Collision in all cases (A/B/C)  
- `.rustc_info.json` reuse guaranteed when path/mtime identical  

---

### Conclusion  
- **Cache Behavior for Case A/B/C**:  
  - `rustc_fingerprint` **equal** → Full cache reuse  
  - Cargo reports: `"reusing existing rustc info cache"`  
- **Symptom Trigger**:  
  Cached `-vV` output (from X) masks actual compiler (Y) → linker error  

---

### Proposed Next Step  
**Investigate via Instrumented Build**:  
```bash
# On Fedora system with compilers X/Y:  
CARGO_LOG=cargo::util::rustc=debug cargo build > cargo.log 2>&1  
```  
**Expected Log Artifacts**:  
1. `DEBUG cargo::util::rustc: reusing existing rustc info cache`  
2. Mismatched crate version errors in build output  

**Rationale**:  
Confirms cache reuse precedes linker errors in real-world runtime.  

--- 

**Session End**  
No further commands executed (source analysis complete).
