# OBSERVED

Public aws/aws-cdk#21374 (merged 2022-07-29). PR 21374 squash `65a210aaaf8f45095170bca7779fd274aab54a00` (parent `fc8d54e866ab313b6b25b80039dff03e47d0a88c`). Local aws-cdk was not performed on this lab host.

PR body: fingerprint cache invalidation incorrectly uses mtime; only day-of-month and fractional seconds. Introduced in #21321 large-asset fingerprint cache.

On failing_ref, `contentFingerprint` builds cacheKey from getUTCDate + getUTCMilliseconds + inode + size, then `fingerprintCache.obtain`. Tests after the repair bump mtime to Date(1337) because fast rewrites collide.

Not this packet: specimen-139 black leftover project-root vs omitted CWD. specimen-075 rustc incremental fingerprint. specimen-090 webpack leftover.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
