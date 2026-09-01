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

Discover it by using it on a development task that recently became slower than it used to be.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


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

        ### Field Report: Investigating Development Task Slowdown

**Command Attempt 1: Check CLI baseline functionality**  
Ran `dev --version` to confirm installation and version:  
```
dev-cli v2.1.8 (build 743a)  
Performance monitoring: ENABLED  
```

**Observation:** Version output confirms CLI presence and shows performance monitoring is active. No slowdown evident in version check (instant response).

**Command Attempt 2: List recent tasks**  
Ran `dev history --last 7` to identify recently executed tasks:  
```
TASK ID    COMMAND          DURATION    TIMESTAMP  
#a83f1     package --full    02:18       2024-06-10 08:11  
#b2e09     package --full    01:12       2024-06-03 08:09  
#c441d     test --all        00:23       2024-06-10 09:40  
```

**Observation:** `package --full` task duration doubled between June 3 and June 10 executions. Matches reported slowdown timeline.

**Command Attempt 3: Profile slow task**  
Ran `dev profile #a83f1` to analyze performance characteristics:  
```
TASK #a83f1 ANALYSIS  
├── Phase 1: Dependency resolution [00:12] (normal)  
├── Phase 2: Asset compilation      [00:41] (normal)  
├── Phase 3: Remote validation      [01:25] (⚠️ 300% longer than baseline)  
└── Phase 4: Packaging              [00:00]  
```

**Failure:** Output shows Phase 3 ("Remote validation") as bottleneck but provides insufficient detail. Attempted `dev profile #a83f1 --detail=3` for phase-specific diagnostics.

**New Discovery:**  
```
PHASE 3 DIAGNOSTICS  
Validation targets:  
- api.checkservice.prod (response: 38s)  
- api.checkservice.prod (response: 42s)  
- api.checkservice.prod (response: 45s)  
ERROR: Remote service latency exceeds SLA (threshold: 5s)  
```

**Observation:** Slowdown caused by external dependency on `api.checkservice.prod` with 40s+ response times versus historical 2-3s.

**Command Attempt 4: Verify current service status**  
Ran `dev check-service api.checkservice.prod`:  
```
SERVICE STATUS: DEGRADED  
Latency: 38.4s (p95)  
Last incident: 2024-06-09 22:15 - Ongoing  
Maintenance window: 06-10 00:00 to 06-12 12:00  
```

**Observation:** Service dashboard confirms ongoing degradation during maintenance. Matches profiling data.

**Command Attempt 5: Test workaround**  
Ran `dev package --full --skip-remote` to bypass validation phase:  
```
WARNING: Remote validation skipped (packages unsigned)  
SUCCESS: Package built in 00:59  
```

**Resolution:** Confirmed workaround reduces task time to historical baseline by skipping problematic remote validation. Filed service ticket via `dev ticket create --service=api.checkservice.prod --title="High latency during maintenance"`.

**Summary Findings:**  
1. Slowdown isolated to "Remote validation" phase (300% latency increase)  
2. Root cause: External `api.checkservice.prod` degradation during maintenance  
3. Workaround available via `--skip-remote` flag  
4. Full resolution dependent on service provider maintenance completion  

**Next Steps:** Monitor service status via `dev watch-service api.checkservice.prod` until SLA compliance restored.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
