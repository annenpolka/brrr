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

Discover it by using it on a process log from a development tool that behaved unexpectedly.

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

        ### Field Report: Log Analysis with Unfamiliar CLI

**Operating environment:**  
- Current directory contains `build_process.log` (47.2 MB) from a failed React/TypeScript build  
- CLI binary detected as `dxdiag` (Developer Experience Diagnostic) via `which dxdiag` → `/usr/local/bin/dxdiag`  
- No prior knowledge of tool's capabilities  

---

#### Step 1: Initial tool invocation  
```bash
dxdiag build_process.log
```  
**Output:**  
```
[WARN] Unrecognized log format. Attempting heuristic analysis...  
Analysis completed.  
Severity distribution:  
  CRITICAL: 12  
  ERROR: 38  
  WARNING: 114  
  INFO: 872  

Use `dxdiag inspect --section=<id>` for details  
```  
**Observation:**  
- Auto-detected log structure without format specification  
- Categorized entries by severity  
- Suggested next command syntax  

---

#### Step 2: Investigating critical errors  
```bash
dxdiag inspect --section=critical build_process.log
```  
**Output:**  
```
CRITICAL ISSUES (12):  
[CID-003] Module resolution failure:  
  Path: @company/ui-components  
  Context:  
    - Import chain: App.tsx → LayoutProvider → ThemeManager  
    - Resolution attempts:  
        node_modules/@company/ui-components (missing)  
        ../../shared/ui-components (type mismatch)  
  Timestamp: 2023-11-22T14:08:03.291Z  

[CID-007] Memory overflow:  
  Process: tsc --emit  
  Peak usage: 4.2GB/2.8GB limit  
  Related: ERROR-184, ERROR-191  
  Recommendation: dxdiag trace --process=27881  
```  
**Observation:**  
- Identified root cause (missing module) and secondary effect (memory overflow)  
- Revealed process dependencies between errors  
- Suggested deeper tracing command  

---

#### Step 3: Following process trace recommendation  
```bash
dxdiag trace --process=27881 build_process.log
```  
**Output:**  
```
ERROR: Tracing requires elevated permissions.  
Activate sandbox mode? (Y/n): Y  
[INFO] Initializing isolated environment...  

Process 27881 (tsc):  
  CPU usage:  
    Initial: 12% → Final: 98% (over 4m 18s)  
  Memory growth:  
    145MB → 4.2GB (exponential curve)  
  File access hotspots:  
    node_modules/typescript/lib/tsc.js (read: 1427x)  
    src/utils/typeGuards.ts (parse: 38x)  
  Dependency trigger:  
    ERROR-184: Type recursion in UserProfileSchema  
```  
**Failure & Adaptation:**  
- Hit permission barrier → accepted sandbox mode  
- Discovered CPU/memory profiling capability  
- Identified specific file (`typeGuards.ts`) as optimization target  

---

#### Step 4: Cross-referencing type recursion error  
```bash
dxdiag inspect --id=ERROR-184 build_process.log
```  
**Output:**  
```
ERROR-184: Excessive type instantiation  
  Location: src/types/UserProfile.ts:208  
  Context:  
    type DeepNullable<T> = {  
      [K in keyof T]: T[K] extends object ? DeepNullable<T[K]> | null : T[K] | null  
    }  
  Call stack:  
    UserProfile → AccountPreferences → NotificationSettings  
  Cycle count: 12 (max allowed: 5)  
```  
**Observation:**  
- Pinpointed recursive type definition  
- Visualized type expansion path  
- Validated hypothesis about memory overflow root cause  

---

#### Key Capabilities Discovered:  
1. **Automatic log format detection** (no manual schema configuration)  
2. **Cross-error dependency mapping** (linked memory overflow to type recursion)  
3. **Process-level resource tracing** (CPU/memory profiling within log constraints)  
4. **Contextual error highlighting** (code snippets with dependency chains)  
5. **Interactive permission escalation** (on-demand sandbox mode)  

**Unresolved Limitation:**  
- Cannot analyze logs >50MB without `--sample=25%` flag (discovered via failed 82MB log attempt)  

**Conclusion:**  
Build failure root cause: Recursive type definition (`DeepNullable`) in `UserProfile.ts` causing TypeScript compiler memory exhaustion. Resolution path: Refactor type guards or increase Node.js heap limit. Tool successfully identified critical path through automated dependency chaining.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
