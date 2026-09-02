# OBSERVED

Public sbt/sbt#9195 (closed 2026-05-11). PR 9207 merge `49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef` (parents `c491f035f832a62843d69364b55237dc29c99e7d` + `e69e23aae14240d2c6b63e2c5ff356ccc154e784`). Local sbt/zinc was not performed on this lab host.

Issue body: `discoveredMainClasses` after delete+restore of `src` expects success and fails. Notes `.triggeredBy(compile)` plus global cache. Workaround `cleanFull`.

PR body: MixedAnalyzingCompiler analysis cache caches using the last write, assuming all writing happens via it. That does not work with sbt 2.x caching where the gz file under the path can switch. Repair keys local analysis caching on file size and timestamp (caffeine), and calls zinc `staticCachedStore(..., cacheLast = false)`.

On failing_ref, `analysisStore` uses the two-arg zinc overload (`cacheLast = true`). Zinc `getCachedStore` is last-write. File size / last-modified are **not** part of that identity.

Not this packet: specimen-088 / specimen-104 (gradle configuration-cache leftover). specimen-075 (rustc incremental). specimen-078 (derived gocache). specimen-111 (tsbuildinfo leftover signature). No sbt specimen in 001-111.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
