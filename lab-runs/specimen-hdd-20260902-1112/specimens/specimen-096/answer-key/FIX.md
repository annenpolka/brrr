KNOWN FIX (sealed): apache/maven-compiler-plugin PR 169 squash merge 52fb27ea14e0aa96fc1acd30e8c3e7fbd07c5563.

failing_ref is squash parent c62de5ccc75ff404d8ab5d6aa428434c127fb161.

resolveProcessorPathEntries on the failing revision used maven-compat org.apache.maven.repository.RepositorySystem.resolve(ArtifactResolutionRequest) with only localRepository + remoteArtifactRepositories. That request does not consult the Maven 3 WorkspaceReader, so a sibling extra processor module that exists only as reactor target/classes (process-test-classes, no install) is not a processorpath file. Public MCOMPILER-496: extra processor from the current multi-module build had to be installed/downloaded. Compile classpath was a different resolver (project artifacts) and never included a GAV that was only in annotationProcessorPaths.

Repair: resolve via org.eclipse.aether.RepositorySystem.resolveDependencies(session.getRepositorySession(), DependencyRequest) with CollectRequest on project.getRemoteProjectRepositories(). The repository session includes WorkspaceReader, so a reactor extra module's target/classes is a processorpath entry (Petr Široký on MCOMPILER-496: MCOMPILER-203-processorpath processorpath contains annotation-processor/target/classes plus commons-lang3 from the local repo). Added IT MCOMPILER-522-unresolvable-dependency: missing extra GAV fails compile with Resolution of annotationProcessorPath dependencies failed / Could not find artifact.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
