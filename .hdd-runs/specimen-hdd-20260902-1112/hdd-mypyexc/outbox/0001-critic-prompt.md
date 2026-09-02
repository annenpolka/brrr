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

mypy `--incremental` can keep the identity of a **previous cache result** after `--untyped-calls-exclude` should have been a different check. `OPTIONS_AFFECTING_CACHE` listed platform/plugins/strict_bytes/fixed_format_cache. `untyped_calls_exclude` is omitted.

On failing_ref `8f2371a565eb9c29f03922b26da8eab054fbbcf8`:

```
OPTIONS_AFFECTING_CACHE: Final = (
    PER_MODULE_OPTIONS
    | {
        "platform",
        "bazel",
        "old_type_inference",
        "plugins",
        "disable_bytearray_promotion",
        "disable_memoryview_promotion",
        "strict_bytes",
        "fixed_format_cache",
    }
) - {"debug_cache"}
```

`self.untyped_calls_exclude: list[str] = []` exists as an option. It is not in OPTIONS_AFFECTING_CACHE.

Public report (python/mypy#16652). `--disallow-untyped-calls --untyped-calls-exclude=bug.Super` errors; `--untyped-calls-exclude=bug` succeeds; a later `--untyped-calls-exclude=bug.Super` with leftover `.mypy_cache` also succeeds until `rmdir .mypy_cache`.

In-tree after the repair (not on failing_ref): `"untyped_calls_exclude"` is a member of OPTIONS_AFFECTING_CACHE. Test `testUntypedCallsExcludeAffectsCache`.

Case A — second mypy with unchanged --untyped-calls-exclude:
  cache identity is current
  not leftover-after-exclude-change

Case B — exclude string flipped, leftover .mypy_cache:
  leftover: previous success/error identity
  untyped_calls_exclude omitted from OPTIONS_AFFECTING_CACHE
  Super-exclude after bug-exclude stays success

Case C — rmdir .mypy_cache then Super-exclude:
  fresh cache identity
  error on untyped draw

Case D — untyped_calls_exclude in OPTIONS_AFFECTING_CACHE (post-repair shape, not on failing_ref):
  cache miss after exclude change
  not leftover previous success

The developer wants to know which identity case B actually used for the incremental cache after the exclude change: leftover previous-exclude results (flag omitted from OPTIONS_AFFECTING_CACHE), current exclude identity, or omitted (no cache).

# OBSERVED

Public python/mypy#16652 (closed 2025-09-06). PR 19801 merge `309b01e287e3afabeb888572455f9bf55d86acad` (parent `8f2371a565eb9c29f03922b26da8eab054fbbcf8`). Local mypy was not performed on this lab host.

Issue body: same command different results depending on leftover cache; Super-exclude errors on a cold cache; after a successful `bug` exclude run, Super-exclude succeeds until `.mypy_cache` is deleted.

On failing_ref, OPTIONS_AFFECTING_CACHE ends at `fixed_format_cache`. `untyped_calls_exclude` is **not** in that set. It is added by PR 19801.

Not this packet: specimen-067 mypy leftover sentinels (issue 21866 / PR 21888 expandtype). specimen-075 rustc incremental. specimen-136 pants vcs_version process cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 8f2371a565eb9c29f03922b26da8eab054fbbcf8
# mypy/options.py OPTIONS_AFFECTING_CACHE

# public shape:
# leftover .mypy_cache after --untyped-calls-exclude change
# untyped_calls_exclude omitted from OPTIONS_AFFECTING_CACHE
# Super-exclude after bug-exclude stays success until rmdir .mypy_cache
```

Source-backed only. Do not execute untrusted checkouts on the host.

python/mypy
  mypy/options.py
  test-data/unit/check-incremental.test
  .mypy_cache

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  --disallow-untyped-calls --untyped-calls-exclude
  leftover .mypy_cache after exclude string change

Case A (second mypy, same exclude):
  current cache identity
  not leftover-after-exclude-change

Case B (exclude flipped Super -> bug -> Super, leftover cache):
  leftover: previous success identity
  untyped_calls_exclude omitted from OPTIONS_AFFECTING_CACHE
  Super-exclude stays success

Case C (rmdir .mypy_cache):
  fresh cache identity
  Super-exclude errors

Case D (untyped_calls_exclude in OPTIONS_AFFECTING_CACHE):
  cache miss after exclude change
  not leftover previous success

Not this packet:
  mypy leftover sentinels (specimen-067)
  rustc incremental (specimen-075)
  pants vcs_version process cache (specimen-136)

### options_affecting_cache_failing.py

# Reduced excerpt of OPTIONS_AFFECTING_CACHE on failing_ref
# mypy/options.py
# 8f2371a565eb9c29f03922b26da8eab054fbbcf8
# untyped_calls_exclude omitted from the cache-identity set.

OPTIONS_AFFECTING_CACHE: Final = (
    PER_MODULE_OPTIONS
    | {
        "platform",
        "bazel",
        "old_type_inference",
        "plugins",
        "disable_bytearray_promotion",
        "disable_memoryview_promotion",
        "strict_bytes",
        "fixed_format_cache",
        # no "untyped_calls_exclude"
    }
) - {"debug_cache"}

# option exists; not hashed into cache identity
self.untyped_calls_exclude: list[str] = []

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

        ### Field Report: Investigating Cache Identity for Case B

#### Step 1: Inspect OPTIONS_AFFECTING_CACHE in failing_ref
**Command:**  
`cat options_affecting_cache_failing.py | grep -A 15 'OPTIONS_AFFECTING_CACHE'`

**Output:**  
```
OPTIONS_AFFECTING_CACHE: Final = (
    PER_MODULE_OPTIONS
    | {
        "platform",
        "bazel",
        "old_type_inference",
        "plugins",
        "disable_bytearray_promotion",
        "disable_memoryview_promotion",
        "strict_bytes",
        "fixed_format_cache",
        # no "untyped_calls_exclude"
    }
) - {"debug_cache"}

# option exists; not hashed into cache identity
self.untyped_calls_exclude: list[str] = []
```

**Observation:**  
Confirmed `untyped_calls_exclude` is absent from `OPTIONS_AFFECTING_CACHE` in failing_ref. The option exists but doesn't contribute to cache identity.

---

#### Step 2: Simulate Cache Identity Hashing
**Command:**  
Use the environment's cache-key simulator (pre-installed `cacheid-tool`):  
`cacheid-tool generate --options=platform:linux,bazel:False,untyped_calls_exclude:bug.Super`

**Output:**  
`Cache Identity Hash: a1b2c3d4e5`

**Command (retry with changed exclude):**  
`cacheid-tool generate --options=platform:linux,bazel:False,untyped_calls_exclude:bug`

**Output:**  
`Cache Identity Hash: a1b2c3d4e5`

**Observation:**  
Identical hash for both exclude values (`bug.Super` and `bug`), confirming `untyped_calls_exclude` is ignored in cache identity. Matches code inspection.

---

#### Step 3: Analyze Case B Scenario
**Input to `cacheid-tool`:**  
- Previous run: `--untyped-calls-exclude=bug` → Success → Cache stored under `a1b2c3d4e5`  
- Current run: `--untyped-calls-exclude=bug.Super` → Cache reused  

**Command:**  
`cacheid-tool resolve-case --previous_hash=a1b2c3d4e5 --current_hash=a1b2c3d4e5`

**Output:**  
```json
{
  "cache_identity_used": "leftover_previous",
  "reason": "Current and previous cache identities match (a1b2c3d4e5). Option change ignored due to OPTIONS_AFFECTING_CACHE omission.",
  "behavior": "Stale results from previous run reused"
}
```

**Observation:**  
Case B uses **leftover previous-exclude results** (cache identity `a1b2c3d4e5`). The environment treats the run as "unchanged" because `untyped_calls_exclude` isn't in the cache-key set.

---

#### Step 4: Verify Against Public Report
**Command:**  
`cacheid-tool cross-reference --issue=python/mypy#16652`

**Output:**  
```json
{
  "match_found": true,
  "artifact": "OPTIONS_AFFECTING_CACHE omission",
  "expected_behavior": "Cache not invalidated on exclude change",
  "observed_behavior": "Matches Case B description (success with stale cache)"
}
```

**Observation:**  
Tool confirms omission in failing_ref directly matches the public issue. No cache miss occurs in Case B due to identical identity hashing.

---

### Conclusion
**Cache Identity for Case B:**  
- **Identity Used:** Leftover previous-exclude results (identical cache key).  
- **Root Cause:** `untyped_calls_exclude` omitted from `OPTIONS_AFFECTING_CACHE` → Cache not invalidated when exclude changes.  
- **Evidence:**  
  1. Source code confirms omission.  
  2. Cache simulator shows identical hashes for different exclude values.  
  3. Resolution tool explicitly maps to "leftover_previous" case.  

**Recommendation:**  
PR #19801 fixed the issue by adding `untyped_calls_exclude` to `OPTIONS_AFFECTING_CACHE`. Case D (cache miss after exclude change) is now enforced.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
