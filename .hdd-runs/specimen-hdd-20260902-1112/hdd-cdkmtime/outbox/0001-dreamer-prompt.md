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

# OBSERVED

Public aws/aws-cdk#21374 (merged 2022-07-29). PR 21374 squash `65a210aaaf8f45095170bca7779fd274aab54a00` (parent `fc8d54e866ab313b6b25b80039dff03e47d0a88c`). Local aws-cdk was not performed on this lab host.

PR body: fingerprint cache invalidation incorrectly uses mtime; only day-of-month and fractional seconds. Introduced in #21321 large-asset fingerprint cache.

On failing_ref, `contentFingerprint` builds cacheKey from getUTCDate + getUTCMilliseconds + inode + size, then `fingerprintCache.obtain`. Tests after the repair bump mtime to Date(1337) because fast rewrites collide.

Not this packet: specimen-139 black leftover project-root vs omitted CWD. specimen-075 rustc incremental fingerprint. specimen-090 webpack leftover.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref fc8d54e866ab313b6b25b80039dff03e47d0a88c
# packages/@aws-cdk/core/lib/fs/fingerprint.ts contentFingerprint

# public shape:
# leftover sha256 fingerprint after same-size rewrite
# cache key uses getUTCDate + getUTCMilliseconds, not full mtime
# cache clear / full mtime key yields the new hash
```

Source-backed only. Do not execute untrusted checkouts on the host.

aws/aws-cdk
  packages/@aws-cdk/core/lib/fs/fingerprint.ts

RELEVANT MATERIAL

### fingerprint_failing.ts

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

### leftover_identity_split.txt

Registry / fixture:
  CDK contentFingerprint large-file cache
  leftover sha256 after same-size rewrite

Case A (second fingerprint, same bytes, same mtime):
  current cache identity
  not leftover-after-rewrite

Case B (contents rewritten, leftover cache hit):
  leftover: previous sha256 fingerprint
  full mtime omitted (day-of-month + ms-of-second)
  same inode and size

Case C (cache cleared / Node < 12 bypass):
  fresh content identity
  not leftover previous hash

Case D (full mtime in cache key):
  new hash after rewrite
  not leftover previous fingerprint

Not this packet:
  black leftover project-root vs omitted CWD (specimen-139)
  rustc incremental fingerprint (specimen-075)

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
