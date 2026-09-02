#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets from 129.

Never overwrite specimen-128 (dart leftover package_config vs workspace).
075 not overwritten. Not bazel#29298. 112==110, 119/124 earthly same PR 3810,
113 vs 111 class skipped.

Packed (unique vs 001-128):
1) com-lihaoyi/mill#6991 / PR 6999: leftover zinc AP-generated .class identity
   omitted from CompileAnalysis. Distinct from 117 sbt leftover extra zinc
   Analysis in last-write cache vs analysis-file size+mtime. Coord skipped
   job-0537 citing mill#4642 (out/ path serialization) — wrong leftover axis.
2) Homebrew/brew#23588 / PR 23597: leftover bottle cache identity omits local
   patch files; previous bottle reused after patch change. Coord skipped
   job-0539 citing Homebrew#20936 (formula_auditor revision) — wrong axis.
3) ninja-build/ninja#2666 / PR 2680: leftover deps-log identity loaded even
   when the producing edge is dirty; previous dep graph after sources flip.
   Distinct from 075/086.

SKIP (READY jobs 0555-0560 except 0558 packed):
- job-0555 eslint leftover cache vs config: no unique leftover-identity
  merged pair distinct from 107/114. job-0498 already skipped this class.
- job-0556 turbo leftover cache hash omitting env: no merged leftover pair.
- job-0557 nx leftover runtime cache inputs: nx#31428 adds NX_PROJECT_ROOT
  env to inputs (feature); not leftover previous cache object after change.
- job-0559 hatch leftover env vs pyproject: hatch#486 adds env caching, not
  leftover previous env identity after pyproject change.
- job-0560 coursier leftover artifact vs checksum: no merged leftover pair
  distinct from 074/021.

