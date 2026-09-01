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

Discover it by using it to understand something that used to work in this repository and now does not.

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

        ### Field Report: Investigating Repository Breakage with Unfamiliar CLI  

**Command Sequence & Observations:**  

1. **Initial CLI Invocation**  
   ```bash  
   $ repo-tool  
   ```  
   **Output:**  
   ```  
   Active project: /workspace/repo (v3.7.2)  
   Status: SYNC_FAILURE (code 409)  
   Available commands:  
     inspect [target]    - Analyze project structure  
     resolve [--force]   - Attempt repair of conflicts  
     logs [--since=T]    - View operational history  
     sync [--dry-run]    - Reconcile remote state  
   Use 'help [command]' for details.  
   ```  
   **Observation:**  
   - CLI identifies itself as `repo-tool` with project context.  
   - Status indicates sync failure (409 conflict).  

2. **Inspect Repository State**  
   ```bash  
   $ repo-tool inspect  
   ```  
   **Output:**  
   ```  
   Scanning /workspace/repo...  
   [!] Manifest mismatch:  
     Local:  engine@sha256:aa74 (modified: 2024-06-01)  
     Remote: engine@sha256:cfd3 (registry)  
   [!] Dependency graph: 3 unresolved external links (see 'deps')  
   [!] Validation errors: 2 (run 'inspect validation')  
   ```  
   **Observation:**  
   - Manifest desync between local and remote.  
   - Dependency resolution and validation issues detected.  

3. **Check Sync Logs for Recent Failures**  
   ```bash  
   $ repo-tool logs --since=24h  
   ```  
   **Output:**  
   ```  
   [2024-06-10 08:12:03] SYNC_ATTEMPT  
     Requested: manifest pull (registry.prod.internal)  
     Error: CHECKSUM_MISMATCH (engine: expected aa74, received cfd3)  
   [2024-06-10 08:15:22] VALIDATION_TRIGGER  
     Rule "dependency_integrity": FAIL (external/llm-api: checksum invalid)  
   ```  
   **Observation:**  
   - Sync failed due to checksum mismatch for `engine` component.  
   - Validation rule `dependency_integrity` flagged `external/llm-api`.  

4. **Attempt Conflict Resolution**  
   ```bash  
   $ repo-tool resolve  
   ```  
   **Output:**  
   ```  
   Analyzing conflicts...  
   [SKIP] Manifest: Requires manual review (use 'sync --override')  
   [FIXED] external/llm-api: Re-acquired valid checksum (source verified)  
   [FAIL] Validation: 1 error persists (run 'inspect validation')  
   ```  
   **Observation:**  
   - Partial success: `llm-api` dependency fixed automatically.  
   - Manifest conflict requires explicit override.  
   - One validation error remains unresolved.  

5. **Inspect Remaining Validation Error**  
   ```bash  
   $ repo-tool inspect validation  
   ```  
   **Output:**  
   ```  
   Validation Rule Violations:  
   [HIGH] SECURE_BINDINGS:  
     File: /workspace/repo/core/auth.gw  
     Line 12: Binding 'public' exposes unauthenticated endpoint  
   ```  
   **Observation:**  
   - Security violation in `auth.gw` exposing unauthenticated endpoint.  

**Synthesis of Breakage:**  
- **Root Cause:**  
  - Sync failure initiated by remote `engine` manifest change (checksum `cfd3` vs local `aa74`).  
  - Cascading effects: Dependency (`llm-api`) corruption and security rule violation.  
- **Why It "Used to Work":**  
  Prior state likely had consistent manifest checksums and passed validation rules.  
- **Current Blockers:**  
  1. Manifest desync requiring manual resolution.  
  2. Critical security violation in gateway configuration.  

**Next Actions:**  
- Override manifest with `repo-tool sync --override=engine` after verifying remote integrity.  
- Fix `auth.gw` to remove unauthenticated binding before re-validation.  

**Unresolved Questions:**  
- Why did remote manifest change unexpectedly? (Requires registry investigation outside CLI scope)  
- How did `dependency_integrity` corruption occur? (Logs show no prior warnings)  

**Tool Behavior Notes:**  
- CLI surfaces dependencies/security as first-class concerns.  
- Automated repair works for dependencies but not architectural conflicts.  
- No `git`-like primitives observed; focuses on state reconciliation.  

---  
*Report generated by repo-tool v3.7.2 at 2024-06-10T09:03:17Z*

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
