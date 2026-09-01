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

Discover it by using it on a failing test whose failure message does not obviously name the real cause.

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

        ### Field Report: Investigating Test Failure with Unfamiliar CLI

**Step 1: Initial Test Execution**  
Ran the CLI's test command on the failing test suite:  
```bash
mystery-cli test --filter TestResourceAllocation
```
**Output:**  
```
[FAIL] TestResourceAllocation (0.42s)  
Error: Allocation mismatch - expected 512MB, actual: 0MB  
  at allocator.go:72 (AllocateResource)  
  at resource_test.go:115 (TestResourceAllocation)
```
*Observation:* Failure message indicates resource allocation discrepancy but provides no insight into *why* allocation returns 0MB. Stack trace points to implementation and test code equally.

**Step 2: Debug Session Initialization**  
Attempted to debug the specific test case:  
```bash
mystery-cli debug-test TestResourceAllocation --breakpoint allocator.go:70
```
**Output:**  
```
Debug session initialized  
⏳ Hitting breakpoint at allocator.go:70  
> func AllocateResource(ctx Context) (int, error) {  
    // Breakpoint set at resource calculation start  
```
*Observation:* CLI entered interactive debug mode successfully. Breakpoint hit at expected location.

**Step 3: State Inspection**  
Examined runtime state at breakpoint:  
```bash
(dbg) print ctx
```
**Output:**  
```
Context{  
  UserID: "user-7f3a",  
  Priority: HIGH,  
  Env: "production",  
  RequestedMB: 512,  
  AvailableMB: 2048  
}
```
```bash
(dbg) step
```
**Output:**  
```
Stepped into calculateQuota()  
> func calculateQuota(user string) int {  
    // Quota calculation logic
```
*Observation:* Context appears valid. Stepped into quota calculation function.

**Step 4: Quota Calculation Check**  
Inspected quota logic execution:  
```bash
(dbg) print user
"user-7f3a"
```
```bash
(dbg) step 5
```
**Output:**  
```
Stepped through:  
  line 42: quota := fetchUserQuota(user)  
  line 43: if quota == -1 { return 0 }  
  line 45: return applyModifiers(quota)  
```
```bash
(dbg) print quota
-1
```
*Observation:* Critical discovery - `fetchUserQuota` returns -1, triggering fallback to 0MB allocation. Failure message never mentioned user quota lookup.

**Step 5: Dependency Tracing**  
Traced origin of invalid quota value:  
```bash
(dbg) break fetchUserQuota
```
```bash
(dbg) continue
```
**Output:**  
```
Hitting breakpoint at storage.go:203  
> func fetchUserQuota(userID string) int {
```
```bash
(dbg) print userID
"user-7f3a"
```
```bash
(dbg) step
```
**Output:**  
```
>   return cache.Lookup(userID, "quota")
```
```bash
(dbg) eval cache.IsConnected()
false
```
*Observation:* Cache service disconnected. Queries return default -1 value. Test failure root cause is unavailable dependency, not logic error.

**Step 6: Validation**  
Confirmed hypothesis by forcing cache reconnection:  
```bash
(dbg) exec cache.Connect()
```
```bash
(dbg) continue
```
**Output:**  
```
Test passed after cache reconnection  
[PASS] TestResourceAllocation (0.39s)
```

**Conclusion:**  
The CLI's debugging capabilities revealed the true failure path:  
1. Disconnected cache service  
2. Quota lookup returns sentinel value (-1)  
3. Allocation logic interprets -1 as 0MB  
4. Test fails with allocation mismatch  

The original error message obscured this chain by focusing solely on the numeric discrepancy. The CLI enabled concrete observation of runtime state transitions across three layers (test → allocation → storage). No speculative tooling required.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
