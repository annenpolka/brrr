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

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Deno Lockfile Discrepancy  

#### **Inspected State**  
To explain the behavioral difference between the two `deno run a.js` invocations without assuming root cause, I focused on state accessible via Deno CLI that could influence lockfile handling:  

1. **Lockfile existence and integrity** (primary suspect from error):  
   ```bash  
   # Check for lockfile presence  
   deno eval "console.log('Lockfile exists?', await Deno.stat('deno.lock').catch(() => 'No'))"  
   ```  
   *Observation:*  
   `Lockfile exists? No`  
   *(This conflicts with the second run's error implying a lockfile was present. Suggests lockfile was deleted after first run or path discrepancy.)*  

2. **Configuration file validation** (error mentions "workspace section"):  
   ```bash  
   # Inspect deno.json/deno.jsonc (common configs affecting lockfile behavior)  
   deno eval "  
   ['deno.json', 'deno.jsonc'].map(async f => {  
     try {  
       const c = await Deno.readTextFile(f);  
       console.log(`${f} found:\n${c}`);  
     } catch { console.log(`${f} missing`) }  
   });"  
   ```  
   *Observation:*  
   `deno.json missing`  
   `deno.jsonc missing`  
   *(No Deno config detected. "workspace" error may stem from implied workspace logic or corrupted lockfile.)*  

3. **Package.json re-inspection** (error references `@.` requirement):  
   ```bash  
   # Re-examine reported package.json  
   deno eval "console.log(await Deno.readTextFile('files/package.json'))"  
   ```  
   *Observation:*  
   `{"dependencies":{"":"."}}`  
   *(Confirmed invalid dependency `"": "."`. Deno doesn't use package.json by default, but may interact if workspace config exists.)*  

4. **Cache verification** (possible version mismatch):  
   ```bash  
   # Check resolved JSR module version in cache  
   deno info jsr:@std/testing/bdd  
   ```  
   *Observation:*  
   ```  
   local: /path/cache/deps/jsr/.../bdd.js  
   type: TypeScript  
   compiled: /path/cache/deno/gen/file/.../bdd.js.js  
   ```  
   *(No version pinned – "jsr:@std/testing/bdd" resolves dynamically. Cache shows no corruption indicators.)*  

---  

#### **Discrepancy Analysis**  
- **First run success:** Likely occurred *without* lockfile. Fresh cache resolved `@std/testing/bdd` successfully.  
- **Second run failure:** Attempted to read missing/corrupted lockfile containing invalid `@.` workspace requirement. Origin hypotheses:  
  1. **Lockfile creation:** First run might have generated `deno.lock` automatically, but:  
     - No `--lock` flag used → Deno shouldn't create lockfile implicitly.  
     - *Contradiction:* Current directory shows no lockfile.  
  2. **External modification:** Lockfile created/deleted by non-Deno process between runs.  
  3. **Path confusion:** `package.json`'s invalid `"": "."` might have been misinterpreted as workspace root during *hypothetical* lockfile creation.  

---  

#### **Critical Unknowns**  
1. **Lockfile provenance:**  
   - If generated during first run, why was it absent during inspection?  
   - If pre-existing, what process created it with invalid `@.` requirement?  
2. **Workspace context:**  
   - Error implies workspace semantics, but no `deno.json` or `package.json` defines workspaces.  

*Recommendation:* If lockfile reappears, inspect with:  
```bash  
deno eval "try { console.log(JSON.parse(await Deno.readTextFile('deno.lock'))) } catch(e) { console.error('Read failed:', e) }"  
```  

**No further action possible** – Lockfile state remains unreproducible per supplied artifacts.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
