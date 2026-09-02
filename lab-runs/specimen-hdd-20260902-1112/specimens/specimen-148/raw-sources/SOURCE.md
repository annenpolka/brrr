repository: containers/buildah
issue: https://github.com/containers/buildah/issues/4522
pr: https://github.com/containers/buildah/pull/4526
failing_ref (first parent of merge): 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4
fixed_ref (DidExecute avoidLookingCache): 3f805bcd8cd2fa522d6d2fd9ecfacf71da6aa5f9
merged_at: 2023-01-18T13:38:19Z
pr_author: flouthoc
merged_by: openshift-merge-robot
changed_files: imagebuildah/stage_executor.go, internal/types.go, tests/bud.bats
pr_title: stage_executor: while mounting stages make sure freshly built stage is used
scout_note: not 066 moby / not 144 skaffold / not 097 buildkit git-dir. leftover RUN --mount from-stage after source rebuilt. unique vs 001-147.
