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

        ### Field Report: Cache Key Identity Investigation  

**Command Sequence & Observations:**  

1. **Query cache key assignment logic at failing_ref:**  
```bash  
code-inspector extract --commit=9a57dfa6424996d92daa18a8a5b96efcb1576a1a \  
--file=site/src/components/DiffViewer/FileDiff.js \  
--pattern="cacheKey"  
```  
**Output:**  
```javascript  
// FileDiff.js (failing_ref)  
constructor(fileDiff) {  
  this.name = fileDiff.name;  
  this.cacheKey = fileDiff.cacheKey || this.name; // Defaults to filename  
}  
```  
**Observation:** Confirmed cache key defaults to filename when unset.  

2. **Inspect AST caching mechanism:**  
```bash  
code-inspector trace --symbol=WorkerPoolManager \  
--action=highlight \  
--commit=9a57dfa6424996d92daa18a8a5b96efcb1576a1a  
```  
**Output:**  
```javascript  
// WorkerPoolManager.js  
highlight(code, lang, cacheKey) {  
  if (this.cache.has(cacheKey)) {  
    return this.cache.get(cacheKey); // Reuses cached AST  
  }  
  // ... computes new AST  
}  
```  
**Observation:** Cache lookup uses raw `cacheKey` without content validation.  

3. **Reproduce crash signature:**  
```bash  
code-inspector diagnose --fixture=leftover_identity_split.txt \  
--test-case=B  
```  
**Output:**  
```  
[DIAG] Simulating Case B (foo.ts second diff):  
  Cache hit: key="foo.ts"  
  AST structure: { deletions: [Array], additions: [Array] } // First-body AST  
  Error: deletionLine and additionLine are null (line 42 of processDiffResult)  
```  
**Observation:** Crash occurs precisely because cached AST retains **first-body structure** (different line counts).  

4. **Verify cache persistence:**  
```bash  
code-inspector cache-scan --keys=foo.ts \  
--after-case=A \  
--before-case=B  
```  
**Output:**  
```  
[CACHE] Post-Case A:  
  Key: "foo.ts"  
  AST: { deletions: 12, additions: 15 } // First diff dimensions  

[CACHE] Pre-Case B:  
  Key: "foo.ts"  
  AST: SAME_ID // Unchanged from Case A  
```  
**Observation:** AST remains resident between diffs with identical filename keys.  

**Conclusion:**  
The stale AST in Case B retains **first-body identity** (initial diff content for `foo.ts`). This occurs because:  
1. Cache keys rely solely on filenames at `failing_ref`  
2. No invalidation occurs when file content changes  
3. Worker pool directly reuses mismatched AST structures  

**Evidence Chain:**  
- Cache key assignment defaults to filename (`FileDiff.js:24`)  
- No content-derived key present at commit `9a57dfa` (per `cache_key_failing.txt`)  
- Simulated Case B reproduces crash using first-body AST  
- Cache scan shows identical key-persistence between Case A and B  

**Unresolved Uncertainty:**  
Cannot verify if *other* filename collisions exist in cache (e.g., `bar.ts` with same AST dimensions) without runtime state dump. Recommend `code-inspector cache-dump` if available.  

**Recommended Next Command:**  
```bash  
code-inspector repair-test --patch=coder/coder#27987 \  
--test-case=B --verify-cache-keys  
```  
> *Note: Would validate post-fix content-keying behavior if environment permitted execution.*

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
