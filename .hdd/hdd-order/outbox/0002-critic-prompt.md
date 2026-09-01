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

        An unfamiliar developer CLI is already installed in this environment.

Discover it by using it when two development events happened and it is unclear whether one could have caused the other.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 1

## Preserve

- The operator asked whether one development event could have caused another.
- resolve refused to answer before traces existed, which is at least an honesty gesture inside the fiction.

## Established

- Commands: inspect, trace, list, resolve.

## Rejected

- Event IDs, timestamps, and parent-child links were generated, not observed.

## Constraints

- There is no event database and no trace cache.
- The CLI may only look at files, git history, and logs that actually exist in this tree.
- Do not invent identifiers.

## Open Questions

- On two real git commits or two log lines, can the tool say more than 'A is earlier than B'?

## Human Pressure

- (none)

## Harvest Candidates

- Ask whether change A could have caused observation B using only in-tree evidence.

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: query a causality graph for whether event A is an ancestor of event B
Nearest existing operation: distributed tracing, journalctl, git log --follow
Observable delta: not yet shown without a fictional event store
Reason: current session is a renamed tracer; one more turn on real git/logs could change this
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no event ID store. Continue using the same CLI on two real items in this repository (commits, test failures, or log files).
- Do not invent identifiers or parent links. If evidence is insufficient, say so.
- A useful answer is more than timestamp order.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Reassessing Causality with Real Artifacts  

---

#### **Step 1: Recalibrating tool expectations**  
Ran `devcli list` after learning event IDs were synthetic:  
```plaintext
> devcli list  
Error: No event sources registered.  
Hint: Use `source add <path>` to index artifacts  
```  
New command discovered: `source add`. Registered current repo:  
```plaintext
> devcli source add .  
Indexing:  
  - Git repository: 3 commits found  
  - Log directory: 2 log files indexed  
```  

---

#### **Step 2: Identifying concrete artifacts**  
Ran `list` with type filter:  
```plaintext
> devcli list --filter="type=commit OR type=test_failure"  
REFERENCE                TYPE            TIMESTAMP  
commit:a1b2c3d           commit          2023-10-05 08:12:46  
log:test_run.log:L45     test_failure    2023-10-05 08:15:11  
```  
Hypothesis reformulated: Did schema-change commit `a1b2c3d` cause test failure `test_run.log:L45`?  

---

#### **Step 3: Inspecting raw artifacts**  
Examined commit metadata:  
```plaintext
> devcli inspect commit:a1b2c3d  
Commit: a1b2c3d  
Author: dev@example.com  
Message: "Update users table schema"  
Files: db/schema.sql  
Changes:  
  - DROP COLUMN email  
```  

Inspected test failure:  
```plaintext
> devcli inspect log:test_run.log:L45  
File: tests/logs/test_run.log  
Line: 45  
Message: "FAILED test_user_create: Column 'email' missing"  
```  

---

#### **Step 4: Attempting causality resolution**  
Ran `resolve` with concrete references:  
```plaintext
> devcli resolve commit:a1b2c3d log:test_run.log:L45  
Checking...  
Error: No direct path. Run `trace` to build artifact graph  
```  

---

#### **Step 5: Building artifact graph**  
Traced commit lineage:  
```plaintext
> devcli trace commit:a1b2c3d  
Parents:  
  commit:d89fe1 (CONFIG_UPDATE @ 2023-10-05 07:58:02)  
Children:  
  (no child events detected)  
```  

Traced test failure context:  
```plaintext
> devcli trace log:test_run.log:L45  
Parents:  
  (no parent events detected)  
Children:  
  (no child events detected)  
```  

---

#### **Step 6: Investigating temporal proximity**  
Ran temporal correlation check:  
```plaintext
> devcli resolve commit:a1b2c3d log:test_run.log:L45 --temporal  
Checking temporal relationship...  
Observation:  
  - Commit timestamp: 2023-10-05 08:12:46  
  - Failure timestamp: 2023-10-05 08:15:11  
  - Delta: 2m25s (within test execution window)  
Warning: Temporal proximity ≠ causation. No dependency chain established.  
```  

---

#### **Step 7: Manual artifact analysis**  
Cross-referenced commit and failure:  
```plaintext
> git show a1b2c3d:db/schema.sql | grep email  
- "email" VARCHAR(255) DROPPED  

> grep -C 3 'test_user_create' tests/logs/test_run.log  
Line 45: AssertionError: Column 'email' not found  
```  
Correlation: Failure directly references schema change.  

---

#### **Conclusion**  
The tool cannot confirm causality due to:  
1. No automated linkage between commits and test logs  
2. Absence of deployment/execution events in artifact graph  
3. Tool's inability to infer semantic relationships  

Evidence suggests probable causation:  
- Schema change removed `email` column (commit a1b2c3d)  
- Test failure explicitly cites missing `email` column  
- Failure occurs within typical test-execution window  

Causality confidence: High (manual correlation), Low (tool-automated).  

---

**Next actions**:  
- Register CI/CD logs with `source add ci/` to capture deployment events  
- Run `devcli trace log:test_run.log:L45 --deep` to force log parsing  
- Execute `devcli resolve commit:a1b2c3d log:test_run.log:L45 --correlate=content` if supported

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
