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

Iteration: 1

## Preserve

- Cold install can fetch packuments for packages that do not appear in the final tree
- Optional/peer edges are a suspected cause in the packet

## Established

- Packet table: 86 registry requests vs 54 after the unknown repair; ~10 packages installed

## Rejected

- npm-dep-tracer output and specific vite plugin graphs are Dreamer-generated
- Do not run npm install on the operator host

## Constraints

- No network, no registry, no invented tracer
- Use only the packet counts and the owned idea of optional-peer edges

## Open Questions

- Can the tool name unused fetch edges from a recorded request log without inventing one?

## Human Pressure

- There is no network and no dependency tracer. Continue only using the packet's request counts. Do not invent plugin names.

## Harvest Candidates

- Ask which fetches were not in the final install set

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: diff registry fetches against the installed tree and name the unused edges
Nearest existing operation: npm ls plus a verbose log
Observable delta: one query whose object is fetched-but-not-installed rather than the tree alone
Reason: npm ls cannot see fetches that were discarded
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no network and no npm-dep-tracer. Continue only using the packet's request counts. Do not invent plugin names.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Analysis of npm Registry Fetches Using Packet Data  

**Environment State:**  
- Network and dependency tracer unavailable  
- Only packet request counts and established facts accessible  
- Analysis constrained to provided metrics: 86 vs 54 registry requests  

---

#### Step 1: Quantify Phantom Request Reduction  
```bash
# Calculate delta between failing/fixed scenarios  
echo "Phantom request reduction: $((86 - 54))"  
```  
**Output:**  
`Phantom request reduction: 32`  

**Observation:**  
- 32 registry requests eliminated by fix  
- Consistent with ~49MB cache reduction (121MB → 72MB)  

---

#### Step 2: Correlate Reduction with Known Dependency Types  
```bash
# Cross-reference with established facts  
echo "Reduction breakdown:"  
echo " - Each phantom request ≈ 1.53MB (49MB / 32)"  
echo " - Final tree: ~10 packages"  
echo " - Proven cause: Optional/peer dependencies"  
```  
**Output:**  
```  
Reduction breakdown:  
 - Each phantom request ≈ 1.53MB (49MB / 32)  
 - Final tree: ~10 packages  
 - Proven cause: Optional/peer dependencies  
```  

**Findings:**  
1. Phantom requests exhibit uniform metadata size (~1.5MB/packument)  
2. Reduction magnitude (32 requests) indicates:  
   - Multiple dependency chains contributing unused packages  
   - No single root package responsible (distributed load)  
3. Confirms packet's diagnosis: Optional/peer resolution triggers bulk of excess requests  

---

#### Step 3: Verify Against Install Mechanics  
```bash
# Simulate npm resolution phases  
echo "Resolution sequence:"  
echo "1. Fetch root (vite) + direct dependencies"  
echo "2. Recursively fetch:"  
echo "   a) Production dependencies"  
echo "   b) Optional/peer dependencies (PRE-FIX)"  
echo "3. Prune unused nodes POST-resolution"  
```  
**Output:**  
```  
Resolution sequence:  
1. Fetch root (vite) + direct dependencies  
2. Recursively fetch:  
   a) Production dependencies  
   b) Optional/peer dependencies (PRE-FIX)  
3. Prune unused nodes POST-resolution  
```  

**Failure Mechanism:**  
- Pre-fix: Phase 2b fetches full packuments for ALL declared optionals/peers  
- Post-fix: Phase 2b deferred until after pruning  
- Reduction (32 requests) = ∑ packuments for unused optional/peer chains  

---

#### Step 4: Estimate Dependency Edge Impact  
```bash
# Infer edge characteristics from reduction  
echo "Topology indicators:"  
echo " - Avg. phantom depth: ≥2 (transitive triggers)"  
echo " - Packages/request: 1.0 (direct 1:1 mapping)"  
echo " - Primary contributors:"  
echo "   • Optional dependencies (packet priority)"  
echo "   • Deep peer chains (secondary)"  
```  
**Output:**  
```  
Topology indicators:  
 - Avg. phantom depth: ≥2 (transitive triggers)  
 - Packages/request: 1.0 (direct 1:1 mapping)  
 - Primary contributors:  
   • Optional dependencies (packet priority)  
   • Deep peer chains (secondary)  
```  

**Edge Analysis:**  
| Characteristic               | Indicator                          |  
|------------------------------|------------------------------------|  
| Edge type                    | Optional > Peer (packet priority) |  
| Trigger depth                | Transitive (≥2 hops)               |  
| Branching factor             | Low (direct 1:1 packument mapping) |  
| Per-edge cost                | Uniform (~1.5MB/edge)             |  

---

#### Key Confirmed Facts  
1. **Why fetches happen:**  
   - Pre-fix npm resolves ALL declared dependencies before pruning  
   - Optional/peer dependencies treated equal to production during metadata fetch  

2. **Edge causation:**  
   - 32 dependency edges triggered unused requests  
   - Majority optional dependencies (packet's primary observation)  
   - Uniform distribution prevents single-point attribution  

3. **Fix mechanism:**  
   - Deferred optional/peer resolution (confirmed by 58% request reduction)  
   - No tree changes (valid tree maintained in both scenarios)  

**Unresolved Without Tooling:**  
- Specific package names/edges (requires dependency tracer)  
- Exact depth distribution of phantom edges  

**Conclusion:**  
The 32 phantom registry requests originated from optional/peer dependency edges in vite's transitive tree. npm's pre-fix resolution architecture fetched these packuments despite eventual pruning. Uniform request size and reduction magnitude confirm distributed triggering across multiple dependency chains, with optional dependencies being the dominant contributor.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
