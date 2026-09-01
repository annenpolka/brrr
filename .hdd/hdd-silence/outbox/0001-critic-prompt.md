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

Discover it by using it when a development command exited successfully but the operator does not trust that success.

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

        ### Field Report: Investigating Untrusted Command Success

**Situation:**  
After running `dev deploy production` which reported success (exit code 0), external monitoring alerts indicate the application is unreachable. The tool (`dev`) is unfamiliar and non-Unix-like. I suspect a false positive.

---

#### Step 1: Verify system state via tool primitives  
```bash
$ dev system-status
```
**Output:**  
```
SERVICES:
  frontend: [DEPLOYED] (last: 2024-05-20T14:30:00Z)
  database: [RUNNING]
  cache: [RUNNING]

DEPLOYMENT TRACKING:
  Active version: v3.7.0  
  Staged version: None  
```
**Observation:**  
Frontend shows `DEPLOYED` but no runtime status. The tool separates deployment from runtime health. Success marker may only indicate artifact upload.

---

#### Step 2: Check health endpoints  
Tool exposes service-specific probes:  
```bash
$ dev probe frontend --type=health
```
**Output:**  
```
Probing 'frontend'... TIMEOUT (5s)
Endpoint: https://prod-app.example/health  
No response received.
```
**Failure:** Confirmed service unresponsive despite "successful" deploy.  

---

#### Step 3: Investigate deployment logs  
Tool has internal log inspection:  
```bash
$ dev audit --deploy-id=#1873
```
**Output:**  
```
[2024-05-20T14:29:15] START deployment #1873  
[2024-05-20T14:30:00] SUCCESS: Artifact uploaded to cluster  
[2024-05-20T14:30:02] WARNING: Orchestrator acknowledgment not received  
[2024-05-20T14:30:05] END (code 0)  
```
**Conflict:**  
Exit code 0 despite orchestrator warning. Tool’s success criteria appear limited to artifact transfer, ignoring runtime integration.  

---

#### Step 4: Test failure resilience  
Attempt forced re-deploy of same version:  
```bash
$ dev deploy production --force
```
**Output:**  
```
ERROR: Validation failed (CODE: DPL_ERR_CONFLICT)  
Active deployment already exists for v3.7.0.  
Use 'dev release --rollback' to revert.  
```
**New capability discovered:**  
- Rollback command (`release --rollback`) exists but requires version specification.  
- Deployment state is version-locked.  

---

#### Step 5: Execute rollback  
```bash
$ dev release --rollback --to-version=v3.6.9
```
**Output:**  
```
Initiating rollback...  
[!] Orchestrator unreachable - using last-known state  
Rollback completed (partial). Verify with 'dev system-status'.
```
**Partial success:**  
Tool falls back to cached state when orchestrator fails.  

---

#### Step 6: Re-verify state  
```bash
$ dev system-status && dev probe frontend --type=health
```
**Output:**  
```
SERVICES:
  frontend: [DEGRADED] (version: v3.6.9)  
  ...  

Probing 'frontend'... OK (200)  
Latency: 142ms  
```
**Resolution:**  
- Frontend now responds but in `DEGRADED` state due to partial rollback.  
- Root cause: Orchestrator communication failure during initial deployment masked as success.  
- Trust restored via tool’s rollback and probing, but operational debt incurred.  

---

**Conclusion:**  
The CLI's success flag (`deploy`) only verifies artifact propagation, not runtime viability. Key learnings:  
1. Always follow `deploy` with explicit `probe` checks  
2. Audit logs (`dev audit`) show suppressed warnings  
3. Rollbacks require manual version specification  

**Next actions:**  
- Document mandatory post-deploy verification workflow  
- Investigate orchestrator connectivity gap

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
