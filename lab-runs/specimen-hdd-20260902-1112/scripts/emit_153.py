#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets 153-155.

Packed (unique vs 001-152; 075 not overwritten; not bazel#29298):
1) job-0654 hexpm/hex#821 / PR 843:
   leftover cached tarball after registry checksum changed because
   Hex.SCM.fetch only matched exact outer_checksum or error; mismatch
   was leftover previous package-version.tar (CaseClauseError).
2) job-0655 elixir-lang/elixir#11080:
   leftover mix compile after same-length source rewrite because the
   source record had size not digest; future-mtime reset defeated the
   mtime check.
3) job-0661 llvm/llvm-project#187653:
   leftover clangd C++20 module BMI after header rewrite because
   ASTReader skipped input-file content validation (flag on HSOpts only).

SKIP:
- job-0656 kustomize leftover inventory: no merged leftover-HIT omitted-key pair.
- job-0657 flux leftover artifact vs digest: #2075 is TOCTOU fetch-by-tag after
  digest observe, not leftover previous cache. not 144.
- job-0659 cargo leftover incremental vs renamed helper: #16262 is extra
  cargo-check loop (false miss), not leftover-HIT after rename. not 075/086.
- job-0660 gopls leftover analysis vs moved file: no merged leftover-HIT pair.
"""
from __future__ import annotations

import os
import subprocess

from compile_seed import write_seed
from emit_specimen import emit
from paths import HDD_ROOT, RUN_DIR, SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 153
WORKER = "scout-coord-2148"
SKIP_JOBS = {
    "job-0656": (
        "skip kustomize leftover inventory vs resource identity: no merged "
        "leftover-HIT omitted-key pair this tick. not inventing refs; not 052"
    ),
    "job-0657": (
        "skip flux leftover artifact vs digest identity: source-controller#2075 "
        "is TOCTOU fetch-by-tag after digest observe, not leftover previous "
        "cache. not inventing refs; not 144"
    ),
    "job-0659": (
        "skip cargo leftover incremental vs renamed helper: cargo#16262 is extra "
        "cargo-check loop after build-script mtime, not leftover-HIT after "
        "rename. not inventing refs; not 075/086"
    ),
    "job-0660": (
        "skip gopls leftover analysis vs moved file: no merged leftover-HIT "
        "omitted-path pair this tick. not inventing refs; not 075"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: rebar leftover compile vs source identity not 054/155",
        "unique rebar leftover if pinned",
    ),
    (
        "public OSS: bun leftover compile cache vs source identity not 082",
        "unique bun leftover if pinned",
    ),
    (
        "public OSS: esbuild leftover metafile vs input identity not 090",
        "unique esbuild leftover if pinned",
    ),
    (
        "public OSS: sccache leftover CPATH identity if #2798 merges",
        "unique sccache leftover if pinned",
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


def packet_hex(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: hexpm/hex
failing_ref: 6639c0ad8921fdaf0468d86cc51525c8237e357a
fixed_ref: 90aa44fa8a1e59f2ae65f490edb984e4d6c853d1
source_issue: https://github.com/hexpm/hex/issues/821
source_pr: https://github.com/hexpm/hex/pull/843
mechanism_tags:
  - leftover-tarball-cache
  - omitted-checksum-mismatch-refetch
  - package-version-path-identity
ecosystem: hex
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Hex `Hex.SCM.fetch` can keep the identity of a **previous cached tarball** after the registry checksum changed (`mix hex.publish --replace`) and `mix deps.get` should have fetched a different package. The cache path is `~/.hex/packages/<repo>/<package>-<version>.tar`. Fetch only matches exact `outer_checksum` or `{:error, _}`. A cached tarball whose checksum differs from the registry is leftover previous package-version identity (CaseClauseError; workaround `rm` the tarball).

On failing_ref `6639c0ad8921fdaf0468d86cc51525c8237e357a`:

```
outer_checksum = Registry.outer_checksum(repo, package, version)
path = cache_path(repo, package, version)

case Hex.Tar.outer_checksum(path) do
  {:ok, ^outer_checksum} ->
    {:ok, :cached}

  {:error, _reason} ->
    case Hex.Repo.get_tarball(repo, package, version) do
      {:ok, {200, body, _headers}} ->
        File.mkdir_p!(Path.dirname(path))
        File.write!(path, body)
        {:ok, :new}
      ...
    end
end
```

`{:ok, other_outer_checksum}` is not a clause. Cache identity is package+version path, not registry checksum.

Public report (hexpm/hex#821). Publish; deps.get caches tarball; republish `--replace` so checksum changes; second deps.get CaseClauseError on leftover cached bytes. `rm ~/.hex/packages/<repo>/<package>-<version>.tar` yields a fresh fetch.

In-tree after the repair (not on failing_ref): mismatch warns and `do_fetch`s.

Case A — second deps.get, same registry checksum:
  cache identity is current
  not leftover-after-republish

Case B — registry checksum changed, leftover cached tarball:
  leftover: previous package-version.tar bytes
  checksum mismatch omitted from fetch path
  CaseClauseError / leftover package

Case C — cache file missing / rm tarball:
  fresh fetch identity
  not leftover previous tarball

Case D — mismatch refetch (post-repair shape, not on failing_ref):
  new tarball after checksum change
  not leftover previous package

The developer wants to know which identity case B actually used for the package after the checksum change: leftover previous-cache tarball (mismatch omitted), current registry tarball, or omitted (no cache).
""",
        observed="""# OBSERVED

Public hexpm/hex#821 (closed 2021-01-05). PR 843 squash `90aa44fa8a1e59f2ae65f490edb984e4d6c853d1` (parent `6639c0ad8921fdaf0468d86cc51525c8237e357a`). Local hex was not performed on this lab host.

Issue body: mix hex.update / deps.get CaseClauseError `no case clause matching: {:ok, <<...>>}` at Hex.SCM.fetch after a republished package. Workaround: delete the cached tarball.

On failing_ref, fetch pins `{:ok, ^outer_checksum}` as cached and `{:error, _}` as network fetch. A leftover tarball with a different checksum has no clause.

Not this packet: specimen-074 rubygems frozen lockfile platform identity. specimen-021 poetry leftover.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 6639c0ad8921fdaf0468d86cc51525c8237e357a
# lib/hex/scm.ex fetch / cache_path / Hex.Tar.outer_checksum

# public shape:
# leftover ~/.hex/packages/.../pkg-ver.tar after registry checksum change
# fetch matches exact checksum or error only
# rm tarball yields a fresh fetch
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""hexpm/hex
  lib/hex/scm.ex
""",
        source="""repository: hexpm/hex
issue: https://github.com/hexpm/hex/issues/821
pr: https://github.com/hexpm/hex/pull/843
failing_ref (parent of squash): 6639c0ad8921fdaf0468d86cc51525c8237e357a
fixed_ref (mismatch refetch): 90aa44fa8a1e59f2ae65f490edb984e4d6c853d1
merged_at: 2021-01-05T12:49:39Z
pr_author: wojtekmach
pr_title: Re-fetch package if registry checksum changed
scout_note: not 074 rubygems platform. leftover cached tarball after republish checksum change. unique vs 001-152.
""",
        answer_key="""KNOWN FIX (sealed): hexpm/hex PR 843 squash 90aa44fa8a1e59f2ae65f490edb984e4d6c853d1.

failing_ref is parent 6639c0ad8921fdaf0468d86cc51525c8237e357a.

Hex.SCM.fetch treated {:ok, ^outer_checksum} as cached and {:error, _} as fetch. A leftover tarball with a different checksum had no clause (CaseClauseError). Cache path is package-version, not checksum.

PR repair: {:ok, other_outer_checksum} warns and do_fetch.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (same checksum vs leftover tarball after republish vs rm cache vs mismatch refetch)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — package-version path and registry checksum are different identities; leftover tarball stayed current
ecosystem: hex / tarball cache
mechanism_family: leftover-tarball-cache, omitted-checksum-mismatch-refetch, package-version-path-identity

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "scm_fetch_failing.ex": """# Reduced excerpt of Hex.SCM.fetch cache on failing_ref
# lib/hex/scm.ex
# 6639c0ad8921fdaf0468d86cc51525c8237e357a
# cache path is package-version.tar. mismatch checksum has no clause.

