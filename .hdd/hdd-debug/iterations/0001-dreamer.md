### Field Report: Investigating CLI Behavior After Recent Change  

**Command Attempted:**  
```bash
dev status --recent
```  
**Observation:**  
- Output: `Error: Unknown flag '--recent'. See 'dev status --help'`  
- Followed suggestion: `dev status --help`  
- Output:  
  ```  
  STATUS USAGE:  
    dev status [--full] [--json]  
    Shows current environment state  
  ```  

**Command Attempted:**  
```bash
dev status --full  
```  
**Observation:**  
```  
ENVIRONMENT STATE:  
Project: my_app (v1.5.0)  
Last deployment: 2023-10-05 14:30 UTC  
Active features:  
  - delta_compression (enabled)  
  - vector_indexing (enabled)  
  - hybrid_runtime (disabled)  
Recent changes:  
  [!] Hybrid runtime disabled via hotfix #8821 (2023-10-07 09:15 UTC)  
```  
**Notable Fact:**  
Hybrid runtime disabled 2 days ago – matches bug appearance timeline.  

**Command Attempted:**  
```bash  
dev test --suite=runtime  
```  
**Observation:**  
```  
Running runtime tests...  
[PASS] Basic execution (0.2s)  
[FAIL] Hybrid mode integration (see log #XR8821-7)  
[ERROR] Resource handshake timeout  
```  
**Hypothesis:**  
Hotfix #8821 broke hybrid mode integration.  

**Command Attempted:**  
```bash  
dev log show #XR8821-7  
```  
**Observation:**  
```  
LOG #XR8821-7 (2023-10-07 09:18:30 UTC):  
[INIT] Hybrid mode test (protocol v3)  
[WARN] Legacy runtime detected  
[ERROR] Handshake failed:  
  Expected: protocol_version >= "3.2"  
  Actual: "3.0"  
```  
**Conflict:**  
Status shows hybrid runtime *disabled*, but test expects v3.2 protocol.  

**Command Attempted:**  
```bash  
dev config get runtime.version  
```  
**Observation:**  
```  
runtime.version = "3.2" (locked)  
```  
**Discrepancy Found:**  
- Config claims runtime v3.2 is active  
- Test log shows actual runtime v3.0  
- Status shows hybrid runtime disabled  

**Command Attempted:**  
```bash  
dev deploy --dry-run --change=hotfix#8821  
```  
**Critical Observation:**  
```  
DRY RUN: Reverting hotfix #8821  
[WARNING] Would reactivate hybrid runtime (v3.0)  
[CONFLICT] Config requires runtime.version=3.2 (incompatible)  
```  

**Conclusion:**  
The hotfix disabled the hybrid runtime without downgrading the locked config version, creating a version conflict that breaks integration tests. The environment expects v3.2 runtime but actually runs v3.0 when hybrid mode is disabled.  

**Next Action Recommended:**  
```bash  
dev config set runtime.version="3.0" --verify  
```  
To align configuration with actual runtime state.
