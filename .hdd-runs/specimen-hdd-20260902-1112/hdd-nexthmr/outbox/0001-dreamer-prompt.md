# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