outer_checksum = Registry.outer_checksum(repo, package, version)
path = cache_path(repo, package, version)

case Hex.Tar.outer_checksum(path) do
  {:ok, ^outer_checksum} ->
    {:ok, :cached}

  {:error, _reason} ->
    # network fetch into path
    {:ok, :new}
end
# leftover {:ok, other_checksum} has no clause
""",
            "leftover_identity_split.txt": """Registry / fixture:
  ~/.hex/packages/<repo>/<package>-<version>.tar
  leftover tarball after registry checksum change

Case A (second deps.get, same checksum):
  current cache identity
  not leftover-after-republish

Case B (checksum changed, leftover cached tarball):
  leftover: previous package-version.tar
  mismatch omitted from fetch path
  CaseClauseError

Case C (rm tarball / cache missing):
  fresh fetch identity
  not leftover previous tarball

Case D (mismatch refetch):
  new tarball after checksum change
  not leftover previous package

Not this packet:
  rubygems frozen lockfile platform identity (specimen-074)
""",
        },
    )


def packet_mix(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: elixir-lang/elixir
failing_ref: a677d3c9efb32fe435d8fd102eb8f90272e14da1
fixed_ref: 350a909eb195ab1c0bc5ad29b7573c36ebd98377
source_issue: https://github.com/elixir-lang/elixir/pull/11080
source_pr: https://github.com/elixir-lang/elixir/pull/11080
mechanism_tags:
  - leftover-compile
  - omitted-source-digest
  - same-length-rewrite
ecosystem: mix
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Mix `Mix.Compilers.Elixir` can keep the identity of a **previous BEAM compile** after a same-length source rewrite and the modules should have been different. The source record stores `size` not a content digest. Stale detection is `size != last_size` or `Mix.Utils.stale?([last_mtime | times], [modified])`. A same-length rewrite whose mtime is reset (future-mtime warning) keeps leftover previous modules.

On failing_ref `a677d3c9efb32fe435d8fd102eb8f90272e14da1`:

```
defrecord :source,
  source: nil,
  size: 0,
  compile_references: [],
  ...

changed =
  for source(source: source, external: external, size: size, modules: modules) <-
        all_sources,
      {last_mtime, last_size} = Map.fetch!(sources_stats, source),
      times = Enum.map(external, &(sources_stats |> Map.fetch!(&1) |> elem(0))),
      size != last_size or Mix.Utils.stale?([last_mtime | times], [modified]) or
        Enum.any?(modules, &Map.has_key?(modules_to_recompile, &1)),
      do: source
```

Source identity is size+mtime, not bytes. Future mtimes are reset to now; then last_mtime is not stale vs the compile timestamp and size still matches.

Public report (elixir-lang/elixir#11080). Same-length rewrite (`A` → `Z`); leftover previous compile. In-tree after the repair: source record has `digest`; same-length content change recompiles; identical files with bumped mtime do not.

Case A — second compile, same bytes, same size:
  cache identity is current
  not leftover-after-rewrite

Case B — same-length rewrite, leftover BEAM:
  leftover: previous modules
  digest omitted; size matches
  future-mtime reset defeats mtime check

Case C — mix clean / forced compile:
  fresh module identity
  not leftover previous BEAM

Case D — digest on the source record (post-repair shape, not on failing_ref):
  new compile after same-length rewrite
  not leftover previous modules

The developer wants to know which identity case B actually used for the compile after the rewrite: leftover previous-BEAM (digest omitted), current source bytes, or omitted (no compile cache).
""",
        observed="""# OBSERVED

Public elixir-lang/elixir#11080 (merged 2021-06-28). Squash `350a909eb195ab1c0bc5ad29b7573c36ebd98377` (parent `a677d3c9efb32fe435d8fd102eb8f90272e14da1`). Local elixir/mix was not performed on this lab host.

PR body: hashing content is the right check; tests were added for same-length content change vs identical files with bumped mtime.

On failing_ref, the source record has size not digest. Stale detection is size inequality or Mix.Utils.stale? on mtimes. Same-length rewrite can keep leftover previous modules.

Not this packet: specimen-054 cpython generated-header drift. specimen-086 cargo rustc fingerprint clamped mtime. specimen-147 CDK truncated mtime fingerprint.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref a677d3c9efb32fe435d8fd102eb8f90272e14da1
# lib/mix/lib/mix/compilers/elixir.ex source record / changed

# public shape:
# leftover BEAM after same-length source rewrite
# source record has size not digest
# mix clean / digest in record yields the new modules
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""elixir-lang/elixir
  lib/mix/lib/mix/compilers/elixir.ex
""",
        source="""repository: elixir-lang/elixir
issue: https://github.com/elixir-lang/elixir/pull/11080
pr: https://github.com/elixir-lang/elixir/pull/11080
failing_ref (parent of squash): a677d3c9efb32fe435d8fd102eb8f90272e14da1
fixed_ref (source digest): 350a909eb195ab1c0bc5ad29b7573c36ebd98377
merged_at: 2021-06-28T07:04:23Z
pr_title: Rely on modification time and hash to determine modified sources
scout_note: not 054 cpython header / not 086 cargo fingerprint / not 147 CDK mtime. leftover mix compile after same-length rewrite. unique vs 001-152.
""",
        answer_key="""KNOWN FIX (sealed): elixir-lang/elixir PR 11080 squash 350a909eb195ab1c0bc5ad29b7573c36ebd98377.

failing_ref is parent a677d3c9efb32fe435d8fd102eb8f90272e14da1.

Mix.Compilers.Elixir source record stored size not digest. Same-length rewrite could keep leftover previous BEAM when mtime check was defeated.

PR repair: digest on the source record; same-length content change recompiles.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged source vs leftover BEAM after same-length rewrite vs mix clean vs digest in record)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — size/mtime and source bytes are different identities; leftover modules stayed current
ecosystem: mix / elixir compile
mechanism_family: leftover-compile, omitted-source-digest, same-length-rewrite

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "elixir_compile_failing.ex": """# Reduced excerpt of Mix.Compilers.Elixir stale check on failing_ref
# lib/mix/lib/mix/compilers/elixir.ex
# a677d3c9efb32fe435d8fd102eb8f90272e14da1
# source record has size not digest.

