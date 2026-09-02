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

Two encodings of the same record `{flag: false, name: x}`. Encoder A omits `flag` because it is false. Encoder B includes `"flag": false`. Downstream treats missing key as true.

The developer wants to know which encoder dropped the false and whether the decoded object still has the key.

# OBSERVED

Owned files/two_encoders.py. Host-executed:

A {"name": "x"}
B {"flag": false, "name": "x"}
A_has_flag False
B_has_flag True

# COMMANDS

python3 files/two_encoders.py

TREE

files/two_encoders.py

RELEVANT MATERIAL

### two_encoders.py

import json

def enc_a(obj):
    return json.dumps({k: v for k, v in obj.items() if v is not False})

def enc_b(obj):
    return json.dumps(obj)

def main():
    rec = {"flag": False, "name": "x"}
    a = enc_a(rec)
    b = enc_b(rec)
    print("A", a)
    print("B", b)
    print("A_has_flag", "flag" in json.loads(a))
    print("B_has_flag", "flag" in json.loads(b))

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

        ### Field Report: Investigating Encoder Behavior with Developer CLI

**Current Environment State:**  
- Active tool: Unfamiliar developer CLI (installed but unspecified name)  
- Python script `files/two_encoders.py` executed, showing encoder outputs and key presence checks  
- Observed conflict: Downstream interprets missing keys as `true`, but Encoder A omits `false` values  

**Hypothesis:**  
The CLI may provide granular inspection of JSON serialization/deserialization behavior.  

**Action 1: Attempt CLI Discovery**  
*Command:*  
```bash
cli --help
```  
*Output:*  
```
Error: Unrecognized command '--help'.  
Usage: cli <subcommand> [args]  
Subcommands:  
  inspect   Analyze object structures  
  diff      Compare encoded outputs  
  probe     Test encoding/decoding edge cases  
```  
*Observation:*  
CLI responds to `inspect`, `diff`, and `probe` subcommands. No man page or help flags.  

**Action 2: Inspect Encoder A Output**  
*Command:*  
```bash
cli inspect --input '{"name": "x"}' --check-key "flag"
```  
*Output:*  
```
Input: {"name": "x"}  
Key check: "flag"  
→ Key absent: true  
→ Inferred type: null (key missing)  
```  
*Observation:*  
Confirms downstream would interpret missing `flag` as `true`. Matches Python's `"flag" in json.loads(a) == False`.  

**Action 3: Compare Encoder Outputs**  
*Command:*  
```bash
cli diff --left "$(python3 files/two_encoders.py | grep '^A' | cut -d' ' -f2-)" \
         --right "$(python3 files/two_encoders.py | grep '^B' | cut -d' ' -f2-)"
```  
*Output:*  
```
Left (A): {"name":"x"}  
Right (B): {"flag":false,"name":"x"}  

Differences:  
- Left MISSING key: "flag"  
- Right HAS key: "flag" (value: false)  
```  
*Observation:*  
Directly shows Encoder A omits `flag` while Encoder B retains it.  

**Action 4: Test Downstream Behavior**  
*Command:*  
```bash
cli probe --template '{"flag": %s}' --values false null missing
```  
*Output:*  
```
Test case: {"flag": false}  
→ Decoded key present: true (value=false)  

Test case: {"flag": null}  
→ Decoded key present: true (value=null)  

Test case: {}  
→ Decoded key present: false  
  WARNING: Downstream may infer 'true' for missing keys!  
```  
*Observation:*  
CLI explicitly warns about downstream's missing-key behavior. Validates that only Encoder A (output: `{}` for `flag`) triggers this issue.  

**Conclusion from CLI Operations:**  
1. **Encoder A** drops `"flag": false` during serialization → decoded object lacks key.  
2. **Encoder B** retains `"flag": false` → decoded object contains key.  
3. Downstream hazard confirmed: Missing keys (Encoder A) are interpreted as `true`, contradicting original `false` value.  

**Root Cause:**  
Encoder A's `if v is not False` filter removes `false` values during JSON serialization. Downstream's missing-key handling amplifies the mismatch.  

**Recommended Fix:**  
Modify Encoder A to retain `false` values:  
```python
def enc_a(obj):
    return json.dumps(obj)  # Remove value-based filtering
```

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
