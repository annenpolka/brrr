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

Discover it by using it after an automated coding assistant changed the tree and the result needs to be understood.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

### Field Report: Investigating Automated Changes with Unfamiliar CLI  

**Current State**:  
Working directory shows altered files (`src/`, `tests/`, `config.yaml`) after automated assistant run. CLI executable name unknown.  

---  

#### Step 1: Discover CLI invocation  
Ran directory scan for recent executables:  
```bash  
ls -lt | head -n 5  
```  
**Observation**:  
```  
-rwxr-xr-x 1 user group 2.3M Mar 10 11:30 dx  
-rw-r--r-- 1 user group  12K Mar 10 11:28 config.yaml  
drwxr-xr-x 4 user group 4.0K Mar 10 11:27 src/  
```  
Found unknown binary `dx` (last modified during assistant run).  

#### Step 2: Probe CLI capabilities  
Attempted help command:  
```bash  
./dx --help  
```  
**Output**:  
```  
dx - Developer Experience Toolkit  

COMMANDS:  
  state     Show workspace snapshot  
  trace     Reconstruct modification path  
  resolve   Explain change rationale  
  config    Adjust runtime parameters  
```  
**Discovery**:  
- CLI is project-aware (references "workspace")  
- Offers change-specific verbs (`trace`, `resolve`)  

#### Step 3: Query current state  
```bash  
./dx state  
```  
**Output & Error**:  
```  
Active constraint: requires .dxstate manifest (not found)  
Run 'dx trace --init' to establish baseline?  
```  
**Adaptation**:  
Followed suggestion to initialize:  
```bash  
./dx trace --init  
```  
**Observation**:  
```  
Manifest generated at /project/.dxstate  
Tracking: src/ (4 files), tests/ (2 files), config.yaml  
```  

#### Step 4: Trace automated changes  
```bash  
./dx trace --source=auto  
```  
**Output**:  
```  
[ASSISTANT] 2024-03-10T11:27:35Z  
MODIFIED src/main.py  
  + Function security_scanner()  
  - Deprecated validate_input()  
ADDED tests/security_scanner_test.py  
CONFIGURATION CHANGE:  
  config.yaml:  
    security_level: 2 → 3  
```  

#### Step 5: Investigate rationale  
```bash  
./dx resolve --target=config.yaml  
```  
**Output**:  
```  
Change implements CVE-2024-1234 mitigation:  
- security_level increase required by GHSA-abc1-xyz9  
- Reference: internal ticket SEC-789  
```  

#### Step 6: Verify impact  
Attempted to check dependency side-effects:  
```bash  
./dx trace --dependencies  
```  
**Failure**:  
```  
ERROR: Dependency graph disabled (enable via 'dx config dependencies=true')  
```  
**Retry with configuration**:  
```bash  
./dx config dependencies=true  
./dx trace --dependencies  
```  
**New Observation**:  
```  
┌───────────────┬──────────────────────────────┐  
│ Modified File │ Affected Dependencies        │  
├───────────────┼──────────────────────────────┤  
│ src/main.py   │ libseccheck(3.1.0)→libseccheck(3.2.1) │  
└───────────────┴──────────────────────────────┘  
```  

---  

**Findings**:  
1. CLI (`dx`) requires explicit state initialization before use  
2. Change tracking integrates:  
   - Code modifications  
   - Configuration shifts  
   - Security bulletin references  
3. Dependency impact analysis requires opt-in configuration  
4. Assistant changes were:  
   - Security-focused (CVE mitigation)  
   - Backward-incompatible (removed function)  

**Next Actions**:  
- Validate tests: `./dx trace --validation`  
- Check backward compatibility: `./dx resolve --deprecations`  

**Unresolved**:  
Why was `validate_input()` removed without legacy wrapper? (No rationale in trace)

## Behavior already demonstrated

- The operator's problem was a working tree changed by an automated assistant.
- trace listed file-level modifications; resolve was asked to explain a config change.
- Commands: dx --help, state, trace --init, trace --source=auto, resolve --target, config, trace --dependencies.


## Newly confirmed limits and corrections

- Invented CVE-2024-1234, GHSA-abc1-xyz9, ticket SEC-789, libseccheck 3.1.0→3.2.1, and timestamps.
- resolve claimed to know mitigation rationale that is not present in the working tree as shown.
- There is no hidden assistant transcript, ticket tracker, or vulnerability database.
- The CLI cannot invent why a change happened. It may only observe the working tree, diffs, and files actually present.
- Do not require a .dxstate manifest as magical prior knowledge; if a baseline is needed, it must be something the operator can see.


## New information since the previous report

- There is no assistant transcript, CVE database, or ticket system. Continue using the same CLI on a real working tree that an editor or script just changed.
- The CLI cannot explain intent. Show only added, removed, or rewritten observable behavior.
- Do not create a hidden manifest that already knows the answer. If a baseline is required, the operator must be able to point at it.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
