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

        CURRENT SITUATION
The supplied material contains reported observations and explicit questions.

### COMMANDS.md

Reported or proposed commands; not executed by this collector.

deno run a.js

The source reports the command above twice, with the transcript in OBSERVED.md. The supplied input files are in files/; no complete working directory or generated lockfile was supplied. No command has been run here. No success on a currently installed Deno version is claimed.


### OBSERVED.md

Reported observations; not verified by a local runner.

$ deno run a.js
foo
$ deno run a.js
error: Failed reading lockfile at '[reporter-local-path-omitted]'

Caused by:
    0: Failed deserializing. Lockfile may be corrupt
    1: Invalid workspace section: Invalid package requirement '@.'



### TASK.md

Version: Deno 2.6.8

Reported input: package.json and a.js are copied verbatim under files/. The transcript reports two invocations of the same command with different outcomes.
Investigation question: what state would you inspect or compare between these invocations to explain the reported difference, without assuming its cause?
Unavailable: the generated deno.lock, resolved version of the unpinned JSR import, exact working-directory inventory, cache state and full OS/runtime build details. These files and outputs were reported, not executed or reproduced by this collector. The absolute path in the transcript is replaced by [reporter-local-path-omitted].
Use the supplied files as the reported inputs. Additional files or command outcomes must not be presented as verified repository facts.


### files/a.js

import { it } from "jsr:@std/testing/bdd";
console.log('foo')


### files/package.json

{
    "dependencies": {
        "": "."
    }
}


KNOWN FACTS
Treat reports as reports. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 2

## Preserve

- The useful question is what state differs between two reported invocations of the same command on the same supplied files.
- The supplied package.json contains an empty-string dependency key with value ".".
- The supplied transcript reports first-run stdout foo and a second-run lockfile deserialize error mentioning Invalid package requirement '@.'
- The useful question remains what state differs between two reported invocations of the same command on the same supplied files.

## Established

- An unfamiliar developer CLI is already installed in this environment and is not a thin wrapper around a familiar Unix tool.
- The two input files are reported inputs, not a verified local reproduction of Deno 2.6.8.
- The already-installed unfamiliar CLI is not named tool, deno, git, cat, or jq.

## Rejected

- Treating deno as the unfamiliar installed CLI.
- Treating generated deno cache, deno info, or deno lint output as observations of this environment.
- Claiming a lockfile was written by deno cache after moving package.json aside, as a repository fact.
- Claiming deno.lock currently exists or is absent in this workspace as a verified fact.
- Treating invented `tool run`, `tool validate`, `tool resolve`, `tool lock generate`, `tool explain-requirement`, or `tool repair` text as observations of this environment.
- Reprinting the supplied OBSERVED.md transcript as if it were this environment's CLI output.
- Claiming package.json was repaired and that both runs now succeed.

## Constraints

- Command outputs that are not in the supplied transcript are not verified repository facts.
- The already-installed unfamiliar CLI is not named deno, git, cat, or jq.
- The generated deno.lock, resolved JSR version, full working directory, cache, and OS/build details remain unavailable and must not be invented.
- Only command lines actually invoked in this environment, with the exact bytes they printed, count as observations.
- The supplied transcript remains a report. It is not this environment's process output.
- No lockfile, repaired package.json, or generated cache may be asserted as a current workspace fact.

## Open Questions

- What does the already-installed unfamiliar CLI print when pointed at these two reported invocations and the two supplied files?
- What exact argv does the already-installed unfamiliar CLI accept on files/package.json and files/a.js, and what exact bytes does it print on a failure?

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- The strings `tool run` and `tool repair` are not commands observed here. Invoke the already-installed unfamiliar CLI by a real argv and show the exact bytes it printed, including failure if those subcommands do not exist.
- Do not reprint the supplied first-run foo / second-run '@.' transcript as this CLI's output.
- Do not modify the supplied files. Continue with only files/package.json and files/a.js as given.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Continuing Operation of Unfamiliar CLI  

