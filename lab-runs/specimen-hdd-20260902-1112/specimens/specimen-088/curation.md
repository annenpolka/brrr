ACCEPT_R1

contrastiveness: high (queried fileTree("src").files + add src/file3 vs files("file1","file2") content rewrite that still loads; Kotlin DSL collectScriptPluginFiles already called Instrumented.fileCollectionObserved; constructed-but-never-queried tree)
reproducibility: source-backed PR + pinned merge parent/merge commit; public 7.6 incorrect-hit sample; Gradle not executed on host
information density: high
safety: public OSS, not executed on host
nontriviality: high — FileCollection query at configuration time omitted from CC identity while the fingerprint writer already knew how to record WorkInputs
ecosystem: gradle
mechanism_family: configuration-cache-fingerprint, omitted-file-collection-observation, configurable-file-tree

Packet is the failing world only. Do not assume a root cause.
