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

Two tests share a module-level list. One test appends. The other asserts the list is empty. Depending on collection/run order, the suite is green or red. The developer wants a first-class view of *what leaked between tests* and *which order is sufficient to expose it*.

# OBSERVED

See files/test_order.py. Captured on this lab host (owned fixture, not untrusted OSS):

```
python3 -m pytest files/test_order.py -q --tb=line
# default file order (test_a then test_b): FAIL test_b
python3 -m pytest files/test_order.py::test_b files/test_order.py::test_a -q --tb=line
# reverse: PASS
```

## Captured host execution
```
--- reverse ---
```

## Captured host execution (stdlib runner, no pytest)
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

# COMMANDS

```
python3 -m pytest files/test_order.py -q --tb=line
python3 -m pytest files/test_order.py::test_b files/test_order.py::test_a -q --tb=line
```

files/test_order.py

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

        ### Field Report: Investigating Test Leakage with Installed CLI Tool

**Operational Context:**  
After observing intermittent test failures due to shared mutable state (`acc` list) in `test_order.py`, I attempted to use the environment's pre-installed developer CLI tool (detected as `testflow-analyzer` via `which` command) to diagnose leakage and order dependencies. The tool appears specialized for test suite analysis.

**Concrete Investigation Steps:**

1. **Initial Tool Invocation:**  
   Ran the CLI against the test file to capture baseline leakage diagnostics:
   ```bash
   testflow-analyzer capture files/test_order.py --output=leakage-scan.json
   ```
   **Output:**  
   ```
   [CAPTURE] State snapshot at module level:
   - Module: test_order
     Variables: ['acc: []']
   [WARNING] Mutable module state detected (1 variable)
   Proceeding with test isolation analysis...
   ```

2. **Order-Dependent Failure Reproduction:**  
   Executed the tool's order permutation mode to systematically test execution sequences:
   ```bash
   testflow-analyzer permute files/test_order.py --max-orders=2
   ```
   **Output:**  
   ```
   ===== ORDER 1: [test_a, test_b] =====
   RUN test_a: PASS
   RUN test_b: FAIL (State delta: acc=['a'])
   ! Leak detected: Variable 'acc' modified by test_a

   ===== ORDER 2: [test_b, test_a] =====
   RUN test_b: PASS
   RUN test_a: PASS
   No state leakage detected
   ```

3. **Detailed Leakage Report:**  
   Generated a dedicated leakage artifact using the initial capture:
   ```bash
   testflow-analyzer report leakage-scan.json --format=verbose
   ```
   **Output Excerpt:**  
   ```
   LEAKAGE SOURCES:
   ┌───────────┬──────────────┬───────────────────────────────┐
   │ Test      │ Variable     │ Impacted Tests               │
   ├───────────┼──────────────┼───────────────────────────────┤
   │ test_a    │ acc (list)   │ test_b (fails if run after)   │
   └───────────┴──────────────┴───────────────────────────────┘

   CRITICAL PATHS:
   - Failure observed in sequences where test_b executes AFTER test_a
   ```

4. **Validation with Known Failure:**  
   Explicitly tested the failing order using tool's direct execution:
   ```bash
   testflow-analyzer run files/test_order.py::test_a files/test_order.py::test_b
   ```
   **Output:**  
   ```
   EXECUTION ORDER: test_a → test_b
   test_a: PASS (State change: acc=['a'])
   test_b: FAIL - AssertionError: ['a'] != []
   ! Leaked state: acc preserved from test_a
   ```

**Key Observations:**  
- The CLI tool automatically detected mutable module state (`acc`) as a leakage risk  
- Confirmed failure occurs ONLY when `test_b` runs after `test_a`  
- Identified `test_a` as the source of leaked state  
- Tool outputs show concrete state deltas (`acc=['a']`) between tests  
- No false negatives: Passing orders show "No state leakage detected"

**Unresolved Questions:**  
- Why does `acc` persist between tests? (Tool indicates module reload behavior not observed)  
- Are other variables vulnerable? (Scan showed only `acc` as mutable state)  

**Next Steps:**  
- Use tool's `--track=all` flag to log variable changes during execution  
- Attempt cleanup hooks via `testflow-analyzer inject-cleanup` to reset state  

**Tool Limitations Encountered:**  
- Cannot explain WHY module state persists (interpreter reload mechanism?)  
- No auto-fix capability for identified leakage paths  

**Conclusion:**  
The CLI tool successfully provided:  
1. First-class leakage report showing `acc` modified by `test_a` impacts `test_b`  
2. Precise order dependency: Failure manifests exclusively in `test_a`→`test_b` sequence  
3. Concrete evidence via state snapshots eliminating speculation about failure conditions

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
