// Reduced excerpt of RUN --mount from-stage cache on failing_ref
// imagebuildah/stage_executor.go
// 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4
// StageMountDetails has MountPoint only. DidExecute omitted.
// leftover RUN --mount cache after source stage rebuilt.

if otherStage, ok := s.executor.stages[from]; ok && otherStage.index < s.index {
	stageMountPoints[from] = internal.StageMountDetails{IsStage: true, MountPoint: otherStage.mountPoint}
}
// cache lookup for this RUN proceeds even if otherStage was rebuilt
