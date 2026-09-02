# TASK

A Maven multi-module tree has an extra annotation-processor module. The consumer module lists that extra module only under `maven-compiler-plugin` `annotationProcessorPaths` (Maven GAV). It is not a `<dependency>` of the consumer, so it is not on the consumer's compile classpath (`project.compileClasspathElements` / `project.getArtifacts()`).

In-tree fixture `src/it/MCOMPILER-203-processorpath/` (three reactor members):

```
compiler-test (pom)
  annotation-processor   artifactId annotation-processor; has org.issue.SimpleAnnotationProcessor
  annotation-verify      a plugin used after compile
  annotation-user        compiles SimpleObject / SimpleTestObject annotated with @SimpleAnnotation
```

Parent `<modules>` lists all three. `annotation-user/pom.xml` compile dependencies are `commons-io:2.7` and `junit:4.13.1` (test). The extra processor is only:

```
<annotationProcessors>
  <annotationProcessor>org.issue.SimpleAnnotationProcessor</annotationProcessor>
</annotationProcessors>
<annotationProcessorPaths>
  <path>
    <groupId>org.issue</groupId>
    <artifactId>annotation-processor</artifactId>
    <version>1.0-SNAPSHOT</version>
  </path>
</annotationProcessorPaths>
```

Invoker on that IT: `process-test-classes` (twice). That lifecycle does not run `install`.

On apache/maven-compiler-plugin `c62de5ccc75ff404d8ab5d6aa428434c127fb161`, `AbstractCompilerMojo` feeds javac like this:

```
compilerConfiguration.setAnnotationProcessors( annotationProcessors );
compilerConfiguration.setProcessorPathEntries( resolveProcessorPathEntries() );
```

`resolveProcessorPathEntries()` walks `annotationProcessorPaths`. For each GAV it builds `org.apache.maven.artifact.DefaultArtifact` and `ArtifactResolutionRequest` with:

```
.setArtifact( artifact )
.setResolveRoot( true )
.setResolveTransitively( true )
.setLocalRepository( session.getLocalRepository() )
.setRemoteRepositories( project.getRemoteArtifactRepositories() )
```

then `repositorySystem.resolve( request )` (`org.apache.maven.repository.RepositorySystem`, maven-compat). Each resolved artifact's `getFile().getAbsolutePath()` is appended to a `LinkedHashSet<String>` that becomes `-processorpath`. Failures wrap as `MojoExecutionException: Resolution of annotationProcessorPath dependencies failed: …`.

Regular compile classpath for the same mojo is the project's resolved compile artifacts (reactor-aware). It does not automatically include `annotationProcessorPaths`.

Case A — extra processor is a published Central GAV already in the local repo (example: a released lombok coordinate). `mvn compile` of a single-module consumer. `-processorpath` is the `~/.m2/repository/…/*.jar` path. Compile classpath does not contain that jar unless it is also a `<dependency>`.

Case B — extra processor is the reactor sibling `org.issue:annotation-processor:1.0-SNAPSHOT`. Consumer is `annotation-user`. Goal `process-test-classes` from the aggregator (no `install`). After `annotation-processor` has compiled, `annotation-processor/target/classes` exists in the reactor checkout. The extra GAV is not on `annotation-user`'s compile classpath. Public MCOMPILER-496 report: annotationProcessorPaths "cannot resolve annotation processor from current multi module build, and it requires annotation processor to be installed/downloaded."

Case C — extra processor GAV does not exist (`org.apache.maven.plugins.compiler.it:annotation-processor-non-existing:1.0-SNAPSHOT`, later IT `MCOMPILER-522-unresolvable-dependency`). Same `resolveProcessorPathEntries` request. Invoker expects build failure whose log contains `Could not find artifact …annotation-processor-non-existing:jar:1.0-SNAPSHOT`.

Case D — extra processor is also declared as a compile `<dependency>` of the consumer (same GAV, reactor sibling). Compile classpath then has the reactor output of that module through ordinary project dependency resolution. `annotationProcessorPaths` still goes through the separate `ArtifactResolutionRequest` above.

The developer wants to know, for case B, which path identity `setProcessorPathEntries` actually stored for the extra reactor module: `annotation-processor/target/classes`, the installed `~/.m2/…/annotation-processor-1.0-SNAPSHOT.jar`, both, omitted, or a resolution failure.
