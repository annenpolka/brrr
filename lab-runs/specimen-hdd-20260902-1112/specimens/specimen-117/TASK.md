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
