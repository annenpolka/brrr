CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

sbt 2.x can keep leftover **extra zinc Analysis identity** after the analysis gz file under a cache path has switched. The leftover identity is the last-write Analysis still sitting in `MixedAnalyzingCompiler.staticCachedStore`, even though the current analysis-file identity (size + last-modified) is a different gz.

On failing_ref `c491f035f832a62843d69364b55237dc29c99e7d`, `Defaults.analysisStore` is:

```
private inline def analysisStore(inline analysisFile: TaskKey[File]): AnalysisStore =
  MixedAnalyzingCompiler.staticCachedStore(
    analysisFile = analysisFile.value.toPath,
    useTextAnalysis = false,
  )
```

That two-arg overload hard-codes `cacheLast = true`. Zinc then wraps the file store:

```
val store1 =
  if cacheLast then AnalysisStore.getCachedStore(fileStore)
  else fileStore
staticCache(analysisFile, AnalysisStore.getThreadSafeStore(store1))
```

`getCachedStore` keys only on last write through that store. It does not include file size or timestamp. sbt 2.x remote/local caching can replace the gz bytes under the same path. The extra leftover Analysis identity remains.

Public report (sbt/sbt#9195) scripted fixture `cache/discoveredMainClasses`:

```
scalaVersion := "2.13.18"
object Main { def main(args: Array[String]): Unit = () }

> checkDiscoveredMainClasses
# actual == Seq("example.Main")
$ copy-file src/main/scala/Main.scala tmp/Main.scala
$ delete src
-> checkDiscoveredMainClasses
$ copy-file tmp/Main.scala src/main/scala/Main.scala
> checkDiscoveredMainClasses
# expect success but failure
```

Workaround recorded on the issue: `cleanFull`.

Case A — first compile, analysis gz written through this store:
  last-write Analysis identity matches the file
  `discoveredMainClasses` is `Seq("example.Main")`
  no leftover extra Analysis

Case B — sbt 2.x cache restores a different gz under the same analysis path:
  leftover: extra last-write Analysis identity
  current file identity (size + mtime) is the restored gz
  last-write cache does not see the switch

Case C — delete `src`, then restore `Main.scala` (issue 9195):
  leftover extra Analysis identity from B (or from the prior write)
  `checkDiscoveredMainClasses` fails after restore
  not a missing-source case (sources are back)

Case D — `cleanFull` then compile:
  leftover Analysis cache dropped
  not this leftover (wipe, not last-write vs file identity)

The developer wants to know which identity case B/C actually used for zinc Analysis: leftover extra last-write Analysis (file identity ignored), current gz file identity (size+mtime), or omitted (no Analysis store at all).

# OBSERVED

Public sbt/sbt#9195 (closed 2026-05-11). PR 9207 merge `49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef` (parents `c491f035f832a62843d69364b55237dc29c99e7d` + `e69e23aae14240d2c6b63e2c5ff356ccc154e784`). Local sbt/zinc was not performed on this lab host.

Issue body: `discoveredMainClasses` after delete+restore of `src` expects success and fails. Notes `.triggeredBy(compile)` plus global cache. Workaround `cleanFull`.

PR body: MixedAnalyzingCompiler analysis cache caches using the last write, assuming all writing happens via it. That does not work with sbt 2.x caching where the gz file under the path can switch. Repair keys local analysis caching on file size and timestamp (caffeine), and calls zinc `staticCachedStore(..., cacheLast = false)`.

On failing_ref, `analysisStore` uses the two-arg zinc overload (`cacheLast = true`). Zinc `getCachedStore` is last-write. File size / last-modified are **not** part of that identity.

Not this packet: specimen-088 / specimen-104 (gradle configuration-cache leftover). specimen-075 (rustc incremental). specimen-078 (derived gocache). specimen-111 (tsbuildinfo leftover signature). No sbt specimen in 001-111.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c491f035f832a62843d69364b55237dc29c99e7d
# main/src/main/scala/sbt/Defaults.scala analysisStore
# zinc MixedAnalyzingCompiler.staticCachedStore cacheLast=true

# public shape (sbt 2.x scripted cache/discoveredMainClasses):
# first checkDiscoveredMainClasses ok
# delete src; restore Main.scala
# leftover: extra last-write Analysis identity
# checkDiscoveredMainClasses fails
```

Source-backed only. Do not execute untrusted checkouts on the host.

sbt/sbt
  main/src/main/scala/sbt/Defaults.scala
  main/src/main/scala/sbt/internal/BuildDef.scala
sbt/zinc
  zinc/src/main/scala/sbt/internal/inc/MixedAnalyzingCompiler.scala

RELEVANT MATERIAL

### analysis_store_failing.scala

# Reduced excerpt of Defaults.analysisStore + zinc staticCachedStore on failing_ref
# sbt main/src/main/scala/sbt/Defaults.scala
# c491f035f832a62843d69364b55237dc29c99e7d
# Last-write Analysis identity is the cache. File size/mtime are omitted.

  private inline def analysisStore(inline analysisFile: TaskKey[File]): AnalysisStore =
    MixedAnalyzingCompiler.staticCachedStore(
      analysisFile = analysisFile.value.toPath,
      useTextAnalysis = false,
    )

# zinc MixedAnalyzingCompiler.scala two-arg overload (cacheLast = true):

  def staticCachedStore(analysisFile: Path, useTextAnalysis: Boolean): AnalysisStore =
    staticCachedStore(
      analysisFile = analysisFile,
      useTextAnalysis = useTextAnalysis,
      useConsistent = false,
      cacheLast = true,
      mappers = ReadWriteMappers.getEmptyMappers(),
      reproducible = true,
      parallelism = Runtime.getRuntime.availableProcessors(),
    )

    val store1 =
      if cacheLast then AnalysisStore.getCachedStore(fileStore)
      else fileStore
    staticCache(analysisFile, AnalysisStore.getThreadSafeStore(store1))

### leftover_identity_split.txt

Registry / fixture:
  sbt 2.x analysis gz path
  MixedAnalyzingCompiler.staticCachedStore cacheLast=true
  scripted cache/discoveredMainClasses

Case A (first compile, write through this store):
  last-write Analysis identity matches file
  no leftover extra Analysis

Case B (sbt 2.x cache restores a different gz under same path):
  leftover: extra last-write Analysis identity
  current file identity is size+mtime of restored gz

Case C (delete src then restore Main.scala):
  leftover extra Analysis identity
  checkDiscoveredMainClasses fails after restore

Case D (cleanFull then compile):
  leftover Analysis dropped
  not this leftover

Not this packet:
  gradle configuration-cache leftover (specimen-088 / specimen-104)
  rustc incremental (specimen-075)
  derived gocache (specimen-078)
  tsbuildinfo leftover signature (specimen-111)

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
