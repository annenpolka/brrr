// Reduced excerpt of contentFingerprint cache on failing_ref
// packages/@aws-cdk/core/lib/fs/fingerprint.ts
// fc8d54e866ab313b6b25b80039dff03e47d0a88c
// cache key uses getUTCDate (day-of-month) + getUTCMilliseconds.
// leftover previous sha256 after same-size rewrite.

const stats = fs.statSync(file, { bigint: true });
const cacheKey = JSON.stringify({
  mtime_unix: stats.mtime.getUTCDate(),
  mtime_ms: stats.mtime.getUTCMilliseconds(),
  inode: stats.ino.toString(),
  size: stats.size.toString(),
});
return fingerprintCache.obtain(cacheKey, () => contentFingerprintMiss(file));
