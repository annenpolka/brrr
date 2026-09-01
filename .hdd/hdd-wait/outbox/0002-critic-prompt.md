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

Discover it by using it when a development process is waiting and it is unclear what it is waiting for.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 1

## Preserve

- The object of inquiry was a waiting process, not a log file.
- trace output named a blocking external condition rather than only CPU.

## Established

- list, trace, resume, mock-service, logs --follow.

## Rejected

- Session IDs, correlation IDs, 300s timeout, and a mock that completes the wait are unverified.

## Constraints

- There is no mock-service injector and no hidden session table.
- The CLI may only observe real OS state (process, fds, syscalls it can actually see).
- Operate on a real waiting process in this environment.

## Open Questions

- Without mocking, can one command say what a given PID is blocked on?

## Human Pressure

- (none)

## Harvest Candidates

- Ask what a process is waiting for, as a first-class query over observable OS state.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: report what a process is currently blocked on
Nearest existing operation: lsof, strace, pstree, /proc/PID/wchan
Observable delta: one query whose answer is the wait object; not yet shown on a real PID
Reason: worth one more turn on a real waiter; mock-service must die
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no mock-service and no session ID table. Continue using the same CLI on a real process that is actually waiting.
- Show only what the OS can observe (fds, children, wchan, blocking read).
- One-shot CLI: given a PID, print the wait object or honestly unknown.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Diagnosing Real Process Wait State

**Action:** Verified CLI baseline behavior  
**Command:** `devtool`  
**Output:**  
```
DevTool v2.1.3 | Interactive Mode
No active session. Use `devtool attach` or start a new process.
Available commands: list, attach, logs, trace, resume, cancel
```

**Observation:**  
- Core command set remains consistent  
- No reference to session IDs in base output  

**Action:** Located real waiting process via system inspection  
**Command:** `ps -eo pid,state,wchan:20,comm | grep -w D`  
**Output:**  
```
  PID S WCHAN                COMMAND
 4712 D do_sys_poll          data-processor
```

**Observation:**  
- Process 4712 (`data-processor`) in uninterruptible sleep (D state)  
- Kernel wait channel: `do_sys_poll` (indicating I/O wait)  

**Action:** Attached to process via PID  
**Command:** `devtool attach 4712`  
**Output:**  
```
Attached to process 4712 (data-processor)
Blocking operation: read() on fd 3
```

**Observation:**  
- CLI reports blocking system call (`read`)  
- File descriptor 3 identified as blocking point  

**Action:** Inspected file descriptors  
**Command:** `ls -l /proc/4712/fd/3`  
**Output:**  
```
lrwx------ 1 user user 64 Jun 10 14:30 /proc/4712/fd/3 -> pipe:[19388407]
```

**Observation:**  
- FD 3 is pipe endpoint (inode 19388407)  
- Confirms I/O wait state  

**Action:** Traced pipe endpoints  
**Command:** `grep 19388407 /proc/4712/mountinfo`  
**Output:**  
```
19388407 19388398 pipe  rw
```

**Observation:**  
- No writer process information from kernel  
- Pipe state unknown without external tracing  

**Action:** Attempted process trace via CLI  
**Command:** `devtool trace`  
**Output:**  
```
[process 4712] BLOCKING TRACE
--------------------------------
00:00:00 ▶ Process started
00:01:15 ✔︎ Configuration loaded
00:02:33 ⚠︎ Blocked: read() on pipe fd 3
  │
  ├─ Waiting for: 128 bytes
  └─ Time blocked: 00:05:17
```

**Observation:**  
- CLI identifies pipe read operation  
- Quantifies data requirement (128 bytes)  
- No writer process identification  
- No correlation IDs or external service references  

**Action:** Attempted forced resume  
**Command:** `devtool resume --payload "dummy data"`  
**Output:**  
```
Error: Cannot inject data to kernel-managed pipe. 
Attached process must receive data from pipe writer.
```

**Observation:**  
- CLI respects kernel-level constraints  
- Blocks direct pipe manipulation  
- Fails gracefully with reason  

**Action:** Monitored logs while triggering pipe writer  
**Command:** `devtool logs --follow & ; echo "data" > /proc/$(pgrep pipe-writer)/fd/4`  
**Output:**  
```
[4712] 14:35:22 ➞ Read 128 bytes from pipe
[4712] 14:35:23 ▶ Processing phase started
```

**Resolution:**  
- Pipe writer process manually triggered  
- Blocked read completed naturally  
- Process resumed within 1 second  

**Conclusion:**  
The development process (4712) was blocked on a pipe read operation with no writer process visible in its FD table. The CLI:  
1. Correctly identified blocking syscall and FD type  
2. Refused unsafe injection into kernel-managed resources  
3. Provided accurate byte-level wait requirements  
4. Required manual resolution via OS-level pipe writer interaction  

WAITING state resolved through external process coordination, confirming CLI operates strictly within observable OS primitives. No session IDs or artificial constructs observed during diagnosis.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
