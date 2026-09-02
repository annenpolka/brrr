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
