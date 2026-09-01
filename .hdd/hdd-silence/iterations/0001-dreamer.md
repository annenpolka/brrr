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
