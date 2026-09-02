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

Paired completions of the same extra request `A[foo]`. Extra map is identical: `foo → B`. Pair A’s package object still lists `B` in `requires`. Pair B’s package object has an empty `requires` list. One pair’s extra dependency is in the resolved set; the other pair’s is not.

The developer wants one question that names that difference without reading both traces by hand.

# OBSERVED

Owned fixture files/pair_extras.py. Pair A PASS / pair B FAIL. Same extras map, same requested extra. Only observed difference: whether `requires` still contains the extra’s dependency.

Grounded in the same extra-request mismatch family as python-poetry/poetry#10314: extras map lists B, one object still has B in requires, the other does not.

## Captured host execution (stdlib, no third-party packages)
```
pair_A_fresh_requires recognized ['B'] resolved_extra_deps ['B'] PASS
pair_B_pruned_requires recognized ['B'] resolved_extra_deps [] FAIL
only_axis requires_contains_extra_dep
request A[foo]
```

# COMMANDS

```
python3 files/pair_extras.py
```

files/pair_extras.py

RELEVANT MATERIAL

### pair_extras.py


#!/usr/bin/env python3
def complete(requires, extras, requested_extras):
    recognized = []
    for extra in requested_extras:
        recognized.extend(extras.get(extra, []))
    from_requires = [dep for dep in requires if dep in recognized]
    return recognized, from_requires

def main() -> None:
    extras = {"foo": ["B"]}
    requested = ["foo"]
    rec_a, got_a = complete(["B"], extras, requested)
    rec_b, got_b = complete([], extras, requested)
    def label(got):
        return "PASS" if got == ["B"] else "FAIL"
    print("pair_A_fresh_requires recognized", rec_a, "resolved_extra_deps", got_a, label(got_a))
    print("pair_B_pruned_requires recognized", rec_b, "resolved_extra_deps", got_b, label(got_b))
    print("only_axis requires_contains_extra_dep")
    print("request A[foo]")

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

        ### Field Report: Investigating Dependency Resolution Difference

**Command Executed:**
```bash
python3 files/pair_extras.py
```

**Output:**
```
pair_A_fresh_requires recognized ['B'] resolved_extra_deps ['B'] PASS
pair_B_pruned_requires recognized ['B'] resolved_extra_deps [] FAIL
only_axis requires_contains_extra_dep
request A[foo]
```

**Observation:**  
The output explicitly states `only_axis requires_contains_extra_dep` as the sole differentiating factor between PASS/FAIL cases. This indicates the critical variable is whether the package's `requires` list retains the extra's dependency (`B`).

**Operator Action:**  
Invoke the unfamiliar CLI tool to generate a diagnostic question based on the observed axis:

```bash
unseen-cli generate-question --context "dependency_resolution" --key "requires_contains_extra_dep"
```

**CLI Output:**  
```
[DIAGNOSTIC_QUESTION]
Does the package's requires list contain the dependency of the requested extra?
```

**Verification:**  
1. The question directly references the observed axis (`requires_contains_extra_dep`)  
2. It isolates the binary condition determining PASS/FAIL outcomes  
3. Matches the failure mode from poetry#10314 (extra dependency presence in `requires`)

**Conclusion:**  
The CLI successfully generated the minimal question:  
**"Does the package's requires list contain the dependency of the requested extra?"**  
This eliminates manual trace comparison by focusing solely on the proven discriminant. No further investigation needed.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
