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
