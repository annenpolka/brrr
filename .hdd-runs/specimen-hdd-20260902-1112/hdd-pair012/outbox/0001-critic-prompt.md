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

Paired runs of the same two tests. The only observed difference is test order. A: PASS. B: FAIL. The developer wants one question that names that difference without reading both traces by hand.

# OBSERVED

Pair A: `pytest test_b test_a` → PASS
Pair B: `pytest test_a test_b` → FAIL test_b assertion acc == []
Same files. Same interpreter. Only order changes.

# COMMANDS

Use files from specimen-009. A vs B as above.

files/test_order.py (same as specimen-009)

RELEVANT MATERIAL

### run_orders.py

#!/usr/bin/env python3
"""Owned order-contrast runner (no third-party pytest)."""
from __future__ import annotations


def run(order: tuple[str, ...]) -> dict:
    acc: list[str] = []
    results = []

    def test_a():
        acc.append("a")

    def test_b():
        assert acc == [], acc

    fns = {"test_a": test_a, "test_b": test_b}
    for name in order:
        try:
            fns[name]()
            results.append((name, "PASS", None))
        except AssertionError as exc:
            results.append((name, "FAIL", str(exc)))
    return {"order": order, "results": results, "acc": list(acc)}


def main() -> None:
    for order in (("test_a", "test_b"), ("test_b", "test_a")):
        rec = run(order)
        print("order", rec["order"])
        for name, status, detail in rec["results"]:
            extra = f" {detail}" if detail else ""
            print(f"  {name} {status}{extra}")
        print("  acc_after", rec["acc"])


if __name__ == "__main__":
    main()

### test_order.py

acc = []

def test_a():
    acc.append("a")

def test_b():
    assert acc == [], acc

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

        ### Field Report: Investigating Test Order Dependency  

**Command Sequence Executed:**  
```bash
python run_orders.py
```

**Output:**  
```
order ('test_a', 'test_b')
  test_a PASS
  test_b FAIL ['a']
  acc_after ['a']
order ('test_b', 'test_a')
  test_b PASS
  test_a PASS
  acc_after ['a']
```

**Observations:**  
1. **Order Dependency Confirmed:**  
   - When `test_a` runs before `test_b` (first order), `test_b` fails with `AssertionError: ['a']`.  
   - When `test_b` runs before `test_a` (second order), both tests pass.  
   - Identical to the `pytest` behavior described in the task.  

2. **Shared State Exposed:**  
   - The accumulator `acc` (a global list) is modified by `test_a` (appends `'a'`).  
   - `test_b` asserts `acc` must be empty.  
   - **Failure occurs when `test_a` contaminates `acc` before `test_b` runs.**  

3. **Tool Behavior:**  
   - The CLI (`run_orders.py`) explicitly logs `acc` state after each run:  
     - Failed run: `acc = ['a']` during `test_b`.  
     - Successful run: `acc = []` during `test_b` (then becomes `['a']` after `test_a`).  

**Operator Question for the Developer:**  
> "Is the test failure in order `test_a`→`test_b` caused by shared mutable state in the global variable `acc` that isn't reset between tests?"  

**Rationale:**  
- The CLI output directly exposes `acc` as the shared state corrupted by test order.  
- No trace analysis needed: the tool surfaces the variable and its invalid state at failure.  
- This isolates the defect to **inter-test dependency via global mutable data**, narrowing the investigation to state cleanup.  

**Next Steps (if needed):**  
```bash
# Hypothetical: If the CLI supported state inspection flags (not implemented here)
# python run_orders.py --inspect-state=acc
# ERROR: Unknown flag '--inspect-state'
```  
**Outcome:** The tool's output suffices to name `acc` as the critical difference. No further commands required.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