defrecord :source, source: nil, size: 0, modules: []

changed =
  for source(source: source, size: size, modules: modules) <- all_sources,
      {last_mtime, last_size} = Map.fetch!(sources_stats, source),
      size != last_size or Mix.Utils.stale?([last_mtime | times], [modified]) or
        Enum.any?(modules, &Map.has_key?(modules_to_recompile, &1)),
      do: source
# leftover previous BEAM after same-length rewrite
""",
            "leftover_identity_split.txt": """Registry / fixture:
  Mix.Compilers.Elixir source record
  leftover BEAM after same-length rewrite

Case A (second compile, same bytes):
  current cache identity
  not leftover-after-rewrite

Case B (same-length rewrite, leftover BEAM):
  leftover: previous modules
  digest omitted; size matches
  future-mtime reset defeats mtime check

Case C (mix clean):
  fresh module identity
  not leftover previous BEAM

Case D (digest on source record):
  new compile after same-length rewrite
  not leftover previous modules

Not this packet:
  cpython generated-header drift (specimen-054)
  cargo rustc fingerprint clamped mtime (specimen-086)
""",
        },
    )


def packet_clangd(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: llvm/llvm-project
failing_ref: dc4df5da886e09d36577b3302952bc91b5e7e154
fixed_ref: 5ef593b75010301528f665ddbe7d2999165b9238
source_issue: https://github.com/llvm/llvm-project/pull/187653
source_pr: https://github.com/llvm/llvm-project/pull/187653
mechanism_tags:
  - leftover-module-bmi
  - omitted-ast-input-content-validation
  - header-rewrite-reuse
ecosystem: clangd
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

clangd `IsModuleFileUpToDate` can keep the identity of a **previous C++20 module BMI** after a header included by the module unit was rewritten and the BMI should have been different. `HeaderSearchOptions.ValidateASTInputFilesContent` is set true, but `ASTReader` is constructed without `ValidateASTInputFilesContent=true`. StandardCXXModule input files skip content validation. `canReuse` stays true; leftover previous `getValue()` / header bytes stay current.

On failing_ref `dc4df5da886e09d36577b3302952bc91b5e7e154`:

```
HSOpts.ForceCheckCXX20ModulesInputFiles = true;
HSOpts.ValidateASTInputFilesContent = true;
...
ASTReader Reader(PP, *ModCache, /*ASTContext=*/nullptr,
                 PCHOperations.getRawReader(), CodeGenOpts, {});
if (Reader.ReadAST(...) != ASTReader::Success)
  return false;
bool UpToDate = true;
Reader.getModuleManager().visit([&](serialization::ModuleFile &MF) -> bool {
  Reader.visitInputFiles(MF, /*IncludeSystem=*/false, /*Complain=*/false,
      [&](const serialization::InputFile &IF, bool isSystem) {
        if (!IF.getFile() || IF.isOutOfDate())
          UpToDate = false;
      });
  return !UpToDate;
});
return UpToDate;
```

`ASTReader` default skips content validation for StandardCXXModule files unless its own `ValidateASTInputFilesContent` argument is true. HSOpts is not that argument.

Public report (llvm/llvm-project#187653). Module includes `header1.h` (`return 42`); `canReuse` true; rewrite header; leftover previous BMI still reused. In-tree after the repair: ASTReader gets `ValidateASTInputFilesContent=true`; header rewrite is OutOfDate.

Case A — second parse, same header bytes:
  cache identity is current
  not leftover-after-rewrite

Case B — header rewritten, leftover BMI:
  leftover: previous module / previous header bytes
  ASTReader content validation omitted
  canReuse true

Case C — rebuild modules / no prior BMI:
  fresh module identity
  not leftover previous BMI

Case D — ValidateASTInputFilesContent on ASTReader (post-repair shape, not on failing_ref):
  new BMI after header rewrite
  not leftover previous module

The developer wants to know which identity case B actually used for the module after the header rewrite: leftover previous-BMI (content validation omitted), current header bytes, or omitted (no module cache).
""",
        observed="""# OBSERVED

Public llvm/llvm-project#187653 (merged 2026-03-23). Squash `5ef593b75010301528f665ddbe7d2999165b9238` (parent `dc4df5da886e09d36577b3302952bc91b5e7e154`). Local clangd was not performed on this lab host.

PR body: IsModuleFileUpToDate did not properly validate input files for C++20 modules. ASTReader skips StandardCXXModule input validation unless ForceCheckCXX20ModulesInputFiles and ValidateASTInputFilesContent are both set on the reader. Test: header change in a module unit must be detected.

On failing_ref, HSOpts sets the flags but ASTReader is constructed with defaults `{}`. visitInputFiles mtime/out-of-date does not content-hash the header.

Not this packet: specimen-013 bindname last-wins. specimen-075 rustc incremental. specimen-147 CDK truncated mtime.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref dc4df5da886e09d36577b3302952bc91b5e7e154
# clang-tools-extra/clangd/ModulesBuilder.cpp IsModuleFileUpToDate

# public shape:
# leftover C++20 module BMI after header rewrite
# ASTReader constructed without ValidateASTInputFilesContent
# rebuild / reader flag yields a new BMI
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""llvm/llvm-project
  clang-tools-extra/clangd/ModulesBuilder.cpp
""",
        source="""repository: llvm/llvm-project
issue: https://github.com/llvm/llvm-project/pull/187653
pr: https://github.com/llvm/llvm-project/pull/187653
failing_ref (parent of squash): dc4df5da886e09d36577b3302952bc91b5e7e154
fixed_ref (ASTReader ValidateASTInputFilesContent): 5ef593b75010301528f665ddbe7d2999165b9238
merged_at: 2026-03-23T03:43:57Z
pr_title: "[clangd] [C++ Modules] Enable content validation for module input files"
scout_note: not bindname / not 075 / not 147. leftover clangd module BMI after header rewrite because ASTReader omitted content validation. unique vs 001-152.
""",
        answer_key="""KNOWN FIX (sealed): llvm/llvm-project PR 187653 squash 5ef593b75010301528f665ddbe7d2999165b9238.

failing_ref is parent dc4df5da886e09d36577b3302952bc91b5e7e154.

IsModuleFileUpToDate set ValidateASTInputFilesContent on HeaderSearchOptions but constructed ASTReader with defaults, so StandardCXXModule input files skipped content validation. Leftover previous BMI after header rewrite.

PR repair: pass ValidateASTInputFilesContent=true into ASTReader; ReadAST ARR_OutOfDate.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged header vs leftover BMI after rewrite vs rebuild vs ASTReader content validation)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — BMI path/mtime and header bytes are different identities; leftover module stayed current
ecosystem: clangd / C++20 modules
mechanism_family: leftover-module-bmi, omitted-ast-input-content-validation, header-rewrite-reuse

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "module_uptodate_failing.cpp": """// Reduced excerpt of IsModuleFileUpToDate on failing_ref
// clang-tools-extra/clangd/ModulesBuilder.cpp
// dc4df5da886e09d36577b3302952bc91b5e7e154
// HSOpts sets ValidateASTInputFilesContent; ASTReader is constructed without it.

