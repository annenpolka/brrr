# TASK

Mill's persistent `compile` dest can keep the identity of **previous annotation-processor-generated `.class` files** after the originating Java source is deleted. Zinc `CompileAnalysis` maps sources it compiled; generated products written as a javac side-effect are omitted from that identity.

On failing_ref `e69f7bb6e18c84793c3950714a4092f4a62bf498`, `compile` is `Task(persistent = true)` so Mill does not wipe `compile.dest/classes` between runs. `zincIncrementalCompilation` is `allSourceFiles().length > 1`. When incremental is on, ZincWorker feeds PreviousResult from the last analysis:

```
pr = if (incrementalCompilation) {
    val prev = store.get()
    PreviousResult.of(prev.map(_.getAnalysis), prev.map(_.getMiniSetup))
} else {
    PreviousResult.of(Optional.empty[CompileAnalysis], Optional.empty[MiniSetup])
}
```

`compileGeneratedSources` (the `-s` directory) is wiped each compile. Generated `.class` files land in `classes/` instead. Zinc warns:

```
[warn] Could not determine source for class com.rkophs.mill.test.ImmutableTestImmutableBeta
[warn] Could not determine source for class com.rkophs.mill.test.ImmutableTestImmutableBeta$Builder
```

Public report (com-lihaoyi/mill#6991). Two modules: immutables annotation processing vs plain POJOs.

Bug 1 (annotation processor, 3-source module):
1. Clean build with 3 sources → generated classes present.
2. Delete one source that others depend on.
3. `mill __.compile` → non-generated module fails (Zinc removes that source's `.class`); generated module **silently succeeds** because leftover AP `.class` files remain.
4. `rm -rf out/ && mill __.compile` → both modules fail.

On this failing_ref, non-incremental compiles (`allSourceFiles().length <= 1`) already wipe `classesDir`. The leftover that remains is incremental + omitted generated-product identity.

Case A — first compile, 3 sources, AP generates Immutable* classes:
  analysis written
  generated classes present
  not leftover (fresh products)

Case B — delete originating source, leftover Immutable*.class under compile.dest/classes:
  leftover: previous generated class identity
  originating source omitted from current sources
  zinc analysis has no source mapping for those products
  compile succeeds

Case C — `rm -rf out/` then compile:
  fresh dest
  compile fails
  not leftover generated identity

Case D — delete a plain Java source with 3 remaining sources (no AP products):
  Zinc removes that source's `.class`
  not this leftover (analysis had the mapping)

The developer wants to know which identity case B actually left in `compile.dest/classes` for the deleted originating source: leftover Immutable*.class from the previous AP run, current generated identity matching remaining sources, or omitted (no generated class files).
