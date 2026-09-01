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

Discover it by using it while investigating a bug that only appears after a recent change.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

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

## Behavior already demonstrated

- The session treated environment state, config, and a recent change as comparable objects.
- A conflict was found: config claims runtime 3.2, a test log shows 3.0, status says hybrid runtime disabled.
- Commands used: dev status --full, test --suite=runtime, log show, config get, deploy --dry-run.


## Newly confirmed limits and corrections

- Unsupported precision: v1.5.0, dates 2023-10-05/07, hotfix #8821, protocol 3.2 vs 3.0, log id XR8821-7.
- There is no deployment system, hotfix tracker, or remote runtime in this environment.
- The CLI has no hidden knowledge of protocol versions. It may only compare what a working tree and its recent local changes actually contain.
- Do not invent log IDs or ticket numbers.


## New information since the previous report

- There is no deploy system and no hotfix tracker. Continue using the same CLI on a real local working tree.
- The CLI cannot know protocol versions or remote runtimes. Show only facts present in files, tests, or recent local changes.
- Produce a one-shot non-interactive invocation, not a dashboard of invented IDs.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
