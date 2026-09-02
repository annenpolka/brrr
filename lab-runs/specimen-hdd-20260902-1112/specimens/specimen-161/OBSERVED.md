# OBSERVED

Public vercel/next.js#96022 (merged 2026-07-22). Squash `286862e35bbc4fa7c023077cf794d5852063463a` (parent `70f8b678877ba69f266e1522fcfacb95cfd3c76e`). Local next was not performed on this lab host.

PR title: Fix stale dev `'use cache'` for cookieless requests and route handlers. Dev invalidation used a cookie-delivered HMR hash. Cookieless clients kept leftover cache after an edit.

On failing_ref, request-store `getHmrRefreshHash` reads `NEXT_HMR_REFRESH_HASH_COOKIE`. Missing cookie → `hmrRefreshHash` undefined → `cacheKeyParts` drops the hash → leftover HIT.

Not this packet: specimen-090 webpack persistent cache. specimen-156 bun define-table omitted from runtime-transpile hash. specimen-157 jest haste mock-name delete.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
