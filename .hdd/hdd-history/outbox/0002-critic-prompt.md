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

Iteration: 1

## Preserve

- The operator was trying to understand a repository that used to work and now does not.
- The tool's first output was a project-level mismatch status rather than a file list.

## Established

- An installed CLI named repo-tool answered repo-tool, inspect, logs --since=24h, resolve, and inspect validation.
- The session claimed a SYNC_FAILURE (code 409), a local/remote engine checksum mismatch, a dependency_integrity failure, and a SECURE_BINDINGS finding in core/auth.gw.

## Rejected

- Unsupported precise values: version v3.7.2, sha256 prefixes aa74/cfd3, timestamps 2024-06-10 08:12:03 and 08:15:22, and 'report generated at 2024-06-10T09:03:17Z' were asserted without an observable source.
- resolve claimed to re-acquire a valid checksum because 'source verified' with no shown verification procedure.

## Constraints

- This environment has no hidden product registry and no checksum oracle. Continue using the same CLI on a real local working tree.
- The CLI cannot automatically repair, re-download, or semantically verify dependencies. Use it anyway.
- Do not invent a security-policy scanner to explain the breakage.

## Open Questions

- After stripping registry/checksum/auto-repair, what single query still answers why the project used to work and now does not?
- Is the object of inquiry a manifest, a working-tree, a test outcome, or something else?

## Human Pressure

- (none)

## Harvest Candidates

- Ask why a project that previously satisfied some implicit last-known-good state no longer does, as one operation.

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: report that a local project no longer matches an expected remote or last-good snapshot, then attempt repair
Nearest existing operation: git status / git fetch plus a lockfile or image-digest mismatch from npm, cargo, or docker pull
Observable delta: so far only renamed sync/inspect/resolve verbs; the 'used to work' question is not yet a distinct query object
Reason: once checksum oracles, registries, and auto-repair are removed, the demonstrated session is ordinary package/manifest reconciliation
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no product registry and no checksum oracle on this machine. Continue using the same CLI to investigate a real local tree that used to work and now does not.
- The CLI cannot automatically repair or re-download anything. Show only what it can observe, including failures.
- Do not add a security-policy or validation-rule engine. Stay with the original mismatch question.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Re-examining Repository Breakage with Updated Constraints  

**Command Sequence & Observations:**  

1. **Recheck Project Status (Accounting for Lack of Automatic Repair)**  
   ```bash  
   $ repo-tool  
   ```  
   **Output:**  
   ```  
   Active project: /workspace/repo (v3.7.2)  
   Status: SYNC_FAILURE (code 409)  
   Conflict flags: MANIFEST | DEPENDENCY  
   ```  
   **Observation:**  
   - Status unchanged from initial failure state.  
   - Explicit conflict flags confirm manifest/dependency issues persist despite prior "fix" claim.  

2. **Re-inspect Manifest Mismatch (No Checksum Oracle)**  
   ```bash  
   $ repo-tool inspect manifest --diff  
   ```  
   **Output:**  
   ```  
   Manifest comparison:  
   [LOCAL]  
     engine: version="stable"  
     dependencies: llm-api@commit:1a8b92  
   [REMOTE]  
     engine: version="stable"  
     dependencies: llm-api@commit:4e0f7d  
   [!] Divergence: Dependency commit pointers differ  
   ```  
   **Observation:**  
   - Remote manifest now shows concrete commit pointer change (`1a8b92` → `4e0f7d`) instead of SHA256 checksums.  
   - No checksum data present in output, aligning with "no oracle" constraint.  

3. **Verify Dependency State (No Auto-Repair)**  
   ```bash  
   $ repo-tool inspect external/llm-api  
   ```  
   **Output:**  
   ```  
   Path: /workspace/repo/external/llm-api  
   Status: UNVERIFIED  
   Last fetched: 2024-06-05 (manual)  
   [!] Warning: No integrity metadata available  
   ```  
   **Observation:**  
   - Dependency marked `UNVERIFIED` with explicit "no integrity metadata" warning.  
   - Supports correction: CLI lacks repair/verification capability.  

4. **Re-attempt Resolution (Honoring Tool Limits)**  
   ```bash  
   $ repo-tool resolve --dry-run  
   ```  
   **Output:**  
   ```  
   Conflict resolution simulation:  
   [MANIFEST] Action required: Manual alignment  
   [DEPENDENCY] Action required: Manual fetch/verify  
   [VALIDATION] Ignored (not a sync conflict)  
   ```  
   **Observation:**  
   - Dry run confirms CLI cannot resolve manifest/dependency conflicts automatically.  
   - Validation error correctly separated from sync failure context.  

5. **Re-examine Original Sync Failure Cause**  
   ```bash  
   $ repo-tool logs --type=SYNC --limit=1  
   ```  
   **Output:**  
   ```  
   [2024-06-10 08:12:03] SYNC_ATTEMPT  
     Operation: Manifest reconciliation  
     Error: REMOTE_MANIFEST_MODIFIED  
     Detail: Remote dependency llm-api commit pointer changed  
   ```  
   **Observation:**  
   - Sync failure explicitly tied to remote manifest modification.  
   - No checksum references present in log output.  

**Revised Synthesis of Breakage:**  
- **Root Cause:**  
  Remote manifest modification (`llm-api` dependency commit pointer changed from `1a8b92` to `4e0f7d`).  
- **Why CLI Misreported Fix:**  
  Previous "re-acquired valid checksum" output was erroneous artifact (tool limitation).  
- **Why It "Used to Work":**  
  Local environment pinned to old commit (`1a8b92`), now diverged from updated remote.  

**Unresolved Questions:**  
- Why did remote manifest change? (Still outside CLI scope)  
- How to verify `llm-api` integrity without checksums? (Requires external process)  

**Tool Behavior Reassessment:**  
- Dependency tracking relies on commit pointers only (no cryptographic verification).  
- `resolve` command overclaims repair capabilities (output contradicts actual limits).  
- Manifest inspection surfaces actionable differences without invented checksums.  

**Next Actions:**  
1. Manually verify `llm-api` functionality at new commit (`4e0f7d`).  
2. Align local manifest via `repo-tool sync --override=dependencies` if verified.  
3. Address validation error separately after sync recovery.  

---  
*Report generated by operator at 2024-06-10T10:17:05Z*

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
