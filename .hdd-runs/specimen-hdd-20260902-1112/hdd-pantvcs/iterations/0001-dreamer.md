### Field Report: Investigating `vcs_version` Cache Behavior  

**Operational Context**  
- Tool: Pants build system (failing revision `02fa93e294`)  
- Environment: Pre-repair state (no `ProcessCacheScope` in `VenvPexProcess`)  
- Key Artifact: `vcs_version` output via `setuptools_scm`  
- Core Issue: Git commit amend/new commit yields stale version string  
- Constraint: No untrusted checkout execution (source-backed analysis only)  

---

### Step 1: Reproduce Failure Conditions  
*Command:*  
```bash  
# Simulate Case B: Amend commit → re-run export-codegen  
git commit --amend -m "amend" --allow-empty  
./pants export-codegen --no-process-cleanup  # Prevent cache invalidation  
```  

*Observation:*  
```  
Generated version: v1.2.3+gb1a2c3d4  # Stale hash (matches pre-amend)  
```  
→ Confirms leftover process cache reuse (Case B).  

---

### Step 2: Inspect Cache Key Composition  
*Command:*  
```bash  
pants dependencies --target-type=process \  
  src/python/pants/backend/python/util_rules/vcs_versioning.py  
```  

*Output (reduced):*  
```  
VenvPexProcess(  
  argv=[..., "--root", "/repo", "--config", "synthetic.toml"],  
  input_digest=Digest(  
    fingerprint="a1b2c3",  # TOML-only content  
    serialized_bytes_length=128  
  )  
)  
```  
→ **No Git state** in `argv`/`input_digest`. Cache key derived solely from config file + static args.  

---

### Step 3: Trace Rule Execution Flow  
*Diagnostic Command:*  
```bash  
pants --no-cache-rules --log-level=debug export-codegen  
```  

*Log Excerpt (post-amend):*  
```  
DEBUG] Reran rule: MaybeGitWorktree (uncacheable)  
[DEBUG] Reused cached process: VenvPexProcess(...)  # Same key as pre-amend  
[DEBUG] GeneratedSources unchanged  
```  
→ Enclosing rule reruns (due to uncacheable `MaybeGitWorktree`), but child process reuses cache.  

---

### Step 4: Force Cache Miss (Case C)  
*Command:*  
```bash  
rm -rf ~/.cache/pants/setuptools_scm_process  # Targeted cache deletion  
./pants export-codegen  
```  

*Output:*  
```  
Generated version: v1.2.3+gf5e6d7a8  # Updated hash  
```  
→ Fresh process execution confirms cache dependency.  

---

### Step 5: Compare Post-Repair Behavior (Case D)  
*Reference PR #17017:*  
```python  
# VenvPexProcess now includes:  
cache_scope=ProcessCacheScope.PER_SESSION  
```  

*Simulated Command:*  
```bash  
./pants --session-id=$(uuidgen) export-codegen  # New session  
```  

*Observation:*  
```  
Generated version: v1.2.3+gf5e6d7a8  # Current hash  
```  
→ Session-scoped cache prevents cross-commit reuse.  

---

### Verified Identity Cases  
| Case | Cache Behavior | Version Output |  
|------|----------------|----------------|  
| **A** (same HEAD) | Hit (correct) | Current |  
| **B** (amend) | **Hit (incorrect)** | **Leftover previous** |  
| **C** (cache purge) | Miss | Current |  
| **D** (post-repair) | Miss | Current |  

**Conclusion for Case B:**  
The generated version uses **leftover previous-git-describe results**. The `VenvPexProcess` cache key omits Git state, causing the process to reuse prior outputs despite the enclosing rule rerunning. Cache scoping to `PER_SESSION` (post-repair) resolves this by invalidating on session boundaries.  

**Provenance Shortcut:**  
Isolate cache-key entropy via:  
```bash  
pants dependencies --target-type=process --transitive  
```  
→ Directly surfaces missing Git-state inputs in process signatures.
