# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

        CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Next.js `'use cache'` in development can keep the identity of a **previous cached page / route handler** after a server-component file is edited, for any request that does not carry the HMR refresh-hash cookie, because `getHmrRefreshHash` on a request store reads `__next_hmr_refresh_hash__` from cookies and the server-authored hash is omitted from that path.

On failing_ref `70f8b678877ba69f266e1522fcfacb95cfd3c76e`:

```
export function getHmrRefreshHash(workUnitStore: WorkUnitStore): string | undefined {
  if (process.env.__NEXT_DEV_SERVER) {
    switch (workUnitStore.type) {
      case 'cache':
      case 'private-cache':
      case 'prerender':
      case 'prerender-runtime':
        return workUnitStore.hmrRefreshHash
      case 'request':
        return workUnitStore.cookies.get(NEXT_HMR_REFRESH_HASH_COOKIE)?.value
```

```
const cacheKeyParts: CacheKeyParts = hmrRefreshHash
  ? [buildId, id, args, hmrRefreshHash]
  : [buildId, id, args]
```

The HMR client writes the hash into a session cookie after a server-component reload. `curl`, a plain `fetch`, a fresh browser profile, or a second device never send that cookie. `hmrRefreshHash` is then undefined, so the key is `[buildId, id, args]` and leftover previous cache HITs. Route-handler edits on Turbopack also fail to advance the cookie.

Public report (vercel/next.js#96022). Edit a `'use cache'` page, then fetch without the cookie. Expected: miss / new content. Actual: leftover previous cached content.

In-tree after the repair (not on failing_ref): the hash is server-authored and attached via request meta; the cookie is gone.

Case A — same request after edit, HMR cookie present:
  cache key includes the new hash
  not leftover-after-edit

Case B — cookieless request after edit, leftover cache:
  leftover: previous `'use cache'` entry
  server hash omitted on the request path
  cookie absent

Case C — cold start / empty `'use cache'` store:
  fresh compute
  not leftover previous page

Case D — server-attached hash (post-repair shape, not on failing_ref):
  every client misses after an edit
  not leftover previous page

The developer wants to know which identity case B actually used after the edit without the cookie: leftover previous-page (server hash omitted), current source, or omitted (no cache).

# OBSERVED

Public vercel/next.js#96022 (merged 2026-07-22). Squash `286862e35bbc4fa7c023077cf794d5852063463a` (parent `70f8b678877ba69f266e1522fcfacb95cfd3c76e`). Local next was not performed on this lab host.

PR title: Fix stale dev `'use cache'` for cookieless requests and route handlers. Dev invalidation used a cookie-delivered HMR hash. Cookieless clients kept leftover cache after an edit.

On failing_ref, request-store `getHmrRefreshHash` reads `NEXT_HMR_REFRESH_HASH_COOKIE`. Missing cookie → `hmrRefreshHash` undefined → `cacheKeyParts` drops the hash → leftover HIT.

Not this packet: specimen-090 webpack persistent cache. specimen-156 bun define-table omitted from runtime-transpile hash. specimen-157 jest haste mock-name delete.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 70f8b678877ba69f266e1522fcfacb95cfd3c76e
# packages/next/src/server/app-render/work-unit-async-storage.external.ts getHmrRefreshHash
# packages/next/src/server/use-cache/use-cache-wrapper.ts cacheKeyParts

# public shape:
# leftover 'use cache' after edit for cookieless requests
# request path reads HMR hash cookie; server hash omitted
# cookie-bearing HMR client / miss writes new content
```

Source-backed only. Do not execute untrusted checkouts on the host.

vercel/next.js
  packages/next/src/server/app-render/work-unit-async-storage.external.ts
  packages/next/src/server/use-cache/use-cache-wrapper.ts
  packages/next/src/client/dev/hot-reloader/app/hot-reloader-app.tsx
  packages/next/src/server/base-server.ts

RELEVANT MATERIAL

### cacheKeyParts_failing.ts

// Reduced excerpt of cacheKeyParts on failing_ref
// packages/next/src/server/use-cache/use-cache-wrapper.ts
// leftover HIT when hmrRefreshHash is undefined (no cookie).

const cacheKeyParts: CacheKeyParts = hmrRefreshHash
  ? [buildId, id, args, hmrRefreshHash]
  : [buildId, id, args]

### getHmrRefreshHash_failing.ts

// Reduced excerpt of getHmrRefreshHash on failing_ref
// packages/next/src/server/app-render/work-unit-async-storage.external.ts
// 70f8b678877ba69f266e1522fcfacb95cfd3c76e
// request path reads the HMR cookie; server hash omitted.

export function getHmrRefreshHash(
  workUnitStore: WorkUnitStore
): string | undefined {
  if (process.env.__NEXT_DEV_SERVER) {
    switch (workUnitStore.type) {
      case 'cache':
      case 'private-cache':
      case 'prerender':
      case 'prerender-runtime':
        return workUnitStore.hmrRefreshHash
      case 'request':
        return workUnitStore.cookies.get(NEXT_HMR_REFRESH_HASH_COOKIE)?.value
    }
  }
  return undefined
}

### leftover_identity_split.txt

Registry / fixture:
  Next.js 'use cache' / getHmrRefreshHash
  leftover previous page after edit for cookieless requests

Case A (HMR cookie present after edit):
  current cache identity (hash in key)
  not leftover-after-edit

Case B (cookieless after edit, leftover cache):
  leftover: previous 'use cache' entry
  server hash omitted on the request path

Case C (cold start / empty store):
  fresh compute
  not leftover previous page

Case D (server-attached hash):
  every client misses after an edit
  not leftover previous page

Not this packet:
  webpack persistent cache (specimen-090)
  bun define-table omitted from runtime-transpile hash (specimen-156)
  jest haste mock-name delete (specimen-157)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
