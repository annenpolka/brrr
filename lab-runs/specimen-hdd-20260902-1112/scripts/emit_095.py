#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet (maven extra processor module).

apache/maven-compiler-plugin MCOMPILER-522 / PR 169. Extra annotation
processor listed only in annotationProcessorPaths is resolved with
maven-compat ArtifactResolutionRequest (local + remote repos). A sibling
reactor module is not a compile dependency, so it is not on the reactor
compile classpath. process-test-classes does not install. Distinct from
Honor-KILLed extraedge (poetry extras table) and unusedfp (gradle CC).
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, with_state
from update_index import main as update_index

JOB_ID = "job-0334"
WORKER = "scout-job-0334"
TRIAL = "hdd-mvnextra"
START_N = 96


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 130):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id in 096-129")


def packet_for(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: apache/maven-compiler-plugin
failing_ref: c62de5ccc75ff404d8ab5d6aa428434c127fb161
fixed_ref: 52fb27ea14e0aa96fc1acd30e8c3e7fbd07c5563
source_issue: https://issues.apache.org/jira/browse/MCOMPILER-522
source_pr: https://github.com/apache/maven-compiler-plugin/pull/169
mechanism_tags:
  - extra-processor-module
  - annotationProcessorPaths
  - reactor-vs-local-repo
  - processorpath-file-identity
ecosystem: maven
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

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
""",
        observed="""# OBSERVED

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
""",
        commands="""# COMMANDS

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
""",
        tree="""apache/maven-compiler-plugin
  src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
  src/it/MCOMPILER-203-processorpath/pom.xml
  src/it/MCOMPILER-203-processorpath/annotation-processor/
  src/it/MCOMPILER-203-processorpath/annotation-user/pom.xml
  src/it/MCOMPILER-522-unresolvable-dependency/pom.xml
  javac -processorpath <resolved extra GAV files>
""",
        source="""repository: apache/maven-compiler-plugin
issue: https://issues.apache.org/jira/browse/MCOMPILER-522
related_issue: https://issues.apache.org/jira/browse/MCOMPILER-496
related_github: https://github.com/apache/maven-compiler-plugin/issues/707
pr: https://github.com/apache/maven-compiler-plugin/pull/169
failing_ref (squash parent): c62de5ccc75ff404d8ab5d6aa428434c127fb161
fixed_ref (squash merge commit): 52fb27ea14e0aa96fc1acd30e8c3e7fbd07c5563
pr_head: a2af18b1ee40f9c998acf36caa663d5211275e83
merged_at: 2023-01-22T19:15:15Z
merged_by: slawekjaranowski
pr_author: psiroky
changed_files: pom.xml, AbstractCompilerMojo.java, src/it/MCOMPILER-522-unresolvable-dependency/*
pr_title: [MCOMPILER-522] Use maven-resolver to resolve 'annotationProcessorPaths' dependencies
scout_note: not Honor-KILLed extraedge (poetry extras table, specimen-021 / hdd-gitextra). not Honor-KILLed unusedfp (gradle configuration-cache unused property identity, specimen-076). not MCOMPILER-320 additionalCompilePathItems (PR 1, WON'T FIX, no fixed_ref). not MCOMPILER-372 extra test-jar --patch-module (PR 27, never merged). not SUREFIRE-2179 additionalClasspathDependencies which documents "Only external dependencies (outside the current Maven reactor) are supported" as a feature. Distinct leftover: extra annotation-processor GAV is a reactor sibling listed only on annotationProcessorPaths; maven-compat ArtifactResolutionRequest uses local+remote and never the reactor compile classpath.
""",
        answer_key="""KNOWN FIX (sealed): apache/maven-compiler-plugin PR 169 squash merge 52fb27ea14e0aa96fc1acd30e8c3e7fbd07c5563.

failing_ref is squash parent c62de5ccc75ff404d8ab5d6aa428434c127fb161.

resolveProcessorPathEntries on the failing revision used maven-compat org.apache.maven.repository.RepositorySystem.resolve(ArtifactResolutionRequest) with only localRepository + remoteArtifactRepositories. That request does not consult the Maven 3 WorkspaceReader, so a sibling extra processor module that exists only as reactor target/classes (process-test-classes, no install) is not a processorpath file. Public MCOMPILER-496: extra processor from the current multi-module build had to be installed/downloaded. Compile classpath was a different resolver (project artifacts) and never included a GAV that was only in annotationProcessorPaths.

Repair: resolve via org.eclipse.aether.RepositorySystem.resolveDependencies(session.getRepositorySession(), DependencyRequest) with CollectRequest on project.getRemoteProjectRepositories(). The repository session includes WorkspaceReader, so a reactor extra module's target/classes is a processorpath entry (Petr Široký on MCOMPILER-496: MCOMPILER-203-processorpath processorpath contains annotation-processor/target/classes plus commons-lang3 from the local repo). Added IT MCOMPILER-522-unresolvable-dependency: missing extra GAV fails compile with Resolution of annotationProcessorPath dependencies failed / Could not find artifact.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (published extra GAV in local repo vs reactor sibling extra GAV with no install vs missing extra GAV vs extra GAV also on compile classpath; processorpath ArtifactResolutionRequest vs compile classpath project artifacts)
reproducibility: source-backed JIRA+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — extra module is in the reactor modules list but not on the consumer compile classpath; processorpath is a second coordinate list resolved without the reactor workspace
ecosystem: maven / maven-compiler-plugin
mechanism_family: extra-processor-module, annotationProcessorPaths, reactor-vs-local-repo

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "resolve_processor_path_failing.java": """// Reduced excerpt of resolveProcessorPathEntries on failing_ref
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
""",
            "set_processor_path_failing.java": """// Reduced excerpt of compiler configuration on failing_ref
// src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
// Processor names and processorpath files are separate from compile classpath.

        compilerConfiguration.setSourceLocations( compileSourceRoots );

        compilerConfiguration.setAnnotationProcessors( annotationProcessors );

        compilerConfiguration.setProcessorPathEntries( resolveProcessorPathEntries() );

        compilerConfiguration.setSourceEncoding( encoding );
""",
            "repository_system_field_failing.java": """// Reduced excerpt of injected resolver on failing_ref
// src/main/java/org/apache/maven/plugin/compiler/AbstractCompilerMojo.java
// org.apache.maven.repository.RepositorySystem is maven-compat (Maven 2 API).

    /**
     * Resolves the artifacts needed.
     */
    @Component
    private RepositorySystem repositorySystem;
""",
            "annotation_user_pom.xml": """<!-- Reduced excerpt of src/it/MCOMPILER-203-processorpath/annotation-user/pom.xml
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
""",
            "leftover_identity_split.txt": """Registry / fixture:
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
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"launched": False, "reason": ""}

    def fn(state):
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == JOB_ID), None)
        if job is None:
            raise SystemExit(f"{JOB_ID} missing")
        if job.get("status") == "CLAIMED" and job.get("worker") == WORKER:
            complete(state, JOB_ID, result="ok", artifact=f"specimens/{spec_id}")
        elif job.get("status") == "DONE" and job.get("artifact") == f"specimens/{spec_id}":
            pass
        else:
            raise SystemExit(
                f"{JOB_ID} status={job.get('status')} worker={job.get('worker')} artifact={job.get('artifact')}"
            )
        ids = {s.get("id") for s in state.get("specimens") or []}
        if spec_id not in ids:
            state.setdefault("specimens", []).append({"id": spec_id})
        already = any(
            j.get("queue") == "READY_R1_DREAM"
            and j.get("specimen") == spec_id
            and j.get("status") in {"READY", "CLAIMED"}
            for j in state.get("ready_jobs") or []
        )
        if not already:
            enqueue(
                state,
                "READY_R1_DREAM",
                input_ref=f"seeds/{spec_id}.md trial={TRIAL}",
                expected_output="0001-dreamer.md",
                kill_condition="15m",
                estimated_cost="r1",
                priority_reason="maven extra processor module not on reactor classpath; not extraedge/unusedfp",
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        ready_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "READY"
        ]
        if claimed_r1:
            note["reason"] = (
                "dream.sh not launched; R1 already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        elif any(j.get("lineage") != TRIAL for j in ready_r1):
            note["reason"] = (
                "dream.sh not launched; READY_R1_DREAM already queued: "
                + ",".join(
                    f"{j['id']}:{j.get('lineage')}"
                    for j in ready_r1
                    if j.get("lineage") != TRIAL
                )
            )
        else:
            note["reason"] = (
                "dream.sh not launched from scout; READY_R1_DREAM enqueued "
                f"trial={TRIAL} (hdd-gitpath in flight; coordinator owns dreamer slots)"
            )
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_for(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(f"enqueued READY_R1_DREAM trial={TRIAL} specimen={spec_id}")
        print(launch_note)
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