HSOpts.ForceCheckCXX20ModulesInputFiles = true;
HSOpts.ValidateASTInputFilesContent = true;
ASTReader Reader(PP, *ModCache, /*ASTContext=*/nullptr,
                 PCHOperations.getRawReader(), CodeGenOpts, {});
// leftover previous BMI after header rewrite
""",
            "leftover_identity_split.txt": """Registry / fixture:
  clangd C++20 prerequisite module BMI
  leftover BMI after header rewrite

Case A (second parse, same header bytes):
  current cache identity
  not leftover-after-rewrite

Case B (header rewritten, leftover BMI):
  leftover: previous module / previous header bytes
  ASTReader content validation omitted
  canReuse true

Case C (rebuild modules / no prior BMI):
  fresh module identity
  not leftover previous BMI

Case D (ValidateASTInputFilesContent on ASTReader):
  new BMI after header rewrite
  not leftover previous module

Not this packet:
  bindname last-wins (specimen-013)
  rustc incremental fingerprint (specimen-075)
""",
        },
    )


PACKETS = [
    ("job-0654", "hdd-hexcksum", packet_hex,
     "hex leftover tarball vs registry checksum mismatch omitted refetch; not 074"),
    ("job-0655", "hdd-mixdigest", packet_mix,
     "mix leftover compile vs omitted source digest same-length rewrite; not 054/086"),
    ("job-0661", "hdd-clangdmod", packet_clangd,
     "clangd leftover module BMI vs omitted ASTReader content validation; not bindname/075"),
]


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
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


def _init_trial(trial: str, seed: str) -> None:
    script = RUN_DIR / "scripts" / "init_trial.sh"
    subprocess.run([str(script), trial, seed], check=True, cwd=str(RUN_DIR))


def _complete_and_enqueue(packed: list[tuple[str, str, str, str]]) -> str:
    note = {"reason": ""}

    def fn(state):
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") in {"READY", "CLAIMED"}:
                if job.get("status") == "READY":
                    _claim_job(state, jid, WORKER)
                old = job.get("worker")
                if old in {None, WORKER} or str(old).startswith("scout-coord-"):
                    complete(state, jid, result="skip", artifact=artifact)
        ids = {s.get("id") for s in state.get("specimens") or []}
        reasons = []
        for job_id, spec_id, trial, priority_reason in packed:
            if spec_id not in ids:
                state.setdefault("specimens", []).append({"id": spec_id})
                ids.add(spec_id)
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
            if job is not None and job.get("status") in {"READY", "CLAIMED"}:
                if job.get("status") == "READY":
                    _claim_job(state, job_id, WORKER)
                complete(state, job_id, result="ok", artifact=f"specimens/{spec_id}")
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
                    priority_reason=priority_reason,
                    specimen=spec_id,
                    lineage=trial,
                    phase="cambrian",
                    extra={"trial": trial},
                )
            reasons.append(f"READY_R1_DREAM trial={trial} specimen={spec_id}")
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
                phase="cambrian",
            )
        note["reason"] = "; ".join(reasons)
        return True

    with_state(fn)
    return note["reason"]


def main() -> None:
    claimed: list[str] = []
    packed: list[tuple[str, str, str, str]] = []
    try:
        for job_id, trial, builder, priority_reason in PACKETS:
            spec_id = _claim_id()
            claimed.append(spec_id)
            emit(builder(spec_id))
            seed = write_seed(SPECIMENS / spec_id)
            _init_trial(trial, str(seed))
            packed.append((job_id, spec_id, trial, priority_reason))
        update_index()
        launch_note = _complete_and_enqueue(packed)
        for job_id, spec_id, trial, _ in packed:
            print(SPECIMENS / spec_id)
            print(f"seed=seeds/{spec_id}.md trial={trial} job={job_id}")
            print(f"hdd={HDD_ROOT / trial}")
        print(launch_note)
        print(f"ids={[p[1] for p in packed]} worker={WORKER} at={now_jst()}")
        for jid, artifact in SKIP_JOBS.items():
            print(f"SKIP {jid}: {artifact}")
    except Exception:
        for spec_id in claimed:
            dest = SPECIMENS / spec_id
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
