### Field Report: BuildKit Git Source Cache Key Analysis  

**Operational Context**  
Executing within a constrained BuildKit analysis environment. No local Git operations permitted; relying solely on provided code excerpts and established facts. Focus is on `source/git/source.go` at failing commit `bc6f7be`.  

---

#### **Concrete Investigation Steps**  

1. **Confirm Cache Key Composition**  
   Inspected `shaToCacheKey` implementation at failing_ref:  
   ```go  
   func (gs *gitSourceHandler) shaToCacheKey(sha string) string {  
       key := sha  // Base key = raw SHA  
       if gs.src.KeepGitDir {  
           key += ".git"  // Append ".git" only if KeepGitDir=true  
       }  
       if gs.src.Subdir != "" {  
           key += ":" + gs.src.Subdir  
       }  
       return key  
   }  
   ```  
   → **Observation**: No named ref (`a/v1.2.3`, `a/v1.2.3-same`) appears in key construction.  

2. **Trace Cache Key Generation for Tags**  
   Examined `CacheKey` logic handling non-SHA refs (tags):  
   ```go  
   // For non-SHA ref (e.g. tag):  
   cacheKey := gs.shaToCacheKey(sha) // sha = resolved commit  
   return cacheKey, sha, nil, true, nil  
   ```  
   → **Observation**:  
   - Input `Ref="a/v1.2.3"` → Resolves to SHA `abc123` → Cache key = `abc123.git`  
   - Input `Ref="a/v1.2.3-same"` → Resolves to **same SHA `abc123`** → Cache key = `abc123.git`  

3. **Verify Key Collision in Case B**  
   Cross-referenced with `leftover_identity_split.txt`:  
   ```  
   Case B (KeepGitDir true, two tags, one commit):  
     failing_ref key = SHA + ".git" for both (keys equal)  
   ```  
   → **Confirmed**: Both tags produce identical cache key `abc123.git`.  

4. **Test Intended Behavior via PR Test**  
   Analyzed `TestMultipleTagAccessKeepGitDir` (from merged PR, not failing_ref):  
   ```go  
   // Expected post-fix behavior:  
   require.Equal(t, key1 != key2, true) // Keys differ for same SHA  
   require.Equal(t, pin1, pin2)        // Pins identical  
   ```  
   → **Contrast**: Failing_ref does **not** include ref in key, while fixed version does.  

---

#### **Key Findings**  

- **Cache Key Identity for Case B**:  
  `shaToCacheKey` stored **SHA-only + ".git"** (e.g., `abc123.git`).  
  - Named refs (`a/v1.2.3`, `a/v1.2.3-same`) were **omitted** from key.  
  - Result: Two refs sharing a commit **collided** under one cache key.  

- **Root Cause**:  
  Cache reuse allowed Snapshot 2 to inherit Snapshot 1's `.git` directory, which lacked `a/v1.2.3-same` ref.  

- **How Failure Manifested**:  
  Subsequent `git rev-parse a/v1.2.3-same` in reused `.git` directory failed (ref missing).  

---

#### **Unresolved Uncertainty**  
- **Why was ref excluded from key?**  
  Code suggests intentional design for raw SHA inputs (Case C), but no guard for named refs.  
- **Mitigation in Fix**:  
  PR #5444 modified key generation to include ref when `KeepGitDir=true` and ref is **not** a raw SHA.  

---

**Conclusion**  
For Case B at failing_ref, `shaToCacheKey` stored a **SHA-only + ".git"** identity. This caused two refs to share a cache entry despite referring to the same commit, resulting in missing ref errors during reuse. The fix introduced ref-aware key splitting for non-SHA identifiers.  

**No further commands executed** – constraints prohibit Git operations or BuildKit runtime. Analysis complete per available artifacts.
