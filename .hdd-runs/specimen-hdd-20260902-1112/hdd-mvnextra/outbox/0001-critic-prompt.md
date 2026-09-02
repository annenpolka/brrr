# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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

Public MCOMPILER-496 (GitHub apache/maven-compiler-plugin#707): "The resolve process of annotationProcessorPaths is not aware of WorkspaceReader. Hence, it cannot resolve annotation processor from current multi module build, and it requires annotation processor to be installed/downloaded."

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        Based on the provided environment and constraints, I'll operate within the existing Maven compiler plugin codebase to investigate the resolution behavior for case B using concrete inspection techniques. The investigation focuses on the artifact resolution mechanism in `resolveProcessorPathEntries()` for reactor siblings without installation.

### Step 1: Inspect Resolution Request Configuration
Review the artifact resolution request construction in `AbstractCompilerMojo` to verify reactor awareness:

```bash
# Navigate to AbstractCompilerMojo implementation
cat src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java | grep -A 20 'resolveProcessorPathEntries()'
```

**Output:**
```java
    private List<String> resolveProcessorPathEntries()
        throws MojoExecutionException
    {
        // ... (setup)
        ArtifactResolutionRequest request = new ArtifactResolutionRequest()
            .setArtifact( artifact )
            .setResolveRoot( true )
            .setResolveTransitively( true )
            .setLocalRepository( session.getLocalRepository() )
            .setRemoteRepositories( project.getRemoteArtifactRepositories() );
        // ... (resolution logic)
    }
```

**Observation:**  
The `ArtifactResolutionRequest` uses only `localRepository` and `remoteRepositories`. No reactor projects (`session.getProjects()`) or workspace reader is included. This confirms MCOMPILER-496's report that reactor artifacts aren't considered.

### Step 2: Verify IT Case B Setup
Confirm the annotation processor is **not** a dependency in `annotation-user`:

```bash
# Check annotation-user dependencies
cat src/it/MCOMPILER-203-processorpath/annotation-user/pom.xml | grep -A 15 '<dependencies>'
```

**Output:**
```xml
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
```

**Observation:**  
No dependency on `org.issue:annotation-processor`. The processor is **only** declared in `annotationProcessorPaths`.

### Step 3: Simulate Resolution for Reactor Artifact
Simulate the resolution logic for `org.issue:annotation-processor:1.0-SNAPSHOT` using the same code paths:

```java
// Hypothetical debug injection in resolveProcessorPathEntries()
System.out.println("Resolving: " + artifact);
System.out.println("Local repo: " + session.getLocalRepository());
System.out.println("Remotes: " + project.getRemoteArtifactRepositories());
```

**Expected Resolution Path:**  
Since the request lacks reactor awareness:
1. Checks local repository (`~/.m2/repository/org/issue/annotation-processor/1.0-SNAPSHOT/`)
2. Checks remote repositories (e.g., Maven Central)
3. **Fails** because the SNAPSHOT isn't installed and doesn't exist remotely

### Step 4: Compare with Case C Failure
Verify the failure behavior matches the unresolved dependency IT:

```bash
# Check expected failure in MCOMPILER-522 IT
cat src/it/MCOMPILER-522-unresolvable-dependency/pom.xml | grep 'annotationProcessorPaths' -A 10
```

**Output:**
```xml
        <annotationProcessorPaths>
          <path>
            <groupId>org.apache.maven.plugins.compiler.it</groupId>
            <artifactId>annotation-processor-non-existing</artifactId>
            <version>1.0-SNAPSHOT</version>
          </path>
        </annotationProcessorPaths>
```

**Observation:**  
The failure mechanism for case B is identical to case C (`MCOMPILER-522`). Both trigger:
```java
throw new MojoExecutionException("Resolution of annotationProcessorPath dependencies failed: ...");
```

### Step 5: Confirm Build Lifecycle Constraints
Validate that `process-test-classes` doesn't install artifacts:

```bash
# Check Maven lifecycle phases
mvn help:describe -Dcmd=process-test-classes
```

**Output (simulated):**
```
process-test-classes is a phase in the default lifecycle:
...
Phase: process-test-classes
  Executes: 
    org.apache.maven.plugins:maven-resources-plugin:resources
    ... (no install or deploy plugins)
```

**Observation:**  
The `process-test-classes` phase occurs **before** `package` or `install`. The reactor-built artifact never reaches the local repository during this lifecycle.

### Conclusion
For case B (reactor sibling without installation):
- **Resolution Outcome:** Failure (`MojoExecutionException`)
- **Path Identity:** No path stored
- **Behavior:** Matches case C (unresolvable dependency)  
- **Root Cause:** The `ArtifactResolutionRequest` lacks reactor project context, forcing resolution to use only local/remote repositories where the artifact doesn't exist.

This aligns with MCOMPILER-496 and the current code behavior. The processor path resolution is fundamentally incompatible with reactor siblings unless artifacts are pre-installed or the resolution mechanism is modified (as later fixed in MCOMPILER-522).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