Already SKIP by scout-coord-1827 (not reclaimed): mix#14189 not_planned,
cabal#6488 open, sccache#2798 open, buck2#976 open, conan/cocoapods/opam
no merged leftover-identity pair this tick.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 129
WORKER = "scout-leftover-129"
PACKED = [
    (
        None,
        WORKER,
        "hdd-apzinc",
        "mill leftover zinc AP-generated class identity omitted from analysis; not 117 last-write Analysis",
    ),
    (
        None,
        WORKER,
        "hdd-brewpatch",
        "homebrew leftover bottle cache omits local patch files; not 001-128",
    ),
    (
        "job-0558",
        WORKER,
        "hdd-ninjadeps",
        "ninja leftover deps log loaded when dirty; previous dep identity after graph change; not 075/086",
    ),
]
SKIP_JOBS = {
    "job-0555": (
        "skip eslint leftover cache vs config identity: no unique leftover-"
        "identity merged pair distinct from 107/114. job-0498 already skipped "
        "this class. not inventing refs"
    ),
    "job-0556": (
        "skip turbo leftover cache hash omitting env: no merged leftover-"
        "identity pair distinct from 119/115. not inventing refs"
    ),
    "job-0557": (
        "skip nx leftover runtime cache inputs: nx#31428 / #20949 merged but "
        "adds NX_PROJECT_ROOT to runtime inputs (feature); not leftover previous "
        "cache object after inputs changed. not inventing refs"
    ),
    "job-0559": (
        "skip hatch leftover env vs pyproject identity: hatch#486 adds build "
        "environment caching, not leftover previous env after pyproject change. "
        "not inventing refs"
    ),
    "job-0560": (
        "skip coursier leftover artifact vs checksum: no merged leftover-"
        "identity pair distinct from 074/021. not inventing refs"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: nuget leftover packages.lock vs assets file identity not 001-128",
        "unique nuget leftover lock",
    ),
    (
        "public OSS: sccache leftover cache vs command identity CPATH not 075/086 if #2798 merges",
        "unique sccache CPATH leftover if pinned",
    ),
    (
        "public OSS: cabal store leftover unit-id vs library identity not 001-128 if #6488 merges",
        "unique cabal store leftover if pinned",
    ),
]


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 180):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_mill(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: com-lihaoyi/mill
failing_ref: e69f7bb6e18c84793c3950714a4092f4a62bf498
fixed_ref: 9a2039b029f26152a9d823ef2fe6abdb073b2dce
source_issue: https://github.com/com-lihaoyi/mill/issues/6991
source_pr: https://github.com/com-lihaoyi/mill/pull/6999
mechanism_tags:
  - leftover-generated-class
  - omitted-annotation-processor-product
  - zinc-analysis-omits-generated
ecosystem: mill-zinc
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

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
""",
        observed="""# OBSERVED

Public com-lihaoyi/mill#6991 (closed 2026-04-12). PR 6999 squash `9a2039b029f26152a9d823ef2fe6abdb073b2dce` (parent `e69f7bb6e18c84793c3950714a4092f4a62bf498`). Local mill was not performed on this lab host.

Issue body: stale `.class` files survive incremental compilation when source files are deleted; AP-generated classes are never cleaned because Zinc cannot map them back to a source.

On failing_ref, `IncrementalAnnotationProcessing.scala` does **not** exist. There is no `incremental-annotation-processing.json` snapshot. `compileGeneratedSources` wipe does not cover `classes/` products.

Not this packet: specimen-117 (sbt leftover extra zinc Analysis in `staticCachedStore` last-write cache vs current analysis-file size+mtime after gz switch). Mill leftover is generated `.class` products omitted from analysis, not extra last-write Analysis vs file identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref e69f7bb6e18c84793c3950714a4092f4a62bf498
# libs/javalib/src/mill/javalib/JavaModule.scala compile / zincIncrementalCompilation
# libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala PreviousResult

# public shape:
# leftover compile.dest/classes/.../ImmutableTestImmutableBeta.class
# mill __.compile succeeds after deleting originating source
# rm -rf out/ && mill __.compile fails
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""com-lihaoyi/mill
  libs/javalib/src/mill/javalib/JavaModule.scala
  libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala
  out/<module>/compile.dest/classes/
  compileGeneratedSources (-s)
""",
        source="""repository: com-lihaoyi/mill
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
""",
        answer_key="""KNOWN FIX (sealed): com-lihaoyi/mill PR 6999 squash 9a2039b029f26152a9d823ef2fe6abdb073b2dce.

failing_ref is squash parent e69f7bb6e18c84793c3950714a4092f4a62bf498.

Zinc analysis omitted AP-generated products; persistent compile.dest kept leftover Immutable*.class after originating source deletion.

PR repair: IncrementalAnnotationProcessing snapshot of generated-product ownership; prepareBeforeCompile deletes staleProducts; persist writes incremental-annotation-processing.json; isolating/aggregating metadata from META-INF/gradle/incremental.annotation.processors.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (first AP compile vs leftover generated class after source delete vs wipe out/ vs plain-Java zinc mapping)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — zinc source-class identity and AP-generated product identity are different objects; leftover class stayed current
ecosystem: mill / zinc / javac-apt
mechanism_family: leftover-generated-class, omitted-product-from-analysis, persistent-compile-dest

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "zinc_previous_result_failing.scala": """// Reduced excerpt on failing_ref
// libs/javalib/src/mill/javalib/JavaModule.scala
// libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala
// e69f7bb6e18c84793c3950714a4092f4a62bf498
// compile dest is persistent. Generated .class identity is omitted from analysis.

  def zincIncrementalCompilation: T[Boolean] = Task { allSourceFiles().length > 1 }

  def compile: T[mill.javalib.api.CompilationResult] = Task(persistent = true) {
    val compileGenSources = compileGeneratedSources()
    os.remove.all(compileGenSources)   // -s dir only
    os.makeDir.all(compileGenSources)
    worker.apply(
      ZincOp.CompileJava(
        incrementalCompilation = zincIncrementalCompilation(),
        workDir = Task.dest
      ),
      ...
    )
  }

      pr = if (incrementalCompilation) {
        val prev = store.get()
        PreviousResult.of(prev.map(_.getAnalysis), prev.map(_.getMiniSetup))
      } else {
        PreviousResult.of(Optional.empty[CompileAnalysis], Optional.empty[MiniSetup])
      }

// IncrementalAnnotationProcessing does not exist on failing_ref.
""",
            "leftover_identity_split.txt": """Registry / fixture:
  mill JavaModule compile.dest/classes persistent
  org.immutables:value annotation processor
  leftover Immutable*.class after originating source deleted

Case A (first compile, 3 sources):
  generated classes written
  not leftover

Case B (delete originating source, leftover AP classes):
  leftover: previous generated class identity
  compile succeeds
  zinc analysis omitted generated products

Case C (rm -rf out/ then compile):
  fresh dest
  compile fails
  not leftover generated identity

Case D (plain Java source delete, analysis had mapping):
  Zinc removes that .class
  not this leftover

Not this packet:
  sbt leftover extra zinc Analysis last-write vs file identity (specimen-117)
  mill#4642 out/ absolute-path serialization (job-0537 skip axis)
""",
        },
    )


