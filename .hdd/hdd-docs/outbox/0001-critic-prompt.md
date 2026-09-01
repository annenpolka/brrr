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

Discover it by using it when documentation and the code it describes have drifted apart.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


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

        ### Field Report: Exploring the Unfamiliar CLI  
**Operational Log**  

**1. Initial Probe**  
Ran base command without arguments to trigger system response:  
```bash
$ devcli
```  
**Observation**:  
```  
Error: Missing subcommand.  
Available: init, build, run, inspect, config  
Use 'devcli <command> --help' for details  
```  

**2. Testing `init` Workflow**  
Attempted project initialization with minimal arguments:  
```bash  
$ devcli init --type web ./project_dir  
```  
**Observation**:  
```  
Project scaffold failed:  
[ERR] Directory './project_dir' exists but lacks .manifest file  
HINT: Run 'devcli init --force' to overwrite or 'devcli inspect dir' to diagnose  
```  
**Action**: Used `inspect` to investigate directory state:  
```bash  
$ devcli inspect dir ./project_dir  
```  
**Output**:  
```  
Directory status:  
  - Contains: 3 .js files, 2 .md files  
  - Missing: .manifest (required)  
  - Detected: legacy config (v0.8) in package.json  
```  

**3. Forced Initialization**  
Applied `--force` flag based on error hint:  
```bash  
$ devcli init --type web --force ./project_dir  
```  
**Observation**:  
```  
Overwriting directory...  
WARNING: Converted package.json → .manifest (v2.3)  
Success: Project initialized. Run 'devcli build' next  
```  

**4. Build Process Test**  
Executed build command:  
```bash  
$ devcli build  
```  
**Output**:  
```  
Building target: web-default  
[STAGE] Dependency resolution... OK  
[STAGE] Transpilation... FAILED  
Error: Missing runtime profile (required for JSX)  
HINT: Set via 'devcli config runtime.profile=env'  
```  

**5. Configuration Adjustment**  
Attempted to set required runtime profile:  
```bash  
$ devcli config set runtime.profile env  
```  
**Observation**:  
```  
Config update failed:  
'env' is not a valid profile. Choices: node, browser, hybrid  
```  
**Retry**:  
```bash  
$ devcli config set runtime.profile browser  
```  
**Output**:  
```  
Configuration updated: runtime.profile = browser  
```  

**6. Build Retry**  
Re-ran build with updated config:  
```bash  
$ devcli build  
```  
**Observation**:  
```  
Building target: web-default  
[STAGE] Dependency resolution... OK  
[STAGE] Transpilation... OK  
[STAGE] Optimization...  
Error: Asset pipeline requires 'devcli build --with-assets'  
```  

**7. Asset Handling Discovery**  
Executed suggested flag:  
```bash  
$ devcli build --with-assets  
```  
**Output**:  
```  
Building target: web-assets  
[ASSET] Processed 12 images → /dist/media  
Success: Built to /dist (size: 14.7MB)  
```  

**8. Runtime Execution Test**  
Launched project:  
```bash  
$ devcli run  
```  
**Observation**:  
```  
Runtime error:  
Port 8080 occupied by process 28491  
HINT: Use 'devcli run --port-auto' or kill conflicting process  
```  
**Action**: Used port auto-selection:  
```bash  
$ devcli run --port-auto  
```  
**Output**:  
```  
Running web server (profile: browser)  
• API: http://localhost:6093  
• Assets: http://localhost:6093/media  
[Ctrl+C to exit]  
```  

**Key Findings**  
- **Stateful Configuration**: Settings persist between commands (`runtime.profile` affected build)  
- **Contextual Errors**: Hints adapt to environment state (port conflicts, directory contents)  
- **Asset Separation**: Non-trivial workflow requiring explicit asset flag  
- **Legacy Conversion**: Automatic v0.8 → v2.3 manifest migration during forced init  
- **Strict Validation**: Rejects invalid config values with enumerated options  

**Unresolved Questions**  
- How project type (web) affects build output?  
- Purpose of `.manifest` vs traditional package managers?  
- Can runtime profile be set per project rather than globally?  

**Next Steps**  
- Test `inspect` on build artifacts  
- Attempt multi-target build (if supported)  
- Profile resource usage during runtime

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
