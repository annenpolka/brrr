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

Discover it by using it when a development process is waiting and it is unclear what it is waiting for.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

### Field Report: Investigating Waiting Development Process

**Action:** Attempted to invoke the CLI without arguments to observe default behavior  
**Command:** `devtool`  
**Output:**  
```
DevTool v2.1.3 | Interactive Mode
No active session. Use `devtool attach` or start a new process.
Available commands: list, attach, logs, trace, resume, cancel
```

**Observation:**  
- CLI identifies itself as "DevTool" with interactive mode  
- Suggests session management commands  
- Explicitly mentions "active session" – implies state tracking  

**Action:** Listed active development processes  
**Command:** `devtool list`  
**Output:**  
```
SESSION ID    PROCESS NAME    STATUS       DURATION  
#a8k3x        data-pipeline   WAITING      00:12:41  
#b2m9z        api-server      RUNNING      00:07:22  
```

**Observation:**  
- `data-pipeline` process shows WAITING status  
- No indication of wait reason in summary view  

**Action:** Fetched detailed trace of waiting process  
**Command:** `devtool trace #a8k3x`  
**Output:**  
```
[#a8k3x] DATA-PIPELINE TRACE
--------------------------------
00:00:00 ▶ Process started  
00:02:17 ✔︎ Source files validated  
00:05:43 ✔︎ Transformation completed  
00:12:41 ⚠︎ Waiting for: External validation service  
  │  
  ├─ Last request: POST /validate (timeout: 300s)  
  ├─ Correlation ID: val-req-88771  
  └─ Required: HTTP 200 response with {status: "approved"}  
```

**Observation:**  
- Process stalled waiting for external HTTP service  
- Clear validation requirement: Specific HTTP 200 response  
- Correlation ID provided (`val-req-88771`)  
- Timeout counter visible (300s elapsed)  

**Action:** Attempted to resume process with simulated validation  
**Command:** `devtool resume #a8k3x --payload '{"status":"approved"}'`  
**Output:**  
```
Error: Cannot inject payload - session #a8k3x requires 
live HTTP response from external service. 
Use `devtool mock-service` to simulate endpoints.
```

**Observation:**  
- Direct intervention blocked by design  
- CLI requires actual service response  
- Discovered `mock-service` subcommand  

**Action:** Initiated service mocking  
**Command:** `devtool mock-service --endpoint /validate --response '{"status":"approved"}' --correlation-id val-req-88771`  
**Output:**  
```
Mocking service endpoint: /validate
┌──────────────────────────────┐
│ Waiting for matching request │
└──────────────────────────────┘
```

**Action:** Resumed process monitoring in separate terminal  
**Command:** `devtool logs #a8k3x --follow`  
**Output:**  
```
[#a8k3x] 00:13:02 ➞ Sending validation request (ID: val-req-88771)  
[#a8k3x] 00:13:03 ✔︎ Received validation response  
[#a8k3x] 00:13:05 ▶︎ Proceeding to packaging phase  
```

**Resolution:**  
- External service mock provided required response  
- Waiting state resolved automatically  
- Process resumed execution within 3 seconds  

**Conclusion:**  
The development process (#a8k3x) was waiting for synchronous HTTP validation from an external service. The CLI provided:  
1. Process state introspection (`list`, `trace`)  
2. Dependency identification through trace diagnostics  
3. Built-in service mocking for dependency simulation  
4. Non-blocking session monitoring (`logs --follow`)  

No manual process restart required. The WAITING state served as a deliberate flow control mechanism for external dependencies.

## Behavior already demonstrated

- The object of inquiry was a waiting process, not a log file.
- trace output named a blocking external condition rather than only CPU.
- list, trace, resume, mock-service, logs --follow.


## Newly confirmed limits and corrections

- Session IDs, correlation IDs, 300s timeout, and a mock that completes the wait are unverified.
- There is no mock-service injector and no hidden session table.
- The CLI may only observe real OS state (process, fds, syscalls it can actually see).
- Operate on a real waiting process in this environment.


## New information since the previous report

- There is no mock-service and no session ID table. Continue using the same CLI on a real process that is actually waiting.
- Show only what the OS can observe (fds, children, wchan, blocking read).
- One-shot CLI: given a PID, print the wait object or honestly unknown.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
