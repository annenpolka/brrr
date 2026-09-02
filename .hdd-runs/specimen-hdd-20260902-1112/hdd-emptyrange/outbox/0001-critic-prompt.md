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

A unified-diff hunk `@@ -2,0 +3 @@` plus `+inserted` is applied to `first\nsecond\nthird\n`. The applier reports success (exit 0), including a frozen-lockfile-style install path. The resulting bytes are not the file the hunk coordinates name.

The developer wants to know which original line the empty old-range was treated as, and why success did not mean the recorded gap.

# OBSERVED

Owned fixture files/patch_insert.py. Transfer of pnpm/pnpm#14343 (Rust patch applier in a Node package-manager install) into a stdlib Python applier.

Public contrast from that PR (not a local pnpm run): given `first\nsecond\nthird\n`, hunk `@@ -2,0 +3 @@` / `+inserted` must yield `first\nsecond\ninserted\nthird\n`. The affected applier yielded `first\ninserted\nsecond\nthird\n` and still reported a successful install, including `--frozen-lockfile`.

## Captured host execution (stdlib, no third-party packages)
```
orig 'first\nsecond\nthird\n'
hunk @@ -2,0 +3 @@ +inserted
result 'first\ninserted\nsecond\nthird\n'
apply_exit 0
frozen_lockfile_install success
```

# COMMANDS

```
python3 files/patch_insert.py
```

files/patch_insert.py

RELEVANT MATERIAL

### patch_insert.py


#!/usr/bin/env python3
def apply_hunk(text: str, old_start: int, old_count: int, insert: str) -> str:
    lines = text.splitlines(keepends=True)
    idx = old_start - 1
    if not insert.endswith("\n"):
        insert += "\n"
    lines.insert(idx, insert)
    return "".join(lines)

def main() -> None:
    orig = "first\nsecond\nthird\n"
    out = apply_hunk(orig, old_start=2, old_count=0, insert="inserted\n")
    print("orig", repr(orig))
    print("hunk", "@@ -2,0 +3 @@ +inserted")
    print("result", repr(out))
    print("apply_exit", 0)
    print("frozen_lockfile_install", "success")

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

        ### Field Report: Investigating Patch Application Anomaly

**OPERATOR ACTION**  
Executed provided command to reproduce the issue:  
```bash
python3 files/patch_insert.py
```

**OBSERVED OUTPUT**  
```
orig 'first\nsecond\nthird\n'
hunk @@ -2,0 +3 @@ +inserted
result 'first\ninserted\nsecond\nthird\n'
apply_exit 0
frozen_lockfile_install success
```

**ANOMALY CONFIRMATION**  
- Expected result based on unified-diff spec: `first\nsecond\ninserted\nthird\n`  
- Actual result: `first\ninserted\nsecond\nthird\n`  
- Exit code 0 indicates successful application despite misplacement  

**OPERATOR ACTION**  
Inspected the `apply_hunk` function logic in `patch_insert.py`:  
```python
def apply_hunk(text: str, old_start: int, old_count: int, insert: str) -> str:
    lines = text.splitlines(keepends=True)
    idx = old_start - 1  # Converts to 0-indexed position
    if not insert.endswith("\n"):
        insert += "\n"
    lines.insert(idx, insert)  # Inserts BEFORE line at calculated index
    return "".join(lines)
```

**KEY OBSERVATION**  
- `old_start=2` → `idx=1` (0-indexed)  
- `lines.insert(1, ...)` inserts BEFORE existing line 1 (second line)  
- Unified diff `@@ -2,0 +3 @@` expects insertion AFTER old line 2  

**HYPOTHESIS**  
The applier treats `old_start` as the insertion target line rather than the contextual anchor for the subsequent new line.  

**OPERATOR ACTION**  
Modified insertion index to use `old_start` (without -1 offset):  
```python
idx = old_start  # Changed from old_start-1
```

Re-executed command:  
```bash
sed -i 's/idx = old_start - 1/idx = old_start/' files/patch_insert.py
python3 files/patch_insert.py
```

**OBSERVED OUTPUT**  
```
orig 'first\nsecond\nthird\n'
hunk @@ -2,0 +3 @@ +inserted
result 'first\nsecond\ninserted\nthird\n'
apply_exit 0
frozen_lockfile_install success
```

**RESOLVED BEHAVIOR**  
- Empty old-range `-2,0` was originally treated as "insert BEFORE line 2"  
- Correct behavior: "insert AFTER line 2" per unified diff semantics  
- Success reported because:  
  1. Index calculation stayed within bounds (1→2 for 3-line file)  
  2. No content validation occurs after insertion  
  3. Exit code only reflects mechanical application success  

**CONCLUSION**  
The empty old-range starting at line 2 was misinterpreted as an insertion *target* rather than contextual *anchor*. The applier lacks context verification, allowing success when mechanical insertion succeeds regardless of semantic correctness.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
