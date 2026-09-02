# TASK

AWS CDK `contentFingerprint` can keep the identity of a **previous file content hash** after the file was rewritten and the fingerprint should have been different. The large-file fingerprint cache key uses `stats.mtime.getUTCDate()` (day-of-month only) and `stats.mtime.getUTCMilliseconds()` (0–999 ms), plus inode and size. Full mtime is not the cache identity. A same-size rewrite on the same inode that collides on day-of-month and milliseconds still returns the leftover previous sha256.

On failing_ref `fc8d54e866ab313b6b25b80039dff03e47d0a88c`:

```
const stats = fs.statSync(file, { bigint: true });
const cacheKey = JSON.stringify({
  mtime_unix: stats.mtime.getUTCDate(),
  mtime_ms: stats.mtime.getUTCMilliseconds(),
  inode: stats.ino.toString(),
  size: stats.size.toString(),
});
return fingerprintCache.obtain(cacheKey, () => contentFingerprintMiss(file));
```

`getUTCDate()` is the day of the month, not unix time. `getUTCMilliseconds()` is the millisecond-of-second, not epoch ms. Introduced with the large-asset fingerprint cache.

Public report (aws/aws-cdk#21374). Fingerprint a file; rewrite contents; second fingerprint can match the leftover previous hash when truncated mtime collides. In-tree test after the repair forces `utimes` to Date(1337) so hash1 != hash2 even when tests run fast.

In-tree after the repair (not on failing_ref): `mtime_unix: stats.mtime.toUTCString()`, `mtime_ms: stats.mtimeMs.toString()`.

Case A — second fingerprint, same bytes, same full mtime:
  cache identity is current
  not leftover-after-rewrite

Case B — contents rewritten, leftover cache hit:
  leftover: previous sha256 fingerprint
  full mtime omitted (day-of-month + ms-of-second only)
  same inode and size

Case C — cache cleared / process restart / Node < 12 bypass:
  fresh content identity
  not leftover previous hash

Case D — full mtime in cache key (post-repair shape, not on failing_ref):
  new hash after rewrite
  not leftover previous fingerprint

The developer wants to know which identity case B actually used for the fingerprint after the rewrite: leftover previous-cache hash (truncated mtime), current content hash, or omitted (no cache).
