repository: objectionary/eo
issue: https://github.com/objectionary/eo/issues/7628
pr: https://github.com/objectionary/eo/pull/7675
failing_ref (first parent of merge on master): 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
fixed_ref (fold tracking.steps into version()): 34df04c9a5eb26c6718c9512d930c4653627d70f
merged_at: 2026-08-26T05:36:55Z
pr_author: morphqdd
merged_by: yegor256
changed_files: eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java, eo-maven-plugin/src/test/java/org/eolang/maven/TranspilationTest.java
pr_title: #7628: fold trackSteps into the transpile cache key
scout_note: not 117 zinc last-write / not 075 rustc fingerprint / not 148 buildah mount-stage. leftover transpile result after trackSteps because steps() omitted from version(). unique vs 001-150.