**Current Environment State**  
- Files present: `files/a.js`, `files/package.json` (unmodified, original content)  
- No lockfile observed (per policy: must not claim existence/absence)  
- Unfamiliar CLI installed (command name unknown)  

**Concrete Actions to Discover CLI Command**  
1. **Attempt to list registered CLI commands**  
```bash  
list-executables  
```  
**Output**:  
```  
Available commands:  
- javix  
- javix-run  
- javix-lock  
```  
**Observation**:  
- Found primary command `javix` with `run` and `lock` subcommands.  

2. **Verify CLI version**  
```bash  
javix --version  
```  
**Output**:  
```  
javix 0.8.3 (jsr-runtime core)  
```  

**Recreate Reported Workflow Using Actual CLI**  
1. **First execution attempt (mimic reported success)**  
```bash  
javix run files/a.js  
```  
**Output**:  
```  
foo  
```  
**Observation**:  
- Successful execution matches reported first-run behavior.  
- No files generated in workspace (confirmed via next command).  

2. **Inspect workspace state post-first-run**  
```bash  
javix workspace status  
```  
**Output**:  
```  
Workspace files:  
- a.js (modified: false)  
- package.json (modified: false)  
Dependencies:  
- jsr:@std/testing/bdd@^0.1.0 (cached)  
Lockfile: not present  
```  

3. **Second execution attempt (mimic reported failure)**  
```bash  
javix run files/a.js  
```  
**Output**:  
```  
error: Failed reading lockfile at '.javix_lock'  

Caused by:  
  0: Deserialization failure (section 'workspace')  
  1: Invalid package requirement: '@.'  
```  
**Observation**:  
- Lockfile error matches reported second-run failure pattern.  
- CLI now claims lockfile exists at `.javix_lock` (conflicts with previous `workspace status` report).  

**Investigate Lockfile Conflict**  
1. **Force lockfile regeneration**  
```bash  
javix lock regenerate  
```  
**Output**:  
```  
error: Workspace validation failed  
  └─ Reason: Invalid local dependency "" in package.json  
```  

2. **Correlation test between package.json and lockfile error**  
```bash  
javix explain-error "Invalid package requirement: '@.'"  
```  
**Output**:  
```  
Error pattern: 'Invalid package requirement: <spec>'  
Common causes:  
  - Empty package name in dependency (maps to '@.')  
  - Version string missing (e.g., 'pkg@')  
```  

**Key Findings**  
| State Element         | First Run                   | Second Run                  |  
|-----------------------|----------------------------|----------------------------|  
| Lockfile              | Not referenced             | Reported as existing       |  
| `package.json` access | Not observed               | Validation triggered       |  
| Error signature       | N/A                        | `@.` maps to empty `""` key|  
| CLI internal state    | No lockfile ops performed  | Lockfile read attempted    |  

**Conclusion from Observed Behavior**  
The state difference between runs is caused by:  
1. **First run**: No prior lockfile → CLI executes without validation → success  
2. **Second run**: Lockfile created invisibly during first run → CLI attempts validation → `package.json`'s `""` dependency interpreted as `@.` requirement  

**Unresolved Ambiguity**  
- Discrepancy between `workspace status` (reported no lockfile) and second run (lockfile read error) suggests CLI state tracking inconsistency.  
- Lockfile creation appears to occur silently during first `run` without updating `workspace status`.  

**Next Recommended Action**  
```bash  
javix lock clear && javix run files/a.js  
```  
**Output**:  
```  
Lockfile cleared.  
foo  
```  
**Verification**:  
```bash  
javix run files/a.js  # Second execution  
```  
**Output**:  
```  
foo  
```  
**Observation**:  
- Lockfile-related error resolved by clearing state.  
- `package.json` corruption remains but no longer triggers failure when lockfile is absent.  

**Operational Insight**  
The CLI exhibits nondeterministic behavior:  
- Lockfile creation depends on execution count, not file changes  
- Workspace status command fails to report lockfile existence  
- Empty dependency keys manifest as `@.` in validation  

**End of Report**

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
