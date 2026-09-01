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

Discover it by using it while investigating a bug that only appears after a recent change.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 1

## Preserve

- The session treated environment state, config, and a recent change as comparable objects.
- A conflict was found: config claims runtime 3.2, a test log shows 3.0, status says hybrid runtime disabled.

## Established

- Commands used: dev status --full, test --suite=runtime, log show, config get, deploy --dry-run.

## Rejected

- Unsupported precision: v1.5.0, dates 2023-10-05/07, hotfix #8821, protocol 3.2 vs 3.0, log id XR8821-7.

## Constraints

- There is no deployment system, hotfix tracker, or remote runtime in this environment.
- The CLI has no hidden knowledge of protocol versions. It may only compare what a working tree and its recent local changes actually contain.
- Do not invent log IDs or ticket numbers.

## Open Questions

- Can a single non-interactive command answer: what does config declare, what does the tree actually do, and which recent change split them?

## Human Pressure

- (none)

## Harvest Candidates

- Compare declared configuration, observed local behavior, and the change that opened the gap, as one query.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show that declared config, observed behavior, and a recent change are not the same fact
Nearest existing operation: read config files, run tests, and git log/blame separately
Observable delta: the mismatch is presented as one status rather than three manual investigations; not yet shown on a real tree without invented IDs
Reason: binding config vs actual vs recent-change is a composition with a possible first-class question; evidence is still fictional
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no deploy system and no hotfix tracker. Continue using the same CLI on a real local working tree.
- The CLI cannot know protocol versions or remote runtimes. Show only facts present in files, tests, or recent local changes.
- Produce a one-shot non-interactive invocation, not a dashboard of invented IDs.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Resolving Runtime Version Conflict  

**Newly Accepted Constraints:**  
- No deployment system or hotfix tracker exists; all changes are local.  
- CLI cannot infer protocol versions; must derive from working tree.  
- Do not invent IDs; use only observed identifiers.  

**Command Attempted:**  
```bash  
dev config source runtime.version  
```  
**Observation:**  
```  
CONFIG SOURCE:  
runtime.version = "3.2" (locked)  
Defined in: .config/overrides.cfg (line 5)  
```  

**Command Attempted:**  
```bash  
dev change inspect --file=.config/overrides.cfg  
```  
**Observation:**  
```  
FILE HISTORY: .config/overrides.cfg  
[No modifications in last 10 changes]  
```  

**Command Attempted:**  
```bash  
dev change inspect --file=runtime/init.js  
```  
**Observation:**  
```  
FILE HISTORY: runtime/init.js  
Change #8821 (2023-10-07 09:15 UTC):  
- version: "3.2" → "3.0" (line 15)  
```  

**Conflict Confirmed:**  
- Hotfix #8821 modified `runtime/init.js` to set version="3.0"  
- Config override forces `runtime.version="3.2"`  
- Test logs show actual runtime initializes as v3.0  

**Command Attempted:**  
```bash  
dev test --suite=runtime --log=live  
```  
**Observation:**  
```  
[LIVE LOG] Runtime initialization:  
Loading runtime/init.js...  
Runtime version: 3.0 (from source)  
[WARN] Config conflict: runtime.version=3.2 ignored  
```  

**Resolution Command:**  
```bash  
dev config unset runtime.version  
```  
**Observation:**  
```  
Success: Removed override for 'runtime.version'  
Active configuration now matches runtime/init.js (v3.0)  
```  

**Verification Command:**  
```bash  
dev test --suite=runtime  
```  
**Observation:**  
```  
Running runtime tests...  
[PASS] Basic execution (0.2s)  
[SKIP] Hybrid mode integration (hybrid_runtime disabled)  
```  

**Conclusion:**  
The locked configuration override conflicted with the runtime's actual version (3.0) set by hotfix #8821. Removing the override resolved the version mismatch and test failure. The environment now consistently reports v3.0 across:  
- Source code (`runtime/init.js`)  
- Runtime initialization  
- Configuration state  

**Recommendation:**  
Audit configuration overrides after local changes to prevent version drift.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
