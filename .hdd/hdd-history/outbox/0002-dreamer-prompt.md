# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

An unfamiliar developer CLI is already installed in this environment.

Discover it by using it to understand something that used to work in this repository and now does not.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

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

## Behavior already demonstrated

- The operator was trying to understand a repository that used to work and now does not.
- The tool's first output was a project-level mismatch status rather than a file list.
- An installed CLI named repo-tool answered repo-tool, inspect, logs --since=24h, resolve, and inspect validation.
- The session claimed a SYNC_FAILURE (code 409), a local/remote engine checksum mismatch, a dependency_integrity failure, and a SECURE_BINDINGS finding in core/auth.gw.


## Newly confirmed limits and corrections

- Unsupported precise values: version v3.7.2, sha256 prefixes aa74/cfd3, timestamps 2024-06-10 08:12:03 and 08:15:22, and 'report generated at 2024-06-10T09:03:17Z' were asserted without an observable source.
- resolve claimed to re-acquire a valid checksum because 'source verified' with no shown verification procedure.
- This environment has no hidden product registry and no checksum oracle. Continue using the same CLI on a real local working tree.
- The CLI cannot automatically repair, re-download, or semantically verify dependencies. Use it anyway.
- Do not invent a security-policy scanner to explain the breakage.


## New information since the previous report

- There is no product registry and no checksum oracle on this machine. Continue using the same CLI to investigate a real local tree that used to work and now does not.
- The CLI cannot automatically repair or re-download anything. Show only what it can observe, including failures.
- Do not add a security-policy or validation-rule engine. Stay with the original mismatch question.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
