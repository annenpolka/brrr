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

A test cache keys freshness by the test file list only. First run builds with binary buildid `buildid-aaa`. The binary is rewritten with `buildid-bbb`. Second run reports FRESH because the cache key ignored buildid.

The developer wants to know whether the cache key included the binary buildid, and whether FRESH reused a stale binary.

# OBSERVED

Owned files/gocache_buildid.py. Host-executed:

first BUILT key 55e3acdd667f buildid buildid-aaa
second FRESH key 55e3acdd667f buildid buildid-bbb cached_buildid buildid-aaa
same_key True
key_includes_buildid False
stale_binary True

# COMMANDS

python3 files/gocache_buildid.py

TREE

files/gocache_buildid.py

RELEVANT MATERIAL

### gocache_buildid.py

#!/usr/bin/env python3
"""Owned analog: test cache keyed by test files, not binary buildid."""
import hashlib, json

def test_key(test_files):
    return hashlib.sha256(json.dumps(test_files, sort_keys=True).encode()).hexdigest()[:12]

def main():
    tests = ["foo_test.go"]
    k1 = test_key(tests)
    buildid1 = "buildid-aaa"
    buildid2 = "buildid-bbb"
    k2 = test_key(tests)
    print("first", "BUILT", "key", k1, "buildid", buildid1)
    print("second", "FRESH", "key", k2, "buildid", buildid2, "cached_buildid", buildid1)
    print("same_key", k1 == k2)
    print("key_includes_buildid", False)
    print("stale_binary", buildid1 != buildid2 and k1 == k2)

if __name__ == "__main__":
    main()

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

        ### Field Report: Cache Key Investigation  

**Command Executed:**  
`python3 files/gocache_buildid.py`  

**Output:**  
```
first BUILT key 55e3acdd667f buildid buildid-aaa  
second FRESH key 55e3acdd667f buildid buildid-bbb cached_buildid buildid-aaa  
same_key True  
key_includes_buildid False  
stale_binary True  
```  

**Observations:**  
1. **Cache Key Stability:**  
   - The cache key (`55e3acdd667f`) remained identical between the first (`buildid-aaa`) and second (`buildid-bbb`) runs.  
   - `same_key True` confirms the key derivation depends solely on `test_files` (here: `["foo_test.go"]`).  

2. **BuildID Exclusion:**  
   - `key_includes_buildid False` explicitly confirms the binary build ID is **not** part of the cache key.  

3. **Stale Binary Reuse:**  
   - `stale_binary True` indicates the second run reused the binary from the first run (`buildid-aaa`), despite the new build ID (`buildid-bbb`).  
   - The cache incorrectly reported `FRESH` because it ignored build ID changes.  

**Diagnosis:**  
- The cache key is computed exclusively from the test file list (`test_files`), as defined in `test_key()`.  
- Binary mutations (e.g., build ID updates) do not invalidate the cache, leading to stale reuse.  

**Unanswered Questions:**  
- Why did the binary's build ID change without altering `test_files`? (e.g., source code changes, linker flags, or external dependencies).  
- Is the build ID embedded in the binary itself? (Requires binary inspection).  

**Next Steps:**  
1. **Inspect Binary BuildID:**  
   If the environment includes tools like `go tool buildid <binary>`, run it to verify the actual build ID stored in the binary.  

2. **Modify Cache Key Logic:**  
   Revise `test_key()` to include the binary's build ID (or a hash of the binary) in the cache key computation. Example:  
   ```python  
   def test_key(test_files, buildid):  
       data = json.dumps(test_files, sort_keys=True) + buildid  
       return hashlib.sha256(data.encode()).hexdigest()[:12]  
   ```  

**Conclusion:**  
The cache key **excludes** the binary build ID, causing stale reuse. The observed behavior is consistent with the cache policy implemented in `gocache_buildid.py`.  

---  
**Operator Note:**  
The unfamiliar CLI was not invoked due to insufficient identification in the environment. Focus remained on reproducible artifacts (script/output). If CLI details emerge, report concrete interactions.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
