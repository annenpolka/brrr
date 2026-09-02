# OBSERVED

Public apache/maven-compiler-plugin MCOMPILER-522 / PR 169 (psiroky, merged 2023-01-22 by slawekjaranowski). Failing world: apache/maven-compiler-plugin `c62de5ccc75ff404d8ab5d6aa428434c127fb161` (parent of squash `52fb27ea14e0aa96fc1acd30e8c3e7fbd07c5563`). Local Maven execution was not performed on this lab host.

In-tree IT `src/it/MCOMPILER-203-processorpath/`: aggregator `compiler-test` with members `annotation-processor`, `annotation-verify`, `annotation-user`. Invoker goals `process-test-classes` then `process-test-classes` again. `annotation-user` names `org.issue:annotation-processor:1.0-SNAPSHOT` only under `annotationProcessorPaths`. That GAV is not a compile dependency.

On the failing revision, `resolveProcessorPathEntries` constructs maven-compat `ArtifactResolutionRequest` with local repository + remote repositories only. It does not pass `session.getProjects()` / reactor project list into that request. `compilerConfiguration.setProcessorPathEntries` then hands the returned absolute file paths to javac as `-processorpath`.

Public MCOMPILER-496 (GitHub apache/maven-compiler-plugin#707): annotationProcessorPaths "cannot resolve annotation processor from current multi module build, and it requires annotation processor to be installed/downloaded."

Case C shape (unresolvable extra GAV) is the IT added by PR 169: compile of a consumer whose `annotationProcessorPaths` names `annotation-processor-non-existing:1.0-SNAPSHOT`. Expected log fragment:

```
Caused by: org.apache.maven.plugin.MojoExecutionException: Resolution of annotationProcessorPath dependencies failed: Could not find artifact org.apache.maven.plugins.compiler.it:annotation-processor-non-existing:jar:1.0-SNAPSHOT
```

Ordinary compile dependencies of `annotation-user` (commons-io, junit) still resolve. The extra processor is a second coordinate list.

Not executed on this lab host.
