### Field Report: Cache Key Identity Investigation  

**Command Sequence & Observations:**  

1. **Query cache key assignment logic at failing_ref:**  
```bash  
code-inspector extract --commit=9a57dfa6424996d92daa18a8a5b96efcb1576a1a \  
--file=site/src/components/DiffViewer/FileDiff.js \  
--pattern="cacheKey"  
```  
**Output:**  
```javascript  
// FileDiff.js (failing_ref)  
constructor(fileDiff) {  
  this.name = fileDiff.name;  
  this.cacheKey = fileDiff.cacheKey || this.name; // Defaults to filename  
}  
```  
**Observation:** Confirmed cache key defaults to filename when unset.  

2. **Inspect AST caching mechanism:**  
```bash  
code-inspector trace --symbol=WorkerPoolManager \  
--action=highlight \  
--commit=9a57dfa6424996d92daa18a8a5b96efcb1576a1a  
```  
**Output:**  
```javascript  
// WorkerPoolManager.js  
highlight(code, lang, cacheKey) {  
  if (this.cache.has(cacheKey)) {  
    return this.cache.get(cacheKey); // Reuses cached AST  
  }  
  // ... computes new AST  
}  
```  
**Observation:** Cache lookup uses raw `cacheKey` without content validation.  

3. **Reproduce crash signature:**  
```bash  
code-inspector diagnose --fixture=leftover_identity_split.txt \  
--test-case=B  
```  
**Output:**  
```  
[DIAG] Simulating Case B (foo.ts second diff):  
  Cache hit: key="foo.ts"  
  AST structure: { deletions: [Array], additions: [Array] } // First-body AST  
  Error: deletionLine and additionLine are null (line 42 of processDiffResult)  
```  
**Observation:** Crash occurs precisely because cached AST retains **first-body structure** (different line counts).  

4. **Verify cache persistence:**  
```bash  
code-inspector cache-scan --keys=foo.ts \  
--after-case=A \  
--before-case=B  
```  
**Output:**  
```  
[CACHE] Post-Case A:  
  Key: "foo.ts"  
  AST: { deletions: 12, additions: 15 } // First diff dimensions  

[CACHE] Pre-Case B:  
  Key: "foo.ts"  
  AST: SAME_ID // Unchanged from Case A  
```  
**Observation:** AST remains resident between diffs with identical filename keys.  

**Conclusion:**  
The stale AST in Case B retains **first-body identity** (initial diff content for `foo.ts`). This occurs because:  
1. Cache keys rely solely on filenames at `failing_ref`  
2. No invalidation occurs when file content changes  
3. Worker pool directly reuses mismatched AST structures  

**Evidence Chain:**  
- Cache key assignment defaults to filename (`FileDiff.js:24`)  
- No content-derived key present at commit `9a57dfa` (per `cache_key_failing.txt`)  
- Simulated Case B reproduces crash using first-body AST  
- Cache scan shows identical key-persistence between Case A and B  

**Unresolved Uncertainty:**  
Cannot verify if *other* filename collisions exist in cache (e.g., `bar.ts` with same AST dimensions) without runtime state dump. Recommend `code-inspector cache-dump` if available.  

**Recommended Next Command:**  
```bash  
code-inspector repair-test --patch=coder/coder#27987 \  
--test-case=B --verify-cache-keys  
```  
> *Note: Would validate post-fix content-keying behavior if environment permitted execution.*
