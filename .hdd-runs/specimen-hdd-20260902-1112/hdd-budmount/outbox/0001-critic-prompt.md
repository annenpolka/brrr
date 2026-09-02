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

Buildah `RUN --mount=type=bind,from=dependencies` can keep the identity of a **previous mounted stage** after that source stage was rebuilt and the copied file should have been different. The RUN layer is reused from cache. The mount-stage map stores `MountPoint` only. Whether the source stage actually executed this build is not part of cache identity.

On failing_ref `4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4`:

```
if otherStage, ok := s.executor.stages[from]; ok && otherStage.index < s.index {
    stageMountPoints[from] = internal.StageMountDetails{IsStage: true, MountPoint: otherStage.mountPoint}
}
// later: cache lookup for this RUN proceeds even if otherStage was rebuilt
```

`StageMountDetails` has `IsStage` and `MountPoint` only. `DidExecute` does not exist.

Public report (containers/buildah#4522). First stage writes `/build/version` `v1`; second stage `RUN --mount=from=dependencies` copies it. Change `v1` to `v2`; second build still prints `Using cache` for the RUN --mount layer and the image still contains leftover `v1`.

In-tree after the repair (not on failing_ref): `DidExecute` on `StageMountDetails` / `StageExecutor`; if any mounted stage `DidExecute`, `avoidLookingCache = true`.

Case A — second build, source stage unchanged:
  cache identity is current
  not leftover-after-source-stage-change

Case B — source stage rebuilt, leftover RUN --mount cache:
  leftover: previous `/version` / previous mounted stage
  DidExecute omitted from cache identity
  `Using cache` on the copy step

Case C — `--no-cache` / `--layers=false`:
  fresh stage identity
  not leftover previous mount

Case D — avoid cache when mounted stage DidExecute (post-repair shape, not on failing_ref):
  new `/version` after source stage change
  not leftover previous mount

The developer wants to know which identity case B actually used for the RUN --mount layer after the source stage change: leftover previous-cache layer (DidExecute omitted), current mounted-stage identity, or omitted (no cache).

# OBSERVED

Public containers/buildah#4522 (closed 2023-01-18). PR 4526 merge `3f805bcd8cd2fa522d6d2fd9ecfacf71da6aa5f9` (first parent `4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4`). Local buildah was not performed on this lab host.

Issue body: RUN --mount=from=otherstage reused from cache even though otherstage changed; resulting image still prints leftover `v1`.

On failing_ref, `runStageMountPoints` records only MountPoint. Cache lookup for the RUN step does not know the source stage was freshly executed.

Not this packet: specimen-066 moby leftover. specimen-144 skaffold leftover remote digest. specimen-097 buildkit leftover git-dir cache key omitting ref.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4
# imagebuildah/stage_executor.go runStageMountPoints / Execute cache lookup

# public shape:
# leftover RUN --mount layer after source stage rebuilt
# StageMountDetails has MountPoint only; DidExecute omitted
# --no-cache yields the new version file
```

Source-backed only. Do not execute untrusted checkouts on the host.

containers/buildah
  imagebuildah/stage_executor.go
  internal/types.go

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  buildah --layers RUN --mount=from=stage
  leftover /version after source stage rebuilt

Case A (second build, source stage unchanged):
  current cache identity
  not leftover-after-source-stage-change

Case B (source stage rebuilt, leftover RUN --mount):
  leftover: previous /version
  DidExecute omitted
  Using cache on the copy step

Case C (--no-cache):
  fresh stage identity
  not leftover previous mount

Case D (avoid cache when mounted stage DidExecute):
  new /version after source change
  not leftover previous mount

Not this packet:
  moby leftover (specimen-066)
  skaffold leftover remote digest (specimen-144)
  buildkit leftover git-dir cache key omitting ref (specimen-097)

### stage_mount_failing.go

// Reduced excerpt of RUN --mount from-stage cache on failing_ref
// imagebuildah/stage_executor.go
// 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4
// StageMountDetails has MountPoint only. DidExecute omitted.
// leftover RUN --mount cache after source stage rebuilt.

if otherStage, ok := s.executor.stages[from]; ok && otherStage.index < s.index {
	stageMountPoints[from] = internal.StageMountDetails{IsStage: true, MountPoint: otherStage.mountPoint}
}
// cache lookup for this RUN proceeds even if otherStage was rebuilt

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

        ### Field Report: Buildah Cache Identity Investigation  

**Operational Context**  
Using Buildah's existing CLI and internal mechanics (as documented in `imagebuildah/stage_executor.go` at failing_ref `4f8706bb`) to probe cache identity behavior for `RUN --mount=from=stage` after source stage rebuild. No local repository clone; relying solely on observed code paths and issue reproduction steps from public report #4522.  

---

#### **Step 1: Reproduce Failure Case B**  
*Command:*  
```bash
buildah build --layers -f Dockerfile .
```  
*Dockerfile:*  
```dockerfile
# Stage 1: Write version file  
FROM alpine AS dependencies  
RUN echo "v1" > /build/version  

# Stage 2: Mount and read version  
FROM alpine  
RUN --mount=type=bind,from=dependencies,source=/build,target=/build cat /build/version  
```  

*Observation (Initial Build):*  
```log
STEP 1/3: FROM alpine AS dependencies  
STEP 2/3: RUN echo "v1" > /build/version  
--> abc123  
STEP 3/3: RUN --mount=from=dependencies cat /build/version  
v1  
--> def456  
```  
Cached layer `def456` stored.  

*Modification:*  
Change `v1` → `v2` in `dependencies` stage. Rebuild.  

*Observation (Rebuild):*  
```log
STEP 1/3: FROM alpine AS dependencies  
RUN echo "v2" > /build/version  # Rebuilt  
--> xyz789  
STEP 3/3: RUN --mount=from=dependencies cat /build/version  
Using cache --> def456  # ⚠️ Reuses cached RUN layer  
Output: v1  # Leftover from first build  
```  
→ Confirms **Case B**: Cached `RUN --mount` layer reused despite source stage rebuild.  

---

#### **Step 2: Inspect Cache Key Components**  
*Hypothesis:* Cache identity hinges on `MountPoint` path (as per `stage_mount_failing.go`), ignoring whether source stage executed.  

*Test:* Forced cache miss via mount-point mutation.  
*Command:*  
```bash
buildah build --layers -f Dockerfile . --build-arg RANDOM=$(date +%s)
```  
*Dockerfile Addendum:*  
```dockerfile
ARG RANDOM  
RUN echo $RANDOM > /dev/null  # Mutate cache key  
```  

*Observation:*  
```log
STEP 3/3: RUN --mount=from=dependencies cat /build/version  
--> Fresh execution (no cache)  
Output: v2  
```  
→ Cache avoided when non-mount inputs change.  

---

#### **Step 3: Probe Cache Identity Logic**  
*Code Analysis (`failing_ref`):*  
```go
// imagebuildah/stage_executor.go  
stageMountPoints[from] = internal.StageMountDetails{  
  IsStage: true,  
  MountPoint: otherStage.mountPoint, // Only MountPoint stored  
}  
```  
→ Cache key for `RUN --mount` includes:  
- Command string (`cat /build/version`)  
- Mount source/target paths  
- **`MountPoint` value** (e.g., `/var/lib/containers/stage/0`)  

*Critical Fact:*  
**`MountPoint` path is stable across source-stage rebuilds.** The same path is reused for the same stage index, regardless of content changes.  

---

#### **Step 4: Verify Identity Case**  
*Test:* Compare cache keys between Case A and Case B:  
1. **Case A (Unchanged source):**  
   - Source stage cache hit → same `MountPoint`  
   - `RUN --mount` cache key identical → reuse expected.  

2. **Case B (Rebuilt source):**  
   - Source stage rebuilt → new content, same `MountPoint`  
   - `RUN --mount` cache key **unchanged** (depends only on path, not content)  
   → Reuses stale layer.  

*Conclusion:*  
**Identity used in Case B:**  
- Same cache key as Case A (`MountPoint` path + command metadata).  
- **Not** "omitted" cache (cache is valid per key).  
- **Not** "current mounted-stage identity" (content not part of key).  

---

#### **Summary of Findings**  
| Case | Source Stage Rebuilt | Cache Identity Mechanism | `RUN --mount` Outcome |  
|------|----------------------|--------------------------|------------------------|  
| **A** | No | `MountPoint` + command | Reuse (correct) |  
| **B** | Yes | **Same as A** (key unchanged) | Reuse (leftover) |  
| **C** | N/A | Cache disabled | Fresh run |  
| **D** | Yes | `DidExecute` flag (post-fix) | Fresh run |  

**Root Cause:**  
Cache key for `RUN --mount` relied solely on stable `MountPoint` path, not stage content or rebuild status. Fix (in later commits) added `DidExecute` to key.  

**Operator Note:**  
No speculative code execution performed. Findings derived from:  
1. Observed build outputs (v1→v2 leftover).  
2. Code structure at `failing_ref`.  
3. Cache bypass via ARG mutation.  
4. Public issue #4522 artifacts.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
