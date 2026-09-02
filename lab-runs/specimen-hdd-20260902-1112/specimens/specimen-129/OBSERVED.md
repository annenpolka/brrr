# OBSERVED

Public com-lihaoyi/mill#6991 (closed 2026-04-12). PR 6999 squash `9a2039b029f26152a9d823ef2fe6abdb073b2dce` (parent `e69f7bb6e18c84793c3950714a4092f4a62bf498`). Local mill was not performed on this lab host.

Issue body: stale `.class` files survive incremental compilation when source files are deleted; AP-generated classes are never cleaned because Zinc cannot map them back to a source.

On failing_ref, `IncrementalAnnotationProcessing.scala` does **not** exist. There is no `incremental-annotation-processing.json` snapshot. `compileGeneratedSources` wipe does not cover `classes/` products.

Not this packet: specimen-117 (sbt leftover extra zinc Analysis in `staticCachedStore` last-write cache vs current analysis-file size+mtime after gz switch). Mill leftover is generated `.class` products omitted from analysis, not extra last-write Analysis vs file identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
