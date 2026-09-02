### Field Report: Investigating Cache Identity in Next.js `'use cache'` Behavior

**Operational Context**  
Using the in-environment CLI (`source-query`) to analyze provided code excerpts and issue data without executing untrusted checkouts. Tool responds with code relationships, control flow, and state implications.

---

#### Step 1: Query cache key formation for cookieless requests  
**Command:**  
```bash
source-query key-provenance \
  --file=cacheKeyParts_failing.ts \
  --func=cacheKeyParts \
  --constraint="hmrRefreshHash=undefined"
```

**Output:**  
```
KEY STRUCTURE: [buildId, id, args]  
INHABITED BY:  
  - Pre-edit requests lacking HMR cookie  
  - Pre-edit prerender/cache work units (if hmrRefreshHash absent during initial set)  
STORAGE LAYER: AsyncLocalStorage-based cache (in-memory)  
INVALIDATION: None triggered by file edits when HMR cookie absent
```

**Observation:**  
Cookieless requests use a minimal key (`[buildId, id, args]`), distinct from HMR keys that include the hash. This key structure persists across edits.

---

#### Step 2: Trace HMR hash acquisition for request-type work units  
**Command:**  
```bash
source-query control-flow \
  --file=getHmrRefreshHash_failing.ts \
  --func=getHmrRefreshHash \
  --workUnitType=request \
  --cookies="__next_hmr_refresh_hash__=absent"
```

**Output:**  
```
PATH: workUnitStore.type = 'request'  
  → workUnitStore.cookies.get('NEXT_HMR_REFRESH_HASH_COOKIE')  
  → undefined (cookie missing)  
RETURN: undefined  
EFFECT:  
  - hmrRefreshHash omitted from cache key  
  - No fallback to server-derived hash (fixed in 286862e)
```

**Observation:**  
Request-type work units (e.g., route handlers, fetch) *exclusively* rely on client cookies for HMR hash. Server-side hash generation is absent in this version.

---

#### Step 3: Cross-reference issue timeline with key behavior  
**Command:**  
```bash
source-query issue-timeline \
  --issue=vercel/next.js#96022 \
  --filter=repro-steps
```

**Output:**  
```
USER REPRO (2026-07-19):  
  1. Start dev server with 'use cache' page  
  2. Load page in Browser A (sets HMR cookie)  
  3. Edit server component  
  4. Browser A: sees update (HMR cookie present → new key)  
  5. curl same URL: returns PRE-EDIT content  
  6. Route handler edits also fail to invalidate  

CONFIRMED:  
  - Affects all cookieless clients  
  - Cache persists until manual reset or buildId change
```

**Observation:**  
Cookieless requests access cache entries created *before edits* under the static key `[buildId, id, args]`. No evidence of current-source computation or cache omission.

---

#### Step 4: Verify cold-start vs. leftover behavior  
**Command:**  
```bash
source-query diff-scenarios \
  --case=cold-start \
  --case=leftover-after-edit \
  --determinant=hmrRefreshHash
```

**Output:**  
```
| SCENARIO          | HMR HASH SOURCE   | CACHE KEY          | CONTENT ORIGIN     |
|-------------------|-------------------|--------------------|--------------------|
| Cold start        | undefined         | [b, id, args]      | Fresh compute      |
| Leftover (case B) | undefined         | [b, id, args]      | Pre-edit cache     |
| HMR client (case A)| Cookie/WorkUnit  | [b, id, args, hash]| Post-edit compute  |
```

**Observation:**  
Case B explicitly uses the *pre-edit cache entry* due to identical key structure (`[buildId, id, args]`). Cold starts share the key schema but compute fresh content when no entry exists.

---

### Conclusion: Cache Identity in Case B  
**Provenance:**  
- **Key:** `[buildId, id, args]` (static, hashless)  
- **Content source:** Cached result from *server component execution prior to edit*  
- **Persistence:** Survives edits due to lack of invalidation mechanism for hashless keys  

**Evidence chain:**  
1. Cache keys exclude HMR hash when cookies are absent (code-proven)  
2. Issue reproductions confirm pre-edit content appears post-edit  
3. No code paths suggest recomputation or cache bypass for this key structure  
4. Fix (286862e) introduces server-authored hash, confirming omission was the defect  

**Answer:**  
Case B used the **leftover previous page** (server hash omitted) identity. The cache entry remained accessible via the static key `[buildId, id, args]` with no invalidation on file change.
