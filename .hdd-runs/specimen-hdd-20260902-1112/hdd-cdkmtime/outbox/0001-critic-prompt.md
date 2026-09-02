# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating AWS CDK Fingerprint Cache Behavior

**Observation 1: Cache Key Construction**  
Using the provided CLI tool `cdk-fprint-inspect`, I examined the cache key generation logic at the failing_ref commit:  
```bash
$ cdk-fprint-inspect key-structure --source fingerprint_failing.ts
```
```output
CACHE KEY COMPONENTS:
- mtime_unix: stats.mtime.getUTCDate() [day-of-month, 1-31]
- mtime_ms: stats.mtime.getUTCMilliseconds() [0-999]
- inode: string representation
- size: string representation
```

**Observation 2: Simulated Cache Collision**  
Created a test file and simulated a same-size rewrite with colliding mtime fragments:  
```bash
$ touch testfile && echo "v1" > testfile
$ cdk-fprint-inspect fingerprint --file testfile
```
```output
Initial fingerprint: 6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b
Cache key: {"mtime_unix":20,"mtime_ms":482,"inode":"517998","size":"3"}
```

Rewrote contents while preserving size and forcing mtime collision:  
```bash
$ echo "v2" > testfile && cdk-fprint-inspect set-mtime --day 20 --ms 482 testfile
$ cdk-fprint-inspect fingerprint --file testfile
```
```output
Fingerprint: 6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b
Cache key: {"mtime_unix":20,"mtime_ms":482,"inode":"517998","size":"3"}
```

**Observation 3: Cache Behavior Verification**  
Forced cache reset and re-fingerprinted:  
```bash
$ cdk-fprint-inspect reset-cache
$ cdk-fprint-inspect fingerprint --file testfile
```
```output
Fingerprint: d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35
```

**Key Findings:**  
1. After same-size rewrite with colliding day/ms fragments (Case B):
   - Returned fingerprint matched initial hash (`6b86...5b4b`)
   - Cache key remained identical despite content change
   - CLI output showed cache hit event: `[CACHE] Using cached fingerprint for key {...}`

2. After cache reset (Case C):
   - New content hash generated (`d473...ab35`)
   - Confirms cache was responsible for prior behavior

3. Environment limitations:
   - Attempt to validate full mtime key (Case D) failed with error:  
     `ERR_UNSUPPORTED: Full mtime key not available in failing_ref`
   - Consistent with known repair being absent at this commit

**Conclusion for Case B Identity:**  
The post-rewrite fingerprint used the **leftover previous-cache hash** (truncated mtime key). This is confirmed by:  
- Identical cache keys pre/post rewrite
- Cache hit diagnostic output
- New hash generation after cache reset
- Inability to use full mtime key at this commit

No evidence of current content hash being used or identity omission occurred during tests. The cache collision in key construction directly caused the stale fingerprint.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
