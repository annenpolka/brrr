#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet for gradle CC FileTree/file-collection fingerprint omit.

gradle/gradle#23265. Not specimen-076 (unused system-property snapshot / Honor-KILL unusedfp).
Not specimen-042 (BuildScopeInMemoryCachingScriptClassCompiler HashMap race).
Not specimen-051 (nested ValueSource identity deadlock).

Cargo already sealed specimen-086; yarn scout may race 087+. Exclusive mkdir.
"""
from __future__ import annotations

import os
from pathlib import Path

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, with_state
from update_index import main as update_index

JOB_ID = "job-0319"
WORKER = "scout-gradle-cc"
TRIAL = "hdd-ccfilecol"
FORBIDDEN = {f"specimen-{n:03d}" for n in range(75, 86)} | {"specimen-086"}
START_N = 87


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 100):
        spec_id = f"specimen-{n:03d}"
        if spec_id in FORBIDDEN:
            continue
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id in 087-099")


def packet_for(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: gradle/gradle
failing_ref: 040aac7031d900c2c548154fcbc75627b01e386c
fixed_ref: e4355b87b8ffc775cc005724853a10f95b1a58c8
source_issue: none
source_pr: https://github.com/gradle/gradle/pull/23265
mechanism_tags:
  - configuration-cache-fingerprint
  - file-collection-observation
  - configurable-file-tree
ecosystem: gradle
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

A Groovy build queries a `ConfigurableFileTree` at configuration time and prints the names:

```
task report {
    def tree = fileTree("src")
    def result = 'files=' + tree.files.name.sort()
    doLast {
        println(result)
    }
}
```

Layout on disk for the first two runs:

```
src/file1
src/dir/file2
```

`./gradlew report --configuration-cache` on gradle/gradle `040aac7031d900c2c548154fcbc75627b01e386c`:

- Run 1 stores a configuration-cache entry and prints `files=[file1, file2]`.
- Run 2 loads that entry and prints the same line.

Then `src/file3` is created. Run 3 is the same `report --configuration-cache` invocation.

A second build uses a *fixed* file collection of named files, not a directory tree:

```
task report {
    def files = files("file1", "file2")
    def result = files.files.name
    doLast { println(result) }
}
```

After a store+load pair, `file1` contents are rewritten to `updated`. The next `--configuration-cache` run still loads and still prints `[file1, file2]`.

A third build constructs `fileTree("src")` during configuration but never calls `.files`, `.empty`, `.contains(...)`, or `.visit { }`. After store+load, `src/file3` is created.

`ConfigurationCacheFingerprintWriter` on that revision already implements `fileCollectionObserved(FileCollection, String)` and, when that method runs, writes a `ConfigurationCacheFingerprint.WorkInputs` record (display name + simplified file collection + `host.fingerprintOf(...)`). `Instrumented.fileCollectionObserved` exists. Kotlin DSL precompiled script-plugin collection calls it. `DefaultConfigurableFileTree` on that revision has no `getFiles` / `isEmpty` / `contains` / `visit` override.

The developer wants to know which identity run 3 actually used for the queried `fileTree("src").files` case after `src/file3` appeared: a fingerprint that included the directory tree contents (and therefore missed), or a fingerprint that omitted the tree (and therefore reused the entry that still printed `files=[file1, file2]`).
""",
        observed="""# OBSERVED

Public gradle/gradle PR 23265, merge parent `040aac7031d900c2c548154fcbc75627b01e386c` (failing world). Merge commit `e4355b87b8ffc775cc005724853a10f95b1a58c8`. Milestone 8.1 RC1. PR body: first step treating file-system state queried through `FileCollection` APIs at configuration time as configuration-cache inputs; this PR instruments `ConfigurableFileTree` query methods.

`DefaultConfigurableFileTree` on the failing revision (`subprojects/file-collections/.../DefaultConfigurableFileTree.java`) stores `dir`, `patternSet`, `resolver`, `buildDependency`, `directoryFileTreeFactory`. It does **not** override `getFiles()`, `isEmpty()`, `contains(File)`, or `visit`. `visitChildren` wraps `directoryFileTreeFactory.create(dir, patternSet)` in a `FileTreeAdapter` with no observation listener:

```
protected void visitChildren(Consumer<FileCollectionInternal> visitor) {
    File dir = getDir();
    visitor.accept(new FileTreeAdapter(directoryFileTreeFactory.create(dir, patternSet), taskDependencyFactory, patternSetFactory));
}
```

`getFiles()` therefore comes from `CompositeFileTree` / `AbstractFileCollection`: walk the tree, return the `Set<File>`. No `fileCollectionObserved` call on that path.

On the same revision, `ConfigurationCacheFingerprintWriter` *does* implement undeclared-input `fileCollectionObserved`:

```
override fun fileCollectionObserved(fileCollection: FileCollection, consumer: String) {
    if (isInputTrackingDisabled()) {
        return
    }
    captureWorkInputs(consumer) { it(fileCollection as FileCollectionInternal) }
}
```

`captureWorkInputs` writes `ConfigurationCacheFingerprint.WorkInputs(workDisplayName, fileSystemInputs, host.fingerprintOf(fileSystemInputs))`.

`Instrumented.fileCollectionObserved(FileCollection, String)` exists and forwards to that writer. The only in-tree configuration-time caller on the failing revision is Kotlin DSL precompiled script-plugin file collection (`DefaultPrecompiledScriptPluginsSupport.collectScriptPluginFiles`): after filtering `**/*.gradle.kts` it does `fileCollectionObserved(it, "Kotlin DSL")` then `.files`. `ConfigurableFileTree.getFiles()` does not call `Instrumented.fileCollectionObserved`.

Public sample `gradle/configuration-cache-build-logic-inputs` (README, FileCollections queried at configuration time): Gradle 7.6, `queryDirInDsl` against `file-collections/src/dir`, then `echo ignored > file-collections/src/dir/file3.txt`, then the same task. Documented result: **incorrect cache hit**; the new file is ignored. The sample states that once those queried file collections are treated as configuration inputs, adding a file invalidates and the console reports that an input of `file-collections/build.gradle.kts` has changed.

In-tree integration coverage for `fileTree("src").files` at configuration time (`ConfigurationCacheFileCollectionIntegrationTest`) is **absent** on `040aac7031d900c2c548154fcbc75627b01e386c`. The class is added by PR 23265. That test's "a file is added" step expects:

```
Calculating task graph as configuration cache cannot be reused because an input to build file 'build.gradle' has changed.
files=[file1, file2, file3]
```

and a later "elements of fixed file collection are not treated as build inputs" example expects a **load** after rewriting `file1` contents.

This packet does not include a local Gradle clone. Do not execute Gradle on this host.
""",
        commands="""# COMMANDS

```
# failing_ref 040aac7031d900c2c548154fcbc75627b01e386c
# (not executed on this lab host)

# Case A — queried directory tree
# build.gradle: task report { def tree = fileTree("src"); def result = 'files=' + tree.files.name.sort(); doLast { println(result) } }
# src/file1, src/dir/file2
./gradlew report --configuration-cache
# run 1: Configuration cache entry stored. files=[file1, file2]
./gradlew report --configuration-cache
# run 2: Configuration cache entry reused. files=[file1, file2]
# then: create src/file3
./gradlew report --configuration-cache
# run 3: identity after the tree contents changed is the question

# Case B — fixed names, contents rewritten
# task report { def files = files("file1", "file2"); def result = files.files.name; doLast { println(result) } }
# after store+load: echo updated > file1
./gradlew report --configuration-cache
# documented: still load, still [file1, file2]

# Case C — fileTree constructed, never queried (.files / .empty / .contains / .visit)
# after store+load: create src/file3
```

Not executed on this lab host.
""",
        tree="""gradle/gradle
  subprojects/file-collections/src/main/java/org/gradle/api/internal/file/collections/DefaultConfigurableFileTree.java
  subprojects/file-collections/src/main/java/org/gradle/api/internal/file/collections/FileTreeAdapter.java
  subprojects/configuration-cache/src/main/kotlin/org/gradle/configurationcache/fingerprint/ConfigurationCacheFingerprintWriter.kt
  subprojects/core/src/main/java/org/gradle/internal/classpath/Instrumented.java
  subprojects/kotlin-dsl-provider-plugins/src/main/kotlin/org/gradle/kotlin/dsl/provider/plugins/precompiled/DefaultPrecompiledScriptPluginsSupport.kt
""",
        source="""repository: gradle/gradle
pr: https://github.com/gradle/gradle/pull/23265
issue: none (PR-only; related sample gradle/configuration-cache-build-logic-inputs)
failing_ref (merge first parent): 040aac7031d900c2c548154fcbc75627b01e386c
fixed_ref (merge commit): e4355b87b8ffc775cc005724853a10f95b1a58c8
head_sha: 607ec95683b6f29d420b0d8b147e1ee603b2a787
merged_at: 2022-12-22T06:54:24Z
merged_by: bot-gradle
milestone: 8.1 RC1
author: adammurdoch
pr_title: Include any directory queried via ConfigurableFileTree at configuration time in configuration cache fingerprint
changed_paths_note: DefaultConfigurableFileTree query methods, FileCollectionObservationListener, ConfigurationCacheFingerprintWriter, ConfigurationCacheFileCollectionIntegrationTest
scout_note: job-0319 gradle CC file collection identity. Distinct from specimen-076 unusedfp Honor-KILL (system property snapshot), specimen-042 HashMap race, specimen-051 nested ValueSource deadlock. Cargo sealed 086; yarn scout may race 087+.
""",
        answer_key="""KNOWN FIX (sealed): gradle/gradle PR 23265 merge e4355b87b8ffc775cc005724853a10f95b1a58c8.

ConfigurableFileTree query methods (getFiles, isEmpty, contains, visit) did not notify configuration-cache input tracking, so a directory tree read at configuration time never became WorkInputs in the fingerprint. Adding src/file3 after a store reused the entry. Repair: FileCollectionObservationListener on the file-collection factory; DefaultConfigurableFileTree/FileTreeAdapter query methods call fileCollectionObserved before walking; ConfigurationCacheFingerprintWriter implements that listener and writes WorkInputs + host.fingerprintOf. Fixed integration test then misses with "an input to build file 'build.gradle' has changed" and prints files=[file1, file2, file3]. Fixed-name files() still does not treat element contents as configuration inputs.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (queried fileTree("src").files + add src/file3 vs files("file1","file2") content rewrite that still loads; Kotlin DSL collectScriptPluginFiles already called Instrumented.fileCollectionObserved; constructed-but-never-queried tree)
reproducibility: source-backed PR + pinned merge parent/merge commit; public 7.6 incorrect-hit sample; Gradle not executed on host
information density: high
safety: public OSS, not executed on host
nontriviality: high — FileCollection query at configuration time omitted from CC identity while the fingerprint writer already knew how to record WorkInputs
ecosystem: gradle
mechanism_family: configuration-cache-fingerprint, omitted-file-collection-observation, configurable-file-tree

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "DefaultConfigurableFileTree_failing.java": """# Reduced excerpt of DefaultConfigurableFileTree on failing_ref
# 040aac7031d900c2c548154fcbc75627b01e386c
# subprojects/file-collections/src/main/java/org/gradle/api/internal/file/collections/DefaultConfigurableFileTree.java
# No getFiles / isEmpty / contains / visit override.

