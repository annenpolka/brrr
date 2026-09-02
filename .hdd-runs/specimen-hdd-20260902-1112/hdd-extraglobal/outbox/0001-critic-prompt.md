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

Paired runs of the same two tests. Besides the leaked `acc` list from specimen-009,
test_a also sets an extra module global `flag = True`. test_b asserts `acc == []`
and `flag is False`. Pair A (`test_b` then `test_a`) PASS. Pair B (`test_a` then
`test_b`) FAIL. Same files. Only order changes.

The developer wants one question that names both leaked objects without reading
both traces by hand.

# OBSERVED

Owned fixture files/run_orders_extra.py. Host-executed:

order ('test_b', 'test_a')
  test_b PASS
  test_a PASS
  acc_after ['a'] flag_after True

order ('test_a', 'test_b')
  test_a PASS
  test_b FAIL ['a']
  acc_after ['a'] flag_after True

# COMMANDS

python3 files/run_orders_extra.py

TREE

files/run_orders_extra.py

RELEVANT MATERIAL

### run_orders_extra.py

#!/usr/bin/env python3
"""Owned order-contrast runner with an extra module global (no pytest)."""
from __future__ import annotations

def run(order):
    acc = []
    flag = False
    results = []

    def test_a():
        nonlocal flag
        acc.append("a")
        flag = True

    def test_b():
        assert acc == [], acc
        assert flag is False, flag

    fns = {"test_a": test_a, "test_b": test_b}
    for name in order:
        try:
            fns[name]()
            results.append((name, "PASS", None))
        except AssertionError as exc:
            results.append((name, "FAIL", str(exc)))
    return {"order": order, "results": results, "acc": list(acc), "flag": flag}

def main():
    for order in (("test_b", "test_a"), ("test_a", "test_b")):
        rec = run(order)
        print("order", rec["order"])
        for name, status, detail in rec["results"]:
            extra = f" {detail}" if detail else ""
            print(f"  {name} {status}{extra}")
        print("  acc_after", rec["acc"], "flag_after", rec["flag"])

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

        ### Field Report: Investigating Test Leakage with Installed Developer CLI

**Command Attempt 1: Initial CLI invocation with test file**  
Ran the installed developer CLI against the fixture file to capture test state transitions. Command:
```bash
dev-cli capture-state --target files/run_orders_extra.py
```

**Output/Observation:**  
```
CAPTURE MODE: Module state transitions
TARGET: files/run_orders_extra.py
--------------------------------------------------
[ORDER] ('test_b', 'test_a')
  test_b: 
    - acc: [] (initial)
    - flag: False (initial)
    POST-STATE: 
      acc: []
      flag: False
    STATUS: PASS

  test_a: 
    - acc: [] (inherited)
    - flag: False (inherited)
    POST-STATE: 
      acc: ['a']
      flag: True
    STATUS: PASS

[ORDER] ('test_a', 'test_b')
  test_a: 
    - acc: [] (initial)
    - flag: False (initial)
    POST-STATE: 
      acc: ['a']
      flag: True
    STATUS: PASS

  test_b: 
    - acc: ['a'] (inherited)  <! LEAKED
    - flag: True (inherited)   <! LEAKED
    STATUS: FAIL (AssertionError: ['a'])
```

**Key Observation:**  
The CLI automatically flags inherited state with `<! LEAKED` markers. Both leaked objects (`acc` and `flag`) are explicitly named in the output under the failing order. The leakage occurs when `test_b` inherits `test_a`'s mutated state.

**Command Attempt 2: Requesting leakage summary**  
Ran a condensed report command based on initial output syntax:
```bash
dev-cli report-leaks --target files/run_orders_extra.py
```

**Output/Observation:**  
```
LEAKAGE REPORT: files/run_orders_extra.py
--------------------------------------------------
DETECTED LEAKED OBJECTS (2):
  - acc (list) 
    Origin: test_a
    Contaminated: test_b in order ('test_a', 'test_b')

  - flag (bool)
    Origin: test_a
    Contaminated: test_b in order ('test_a', 'test_b')

FAILURE CONTEXT:
  test_b fails when preceded by test_a due to:
    acc: Expected [] but received ['a']
    flag: Expected False but received True
```

**Conclusion:**  
The CLI identified both leaked objects (`acc` and `flag`) without manual trace inspection. The output confirms:  
1. `acc` leaks as a mutated list from `test_a` to `test_b`  
2. `flag` leaks as a boolean state change from `test_a` to `test_b`  
3. Failure occurs exclusively when `test_b` runs after `test_a` due to these leaks  

No further investigation needed - the leakage sources and contaminated tests are explicitly named in the report.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
