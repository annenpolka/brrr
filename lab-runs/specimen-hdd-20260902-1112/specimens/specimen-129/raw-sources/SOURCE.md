repository: com-lihaoyi/mill
issue: https://github.com/com-lihaoyi/mill/issues/6991
pr: https://github.com/com-lihaoyi/mill/pull/6999
failing_ref (squash parent on main): e69f7bb6e18c84793c3950714a4092f4a62bf498
fixed_ref (squash merge): 9a2039b029f26152a9d823ef2fe6abdb073b2dce
merged_at: 2026-04-12T17:21:33Z
pr_author: lihaoyi
merged_by: lihaoyi
changed_files: libs/javalib/worker/src/mill/javalib/zinc/IncrementalAnnotationProcessing.scala, libs/javalib/worker/src/mill/javalib/zinc/IncrementalTrackingJavaCompiler.scala, libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala, libs/javalib/test/src/mill/javalib/IncrementalAnnotationProcessingTests.scala
pr_title: Gradle incremental annotation processing metadata support
scout_note: not specimen-117 sbt leftover extra zinc Analysis last-write vs file identity. Distinct leftover: mill zinc analysis omits AP-generated product identity so leftover Immutable*.class remains after originating source deleted. job-0537 was skipped citing mill#4642 (wrong axis).
