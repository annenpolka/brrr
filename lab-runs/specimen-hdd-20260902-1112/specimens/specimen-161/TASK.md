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