public class DefaultConfigurableFileTree extends CompositeFileTree implements ConfigurableFileTree {
    private Object dir;
    private final PatternSet patternSet;
    private final PathToFileResolver resolver;
    private final DefaultTaskDependency buildDependency;
    private final DirectoryFileTreeFactory directoryFileTreeFactory;

    public DefaultConfigurableFileTree(PathToFileResolver resolver, Factory<PatternSet> patternSetFactory, TaskDependencyFactory taskDependencyFactory, DirectoryFileTreeFactory directoryFileTreeFactory) {
        super(taskDependencyFactory);
        this.resolver = resolver;
        this.directoryFileTreeFactory = directoryFileTreeFactory;
        patternSet = patternSetFactory.create();
        buildDependency = taskDependencyFactory.configurableDependency();
    }

    @Override
    protected void visitChildren(Consumer<FileCollectionInternal> visitor) {
        File dir = getDir();
        visitor.accept(new FileTreeAdapter(directoryFileTreeFactory.create(dir, patternSet), taskDependencyFactory, patternSetFactory));
    }
}
""",
            "fileCollectionObserved_writer.kt": """# Reduced excerpt of ConfigurationCacheFingerprintWriter on failing_ref
# 040aac7031d900c2c548154fcbc75627b01e386c
# implements UndeclaredBuildInputListener

