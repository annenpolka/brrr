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

Discover it by using it on a CI job that passed locally and failed remotely, or the reverse.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

### Field Report: Investigating CI Discrepancy with Unfamiliar CLI  

**Command Sequence & Observations:**  

1. **Initial Tool Probe**  
   ```bash
   ci-debug --version  
   ```  
   **Output:**  
   ```  
   ci-debug v2.1.3 | Environment Diff Toolkit  
   ```  
   *Note: Confirmed tool name (`ci-debug`) and purpose ("Environment Diff Toolkit").*  

2. **Help Documentation Inspection**  
   ```bash
   ci-debug --help  
   ```  
   **Relevant Snippet:**  
   ```  
   COMMANDS:  
     capture   Record environment state (files, processes, env vars)  
     diff      Compare two captures  
     replay    Execute a command in a captured environment  
   ```  

3. **Local Environment Capture (Simulating Passing Job)**  
   ```bash
   ci-debug capture --label local-pass --cwd ./project --env env_vars.local  
   ```  
   **Output:**  
   ```  
   Captured state to .ci-debug/captures/local-pass (snapshot ID: lp-8a3d2f)  
   ```  

4. **Remote Environment Capture (Using Failed CI Artifact)**  
   *Downloaded CI artifact `failed_job_env.tar` from build #117.*  
   ```bash
   ci-debug capture --label remote-fail --from-tar failed_job_env.tar  
   ```  
   **Output:**  
   ```  
   Imported capture .ci-debug/captures/remote-fail (snapshot ID: rf-41c9b0)  
   ```  

5. **Diff Analysis**  
   ```bash
   ci-debug diff local-pass remote-fail --exclude .git,node_modules  
   ```  
   **Critical Output:**  
   ```  
   ENVIRONMENT VARIABLES:  
     [MISSING] LOCAL_PASS: API_KEY="test_123"  
     [EXTRA]   REMOTE_FAIL: API_KEY="prod_secure_vault_ref"  

   FILES:  
     [DIFF]    config.yaml:  
               - Local:  db_adapter: sqlite  
               + Remote: db_adapter: postgres  

   PROCESSES:  
     [EXTRA]   Remote: /usr/bin/security-daemon (PID 204)  
   ```  

6. **Replay Test with Remote Configuration**  
   ```bash
   ci-debug replay remote-fail --command "npm run test-integration"  
   ```  
   **Result:**  
   ```  
   > Test suite failed (Exit code 1)  
   [LOG] Database connection error: TLS required for Postgres  
   ```  

**Findings:**  
- The remote environment uses a production-ready Postgres configuration requiring TLS, while local tests use SQLite.  
- The CI job injects a vault reference (`API_KEY="prod_secure_vault_ref"`) instead of a plaintext key.  
- A security daemon running remotely interferes with network-bound tests.  

**Resolution Workflow:**  
1. **Local Environment Adjustment:**  
   ```bash
   ci-debug capture --label local-postgres --modify config.yaml:db_adapter=postgres  
   ```  
2. **Replay with Modifications:**  
   ```bash
   ci-debug replay local-postgres --command "npm run test-integration"  
   ```  
   **Output:**  
   ```  
   > Test suite passed (Exit code 0)  
   ```  

**Conclusion:**  
The discrepancy originated from environment-specific database configurations and secret management. The CLI's `capture/diff/replay` workflow isolated the issues without speculative debugging. Next step: Add `ci-debug` to CI pipeline for automatic capture on failures.  

**Unresolved Question:**  
Why does the security daemon only run remotely? (Requires infra investigation outside CLI scope.)

## Behavior already demonstrated

- The problem was a job that passed locally and failed remotely.
- The CLI's verbs were capture, diff, and replay rather than 'debug the test'.
- Commands: ci-debug --version, --help, capture --label, capture --from-tar, diff, replay --command.


## Newly confirmed limits and corrections

- Invented snapshot IDs, API_KEY values, security-daemon PID 204, and a successful replay after a fictional config modify.
- There is no CI artifact tarball, vault, or remote daemon in this environment.
- Replay cannot magically reconstruct Postgres+TLS. It may only export and apply environment variables and files that were actually captured.
- Operate on two real local directories or processes.


## New information since the previous report

- There is no CI tarball and no vault. Continue using the same CLI on two real local working trees or two real command invocations.
- Replay may only apply captured environment variables and files; it cannot invent services.
- Show a non-interactive capture and diff whose output is ordinary text or JSON.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