def packet_brew(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: Homebrew/brew
failing_ref: 4f6e4df964fa22f12591ca4b27e9b52df34b9494
fixed_ref: b62af44bc2d4173d113d07648eb78a9facb73fcf
source_issue: https://github.com/Homebrew/brew/issues/23588
source_pr: https://github.com/Homebrew/brew/pull/23597
mechanism_tags:
  - leftover-bottle-cache
  - omitted-local-patch
  - formula-path-only-diff
ecosystem: homebrew
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Homebrew test-bot bottle cache can keep the identity of a **previous bottle** after a local patch file has changed. `no_diff?` diffs only the formula path against the bottle's `tap_git_revision`. Patch files listed on the formula are omitted from that identity.

On failing_ref `4f6e4df964fa22f12591ca4b27e9b52df34b9494`, `artifact_cache_valid?` is:

```
sha = local_bottle_hash(formula.name, bottle_dir: artifact_cache)
        &.dig(formula.name, "formula", "tap_git_revision")
return false if sha.blank?
return false unless no_diff?(formula, sha)
```

and `no_diff?` is:

```
relative_formula_path = formula.path.relative_path_from(repository)
!!system(git, "-C", repository, "diff", "--no-ext-diff", "--quiet", git_ref, "--",
         relative_formula_path.to_s)
```

Public report (Homebrew/brew#23588). CI for homebrew-core gcc:

```
==> brew install artifact-cache/gcc--16.2.0.tahoe.bottle.tar.gz
Notice: Bottle for gcc built at 7df12339119 (Merge e5a39e93eb ... into 860ea91cd8 ...)
```

The formula file itself was unmodified. The local patch the formula refers to changed between runs. Leftover bottle from the previous patch identity was installed.

Case A — first bottle, formula and local patch match `tap_git_revision`:
  cache valid
  not leftover after patch change

Case B — local `patches/foo.diff` edited, formula.rb unchanged, leftover bottle in artifact-cache:
  leftover: previous bottle identity
  current patch identity is the new diff
  `no_diff?` is true (formula path only)
  leftover bottle reused

Case C — formula.rb itself edited:
  `no_diff?` is false
  cache invalid
  not this leftover (formula path is the identity)

Case D — delete artifact-cache bottle then fetch:
  fresh bottle
  not leftover cache identity

The developer wants to know which identity case B actually installed: leftover previous bottle (old patch), current bottle rebuilt for the new patch, or omitted (no bottle).
""",
        observed="""# OBSERVED

Public Homebrew/brew#23588 (closed 2026-08-20; PR merged 2026-08-21). PR 23597 merge `b62af44bc2d4173d113d07648eb78a9facb73fcf` (first parent `4f6e4df964fa22f12591ca4b27e9b52df34b9494`). Local brew was not performed on this lab host.

Issue body: test-bot used a bottle from cache even though a local patch file changed without modifying the formula.

On failing_ref, `no_diff?` only passes `formula.path`. `formula.patchlist.grep(LocalPatch)` is **not** part of the cache identity.

Not this packet: Homebrew#20936 formula_auditor revision/compatibility_version (job-0539 skip axis). Distinct leftover: bottle cache identity omits local patch files so leftover previous bottle is reused after patch change.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 4f6e4df964fa22f12591ca4b27e9b52df34b9494
# Library/Homebrew/test_bot/test_formulae.rb no_diff? / artifact_cache_valid?

# public shape:
# leftover artifact-cache/gcc--*.bottle.tar.gz
# formula.rb unchanged; patches/foo.diff changed
# brew install leftover bottle
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""Homebrew/brew
  Library/Homebrew/test_bot/test_formulae.rb
  Library/Homebrew/test/test_bot/test_formulae_spec.rb
  artifact-cache/<formula>--*.bottle.tar.gz
  <tap>/patches/*.diff
""",
        source="""repository: Homebrew/brew
issue: https://github.com/Homebrew/brew/issues/23588
pr: https://github.com/Homebrew/brew/pull/23597
failing_ref (merge first parent on main): 4f6e4df964fa22f12591ca4b27e9b52df34b9494
fixed_ref (merge commit): b62af44bc2d4173d113d07648eb78a9facb73fcf
merged_at: 2026-08-21T11:13:54Z
pr_author: MikeMcQuaid
merged_by: MikeMcQuaid
changed_files: Library/Homebrew/test_bot/test_formulae.rb, Library/Homebrew/test/test_bot/test_formulae_spec.rb
pr_title: Invalidate bottle cache for local patches
scout_note: not Homebrew#20936 formula_auditor (job-0539 skip axis). Distinct leftover: bottle cache identity omits local patch files so leftover previous bottle is reused after patch change. Unique vs 001-128 (no Homebrew/brew leftover bottle).
""",
        answer_key="""KNOWN FIX (sealed): Homebrew/brew PR 23597 merge b62af44bc2d4173d113d07648eb78a9facb73fcf.

failing_ref is merge first parent 4f6e4df964fa22f12591ca4b27e9b52df34b9494.

no_diff? keyed only formula.path; local patch files omitted; leftover bottle reused after patch change.

PR repair: relative_paths includes formula.path plus formula.patchlist.grep(LocalPatch) map file; regression test rejects a bottle when a local patch has changed.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (matching formula+patch vs leftover bottle after patch-only change vs formula.rb edit vs wipe cache)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — formula-file identity and local-patch identity are different objects; leftover bottle stayed current
ecosystem: homebrew / bottles
mechanism_family: leftover-bottle-cache, omitted-local-patch, formula-path-only-diff

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "no_diff_failing.rb": """# Reduced excerpt of no_diff? / artifact_cache_valid? on failing_ref
# Library/Homebrew/test_bot/test_formulae.rb
# 4f6e4df964fa22f12591ca4b27e9b52df34b9494
# Cache identity is formula path vs tap_git_revision. Local patches omitted.

      def no_diff?(formula, git_ref)
        return false unless repository.directory?
        @fetched_refs ||= T.let([], T.nilable(T::Array[String]))
        if @fetched_refs.exclude?(git_ref)
          test git.to_s, "-C", repository.to_s, "fetch", "origin", git_ref, ignore_failures: true
          @fetched_refs << git_ref if steps.fetch(-1).passed?
        end

        relative_formula_path = formula.path.relative_path_from(repository)
        !!system(git.to_s, "-C", repository.to_s, "diff", "--no-ext-diff", "--quiet", git_ref, "--",
                 relative_formula_path.to_s)
      end

      def artifact_cache_valid?(formula, formulae_dependents: false)
        sha = local_bottle_hash(formula.name, bottle_dir: artifact_cache)
          &.dig(formula.name, "formula", "tap_git_revision")
        return false if sha.blank?
        return false unless no_diff?(formula, sha)
        # ...
      end
""",
            "leftover_identity_split.txt": """Registry / fixture:
  artifact-cache leftover bottle
  formula.rb unchanged
  patches/foo.diff old then new
  tap_git_revision of previous bottle

Case A (formula+patch match bottle revision):
  cache valid
  not leftover after patch change

Case B (patch edited, leftover bottle):
  leftover: previous bottle identity
  no_diff? true (formula path only)
  leftover bottle installed

Case C (formula.rb edited):
  no_diff? false
  cache invalid
  not this leftover

Case D (delete artifact-cache bottle):
  fresh bottle
  not leftover cache identity

Not this packet:
  Homebrew#20936 formula_auditor revision (job-0539 skip axis)
""",
        },
    )


def packet_ninja(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: ninja-build/ninja
failing_ref: 77d328f5f679bfef14b1f67f3cd431b729bc786f
fixed_ref: 88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68
source_issue: https://github.com/ninja-build/ninja/issues/2666
source_pr: https://github.com/ninja-build/ninja/pull/2680
mechanism_tags:
  - leftover-deps-log
  - omitted-dirty-from-deps-load
  - previous-depfile-identity
ecosystem: ninja
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Ninja's `.ninja_deps` log can keep the identity of a **previous discovered-deps graph** after the producing edge is dirty (sources / command changed). `RecomputeNodeDirty` loads leftover deps before it knows the edge is dirty. The leftover previous edges stay in the graph.

On failing_ref `77d328f5f679bfef14b1f67f3cd431b729bc786f`:

```
if (!edge->deps_loaded_) {
  edge->deps_loaded_ = true;
  // ...
  if (!dep_loader_.LoadDeps(edge, err)) {
    dirty = edge->deps_missing_ = true;
  }
}
```

`LoadDeps` with `deps=` uses `LoadDepsFromLog`: `deps_log_->GetDeps(output)` is accepted if the output mtime is not newer than the stored deps mtime. Dirty/command identity is omitted from that validity check.

Public report (ninja-build/ninja#2666). C++ modules `a`/`b` dyndep flip:

```
# first build: b imports a   (edge a.pcm -> b.pcm)
# edit: a imports b, b does not import a
$ ninja
ninja: error: dependency cycle: CMakeFiles/hasmodules.dir/a.pcm -> CMakeFiles/hasmodules.dir/b.pcm -> CMakeFiles/hasmodules.dir/a.pcm
```

Leftover: previous deps-log edge (`a.pcm -> scanned_Release` / previous import) is loaded while the producing compile is dirty. Combined with the new import, Ninja reports a cycle.

Case A — first build, deps log written for current imports:
  deps identity matches current sources
  not leftover previous graph

Case B — sources flipped, leftover `.ninja_deps` loaded because edge not yet marked dirty:
  leftover: previous discovered-deps identity
  current command/source identity is the flipped import
  cycle reported

Case C — delete `.ninja_deps` then ninja:
  no leftover deps-log identity
  rebuild without previous edges
  not leftover

Case D — output mtime newer than stored deps mtime:
  LoadDepsFromLog rejects stored deps
  not leftover (mtime check fired)

The developer wants to know which identity case B actually used for the module compile graph: leftover previous deps-log edges, current depfile from the flipped sources, or omitted (no discovered deps).
""",
        observed="""# OBSERVED

Public ninja-build/ninja#2666 (closed 2026-07-19). PR 2680 merge `88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68` (first parent `77d328f5f679bfef14b1f67f3cd431b729bc786f`). Local ninja was not performed on this lab host.

Issue comment (root-cause rewrite): Ninja loads an old deps-log dependency even though the target will be regenerated; leftover obsolete deps cause cycle detection. Ninja should only load a deps file if the target producing it is not dirty.

On failing_ref, `LoadDeps` runs in `RecomputeNodeDirty` before the dirty walk finishes. `LoadDepsFromLog` validity is output mtime vs stored deps mtime. Dirty/command identity is omitted.

Not this packet: specimen-075 rustc incremental fingerprint. specimen-086 cargo rustc extra-filename. Distinct leftover: ninja deps-log identity loaded while the producing edge is dirty.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 77d328f5f679bfef14b1f67f3cd431b729bc786f
# src/graph.cc RecomputeNodeDirty / ImplicitDepLoader::LoadDepsFromLog

# public shape:
# leftover .ninja_deps previous import edges
# ninja: error: dependency cycle: a.pcm -> b.pcm -> a.pcm
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""ninja-build/ninja
  src/graph.cc
  src/graph.h
  src/deps_log.h
  .ninja_deps
""",
        source="""repository: ninja-build/ninja
issue: https://github.com/ninja-build/ninja/issues/2666
pr: https://github.com/ninja-build/ninja/pull/2680
failing_ref (merge first parent on master): 77d328f5f679bfef14b1f67f3cd431b729bc786f
fixed_ref (merge commit): 88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68
merged_at: 2026-07-19T12:17:57Z
pr_author: moritzx22
merged_by: jhasse
changed_files: src/graph.cc, src/graph.h, src/graph_test.cc, src/build_test.cc, src/build_log.cc, src/build_log.h, src/disk_interface_test.cc, src/missing_deps.cc
pr_title: Only load depsfile if not dirty [Fix #2666]
scout_note: not 075/086. Distinct leftover: ninja deps-log identity loaded when producing edge is dirty so leftover previous dep graph remains after sources flip. job-0558.
""",
        answer_key="""KNOWN FIX (sealed): ninja-build/ninja PR 2680 merge 88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68.

failing_ref is merge first parent 77d328f5f679bfef14b1f67f3cd431b729bc786f.

RecomputeNodeDirty loaded leftover deps-log before dirty was known; LoadDepsFromLog omitted dirty/command identity.

PR repair: only load depsfile if the producing edge is not dirty; RecomputeOutputsDirtyCache follow-up after deps load.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (first matching deps vs leftover deps-log after flip vs wipe .ninja_deps vs mtime-stale reject)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — current command identity and leftover deps-log identity are different objects; leftover edges caused cycle
ecosystem: ninja / deps-log
mechanism_family: leftover-deps-log, omitted-dirty, previous-depfile-identity

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "load_deps_failing.cc": """// Reduced excerpt of RecomputeNodeDirty / LoadDepsFromLog on failing_ref
// src/graph.cc
// 77d328f5f679bfef14b1f67f3cd431b729bc786f
// Leftover deps-log identity is loaded before dirty is known.
// Validity is output mtime vs stored deps mtime. Dirty/command omitted.

  if (!edge->deps_loaded_) {
    edge->deps_loaded_ = true;
    if (!dep_loader_.LoadDeps(edge, err)) {
      dirty = edge->deps_missing_ = true;
    }
  }

bool ImplicitDepLoader::LoadDeps(Edge* edge, string* err) {
  string deps_type = edge->GetBinding("deps");
  if (!deps_type.empty())
    return LoadDepsFromLog(edge, err);
  // ...
}

bool ImplicitDepLoader::LoadDepsFromLog(Edge* edge, string* err) {
  Node* output = edge->outputs_[0];
  DepsLog::Deps* deps = deps_log_ ? deps_log_->GetDeps(output) : NULL;
  if (!deps) return false;
  if (output->mtime() > deps->mtime) return false;  // mtime only
  edge->inputs_.insert(..., nodes, nodes + node_count);
  return true;
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  .ninja_deps leftover previous import edges
  a.pcm / b.pcm C++ modules
  first build: b imports a
  edit: a imports b

Case A (first build):
  deps log matches current imports
  not leftover

Case B (sources flipped, leftover deps log):
  leftover: previous discovered-deps identity
  LoadDeps before dirty
  cycle a.pcm -> b.pcm -> a.pcm

Case C (delete .ninja_deps then ninja):
  no leftover deps-log identity
  not leftover

Case D (output mtime newer than stored deps):
  LoadDepsFromLog rejects
  not leftover mtime-valid log

Not this packet:
  rustc incremental fingerprint (specimen-075)
  cargo rustc extra-filename (specimen-086)
""",
        },
    )


def _claim_job(state, job_id: str, worker: str) -> None:
    job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
    if job is None:
        return
    if job.get("status") == "READY":
        job["status"] = "CLAIMED"
        job["claimed_at"] = now_jst()
        job["worker"] = worker
        workers = state.setdefault("workers", [])
        rec = next((w for w in workers if w.get("id") == worker), None)
        if rec is None:
            workers.append({"id": worker, "status": "active", "job": job_id})
        else:
            rec["status"] = "active"
            rec["job"] = job_id
    elif job.get("status") == "CLAIMED":
        old = job.get("worker")
        if old not in {None, worker} and not str(old).startswith("scout-coord-"):
            raise SystemExit(f"{job_id} status=CLAIMED worker={old}")
        job["worker"] = worker
        job["claimed_at"] = job.get("claimed_at") or now_jst()
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')} worker={job.get('worker')}")


def _register(state, spec_id: str, trial: str, reason: str) -> None:
    ids = {s.get("id") for s in state.get("specimens") or []}
    if spec_id not in ids:
        state.setdefault("specimens", []).append({"id": spec_id})
    already = any(
        j.get("queue") == "READY_R1_DREAM"
        and j.get("specimen") == spec_id
        and j.get("status") in {"READY", "CLAIMED"}
        for j in state.get("ready_jobs") or []
    )
    if not already:
        enqueue(
            state,
            "READY_R1_DREAM",
            input_ref=f"seeds/{spec_id}.md trial={trial}",
            expected_output="0001-dreamer.md",
            kill_condition="15m",
            estimated_cost="r1",
            priority_reason=reason,
            specimen=spec_id,
            lineage=trial,
            phase="cambrian",
            extra={"trial": trial},
        )


def _complete_and_enqueue(ids: list[str]) -> str:
    note = {"reason": ""}
    packets = list(zip(PACKED, ids))

    def fn(state):
        for (job_id, worker, trial, reason), spec_id in packets:
            if job_id:
                _claim_job(state, job_id, worker)
                job = next((j for j in state["ready_jobs"] if j["id"] == job_id), None)
                if job and job.get("status") == "CLAIMED" and job.get("worker") == worker:
                    complete(state, job_id, artifact=f"specimens/{spec_id} {trial}")
            _register(state, spec_id, trial, reason)
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") == "READY":
                job["status"] = "CLAIMED"
                job["worker"] = WORKER
                job["claimed_at"] = now_jst()
                complete(state, jid, result="skip", artifact=artifact)
            elif job.get("status") == "CLAIMED":
                old = job.get("worker")
                if old in {None, WORKER} or str(old).startswith("scout-coord-"):
                    complete(state, jid, result="skip", artifact=artifact)
        existing_inputs = {
            j.get("input")
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_SPECIMEN_SCOUT"
        }
        for input_ref, reason in NEXT_SCOUTS:
            if input_ref in existing_inputs:
                continue
            enqueue(
                state,
                "READY_SPECIMEN_SCOUT",
                input_ref=input_ref,
                expected_output="specimens/specimen-NNN leftover-identity packet",
                kill_condition="25m no unique leftover-identity pair; skip bazel#29298; never overwrite 075",
                estimated_cost="low",
                priority_reason=reason,
            )
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if claimed_r1:
            note["reason"] = (
                "dream.sh not launched; READY_R1_DREAM already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        else:
            note["reason"] = (
                "dream.sh not launched from scout; READY_R1_DREAM enqueued trials="
                + ",".join(t for _, _, t, _ in PACKED)
            )
        return ids

    with_state(fn)
    return note["reason"]


def main() -> None:
    ids = [_claim_id() for _ in PACKED]
    dests = [SPECIMENS / i for i in ids]
    builders = [packet_mill, packet_brew, packet_ninja]
    try:
        for spec_id, builder in zip(ids, builders):
            emit(builder(spec_id))
            write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(ids)
        for spec_id, packed in zip(ids, PACKED):
            print(f"{spec_id} {packed[2]} {packed[0]}")
        print(launch_note)
        print("ids=" + ",".join(ids))
    except Exception:
        for dest in dests:
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
