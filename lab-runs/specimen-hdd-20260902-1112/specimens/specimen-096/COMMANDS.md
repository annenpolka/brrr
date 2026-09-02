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
