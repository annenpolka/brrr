# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Mill's persistent `compile` dest can keep the identity of **previous annotation-processor-generated `.class` files** after the originating Java source is deleted. Zinc `CompileAnalysis` maps sources it compiled; generated products written as a javac side-effect are omitted from that identity.

On failing_ref `e69f7bb6e18c84793c3950714a4092f4a62bf498`, `compile` is `Task(persistent = true)` so Mill does not wipe `compile.dest/classes` between runs. `zincIncrementalCompilation` is `allSourceFiles().length > 1`. When incremental is on, ZincWorker feeds PreviousResult from the last analysis:

```
pr = if (incrementalCompilation) {
    val prev = store.get()
    PreviousResult.of(prev.map(_.getAnalysis), prev.map(_.getMiniSetup))
} else {
    PreviousResult.of(Optional.empty[CompileAnalysis], Optional.empty[MiniSetup])
}
```

`compileGeneratedSources` (the `-s` directory) is wiped each compile. Generated `.class` files land in `classes/` instead. Zinc warns:

```
[warn] Could not determine source for class com.rkophs.mill.test.ImmutableTestImmutableBeta
[warn] Could not determine source for class com.rkophs.mill.test.ImmutableTestImmutableBeta$Builder
```

Public report (com-lihaoyi/mill#6991). Two modules: immutables annotation processing vs plain POJOs.

Bug 1 (annotation processor, 3-source module):
1. Clean build with 3 sources → generated classes present.
2. Delete one source that others depend on.
3. `mill __.compile` → non-generated module fails (Zinc removes that source's `.class`); generated module **silently succeeds** because leftover AP `.class` files remain.
4. `rm -rf out/ && mill __.compile` → both modules fail.

On this failing_ref, non-incremental compiles (`allSourceFiles().length <= 1`) already wipe `classesDir`. The leftover that remains is incremental + omitted generated-product identity.

Case A — first compile, 3 sources, AP generates Immutable* classes:
  analysis written
  generated classes present
  not leftover (fresh products)

Case B — delete originating source, leftover Immutable*.class under compile.dest/classes:
  leftover: previous generated class identity
  originating source omitted from current sources
  zinc analysis has no source mapping for those products
  compile succeeds

Case C — `rm -rf out/` then compile:
  fresh dest
  compile fails
  not leftover generated identity

Case D — delete a plain Java source with 3 remaining sources (no AP products):
  Zinc removes that source's `.class`
  not this leftover (analysis had the mapping)

The developer wants to know which identity case B actually left in `compile.dest/classes` for the deleted originating source: leftover Immutable*.class from the previous AP run, current generated identity matching remaining sources, or omitted (no generated class files).

# OBSERVED

Public com-lihaoyi/mill#6991 (closed 2026-04-12). PR 6999 squash `9a2039b029f26152a9d823ef2fe6abdb073b2dce` (parent `e69f7bb6e18c84793c3950714a4092f4a62bf498`). Local mill was not performed on this lab host.

Issue body: stale `.class` files survive incremental compilation when source files are deleted; AP-generated classes are never cleaned because Zinc cannot map them back to a source.

On failing_ref, `IncrementalAnnotationProcessing.scala` does **not** exist. There is no `incremental-annotation-processing.json` snapshot. `compileGeneratedSources` wipe does not cover `classes/` products.

Not this packet: specimen-117 (sbt leftover extra zinc Analysis in `staticCachedStore` last-write cache vs current analysis-file size+mtime after gz switch). Mill leftover is generated `.class` products omitted from analysis, not extra last-write Analysis vs file identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref e69f7bb6e18c84793c3950714a4092f4a62bf498
# libs/javalib/src/mill/javalib/JavaModule.scala compile / zincIncrementalCompilation
# libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala PreviousResult

# public shape:
# leftover compile.dest/classes/.../ImmutableTestImmutableBeta.class
# mill __.compile succeeds after deleting originating source
# rm -rf out/ && mill __.compile fails
```

Source-backed only. Do not execute untrusted checkouts on the host.

com-lihaoyi/mill
  libs/javalib/src/mill/javalib/JavaModule.scala
  libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala
  out/<module>/compile.dest/classes/
  compileGeneratedSources (-s)

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  mill JavaModule compile.dest/classes persistent
  org.immutables:value annotation processor
  leftover Immutable*.class after originating source deleted

Case A (first compile, 3 sources):
  generated classes written
  not leftover

Case B (delete originating source, leftover AP classes):
  leftover: previous generated class identity
  compile succeeds
  zinc analysis omitted generated products

Case C (rm -rf out/ then compile):
  fresh dest
  compile fails
  not leftover generated identity

Case D (plain Java source delete, analysis had mapping):
  Zinc removes that .class
  not this leftover

Not this packet:
  sbt leftover extra zinc Analysis last-write vs file identity (specimen-117)
  mill#4642 out/ absolute-path serialization (job-0537 skip axis)

### zinc_previous_result_failing.scala

// Reduced excerpt on failing_ref
// libs/javalib/src/mill/javalib/JavaModule.scala
// libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala
// e69f7bb6e18c84793c3950714a4092f4a62bf498
// compile dest is persistent. Generated .class identity is omitted from analysis.

  def zincIncrementalCompilation: T[Boolean] = Task { allSourceFiles().length > 1 }

  def compile: T[mill.javalib.api.CompilationResult] = Task(persistent = true) {
    val compileGenSources = compileGeneratedSources()
    os.remove.all(compileGenSources)   // -s dir only
    os.makeDir.all(compileGenSources)
    worker.apply(
      ZincOp.CompileJava(
        incrementalCompilation = zincIncrementalCompilation(),
        workDir = Task.dest
      ),
      ...
    )
  }

      pr = if (incrementalCompilation) {
        val prev = store.get()
        PreviousResult.of(prev.map(_.getAnalysis), prev.map(_.getMiniSetup))
      } else {
        PreviousResult.of(Optional.empty[CompileAnalysis], Optional.empty[MiniSetup])
      }

// IncrementalAnnotationProcessing does not exist on failing_ref.

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
