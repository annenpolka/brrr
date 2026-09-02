// Reduced excerpt of cacheKeyParts on failing_ref
// packages/next/src/server/use-cache/use-cache-wrapper.ts
// leftover HIT when hmrRefreshHash is undefined (no cookie).

const cacheKeyParts: CacheKeyParts = hmrRefreshHash
  ? [buildId, id, args, hmrRefreshHash]
  : [buildId, id, args]
