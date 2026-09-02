KNOWN FIX (sealed): com-lihaoyi/mill PR 6999 squash 9a2039b029f26152a9d823ef2fe6abdb073b2dce.

failing_ref is squash parent e69f7bb6e18c84793c3950714a4092f4a62bf498.

Zinc analysis omitted AP-generated products; persistent compile.dest kept leftover Immutable*.class after originating source deletion.

PR repair: IncrementalAnnotationProcessing snapshot of generated-product ownership; prepareBeforeCompile deletes staleProducts; persist writes incremental-annotation-processing.json; isolating/aggregating metadata from META-INF/gradle/incremental.annotation.processors.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
