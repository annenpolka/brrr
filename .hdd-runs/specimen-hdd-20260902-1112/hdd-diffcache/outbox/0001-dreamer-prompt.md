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

Coder's diff highlighter can keep the identity of a **filename-keyed highlight AST** after a later edit of the same path has a different patch body. `@pierre/diffs` keys its worker-pool cache by `cacheKey`, which the components default to the file name when unset. Leftover AST from the first diff is reused for the second; rendering throws `deletionLine and additionLine are null`.

On failing_ref `9a57dfa6424996d92daa18a8a5b96efcb1576a1a`, `parsePatchFiles` is called without a content key. Parsed `FileDiffMetadata` has no `cacheKey`. The library assigns `cacheKey = fileDiff.name`. Two consecutive `edit_files` turns on one path share leftover highlight identity.

Public report (coder/coder#27987): two user-visible bugs from `@pierre/diffs` 1.3.x (#27932) keying the singleton worker-pool highlight cache by filename:

1. Stale-AST crash: two different diff bodies for the same path shared one cache entry.
2. Truncated synthetic diffs: N same-name file entries kept entry one.

`RemoteDiffPanel` already used a timestamp-scoped prefix; chat tool renderers and `LocalDiffPanel` parsed without one.

In-tree after the repair (not on failing_ref): `parseDiffString` stamps `cacheKey` with `getContentCacheKey` (FNV-1a of name, prevName, lang, hunks, line arrays). Unchanged files hit; changed files miss.

Case A — first diff of path `foo.ts`:
  highlight AST stored under filename
  not leftover yet

Case B — second diff of `foo.ts` with different hunks, leftover cache:
  leftover: stale AST of first body
  crash on shorter additionLines/deletionLines

Case C — content-derived cacheKey (post-repair shape, not on failing_ref):
  miss
  not leftover filename identity

Case D — different path:
  unique filename key
  not this leftover

The developer wants to know which identity case B actually left in the highlight cache: leftover first-body AST for `foo.ts`, content-keyed miss, or omitted (no cache entry).

# OBSERVED

Public coder/coder#27987 (merged 2026-08-11). Squash `df278ec0795cda3af53bae17aae5108ddcfe2d69` (parent `9a57dfa6424996d92daa18a8a5b96efcb1576a1a`). Upstream pierrecomputer/pierre#1052 tracks the throw. Local coder UI was not performed on this lab host.

PR body: parse without cacheKey → library uses filename → leftover highlight AST for a later diff of the same path. Reproduced against shipped 1.3.3 by seeding the pool cache with a first diff and rendering a second of the same path.

On failing_ref, parsePatchFiles is unkeyed. Content checksum is **not** on the failing revision. It is added by PR 27987 (`getContentCacheKey` / `stampCacheKey`).

Not this packet: specimen-090 (webpack leftover cache). specimen-094 (vitest cache key). next.js webpack cache leftover (job-0465 hunt: no merged leftover-identity pair).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 9a57dfa6424996d92daa18a8a5b96efcb1576a1a
# parsePatchFiles without cacheKey
# @pierre/diffs FileDiff.js cacheKey = fileDiff.name

# public shape:
# leftover highlight AST for foo.ts
# second diff of foo.ts throws deletionLine/additionLine null
```

Source-backed only. Do not execute untrusted checkouts on the host.

coder/coder
  site/src/components/DiffViewer (parseDiff / parsePatchFiles)

RELEVANT MATERIAL

### cache_key_failing.txt

Reduced shape of unkeyed parse on failing_ref
9a57dfa6424996d92daa18a8a5b96efcb1576a1a

parsePatchFiles(diff) → FileDiffMetadata without cacheKey
@pierre/diffs FileDiff.js: cacheKey = fileDiff.name when absent
WorkerPoolManager highlight cache keyed only by that cacheKey

Two diffs of foo.ts:
  first body stored under foo.ts
  leftover: second body hits foo.ts
  processDiffResult indexes shorter additionLines/deletionLines
  throw deletionLine and additionLine are null

### leftover_identity_split.txt

Registry / fixture:
  two edit_files turns on foo.ts
  leftover highlight cache keyed by filename

Case A (first diff of foo.ts):
  AST stored under filename
  not leftover yet

Case B (second diff, different hunks, leftover cache):
  leftover: stale first-body AST
  crash

Case C (content-derived cacheKey):
  miss
  not leftover filename identity

Case D (different path):
  unique filename key
  not this leftover

Not this packet:
  webpack leftover cache (specimen-090)
  vitest cache key (specimen-094)
  next.js webpack cache leftover (no merged pair)

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
