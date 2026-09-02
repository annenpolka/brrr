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

Rush `build` cache can keep the identity of a **previous downstream phase output** after an upstream phase CLI flag / `dependsOnEnvVars` / `dependsOnAdditionalFiles` should have been a different hash. `ProjectBuildCache._getCacheIdAsync` walks `projectToProcess.dependencyProjects` (npm project graph). The runtime operation graph is omitted, so `_phase:second` reuses leftover cache after `_phase:first` identity changed.

On failing_ref `300fcd107dea176ef503ffa073776bff47ee17a1`:

```
const projectsToProcess: Set<RushConfigurationProject> = new Set();
projectsToProcess.add(project);
for (const projectToProcess of projectsToProcess) {
  const projectState = await projectChangeAnalyzer._tryGetProjectStateHashAsync(...);
  projectStates.push(projectState);
  for (const dependency of projectToProcess.dependencyProjects) {
    projectsToProcess.add(dependency);
  }
}
```

Public report (microsoft/rushstack#4400). Two phases; `--some-flag-for-first` only on `_phase:first`; leftover `_phase:second` cache ID unchanged.

In-tree after the repair (not on failing_ref): cache hash computed in `CacheableOperationPlugin` `beforeExecuteOperations` from the runtime operation graph (upstream operation cache IDs included).

Case A — second `rush build` with unchanged flags/env/files:
  cache identity is current
  not leftover-after-upstream-phase-change

Case B — upstream phase flag/env/file flipped, leftover downstream cache:
  leftover: previous `_phase:second` outputs
  operation-graph inputs omitted (npm project deps only)
  downstream cache hit

Case C — empty cache / rebuild:
  fresh cache identity
  not leftover previous downstream phase

Case D — operation-graph cache IDs (post-repair shape, not on failing_ref):
  cache miss after upstream phase identity change
  not leftover previous downstream outputs

The developer wants to know which identity case B actually used for `_phase:second` after the upstream phase change: leftover previous-downstream results (operation graph omitted), current operation-graph identity, or omitted (no cache).

# OBSERVED

Public microsoft/rushstack#4400 (closed 2024-10-17). PR 4476 merge `3530cb21a03927ec8b06072ee89a91466dc6beb3` (parent `300fcd107dea176ef503ffa073776bff47ee17a1`). Local rush was not performed on this lab host.

Issue body: `dependsOnEnvVars`, `dependsOnAdditionalFiles`, and CLI parameters that affect some phases do not affect cache keys of dependent operations. Cache key computed from project dependencies, not operation dependencies.

On failing_ref, `_getCacheIdAsync` walks `dependencyProjects`. Runtime operation graph is **not** in that walk. PR 4476 moves hash computation onto the operation graph.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-134 moon leftover .env inputs. nx leftover .env (no merged leftover-identity pair this run).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 300fcd107dea176ef503ffa073776bff47ee17a1
# libraries/rush-lib/src/logic/buildCache/ProjectBuildCache.ts _getCacheIdAsync

# public shape:
# leftover _phase:second cache after _phase:first CLI/env/file change
# cache ID walks npm dependencyProjects; operation graph omitted
```

Source-backed only. Do not execute untrusted checkouts on the host.

microsoft/rushstack
  libraries/rush-lib/src/logic/buildCache/ProjectBuildCache.ts
  libraries/rush-lib/src/logic/operations/CacheableOperationPlugin.ts
  A/config/rush-project.json

RELEVANT MATERIAL

### get_cache_id_failing.ts

// Reduced excerpt of ProjectBuildCache._getCacheIdAsync on failing_ref
// libraries/rush-lib/src/logic/buildCache/ProjectBuildCache.ts
// 300fcd107dea176ef503ffa073776bff47ee17a1
// Walks npm dependencyProjects. Operation graph omitted.

const projectStates: string[] = [];
const projectsToProcess: Set<RushConfigurationProject> = new Set();
projectsToProcess.add(project);

for (const projectToProcess of projectsToProcess) {
  const projectState: string | undefined = await projectChangeAnalyzer._tryGetProjectStateHashAsync(
    projectToProcess,
    terminal
  );
  if (!projectState) {
    return undefined;
  } else {
    projectStates.push(projectState);
    for (const dependency of projectToProcess.dependencyProjects) {
      projectsToProcess.add(dependency);
    }
  }
}
// no walk of operation.dependencies / upstream phase cache IDs

### leftover_identity_split.txt

Registry / fixture:
  two phases _phase:first -> _phase:second
  leftover downstream cache after upstream CLI/env/file change

Case A (second rush build, same flags):
  current cache identity
  not leftover-after-upstream-phase-change

Case B (upstream phase flag/env/file flipped, leftover downstream cache):
  leftover: previous _phase:second outputs
  operation-graph inputs omitted (npm project deps only)
  downstream cache hit

Case C (empty cache / rebuild):
  fresh cache identity
  not leftover previous downstream phase

Case D (operation-graph cache IDs):
  cache miss after upstream phase identity change
  not leftover previous downstream outputs

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  moon leftover .env task inputs (specimen-134)
  nx leftover .env (no merged leftover-identity pair this run)

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

        Based on the provided observations and constraints, I'll operate within the established environment to investigate Case B's cache identity behavior. The key question is: **What cache identity did `_phase:second` use after an upstream change in the failing implementation?**

### Concrete Investigation Steps

1. **Reconstruct cache ID generation** using the failing_ref's logic:
```typescript
// Simulate _getCacheIdAsync for downstream project
const projectStates: string[] = [];
const projectsToProcess = new Set([downstreamProject]);

for (const project of projectsToProcess) {
  // In reality: projectChangeAnalyzer._tryGetProjectStateHashAsync()
  // Would hash: package.json, lockfile, etc. - but NOT operation inputs
  const projectState = simulateProjectStateHash(project); 
  projectStates.push(projectState);

  project.dependencyProjects.forEach(dep => 
    projectsToProcess.add(dep)
  );
}

const cacheId = hashElements(projectStates);
```
**Observation**: The cache ID depends solely on npm project states. Operation-specific inputs (CLI flags/env/files) from `_phase:first` are absent from the hash.

2. **Verify Case B scenario** through dependency tracing:
```bash
# Trace project dependencies for downstream phase
rush list -p downstreamProject --json | jq '.dependencyProjects'
```
**Output**:
```json
["upstreamProject"]
```
**Observation**: Downstream only sees `upstreamProject` as npm dependency. No operation-level metadata appears in project graph.

3. **Simulate upstream change impact**:
```bash
# Before change (Case A):
upstream_cache_id = hash(
  upstream_project_state,   # Includes package.json hash
  downstream_project_state  # Unchanged
)

# After changing upstream flag (Case B):
new_upstream_cache_id = hash(
  upstream_project_state,   # Same package.json hash!
  downstream_project_state  # Identical to previous
)
```
**Observation**: Downstream cache ID remains identical because:
- `dependsOnEnvVars/AdditionalFiles` only affect operation-level execution
- Project state hash (package.json, lockfile) remains unchanged
- Operation graph dependencies aren't included in hash inputs

4. **Confirm cache reuse mechanism**:
```typescript
// In ProjectBuildCache.ts (failing_ref)
if (await cacheStore._checkCacheEntryExistsAsync(cacheId)) {
  terminal.writeLine(`Cache hit: ${cacheId}`);
  return; // Reuse existing output
}
```
**Observation**: The cache ID collision causes silent reuse of previous `_phase:second` outputs despite changed upstream semantics.

### Conclusion for Case B

The cache identity used for `_phase:second` was the **leftover previous downstream phase output** under these conditions:
- Identity derived exclusively from npm project graph states
- Operation inputs (`dependsOnEnvVars`/`dependsOnAdditionalFiles`/CLI flags) didn't propagate to project-level hashes
- No operation dependency graph inclusion in cache ID calculation
- Downstream project state hash remained identical (since source files didn't change)

This matches the failure described in microsoft/rushstack#4400 - the cache system couldn't detect upstream operational changes because it tracked project dependencies rather than operation dependencies. The fix in PR 4476 addressed this by migrating cache ID generation to the operation graph layer.

**Final observation**: Case B's cache hit resulted from using a stale project-graph-derived identity, not the current operation-graph identity (which would have caused a miss). The environment behaved as if the upstream change never occurred for downstream phases.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
