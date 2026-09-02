CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# COMMANDS

```
# not executed on this lab host
# failing_ref c62de5ccc75ff404d8ab5d6aa428434c127fb161
# src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
#   resolveProcessorPathEntries / setProcessorPathEntries
# src/it/MCOMPILER-203-processorpath/  (reactor extra processor)
# src/it/MCOMPILER-522-unresolvable-dependency/  (missing extra GAV)

# public case B (aggregator, extra module not a compile dependency):
# mvn process-test-classes
# extra GAV: org.issue:annotation-processor:1.0-SNAPSHOT
# compile classpath of annotation-user: commons-io + junit (test)
# processorpath: output of resolveProcessorPathEntries (local+remote ArtifactResolutionRequest)

# public case C (missing extra GAV):
# mvn compile
# Resolution of annotationProcessorPath dependencies failed:
# Could not find artifact …:annotation-processor-non-existing:jar:1.0-SNAPSHOT
```

Source-backed only. Do not execute untrusted checkouts on the host.

apache/maven-compiler-plugin
  src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
  src/it/MCOMPILER-203-processorpath/pom.xml
  src/it/MCOMPILER-203-processorpath/annotation-processor/
  src/it/MCOMPILER-203-processorpath/annotation-user/pom.xml
  src/it/MCOMPILER-522-unresolvable-dependency/pom.xml
  javac -processorpath <resolved extra GAV files>

RELEVANT MATERIAL

### annotation_user_pom.xml

<!-- Reduced excerpt of src/it/MCOMPILER-203-processorpath/annotation-user/pom.xml
     failing_ref c62de5ccc75ff404d8ab5d6aa428434c127fb161
     Extra processor GAV is not a <dependency>. -->
  <artifactId>annotation-user</artifactId>

  <dependencies>
    <dependency>
      <groupId>commons-io</groupId>
      <artifactId>commons-io</artifactId>
      <version>2.7</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.1</version>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <artifactId>maven-compiler-plugin</artifactId>
        <configuration>
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
        </configuration>
      </plugin>
    </plugins>
  </build>

### leftover_identity_split.txt

Registry / fixture:
  in-tree: src/it/MCOMPILER-203-processorpath (reactor extra processor)
  in-tree: src/it/MCOMPILER-522-unresolvable-dependency (missing extra GAV)
  public MCOMPILER-496: extra processor in current multi-module build requires install/download

Extra GAV (cases B/C):
  org.issue:annotation-processor:1.0-SNAPSHOT
  org.apache.maven.plugins.compiler.it:annotation-processor-non-existing:1.0-SNAPSHOT

Case A (published extra GAV already in local repo):
  -processorpath ~/.m2/repository/…/*.jar
  compile classpath does not contain it unless also a <dependency>

Case B (reactor sibling extra, process-test-classes, no install):
  extra GAV not on annotation-user compile classpath
  annotation-processor/target/classes exists in the reactor checkout
  resolveProcessorPathEntries uses local+remote ArtifactResolutionRequest
  public report: cannot resolve from current multi-module build

Case C (missing extra GAV):
  Resolution of annotationProcessorPath dependencies failed
  Could not find artifact …:annotation-processor-non-existing:jar:1.0-SNAPSHOT

Case D (extra GAV also a compile <dependency>):
  compile classpath uses ordinary reactor project artifacts
  processorpath still uses the separate ArtifactResolutionRequest

Not this packet:
  poetry extras table miss (specimen-021)
  gradle configuration-cache unused property identity (specimen-076)
  MCOMPILER-320 additionalCompilePathItems (PR 1, WON'T FIX, unpinned)
  MCOMPILER-372 extra test-jar --patch-module (PR 27, unmerged)
  SUREFIRE-2179 additionalClasspathDependencies (external-only by design)

### repository_system_field_failing.java

// Reduced excerpt of injected resolver on failing_ref
// src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
// org.apache.maven.repository.RepositorySystem is maven-compat (Maven 2 API).

    /**
     * Resolves the artifacts needed.
     */
    @Component
    private RepositorySystem repositorySystem;

### resolve_processor_path_failing.java

// Reduced excerpt of resolveProcessorPathEntries on failing_ref
// src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
// c62de5ccc75ff404d8ab5d6aa428434c127fb161
// Extra GAVs in annotationProcessorPaths. maven-compat resolve.
// Request carries local repo + remotes only.

    private List<String> resolveProcessorPathEntries()
        throws MojoExecutionException
    {
        if ( annotationProcessorPaths == null || annotationProcessorPaths.isEmpty() )
        {
            return null;
        }

        try
        {
            Set<String> elements = new LinkedHashSet<>();
            for ( DependencyCoordinate coord : annotationProcessorPaths )
            {
                ArtifactHandler handler = artifactHandlerManager.getArtifactHandler( coord.getType() );

                Artifact artifact = new DefaultArtifact(
                     coord.getGroupId(),
                     coord.getArtifactId(),
                     VersionRange.createFromVersionSpec( coord.getVersion() ),
                     Artifact.SCOPE_RUNTIME,
                     coord.getType(),
                     coord.getClassifier(),
                     handler,
                     false );

                ArtifactResolutionRequest request = new ArtifactResolutionRequest()
                                .setArtifact( artifact )
                                .setResolveRoot( true )
                                .setResolveTransitively( true )
                                .setLocalRepository( session.getLocalRepository() )
                                .setRemoteRepositories( project.getRemoteArtifactRepositories() );

                ArtifactResolutionResult resolutionResult = repositorySystem.resolve( request );

                resolutionErrorHandler.throwErrors( request, resolutionResult );

                for ( Artifact resolved : resolutionResult.getArtifacts() )
                {
                    elements.add( resolved.getFile().getAbsolutePath() );
                }
            }
            return new ArrayList<>( elements );
        }
        catch ( Exception e )
        {
            throw new MojoExecutionException( "Resolution of annotationProcessorPath dependencies failed: "
                + e.getLocalizedMessage(), e );
        }
    }

### set_processor_path_failing.java

// Reduced excerpt of compiler configuration on failing_ref
// src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
// Processor names and processorpath files are separate from compile classpath.

        compilerConfiguration.setSourceLocations( compileSourceRoots );

        compilerConfiguration.setAnnotationProcessors( annotationProcessors );

        compilerConfiguration.setProcessorPathEntries( resolveProcessorPathEntries() );

        compilerConfiguration.setSourceEncoding( encoding );

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
