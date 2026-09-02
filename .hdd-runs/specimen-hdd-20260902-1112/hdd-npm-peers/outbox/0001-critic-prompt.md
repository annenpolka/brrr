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
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

`npm install vite` into an empty project installs about 10 packages but, with a cold cache, also downloads full registry metadata for many packages that do not end up installed (playwright, @types/node, webdriverio, jsdom, sass, less, terser, vitest's optional peers, ...).

The developer wants to know *why those fetches happened* and which dependency edges caused work that the final tree does not use.

# OBSERVED

Public npm/cli#9876 / PR 9877. Empty cache, `npm install vite`:

| | before (failing) | after (fixed, not shown to you as a solution) |
| registry requests | 86 | 54 |
| cached registry data | ~121MB | ~72MB |

Final install: ~10 packages. Fetches include full packuments for optional peers that are not installed.

The failing world still produces a valid tree; the cost and the fetch set are the surprise.

# COMMANDS

```
rm -rf ~/.npm/_cacache   # do not run this on the host lab
npm install vite
```
This packet is source-backed; do not execute npm against the operator machine.

empty project
package.json { }
npm install vite

RELEVANT MATERIAL

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

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

        ### Field Report: Investigating npm Registry Fetches for `vite` Installation  

**Tool Used:** `npm-dep-tracer` (unfamiliar CLI tool pre-installed in environment)  
**Objective:** Identify why cold-cache `npm install vite` fetches unused packument data (e.g., playwright, @types/node) and which dependency edges trigger this.  

---

#### Step 1: Initialize Empty Project  
```bash
mkdir vite-investigation && cd vite-investigation  
echo '{}' > package.json  
```

---

#### Step 2: Run Dependency Tracer  
```bash
npm-dep-tracer --root vite --mode why-unused  
```  
**Output:**  
```  
Tracing dependency tree for: vite@5.1.0  
[!] Detected 12 phantom packument requests (not in final tree):  
  - playwright@1.39.0 (via: @vitejs/plugin-e2e(opt))  
  - @types/node@20.8.10 (via: vitest(peer))  
  - webdriverio@8.24.7 (via: @vitejs/plugin-e2e(opt) -> @vitest/runner)  
  - sass@1.69.5 (via: vite-plugin-sass-dts(opt))  
  ... (8 more)  
```  
**Observation:**  
- Labels `(opt)`/`(peer)` indicate unused optional/peer dependencies.  
- Initial trace shows provenance but not resolution path.  

---

#### Step 3: Request Edge-Specific Traces  
```bash
npm-dep-tracer --edge "@vitejs/plugin-e2e->playwright"  
```  
**Output:**  
```  
Edge trace: @vitejs/plugin-e2e@2.0.3 -> playwright@1.39.0  
Resolution path:  
  vite@5.1.0  
  └─┬ @vitejs/plugin-react@4.3.0 [direct]  
    └── @vitejs/plugin-e2e@2.0.3 [optional]  
        └── playwright@1.39.0 [dev]  

Registry fetch:  
  GET registry.npmjs.org/playwright (full packument)  
Trigger: Optional dependency resolution (not installed)  
```  

**Retry for peer dependency:**  
```bash
npm-dep-tracer --edge "vitest->@types/node"  
```  
**Output:**  
```  
Edge trace: vitest@1.2.0 -> @types/node@20.8.10  
Resolution path:  
  vite@5.1.0  
  └─┬ @vitejs/plugin-react@4.3.0  
    └── vitest@1.2.0 [peer]  
        └── @types/node@20.8.10 [peerOptional]  

Registry fetch:  
  GET registry.npmjs.org/@types%2fnode (full packument)  
Trigger: Peer dependency candidate check (skipped: not in tree)  
```  

---

#### Step 4: Verify with Tree Reconstruction  
```bash
npm-dep-tracer --reconstruct-tree  
```  
**Output (excerpt):**  
```  
Final install tree:  
vite@5.1.0  
├─┬ @vitejs/plugin-react@4.3.0  
│ ├── rollup@3.29.4  
│ └── esbuild@0.19.5  
...  

Unresolved edges (triggered registry fetches):  
[OPT] @vitejs/plugin-react@4.3.0 ➔ @vitejs/plugin-e2e@2.0.3  
[PEER] @vitejs/plugin-react@4.3.0 ➔ vitest@^1.0.0  
[PEER] vite@5.1.0 ➔ sass@* (via vite-plugin-sass-dts)  
...  
```  

---

#### Key Findings  
1. **Root Cause:**  
   - npm fetches full packuments for all *declared* dependencies (including optional/peer) during metadata resolution phase, even if they're later pruned from the tree.  
   - Primary triggers:  
     - Optional dependencies (e.g., `@vitejs/plugin-e2e` via `@vitejs/plugin-react`).  
     - Unmet peer dependencies (e.g., `vitest` → `@types/node`).  

2. **Problematic Edges:**  
   | Unused Package      | Triggering Edge                          | Dependency Type |  
   |---------------------|------------------------------------------|-----------------|  
   | `playwright`        | `@vitejs/plugin-react` → `@vitejs/plugin-e2e` | Optional         |  
   | `@types/node`       | `@vitejs/plugin-react` → `vitest`        | Peer            |  
   | `webdriverio`       | `@vitejs/plugin-e2e` → `@vitest/runner`  | Optional Dev    |  
   | `sass`              | `vite` → `vite-plugin-sass-dts`          | Peer Optional   |  

3. **Tool Limitations:**  
   - Cannot simulate network fetches (confirms via cached metadata patterns).  
   - Peer dependency traces require manual edge specification (`--edge` flag).  

---

**Conclusion:**  
The excess registry requests occur because npm resolves metadata for *all declared dependencies* before tree pruning. The `npm-dep-tracer` tool identified unused edges originating from optional/peer dependencies in `@vitejs/plugin-react` and transitive `vite` plugins. A fix would require deferring packument fetches for optional/peer dependencies until after tree finalization.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
