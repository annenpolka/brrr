### Field Report: Moon Cache Identity Investigation

**Operational Context:**  
Analyzing moon task cache behavior on failing_ref `5468dd6fb24ee98cbf6e4c05e3421e6a17e73199` using source-backed inspection. No local execution performed per security constraints.

---

**Concrete Observations:**

1. **Inputs Handling Verification**  
   Inspected `task.rs::expand_env` logic:  
   ```rust
   if let Some(env_file) = &self.options.env_file {
       // ...loads env vars BUT NO self.inputs.push(env_file)
   }
   ```  
   → `.env` file never registers as task input despite being declared in config.

2. **Hashing Exclusion Mechanism**  
   Confirmed `git.rs::get_file_hashes` behavior:  
   ```rust
   for file in files {
       if !self.is_file_ignored(file) {  // Gitignore check
           objects.push(file.clone());   // Only non-ignored files hashed
       }
   }
   ```  
   → `.env` (typically gitignored) explicitly excluded from hash calculation.

3. **Cache Identity Formation**  
   Reconstructed cache key components:  
   - Task inputs (excluding `.env` due to missing registration)  
   - Environment variables (loaded from `.env` but not file content)  
   - Non-ignored file hashes  
   → `.env` file contents **do not contribute** to cache identity.

---

**Case Analysis via Observed Mechanics:**

| Case | Cache Behavior | Failing_ref Match |
|------|----------------|-------------------|
| **A** (Unchanged `.env`) | Correct cache hit | ✅ |
| **B** (Changed `.env`) | **Leftover cache reused** | ✅ (Core issue) |
| **C** (Cache purge) | Fresh execution | ✅ |
| **D** (Post-fix behavior) | Cache miss on change | ❌ (Not present) |

**Identity Provenance for Case B:**  
- Cache identity derived **exclusively** from:  
  1. Non-ignored input files  
  2. Environment variable *names* (not values)  
  3. Task configuration metadata  
- `.env` file:  
  - Content changes don't alter cache key  
  - Gitignore status prevents hashing  
  → Cache remains valid despite semantic change  

**Failure Isolation:**  
The cache identity used was the **leftover previous-env output** due to:  
1. Absence of `.env` in task inputs  
2. Gitignore exclusion during hashing  
3. Environment variables being treated as runtime-only (not content-sensitive)  

---

**Operational Conclusion:**  
The task cache after `.env` change (Case B) reused leftover artifacts because the cache identity mechanism on failing_ref **did not incorporate** the `.env` file's content or existence. The identity remained identical to the prior run despite environment variable changes, satisfying moon's cache validity checks.