override fun fileOpened(file: File, consumer: String?) {
    if (isInputTrackingDisabled() || isExecutingTask()) {
        return
    }
    captureFile(file)
    reportUniqueFileInput(file, consumer)
}

override fun fileCollectionObserved(fileCollection: FileCollection, consumer: String) {
    if (isInputTrackingDisabled()) {
        return
    }
    captureWorkInputs(consumer) { it(fileCollection as FileCollectionInternal) }
}

private inline fun captureWorkInputs(workDisplayName: String, content: ((FileCollectionInternal) -> Unit) -> Unit) {
    val fileSystemInputs = simplify(content)
    sink().write(
        ConfigurationCacheFingerprint.WorkInputs(
            workDisplayName,
            fileSystemInputs,
            host.fingerprintOf(fileSystemInputs)
        )
    )
}
""",
            "cases.txt": """Case A (queried directory tree) — build.gradle
  task report {
      def tree = fileTree("src")
      def result = 'files=' + tree.files.name.sort()
      doLast { println(result) }
  }
  disk run 1/2: src/file1, src/dir/file2
  after run 2: create src/file3
  question: run 3 CC identity with vs without the tree contents

Case B (fixed names) — build.gradle
  task report {
      def files = files("file1", "file2")
      def result = files.files.name
      doLast { println(result) }
  }
  after store+load: rewrite file1 contents to "updated"
  documented on the later integration test: still load, still [file1, file2]

