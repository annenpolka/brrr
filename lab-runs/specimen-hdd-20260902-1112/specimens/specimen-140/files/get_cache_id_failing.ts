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
