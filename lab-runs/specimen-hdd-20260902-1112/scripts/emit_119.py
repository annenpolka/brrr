#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets from 119.

Packed (unique vs 001-118; 075 not overwritten; not bazel#29298):
1) prefix-dev/pixi#3758 / PR 3782: leftover task cache filename keyed by
   run-environment+task-name, omitting task arguments. Distinct from
   specimen-115 go-task leftover wildcard checksum omitting MATCH.
2) swiftlang/swift-package-manager#9144 (cherry-pick PR 9210): leftover
   registry metadata cache inverted TTL so previous checksum fingerprint
   is stored for a new version. Distinct from 075 rustc fingerprint,
   086 cargo rustc extra-filename, 115 wildcard.
3) mesonbuild/meson#10348 / PR 10728: leftover wrap-file identity vs
   leftover subproject checkout; wrap hash omitted so
   `.meson-subproject-wrap-hash.txt` is not the identity. Distinct from
   064/070/092 nix NAR. meson#10159 closed without PR (CI packagecache
   discussion) — packed 10728 instead.

SKIP:
- job-0480 poetry vcs leftover vs 021/102: no unique leftover git-vs-path
  pair distinct from 021 lock leftover / 102 uv vcs leftover.
- job-0482 gradle artifact transform leftover vs 076/088/104: no merged
  leftover-identity pair (transform issues #19747/#31501/#34719 still
  open; #22963 reopen).
- tuist#11870 name-vs-identity: grouping collision of two current
  packages, not leftover previous object after change.
- steipete/summarize#171: cache hash omitting context is THIN_WRAPPER of
  two hashes (content vs content+context).
- hatch dist/lock leftover: no merged leftover-identity pair.
- job-0508/0509/0510/0511: already 086 / 078 / 064-070-092 / 082-100.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 119
WORKER = "scout-leftover-119"
PACKED = [
    (
        None,
        WORKER,
        "hdd-pixiargs",
        "pixi leftover task cache filename omits args; not 115 wildcard MATCH",
    ),
    (
        None,
        WORKER,
        "hdd-regttl",
        "spm leftover registry metadata TTL inverted; previous checksum for new version; not 075/086/115",
    ),
    (
        "job-0497",
        WORKER,
        "hdd-wraphash",
        "meson leftover wrap-file vs leftover subproject; wrap-hash omitted; not 064/070/092",
    ),
]
SKIP_JOBS = {
    "job-0480": (
        "skip poetry vcs leftover git vs path identity: no unique leftover "
        "git-vs-path merged pair distinct from specimen-021 poetry lock leftover "
        "and specimen-102 uv vcs leftover. not inventing refs; not 021/102"
    ),
    "job-0482": (
        "skip gradle artifact transform leftover vs input identity: no merged "
        "pinned leftover-identity pair distinct from 076/088/104. gradle#19747 "
        "transform mutates input still open; #31501 transform fingerprint cache "
        "open; #34719 transform param cache debug open; #22963 transform not "
        "triggered reopen. not inventing refs"
    ),
    "job-0508": (
        "skip cargo rustc crate-hash leftover vs extra-filename: already "
        "specimen-086. not inventing refs"
    ),
    "job-0509": (
        "skip go build cache action id leftover vs content: already specimen-078. "
        "not inventing refs"
    ),
    "job-0510": (
        "skip nix flake leftover narHash vs rev: already specimen-064/070/092. "
        "not inventing refs"
    ),
    "job-0511": (
        "skip bun leftover workspace catalog protocol: already specimen-082/100 "
        "Honor-KILL catleft. not inventing refs"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: sccache leftover cache identity vs compiler fingerprint not 075/086",
        "unique sccache leftover",
    ),
    (
        "public OSS: ccache leftover hash vs extra-filename identity not 086",
        "unique ccache leftover",
    ),
    (
        "public OSS: pants leftover fingerprint vs source identity not 076/088/104/115",
        "unique pants leftover retry",
    ),
    (
        "public OSS: cmake fileapi leftover vs compile_commands identity not 001-118",
        "unique cmake fileapi leftover",
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


def packet_pixi(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: prefix-dev/pixi
failing_ref: 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
fixed_ref: 804d2360157ca9c3d9197a4519ea803d28220e59
source_issue: https://github.com/prefix-dev/pixi/issues/3758
source_pr: https://github.com/prefix-dev/pixi/pull/3782
mechanism_tags:
  - leftover-task-cache-filename
  - omitted-task-arguments
  - run-environment-task-name-key
ecosystem: pixi
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Pixi's task cache can keep the identity of **one parametrized invocation** after a later invocation of the same task name with different arguments should be a different cache object. The cache filename is `run-environment-task-name.json`. Task arguments that render `inputs` / `outputs` are omitted from that filename.

On failing_ref `1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05`, `ExecutableTask::cache_name` is:

```
pub(crate) fn cache_name(&self) -> String {
    format!(
        "{}-{}.json",
        self.run_environment.name(),
        self.name().unwrap_or("default")
    )
}
```

`can_skip` and `save_cache` both join that name under the task-cache folder. Two `create` invocations with `A.txt` then `B.txt` share one file. The second overwrites the first; the next `A.txt` misses.

Public report (prefix-dev/pixi#3758):

```
[tasks.create]
args = ["file"]
cmd = "touch {{ file }}"
outputs = ["{{ file }}"]

[tasks.multiple]
depends-on = [
    { task = "create", args = ["A.txt"] },
    { task = "create", args = ["B.txt"] }
]
```

```
pixi run multiple   # touch A.txt; touch B.txt
pixi run multiple   # touch A.txt; touch B.txt  — no cache hit
```

A single parametrized depend (`create` with `single.txt`) does hit. Two non-parametrized tasks (`create1` / `create2`) each have their own filename and hit.

In-tree after the repair (not on failing_ref): `cache_name` takes a `NameHash` of rendered inputs/outputs; tests `test_task_caching_with_multiple_outputs_args` / `test_task_caching_with_multiple_inputs_args`.

Case A — first `pixi run multiple` (A then B):
  cache file written for env+name
  B overwrites A's hash
  not leftover reuse yet (both ran)

Case B — second `pixi run multiple` with leftover env+name file from B:
  leftover: B's computation hash under `default-create.json`
  A omitted from the filename
  both run again (no cache hit)

Case C — `pixi run single` (one parametrized depend):
  unique env+name file matches that one arg-set
  cache hit
  not this leftover (only one instantiation)

Case D — delete the task-cache folder then `pixi run multiple`:
  fresh identity
  not leftover filename

The developer wants to know which identity case B actually left in the task-cache folder: leftover B hash reused as A's filename, split files per rendered args, or omitted (no cache file).
""",
        observed="""# OBSERVED

Public prefix-dev/pixi#3758 (closed 2025-05-20). PR 3782 squash `804d2360157ca9c3d9197a4519ea803d28220e59` (parent `1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05`). Local pixi was not performed on this lab host.

Issue body: `pixi run multiple` never reports cache hit; `pixi run single` and `pixi run create-all` (two distinct task names) do.

On failing_ref, cache filename is run-environment + task-name. Rendered inputs/outputs and ArgValues are not that filename. `TaskHash::computation_hash` still hashes file contents inside the file; the *name* of the file is the leftover identity.

`NameHash` / `task_args_hash` are **not** on the failing revision. They are added by PR 3782.

Not this packet: specimen-115 (go-task leftover wildcard fingerprint omitting MATCH; template name `build-*` vs MATCH instantiation). Pixi leftover is one named task with two argument instantiations sharing `env-name.json`.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
# src/task/executable_task.rs cache_name / can_skip / save_cache

# public shape:
# leftover default-create.json from create args=B.txt
# pixi run multiple with create args=A.txt then B.txt: no cache hit
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""prefix-dev/pixi
  src/task/executable_task.rs
  src/task/task_hash.rs
  tests/integration_python/test_run_cli.py
""",
        source="""repository: prefix-dev/pixi
issue: https://github.com/prefix-dev/pixi/issues/3758
pr: https://github.com/prefix-dev/pixi/pull/3782
failing_ref (squash parent): 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
fixed_ref (squash merge): 804d2360157ca9c3d9197a4519ea803d28220e59
merged_at: 2025-05-20T07:56:04Z
pr_author: nichmor
merged_by: ruben-arts
changed_files: crates/pixi_manifest/src/task.rs, crates/pixi_manifest/src/toml/task.rs, src/cli/run.rs, src/task/executable_task.rs, src/task/task_hash.rs, tests/integration_python/test_run_cli.py
pr_title: fix: take into account tasks arguments when caching
scout_note: not specimen-115 go-task leftover wildcard checksum omitting MATCH. Distinct leftover: pixi task cache filename keyed by run-environment+task-name, omitting rendered args.
""",
        answer_key="""KNOWN FIX (sealed): prefix-dev/pixi PR 3782 squash 804d2360157ca9c3d9197a4519ea803d28220e59.

failing_ref is squash parent 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05.

cache_name was run-environment + task-name. Two ArgValues instantiations of one task shared leftover cache file; the later hash overwrote the earlier.

PR repair: NameHash of rendered inputs/outputs is part of the filename; can_skip/save_cache call TaskHash::task_args_hash.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (first A/B overwrite vs leftover B filename reused as A vs single-arg hit vs wipe cache)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — env+name identity and arg-instantiation identity are different objects; leftover filename blocked cache
ecosystem: pixi / conda
mechanism_family: leftover-task-cache, omitted-arguments, filename-key

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "cache_name_failing.rs": """// Reduced excerpt of ExecutableTask::cache_name on failing_ref
// src/task/executable_task.rs
// 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
// Filename identity is run-environment + task-name.
// ArgValues / rendered inputs/outputs are omitted from the filename.

    pub(crate) fn cache_name(&self) -> String {
        format!(
            "{}-{}.json",
            self.run_environment.name(),
            self.name().unwrap_or("default")
        )
    }

    pub(crate) async fn can_skip(&self, lock_file: &LockFile) -> Result<CanSkip, std::io::Error> {
        let cache_name = self.cache_name();
        let cache_file = self.project().task_cache_folder().join(cache_name);
        // ...
    }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  tasks.create args=["file"] outputs=["{{ file }}"]
  tasks.multiple depends-on create A.txt then create B.txt
  leftover task-cache default-create.json

Case A (first pixi run multiple):
  A writes default-create.json
  B overwrites same filename
  both ran

Case B (second pixi run multiple, leftover B file):
  leftover: B computation hash under env+name
  A omitted from filename
  no cache hit

Case C (single parametrized depend):
  one instantiation
  cache hit
  not this leftover

Case D (delete task-cache folder):
  fresh identity
  not leftover filename

Not this packet:
  go-task leftover wildcard fingerprint omitting MATCH (specimen-115)
""",
        },
    )


def packet_swiftpm(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: swiftlang/swift-package-manager
failing_ref: d8ae00bc06a6c5f643d5b843537a8118766c3c7c
fixed_ref: 1abd9a2f87e568fdfa67bd4564cea65872aaeaac
source_issue: https://github.com/swiftlang/swift-package-manager/issues/8981
source_pr: https://github.com/swiftlang/swift-package-manager/pull/9144
mechanism_tags:
  - leftover-registry-metadata-cache
  - inverted-ttl
  - omitted-version-from-cache-key
  - tofu-checksum-fingerprint
ecosystem: swift-package-manager
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

SwiftPM's in-memory registry metadata cache can keep the identity of a **previous version's checksum** after a later resolve of a new version should fetch that version's metadata. `MetadataCacheKey` is `(registry, package)` — version is omitted. The TTL predicate is inverted (`cached.expires < .now()`), so the cache is used only *after* the 60-minute TTL, which is when a new release is most likely.

On failing_ref `d8ae00bc06a6c5f643d5b843537a8118766c3c7c`, `_getRawPackageVersionMetadata` is:

```
let cacheKey = MetadataCacheKey(registry: registry, package: package)
if let cached = self.metadataCache[cacheKey], cached.expires < .now() {
    return cached.metadata
}
```

`metadataCacheTTL` is 60*60 seconds. After expiry, leftover metadata (including checksum) is returned for any version of that package. `ChecksumTOFU.getExpectedChecksum` then `writeToStorage` that leftover checksum as the fingerprint for the *new* version under `~/Library/org.swift.swiftpm/security/fingerprints/`.

Public report (swiftlang/swift-package-manager#9144 / related #8981):

1. Keep Xcode / libSwiftPM open ≥ 1 hour after a resolve (cache populated).
2. Publish a new package version to the registry.
3. Resolve the new version.
4. Leftover: previous checksum fingerprint is stored for the new version.
5. `swift package resolve` then fails:

```
invalid registry source archive checksum 'newchecksum', expected 'previouschecksum'
```

Workaround: purge fingerprint storage. Cherry-pick of the same repair is PR 9210 on `release/6.2`.

In-tree after the repair (not on failing_ref): `MetadataCacheKey` includes `version`; predicate is `cached.expires > .now()`; test `getPackageVersionMetadataInCache` fetches 1.1.1 then 1.1.0 as distinct keys.

Case A — first fetch of version 1.1.0 within TTL:
  inverted predicate does *not* return cache
  network fetch
  not leftover (fresh metadata written)

Case B — after TTL, fetch of new version 1.1.1 with leftover cache of 1.1.0:
  leftover: 1.1.0 metadata (checksum) reused as 1.1.1
  version omitted from MetadataCacheKey
  TOFU writes previouschecksum for 1.1.1

Case C — version included in the cache key (post-repair shape, not on failing_ref):
  miss
  not leftover previous-version identity

Case D — delete fingerprint storage then resolve:
  fresh TOFU identity
  not leftover on-disk fingerprint

The developer wants to know which identity case B actually left in fingerprint storage for 1.1.1: leftover previouschecksum of 1.1.0, newchecksum of 1.1.1, or omitted (no fingerprint file).
""",
        observed="""# OBSERVED

Public swiftlang/swift-package-manager PR 9144 (merged 2025-09-29) squash `1abd9a2f87e568fdfa67bd4564cea65872aaeaac` (parent `d8ae00bc06a6c5f643d5b843537a8118766c3c7c`). Cherry-pick PR 9210 onto `release/6.2`. Related issue #8981. Local SwiftPM was not performed on this lab host.

PR body: inverted `expires < now` means the cache is used only after TTL. MetadataCacheKey omits version, so leftover checksum of the previous release is written as TOFU fingerprint for the new release.

On failing_ref, `_getRawPackageVersionMetadata` keys only registry+package. Version is a function argument used to build the HTTP URL, not the cache key. `ChecksumTOFU.writeToStorage` records whatever checksum that leftover metadata supplied.

Including `version` on MetadataCacheKey and reversing the TTL predicate are **not** on the failing revision. They are added by PR 9144.

Not this packet: specimen-075 (rustc incremental fingerprint). specimen-086 (cargo rustc extra-filename). specimen-115 (go-task wildcard checksum omitting MATCH).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref d8ae00bc06a6c5f643d5b843537a8118766c3c7c
# Sources/PackageRegistry/RegistryClient.swift _getRawPackageVersionMetadata
# Sources/PackageRegistry/ChecksumTOFU.swift writeToStorage

# public shape:
# leftover metadataCache[registry,package] after TTL
# new version resolve writes previouschecksum into fingerprints/
# invalid registry source archive checksum 'newchecksum', expected 'previouschecksum'
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""swiftlang/swift-package-manager
  Sources/PackageRegistry/RegistryClient.swift
  Sources/PackageRegistry/ChecksumTOFU.swift
  Tests/PackageRegistryTests/RegistryClientTests.swift
  ~/Library/org.swift.swiftpm/security/fingerprints/
""",
        source="""repository: swiftlang/swift-package-manager
issue: https://github.com/swiftlang/swift-package-manager/issues/8981
pr: https://github.com/swiftlang/swift-package-manager/pull/9144
cherry_pick_pr: https://github.com/swiftlang/swift-package-manager/pull/9210
failing_ref (squash parent of 9144 on main): d8ae00bc06a6c5f643d5b843537a8118766c3c7c
fixed_ref (squash merge of 9144): 1abd9a2f87e568fdfa67bd4564cea65872aaeaac
cherry_pick_base (release/6.2): 0da281d271f090f4d61e4182e8584f36a8026e26
cherry_pick_head: ae39ccbcb8e8a14263a197c2825c8d4d5811c7d7
merged_at: 2025-09-29T21:43:54Z
pr_author: ZachNagengast
merged_by: plemarquand
changed_files: Sources/PackageRegistry/RegistryClient.swift, Tests/PackageRegistryTests/RegistryClientTests.swift
pr_title: Fix inverted logic on registry cache expiration
scout_note: not specimen-075/086/115. Distinct leftover: inverted TTL + MetadataCacheKey omits version so leftover checksum fingerprint is stored for a new version. Cherry-pick PR 9210 is the same repair on release/6.2.
""",
        answer_key="""KNOWN FIX (sealed): swiftlang/swift-package-manager PR 9144 squash 1abd9a2f87e568fdfa67bd4564cea65872aaeaac.

failing_ref is squash parent d8ae00bc06a6c5f643d5b843537a8118766c3c7c.

MetadataCacheKey omitted version; inverted expires < now returned leftover metadata after TTL; ChecksumTOFU wrote that leftover checksum as the new version's fingerprint.

PR repair: add version to MetadataCacheKey; use expires > now; cherry-pick PR 9210 onto release/6.2.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (in-TTL fetch vs leftover previous-version checksum after TTL vs versioned key miss vs wipe fingerprints)
reproducibility: source-backed PR + pinned squash parent/commit + cherry-pick 9210; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — package identity and version identity are different objects; leftover metadata poisoned TOFU for the new version
ecosystem: swift / package-registry
mechanism_family: leftover-metadata-cache, inverted-ttl, omitted-version, tofu-fingerprint

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "metadata_cache_key_failing.swift": """// Reduced excerpt of _getRawPackageVersionMetadata on failing_ref
// Sources/PackageRegistry/RegistryClient.swift
// d8ae00bc06a6c5f643d5b843537a8118766c3c7c
// Cache key is registry+package. Version is omitted.
// Predicate uses expires < now (inverted TTL).

        let cacheKey = MetadataCacheKey(registry: registry, package: package)
        if let cached = self.metadataCache[cacheKey], cached.expires < .now() {
            return cached.metadata
        }
        // HTTP GET .../scope/name/version
        // on 200:
        self.metadataCache[cacheKey] = (metadata: metadata, expires: .now() + Self.metadataCacheTTL)

    private struct MetadataCacheKey: Hashable {
        let registry: Registry
        let package: PackageIdentity.RegistryIdentity
        // no version
    }

    private static let metadataCacheTTL: DispatchTimeInterval = .seconds(60 * 60)
""",
            "leftover_identity_split.txt": """Registry / fixture:
  in-memory metadataCache
  ChecksumTOFU fingerprints/ for new version
  leftover previouschecksum after TTL

Case A (first fetch 1.1.0 within TTL):
  inverted predicate misses
  network fetch
  not leftover

Case B (after TTL, fetch 1.1.1, leftover 1.1.0 cache):
  leftover: 1.1.0 metadata reused
  TOFU writes previouschecksum for 1.1.1
  invalid registry source archive checksum

Case C (version on MetadataCacheKey):
  miss
  not leftover previous-version identity

Case D (delete fingerprints/):
  fresh TOFU identity
  not leftover on-disk fingerprint

Not this packet:
  rustc incremental fingerprint (specimen-075)
  cargo rustc extra-filename (specimen-086)
  go-task leftover wildcard MATCH (specimen-115)
""",
        },
    )


def packet_meson(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: mesonbuild/meson
failing_ref: 97f248db24fe88495dbe35bbae6eafd643c0c94b
fixed_ref: 004575874ffdb77ee997f9c19e0a041d144994d6
source_issue: https://github.com/mesonbuild/meson/issues/10348
source_pr: https://github.com/mesonbuild/meson/pull/10728
mechanism_tags:
  - leftover-wrap-file-identity
  - omitted-wrap-hash
  - leftover-subproject-checkout
ecosystem: meson
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Meson wrap resolution can keep the identity of a **previous wrap-file checkout** after the wrap file on disk has a new revision / source_hash / directory. If `subprojects/<dir>/meson.build` already exists, `Resolver.resolve` returns that leftover directory and does not compare wrap-file identity.

On failing_ref `97f248db24fe88495dbe35bbae6eafd643c0c94b`, `PackageDefinition` has no `wrapfile_hash`. There is no `.meson-subproject-wrap-hash.txt`. `resolve` is:

```
# The directory is there and has meson.build? Great, use it.
if method == 'meson' and os.path.exists(meson_file):
    return rel_path
```

Wrap-file contents (revision, source_url, source_hash, directory) are not that identity. Leftover checkout from the previous wrap file is kept.

Public report (mesonbuild/meson#10348): change wrap-file version/revision; ninja does not reconfigure; leftover subproject stays. meson#10159 (CI packagecache leftover across wrap-file updates) closed without a PR.

In-tree after the repair (not on failing_ref): `wrapfile_hash` SHA-256 of the wrap file; `update_hash_cache` writes `.meson-subproject-wrap-hash.txt`; `validate()` warns when stored hash ≠ current wrap-file hash. Unit test `test_wrap_git` changes `revision = master` to `not-master` and expects `revision may be out of date` on `--reconfigure`.

Case A — first `meson setup`, wrap matches the checkout just fetched:
  no leftover
  wrap-hash omitted (file does not exist yet)

Case B — wrap file edited (new revision / source_hash), leftover `subprojects/<dir>/meson.build`:
  leftover: previous wrap-file checkout
  current wrap-file identity is the new revision
  resolve returns leftover directory
  no wrap-hash compare

Case C — delete `subprojects/<dir>` then setup:
  fresh fetch from current wrap file
  not leftover checkout

Case D — cmake method with leftover directory (`CMakeLists.txt` present):
  leftover cmake checkout used
  same omitted wrap-file identity (meson path is the reported one)

The developer wants to know which identity case B actually used for the subproject: leftover previous wrap-file checkout, current wrap-file identity, or omitted (no subproject directory).
""",
        observed="""# OBSERVED

Public mesonbuild/meson#10348 (closed 2022-09-19). PR 10728 commit `004575874ffdb77ee997f9c19e0a041d144994d6` (parent `97f248db24fe88495dbe35bbae6eafd643c0c94b`). meson#10159 closed without a pull request. Local meson was not performed on this lab host.

Issue body: changing wrap-file contents does not trigger rebuild/reconfigure of the subproject.

On failing_ref, `resolve` treats an existing `meson.build` as identity. Wrap-file hash is not computed. `.meson-subproject-wrap-hash.txt` is not written. `update_hash_cache` / `validate` are **not** on the failing revision. They are added by PR 10728.

Not this packet: specimen-064/070/092 (nix NAR hash leftover vs rev). Distinct leftover: wrap-file identity vs leftover subproject checkout with wrap-hash omitted.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 97f248db24fe88495dbe35bbae6eafd643c0c94b
# mesonbuild/wrap/wrap.py Resolver.resolve

# public shape:
# leftover subprojects/<dir>/meson.build from previous wrap
# wrap file now has a different revision
# meson setup / ninja does not pick up wrap-file identity
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""mesonbuild/meson
  mesonbuild/wrap/wrap.py
  mesonbuild/msubprojects.py
  unittests/allplatformstests.py
  subprojects/<dir>/.meson-subproject-wrap-hash.txt
""",
        source="""repository: mesonbuild/meson
issue: https://github.com/mesonbuild/meson/issues/10348
pr: https://github.com/mesonbuild/meson/pull/10728
failing_ref (parent of wrap-hash commit on master): 97f248db24fe88495dbe35bbae6eafd643c0c94b
fixed_ref (Warn if wrap file changes): 004575874ffdb77ee997f9c19e0a041d144994d6
merged_at: 2022-09-19T02:48:50Z
pr_author: nosracd
merged_by: eli-schwartz
changed_files: mesonbuild/wrap/wrap.py, mesonbuild/msubprojects.py, unittests/allplatformstests.py
pr_title: Git subproject revision checking
scout_note: not specimen-064/070/092 nix NAR. Distinct leftover: wrap-file identity vs leftover subproject checkout; wrap-hash omitted. meson#10159 closed without PR (CI packagecache discussion). job-0497.
""",
        answer_key="""KNOWN FIX (sealed): mesonbuild/meson PR 10728 commit 004575874ffdb77ee997f9c19e0a041d144994d6.

failing_ref is parent 97f248db24fe88495dbe35bbae6eafd643c0c94b.

resolve treated existing meson.build as identity and omitted wrap-file hash, so leftover checkout from the previous wrap file was kept.

PR repair: SHA-256 wrapfile_hash; update_hash_cache writes .meson-subproject-wrap-hash.txt; validate() warns when stored hash differs from current wrap file.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (first setup vs leftover checkout after wrap edit vs wipe subproject vs cmake leftover path)
reproducibility: source-backed issue+PR + pinned parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — wrap-file identity and leftover checkout identity are different objects; wrap-hash omitted so leftover dir was identity
ecosystem: meson / wraps
mechanism_family: leftover-wrap-file, omitted-wrap-hash, leftover-checkout

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "wrap_resolve_failing.py": """# Reduced excerpt of Resolver.resolve on failing_ref
# mesonbuild/wrap/wrap.py
# 97f248db24fe88495dbe35bbae6eafd643c0c94b
# Existing meson.build is the identity. Wrap-file hash is omitted.

        meson_file = os.path.join(self.dirname, 'meson.build')
        cmake_file = os.path.join(self.dirname, 'CMakeLists.txt')

        # The directory is there and has meson.build? Great, use it.
        if method == 'meson' and os.path.exists(meson_file):
            return rel_path
        if method == 'cmake' and os.path.exists(cmake_file):
            return rel_path

# PackageDefinition.__init__ has no wrapfile_hash.
# get_hashfile / update_hash_cache / validate do not exist.
""",
            "leftover_identity_split.txt": """Registry / fixture:
  subprojects/wrap_git.wrap revision = master then not-master
  leftover subprojects/<dir>/meson.build
  no .meson-subproject-wrap-hash.txt on failing_ref

Case A (first meson setup):
  checkout matches wrap
  wrap-hash omitted (no file)

Case B (wrap file edited, leftover meson.build):
  leftover: previous wrap-file checkout
  current wrap-file identity is new revision
  resolve returns leftover directory

Case C (delete subprojects/<dir> then setup):
  fresh fetch
  not leftover checkout

Case D (cmake leftover CMakeLists.txt):
  leftover cmake checkout
  wrap-file identity still omitted

Not this packet:
  nix NAR leftover vs rev (specimen-064/070/092)
  meson#10159 CI packagecache discussion (no PR)
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
    builders = [packet_pixi, packet_swiftpm, packet_meson]
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
