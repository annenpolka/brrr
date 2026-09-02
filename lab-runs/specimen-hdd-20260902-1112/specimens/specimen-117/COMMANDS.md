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
