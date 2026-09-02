ACCEPT_R1

contrastiveness: high (published extra GAV in local repo vs reactor sibling extra GAV with no install vs missing extra GAV vs extra GAV also on compile classpath; processorpath ArtifactResolutionRequest vs compile classpath project artifacts)
reproducibility: source-backed JIRA+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — extra module is in the reactor modules list but not on the consumer compile classpath; processorpath is a second coordinate list resolved without the reactor workspace
ecosystem: maven / maven-compiler-plugin
mechanism_family: extra-processor-module, annotationProcessorPaths, reactor-vs-local-repo

Packet is the failing world only. Do not assume a root cause.
