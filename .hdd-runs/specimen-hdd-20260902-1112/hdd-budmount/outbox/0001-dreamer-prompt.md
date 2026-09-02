# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
