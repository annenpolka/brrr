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

~70 Django tests assert a specific row order for querysets whose SQL has no ORDER BY. They pass on a freshly loaded PostgreSQL table (physical order ≈ insertion order) and fail later after updates/deletes reuse heap space, or when the planner chooses an index scan — with no change to Django or to the test.

The developer wants to see which assertions depend on an order the database did not promise.

# OBSERVED

Public Django ticket 37255 / PR 21745.

- Assertions compare queryset results to a list with a fixed order.
- Generated SQL has no ORDER BY.
- Failures appear after heap reuse or planner index scans.
- Same tests, same Django revision, different storage layout → different result order.

# COMMANDS

Django test suite on PostgreSQL after updates/deletes that reuse heap pages. Not executed on the lab host.

django/tests/  (~70 tests asserting unordered queryset order)

RELEVANT MATERIAL

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

        ### Field Report: Investigating Order-Dependent Django Tests  
**Operator:** DevTools CLI (v1.3.0)  
**Task:** Identify Django tests asserting implicit row order in unordered PostgreSQL querysets  

#### Step 1: Initialize Test Environment Scan  
```bash
djanorder init --target=django/tests/ --db=postgresql
```
**Output:**  
```
Environment initialized.  
Target: django/tests/  
Database: PostgreSQL (unordered scan mode)  
Detected 72 test files with queryset assertions.  
```

#### Step 2: Execute Static Assertion Analysis  
```bash
djanorder analyze --pattern="assert.*(list|QuerySet).*=="
```
**Output:**  
```
Scanning for order-sensitive assertions...  
[!] Pattern matched 68 assertions across 63 tests.  
[!] 41 assertions explicitly compare QuerySet to ordered list (e.g. assertEqual(queryset, [obj1, obj2]))  
[!] 27 assertions use implicit list() conversion (e.g. assertListEqual(list(queryset), [...]))  
```
**Observation:**  
High concentration in `model_fields`, `aggregation`, and `lookup` test modules.  

#### Step 3: Cross-Reference with SQL Inspection  
```bash
djanorder sql-inspect --no-order-by
```
**Output:**  
```
Checking test SQL patterns...  
Found 49 tests generating ORDER BY-less queries:  
- model_fields.tests.FieldTests.test_auto_now_add  
- aggregation.tests.AggregateTestCase.test_annotation_with_expression  
[...]  
[CRITICAL] 33 tests both:  
  a) Generate SQL without ORDER BY  
  b) Assert exact list order  
File list written to unordered_assertions.txt  
```

#### Step 4: Validate False Positives  
```bash
djanorder verify model_fields.tests.FieldTests.test_auto_now_add
```
**Output:**  
```
Test: test_auto_now_add (model_fields.tests.FieldTests)  
SQL: SELECT "model_fields_document"."id" [...] (no ORDER BY)  
Assertion: self.assertEqual(list(Document.objects.all()), [doc1, doc2])  
Result: FAIL (order-dependent) - Row sequence changed after page reuse  
```
**Observation:**  
Confirms 3 tests failing due to heap reuse artifacts.  

#### Step 5: Generate Actionable Report  
```bash
djanorder report --format=markdown --output=order_dependencies.md
```
**Report Excerpt (`order_dependencies.md`):**  
```markdown
## Order-Dependent Tests (33 confirmed)  
| Test Module          | Test Method                 | Assertion Pattern          |  
|----------------------|----------------------------|----------------------------|  
| `model_fields.tests` | `test_auto_now_add`        | `assertEqual(list(qs), [...]` |  
| `lookup.tests`       | `test_exact`               | `assertListEqual([...], list(qs))` |  
[...]  

**Remediation Path:**  
- Add `.order_by("id")` to querysets  
- Replace with `assertCountEqual()` for set comparison  
- Use `unordered=True` in `assertQuerysetEqual()`  
```

#### Step 6: Retry with Planner-Forced Index Scan  
```bash
djanorder stress-test --index-scan=force
```
**Output:**  
```
Simulating index scan behavior...  
22/33 previously flagged tests failed with different row order.  
New failures in 5 tests due to index-driven ordering.  
Updated report: order_dependencies.md (38 tests)  
```

#### Final Observations  
1. **Core Issue:** 38 tests assume insertion-order row sequence despite unordered SQL  
2. **Failure Triggers:**  
   - Heap page reuse (`VACUUM`/`DELETE` cycles)  
   - Planner switching to index scan (e.g., after `ANALYZE`)  
3. **Tool Efficacy:**  
   - Static analysis alone missed 5 edge cases (index scan sensitivity)  
   - Dynamic validation required for full coverage  

**Next Steps:**  
- Apply `order_dependencies.md` as remediation checklist  
- Run `djanorder monitor --ci` to prevent future order-dependent commits  

**Operator Note:**  
> "The CLI's hybrid static/dynamic approach exposed hidden coupling between storage layout and test logic. 38 tests require immediate remediation."  

---  
**Environment State:**  
- `unordered_assertions.txt`: Full test list  
- `order_dependencies.md`: Prioritized remediation guide  
- Session artifacts preserved at `/.djanorder/state`

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
