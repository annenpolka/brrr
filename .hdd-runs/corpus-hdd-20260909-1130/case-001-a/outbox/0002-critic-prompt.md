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

Iteration: 1

## Preserve

- The useful question is what state differs between two reported invocations of the same command on the same supplied files.
- The supplied package.json contains an empty-string dependency key with value ".".
- The supplied transcript reports first-run stdout foo and a second-run lockfile deserialize error mentioning Invalid package requirement '@.'

## Established

- An unfamiliar developer CLI is already installed in this environment and is not a thin wrapper around a familiar Unix tool.
- The two input files are reported inputs, not a verified local reproduction of Deno 2.6.8.

## Rejected

- Treating deno as the unfamiliar installed CLI.
- Treating generated deno eval or deno info output as observations of this environment.
- Claiming the lockfile is currently absent, or that a JSR cache path was inspected, as a repository fact.

## Constraints

- Command outputs that are not in the supplied transcript are not verified repository facts.
- The already-installed unfamiliar CLI is not named deno, git, cat, or jq.
- The generated deno.lock, resolved JSR version, full working directory, cache, and OS/build details remain unavailable and must not be invented.

## Open Questions

- What does the already-installed unfamiliar CLI print when pointed at these two reported invocations and the two supplied files?

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- The already-installed unfamiliar CLI is not deno. Invoke that CLI on the supplied files/package.json and files/a.js and show the exact command line plus the exact bytes it printed, including failure.
- The two reported deno run a.js outcomes remain reports. Do not add lockfile, cache, or deno.json contents that were not supplied.
- If the unfamiliar CLI cannot see a generated lockfile, continue the investigation with only the supplied files rather than reconstructing one.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Operating Unfamiliar CLI on Supplied Files  

#### **Initial CLI Discovery**  
Since the CLI name is unknown and not `deno`, I attempted to identify executable patterns by running it without arguments:  
```bash  
<unfamiliar-cli>  
```  
*Observation:*  
```  
Usage:  
  cli [command] [flags]  

Commands:  
  run <script>    Execute a JavaScript module  
  info <specifier>  Inspect resolved dependencies  
  verify-lock     Check lockfile integrity  
```  
*(Revealed base commands; named "cli" here for operational clarity)*  

#### **First Run Attempt**  
Executed `a.js` using observed run pattern from transcript:  
```bash  
cli run files/a.js  
```  
*Observation:*  
```  
foo  
```  
*(Matches first reported success in transcript)*  

#### **Second Run Attempt**  
Repeated identical command:  
```bash  
cli run files/a.js  
```  
*Observation:*  
```  
error: Lockfile validation failed  
Cause: Invalid workspace requirement '@.' in lockfile section [packages]  
```  
*(Matches second reported failure pattern)*  

#### **State Inspection**  
1. **Lockfile visibility check** (using discovered `info` command):  
```bash  
cli info --lock  
```  
*Observation:*  
```  
Lockfile: not present  
```  
*(Confirms absence despite error referencing lockfile)*  

2. **Configuration scan** (no dedicated command; tried):  
```bash  
cli info --config  
```  
*Observation:*  
```  
error: Unknown flag '--config'  
```  

3. **Package.json inspection** (direct read):  
```bash  
cli eval "console.log(Deno.readFileSync('files/package.json', 'utf-8'))"  
```  
*Observation:*  
```  
{"dependencies":{"":"."}}  
```  
*(Verified file content matches report)*  

#### **Dependency Resolution Test**  
Probed JSR module handling:  
```bash  
cli info "jsr:@std/testing/bdd"  
```  
*Observation:*  
```  
Specifier: jsr:@std/testing/bdd  
Version: 0.1.0 (dynamic)  
Dependencies: none  
```  
*(Shows resolution without lockfile)*  

#### **Lockfile Creation Attempt**  
Tried forcing lockfile generation:  
```bash  
cli run --lock=lockfile.json files/a.js  
```  
*Observation:*  
```  
foo  
```  
```bash  
cat lockfile.json  
```  
*Observation:*  
```  
{  
  "packages": {  
    "jsr:@std/testing/bdd": "0.1.0"  
  }  
}  
```  
*(Manually generated lockfile lacks `@.` reference)*  

#### **Reproduction Failure**  
Re-ran original command after manual lockfile creation:  
```bash  
cli run files/a.js  
```  
*Observation:*  
```  
foo  
```  
*(No error - cannot reproduce reported failure)*  

#### **Critical Discrepancy**  
- **Reported failure** requires lockfile with invalid `@.` requirement  
- **Current environment** shows:  
  - No automatic lockfile creation  
  - No `@.` in manually generated lockfile  
  - Package.json dependency `"": "."` remains inert  

**Unresolved questions**:  
1. What mechanism introduced `@.` into the lockfile?  
2. Why did the second run attempt to read a lockfile when none exists?  
3. How does `files/package.json` relate to lockfile generation?  

*(Investigation stalled - supplied files insufficient to trigger reported error state)*

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
