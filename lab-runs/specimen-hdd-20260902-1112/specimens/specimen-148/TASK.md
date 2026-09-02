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