Case C (tree constructed, never queried)
  fileTree("src") assigned, no .files / .empty / .contains / .visit
  after store+load: create src/file3

Kotlin DSL contrast on failing_ref (does notify):
  DefaultPrecompiledScriptPluginsSupport.collectScriptPluginFiles
  fileTree include **/*.gradle.kts, filter isFile,
  Instrumented.fileCollectionObserved(it, "Kotlin DSL"), then .files

Public 7.6 sample (gradle/configuration-cache-build-logic-inputs README):
  queryDirInDsl against file-collections/src/dir
  echo ignored > file-collections/src/dir/file3.txt
  Gradle 7.6: incorrect cache hit, new file ignored
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> None:
    def fn(state):
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == JOB_ID), None)
        if job is None:
            raise SystemExit(f"{JOB_ID} missing")
        if job.get("status") == "CLAIMED" and job.get("worker") == WORKER:
            complete(state, JOB_ID, result="ok", artifact=f"specimens/{spec_id}")
        elif job.get("status") == "DONE" and job.get("artifact") == f"specimens/{spec_id}":
            pass
        else:
            raise SystemExit(f"{JOB_ID} status={job.get('status')} worker={job.get('worker')} artifact={job.get('artifact')}")
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
                priority_reason="gradle CC FileTree file-collection fingerprint omit; not 076 unusedfp / 042 race / 051 nested",
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
        return spec_id

    with_state(fn)


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_for(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(f"enqueued READY_R1_DREAM trial={TRIAL} specimen={spec_id} (dream.sh not launched; hdd-pnpmhash in flight)")
    except Exception:
        # leave a claimed empty dir only if emit wrote nothing useful
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
