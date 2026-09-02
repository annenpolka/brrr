KNOWN FIX (sealed): aws/aws-cdk PR 21374 squash 65a210aaaf8f45095170bca7779fd274aab54a00.

failing_ref is parent fc8d54e866ab313b6b25b80039dff03e47d0a88c.

contentFingerprint cached on getUTCDate() (day-of-month) + getUTCMilliseconds() + inode + size. Same-size rewrite could keep leftover previous sha256.

PR repair: mtime_unix = stats.mtime.toUTCString(); mtime_ms = stats.mtimeMs.toString().

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
