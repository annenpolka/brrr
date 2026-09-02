# OBSERVED

Public coder/coder#27987 (merged 2026-08-11). Squash `df278ec0795cda3af53bae17aae5108ddcfe2d69` (parent `9a57dfa6424996d92daa18a8a5b96efcb1576a1a`). Upstream pierrecomputer/pierre#1052 tracks the throw. Local coder UI was not performed on this lab host.

PR body: parse without cacheKey → library uses filename → leftover highlight AST for a later diff of the same path. Reproduced against shipped 1.3.3 by seeding the pool cache with a first diff and rendering a second of the same path.

On failing_ref, parsePatchFiles is unkeyed. Content checksum is **not** on the failing revision. It is added by PR 27987 (`getContentCacheKey` / `stampCacheKey`).

Not this packet: specimen-090 (webpack leftover cache). specimen-094 (vitest cache key). next.js webpack cache leftover (job-0465 hunt: no merged leftover-identity pair).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
