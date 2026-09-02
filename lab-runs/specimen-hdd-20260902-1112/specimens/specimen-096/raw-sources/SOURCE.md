repository: apache/maven-compiler-plugin
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
