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
A cache key is hashed from commit and tags. A linked worktree path changed. Second build is FRESH. Extra worktree-local file is missing. Which identity component was omitted from the key?

# OBSERVED
Owned files/wt_cache.py.

python3 files/wt_cache.py

files/wt_cache.py

RELEVANT MATERIAL

### expand_ranges_failing.py

# Reduced excerpt of expand_ranges on failing_ref
# src/tox/config/loader/ini/factor.py

return re.sub(
    r"""
    (                       # outer capture group
        ( \d+ ) - ( \d+ )   # closed range: start-end
        |
        ( \d+ ) -           # right-open range: start-
        |
        (?<= [{,] ) - ( \d+ )  # left-open range: -end (preceded by { or ,)
        |
        \d+                 # single number
    )
    (?: , | \} )            # followed by comma or closing brace
    """,
    _expand,
    value,
    flags=re.VERBOSE,
)

### observed_expansions.txt

written: py313-django4-2
produced: py313-django4 , 3 , 2
missing:  py313-django4-2

written: py310-1,py310-2
produced: hundreds of names counting down from 310

written: {2-4}
produced: {2,3,4}   (still wanted)

written: py3{10-11}
produced: py310, py311   (still wanted)

### wt_cache.py

import hashlib, json
def key(parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:12]
a={"commit":"abc","tags":"v1"}
b={"commit":"abc","tags":"v1","worktree":"/tmp/wt2"}
print("key_a", key(a))
print("key_b_if_included", key(b))
print("same_if_worktree_omitted", key(a)==key({"commit":"abc","tags":"v1"}))
print("fresh_misses_worktree", True)

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

        ### Field Report: Investigating Cache Key Omission  

**Operational Context:**  
Using the installed developer CLI (`tox-worktree-util`) to probe cache behavior. The tool manages worktree-linked builds and cache operations.  

**Concrete Task Sequence:**  

1. **Verify Cache Key Composition:**  
   Run the provided `wt_cache.py` to confirm baseline key behavior.  
   ```bash  
   python3 files/wt_cache.py  
   ```  
   **Output:**  
   ```  
   key_a 3f5c2a89b1f2  
   key_b_if_included 7d8e1f3a0b6c  
   same_if_worktree_omitted True  
   fresh_misses_worktree True  
   ```  
   **Observation:**  
   - Keys for `a` (commit + tags) and `b` (commit + tags + worktree) differ.  
   - Omitting `worktree` yields identical keys for `a` and `b`-without-worktree.  
   - Explicit note: `fresh_misses_worktree` is `True`, indicating worktree changes force cache misses.  

2. **Inspect Cache Key Generation via CLI:**  
   Use `tox-worktree-util keygen` to generate cache keys in different worktrees.  
   ```bash  
   tox-worktree-util keygen --commit "abc" --tags "v1"  
   ```  
   **Output (Primary Worktree):**  
   ```  
   Cache key: 3f5c2a89b1f2  
   Components: commit, tags  
   ```  
   **Output (Linked Worktree `/tmp/wt2`):**  
   ```  
   Cache key: 3f5c2a89b1f2  
   Components: commit, tags  
   ```  
   **Observation:**  
   - Keys match across worktrees. `worktree` path is **not** included in components.  

3. **Simulate Build with Cache Lookup:**  
   Run build in linked worktree (`/tmp/wt2`) with cache diagnostics:  
   ```bash  
   tox-worktree-util build --diagnose  
   ```  
   **Output:**  
   ```  
   Build target: default  
   Cache key: 3f5c2a89b1f2 (commit=abc, tags=v1)  
   Cache status: FRESH (worktree context mismatch)  
   Missing worktree-local file: /tmp/wt2/.envconfig  
   ```  
   **Failure:**  
   - Build marked `FRESH` despite matching commit/tags key.  
   - Error: Missing worktree-local file (`.envconfig`).  

4. **Investigate Worktree Context Mismatch:**  
   Query the tool’s cache metadata for key `3f5c2a89b1f2`:  
   ```bash  
   tox-worktree-util cache inspect 3f5c2a89b1f2  
   ```  
   **Output:**  
   ```  
   Cache entry: 3f5c2a89b1f2  
   Created: 2023-10-05 14:30:00 (worktree: /tmp/wt1)  
   Metadata:  
     - worktree: /tmp/wt1  
     - files: [".envconfig", "tox.ini"]  
   ```  
   **Observation:**  
   - Cache entry stores `worktree` path (`/tmp/wt1`) and file list internally.  
   - Cache retrieval fails in `/tmp/wt2` due to:  
     - Absence of `.envconfig` (worktree-local file).  
     - Mismatched worktree path in metadata.  

5. **Retry with Explicit Worktree Inclusion:**  
   Force-include worktree in key generation:  
   ```bash  
   tox-worktree-util keygen --commit "abc" --tags "v1" --worktree "/tmp/wt2"  
   ```  
   **Output:**  
   ```  
   Cache key: 7d8e1f3a0b6c  
   Components: commit, tags, worktree  
   ```  
   **Observation:**  
   - Key now differs from original (`3f5c2a89b1f2` → `7d8e1f3a0b6c`).  
   - Build with this key would avoid "FRESH" status (tested in isolated run).  

### Key Findings:  
1. **Omitted Identity Component:**  
   The cache key **excludes the worktree path** despite it being critical for worktree-local state (e.g., `.envconfig`). This violates contextual uniqueness.  

2. **Root Cause of "FRESH" Build:**  
   - Cache retrieval checks metadata (including worktree path and files) even if the key matches.  
   - The linked worktree (`/tmp/wt2`) fails this check because:  
     - `.envconfig` is missing (worktree-local file).  
     - Metadata references `/tmp/wt1`, not `/tmp/wt2`.  
   - Result: Cache is bypassed, triggering a fresh build.  

3. **System Behavior Confirmation:**  
   The `fresh_misses_worktree: True` output from `wt_cache.py` aligns with the CLI’s behavior—worktree changes invalidate cache hits *despite identical commit/tags keys*.  

### Conclusion:  
The **worktree path** was omitted from the cache key, causing a metadata mismatch during retrieval. Including `worktree` in the key would isolate cache entries per worktree, preventing invalid reuse. No speculative physics or hidden infrastructure was invoked; failure replicated via CLI commands and metadata inspection.  

**Recommended Action:**  
Modify `key(parts)` in `wt_cache.py` to include `"worktree"` as a required component.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
