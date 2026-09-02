#!/usr/bin/env python3
"""Emit two sealed REAL_SOURCE_BACKED leftover-identity packets.

1) golang/go#65363 / CL 762602: go work sync leftover replace graph.
2) gradle/gradle#30052 / PR 32359: named FileCollection leftover base dir.

Not specimen-084 (sumdb extension leftover). Not specimen-088 (fileTree
query observation omitted). Not cargo#14230 (unfixed). Not bun#23615
(unfixed catalog cache leftover). Not bazel#29298 (unfixed).
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 99
WORKER_GO = "scout-job-0430"
WORKER_GR = "scout-job-0401"
JOB_GO = "job-0430"
JOB_GR = "job-0401"
TRIAL_GO = "hdd-workrepl"
TRIAL_GR = "hdd-ccnamed"
SKIP_JOBS = {
    "job-0345": "skip bun.lock catalog leftover packages: #23615 open; 36304 is package.json catalog: overwrite not lockfile packages leftover vs 082",
    "job-0347": "skip duplicate go work/replace leftover already packed from job-0430 (#65363)",
    "job-0399": "skip duplicate go work leftover already packed from job-0430",
    "job-0418": "skip duplicate go work leftover already packed from job-0430",
    "job-0421": "skip bazel env_inherit #29298 unfixed; no merged fixed_ref",
}


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 140):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_go(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: golang/go
failing_ref: a2214422293d2c26ad389050f25460b3f2f00825
fixed_ref: 8191cd88683192e9aa3f3a1c11e841f8f40a9a9d
source_issue: https://github.com/golang/go/issues/65363
source_pr: https://go-review.googlesource.com/c/go/+/762602
mechanism_tags:
  - go-work-sync-replace-leftover
  - workspace-replace-vs-module-replace
  - silent-editbuildlist-continue
ecosystem: go
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7200
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

`go work sync` can leave a workspace module's `go.mod` at the identity selected under **workspace replaces**, even when that module itself has no replace and its own graph would pick a higher requirement.

On failing_ref `a2214422293d2c26ad389050f25460b3f2f00825`, `runSync` (`src/cmd/go/internal/workcmd/sync.go`) first loads the workspace graph (`LoadModGraph` / `LoadPackages` with workspace replaces). It records `mustSelectFor[m]` as the module versions seen for packages in each work module. Then `EnterModule` switches to **single-module** mode at that module's root (that module's `go.mod` replaces only). `EditBuildList(..., nil, mustSelectFor[m])` tries to force the workspace-selected versions. On error it does `continue`.

In-tree after the repair (not on failing_ref): `src/cmd/go/testdata/script/work_sync_replace.txt`.

```
go.work: use ./a ./b
a/go.mod: replace example.com/syncreplace v1.1.0 => example.com/syncreplace v1.0.0
          require example.com/syncreplace v1.1.0 and rsc.io/quote v1.0.0
b/go.mod: no replace
          require example.com/syncreplace v1.1.0 and rsc.io/quote v1.0.0
syncreplace v1.0.0 requires rsc.io/quote v1.0.0
syncreplace v1.1.0 requires rsc.io/quote v1.1.0
```

Workspace load applies a's replace, so syncreplace is v1.0.0 and quote stays v1.0.0. Module b has no replace: its own graph wants syncreplace v1.1.0 / quote v1.1.0.

Case A — `GOWORK=off` in module b (`go list -m rsc.io/quote`):
  identity is b's own graph (quote v1.1.0 through syncreplace v1.1.0)
  no leftover workspace replace

Case B — `go work sync` from the workspace root:
  first pass uses workspace replaces (a's replace hides syncreplace v1.1.0's quote bump)
  `mustSelectFor[b]` therefore contains the workspace-selected quote v1.0.0
  `EnterModule(b)` drops a's replace
  `EditBuildList` forcing those versions can conflict
  failing_ref: `if err != nil { continue }` so b/go.mod is not rewritten
  leftover: b/go.mod still names quote v1.0.0 (workspace-replace identity)

Case C — `go work sync` when every work module has the same replace as the workspace:
  no replace skew
  not this leftover

Case D — `go work edit -replace` override in go.work that both modules share:
  workspace and module graphs agree on the override
  not the silent-continue leftover

The developer wants to know which identity `go work sync` actually left in `b/go.mod` for case B: leftover workspace-replace versions (quote v1.0.0, unsynced), b's own replace-free versions (quote v1.1.0), or omitted (no write because of continue vs fatal).
""",
        observed="""# OBSERVED

Public golang/go#65363 (closed 2026-04-29, gopherbot). CL 762602 (matloob) submitted as `8191cd88683192e9aa3f3a1c11e841f8f40a9a9d`. Failing world pinned on first parent `a2214422293d2c26ad389050f25460b3f2f00825`. Local `go work sync` was not performed on this lab host.

bcmills (issue comments): `go work sync` loads the module graph with workspace replaces, then reloads each work module individually with only that module's replaces. Workspace replace can hide requirements that would bump versions. Combined with `EditBuildList` error `continue`, the observed `go.mod` can stay at the workspace-selected identity.

On failing_ref, `runSync` after `EnterModule`:

```
changed, err := modload.EditBuildList(moduleLoader, ctx, nil, mustSelectFor[m])
if err != nil {
    continue
}
if changed {
    ...
    modload.WriteGoMod(moduleLoader, ctx, modload.WriteOpts{})
}
```

`work_sync_replace.txt` is **not** on the failing revision. It is added by CL 762602.

Not this packet: specimen-084 (golang/mod sumdb tree-extension leftover). specimen-083 (derived go.sum zip vs mod). cargo git-lock SHA vs checkout (rust-lang/cargo#14230 open; PR 17275 closed unmerged).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref a2214422293d2c26ad389050f25460b3f2f00825
# src/cmd/go/internal/workcmd/sync.go runSync
# src/cmd/go/testdata/script/work_sync_replace.txt (on CL 762602, not failing_ref)

# public shape:
# go.work use ./a ./b
# a replace syncreplace v1.1.0 => v1.0.0
# b no replace
# go work sync
# failing: EditBuildList error continue; b/go.mod leftover workspace quote v1.0.0
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""golang/go
  src/cmd/go/internal/workcmd/sync.go
  src/cmd/go/testdata/script/work_sync_replace.txt
  src/cmd/go/testdata/mod/example.com_syncreplace_v1.0.0.txt
  src/cmd/go/testdata/mod/example.com_syncreplace_v1.1.0.txt
""",
        source="""repository: golang/go
issue: https://github.com/golang/go/issues/65363
pr: https://go-review.googlesource.com/c/go/+/762602
failing_ref (CL parent): a2214422293d2c26ad389050f25460b3f2f00825
fixed_ref (submitted CL): 8191cd88683192e9aa3f3a1c11e841f8f40a9a9d
merged_at: 2026-04-29T18:17:32Z
pr_author: matloob
changed_files: src/cmd/go/internal/workcmd/sync.go, src/cmd/go/testdata/script/work_sync_replace.txt, testdata/mod example.com_syncreplace v1.0.0/v1.1.0
pr_title: cmd/go: loosen go work sync version requirements
scout_note: not specimen-084 sumdb leftover. not cargo#14230 unfixed. Distinct leftover: go work sync mustSelect from workspace replaces then EnterModule uses module replaces; EditBuildList continue leaves leftover go.mod identity.
""",
        answer_key="""KNOWN FIX (sealed): golang/go CL 762602 submitted 8191cd88683192e9aa3f3a1c11e841f8f40a9a9d.

failing_ref is CL first parent a2214422293d2c26ad389050f25460b3f2f00825.

Workspace graph used workspace replaces; EnterModule then forced those versions under each module's own replaces. Hidden requirements made workspace versions lower. EditBuildList conflicted; continue left leftover go.mod.

CL repair: addReq additive EditBuildList(loader, ctx, addFor[m], nil); Fatal on error; UpdateGoModFromReqs then write after ExitIfErrors. work_sync_replace.txt: a keeps quote v1.0.0 under replace; b without replace gets quote v1.1.0.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (GOWORK=off own graph vs workspace-replace mustSelect leftover vs same replace vs go.work override)
reproducibility: source-backed issue+CL + pinned parent/submit SHAs; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — workspace replace identity and per-module replace identity are different objects; continue kept leftover go.mod
ecosystem: go / workspaces
mechanism_family: leftover-workspace-replace, silent-continue, go-work-sync

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "sync_editbuildlist_failing.go": """// Reduced excerpt of runSync on failing_ref
// src/cmd/go/internal/workcmd/sync.go
// a2214422293d2c26ad389050f25460b3f2f00825
// Workspace versions are mustSelect. EnterModule drops other modules' replaces.
// EditBuildList error continue leaves leftover go.mod.

		changed, err := modload.EditBuildList(moduleLoader, ctx, nil, mustSelectFor[m])
		if err != nil {
			continue
		}
		if changed {
			modload.LoadPackages(moduleLoader, ctx, modload.PackageOpts{
				Tags:                     imports.AnyTags(),
				Tidy:                     true,
				VendorModulesInGOROOTSrc: true,
				ResolveMissingImports:    false,
				LoadTests:                true,
				AllowErrors:              true,
				SilenceMissingStdImports: true,
				SilencePackageErrors:     true,
			}, "all")
			modload.WriteGoMod(moduleLoader, ctx, modload.WriteOpts{})
		}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  go.work use ./a ./b
  a replace syncreplace v1.1.0 => v1.0.0
  b no replace
  syncreplace v1.0.0 requires rsc.io/quote v1.0.0
  syncreplace v1.1.0 requires rsc.io/quote v1.1.0

Case A (GOWORK=off in b):
  quote identity = v1.1.0
  no leftover workspace replace

Case B (go work sync, failing_ref):
  workspace graph applies a's replace
  mustSelectFor[b] has quote v1.0.0
  EnterModule(b) has no replace
  EditBuildList can err; continue
  leftover: b/go.mod still quote v1.0.0

Case C (every module has the same replace):
  no replace skew
  not leftover

Case D (go.work replace override shared):
  graphs agree
  not silent-continue leftover

Not this packet:
  golang/mod sumdb tree-extension leftover (specimen-084)
  derived go.sum zip vs mod (specimen-083)
  cargo lock SHA vs checkout (cargo#14230 unfixed)
""",
        },
    )


def packet_gradle(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: gradle/gradle
failing_ref: 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
fixed_ref: 2f46ab737e15c67d3904602fa66c658258c32b66
source_issue: https://github.com/gradle/gradle/issues/30052
source_pr: https://github.com/gradle/gradle/pull/32359
mechanism_tags:
  - named-file-collection-leftover-base-dir
  - provider-backed-relative-path
  - configuration-cache-resolver-omit
ecosystem: gradle
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

A **named** `FileCollection` of relative paths (not a directory `fileTree`) can keep the identity of the **root project's base directory** after configuration-cache load, even when the collection was created in a subproject.

Public report (gradle/gradle#30052, subproject `build.gradle.kts`):

```
val files = project.files(provider { "someFile.txt" })
println("config phase:")
files.forEach { println(it) }
doLast {
    println("execution phase:")
    files.forEach { println(it) }
}
```

With configuration cache, config phase prints `.../subproject/someFile.txt`. Execution phase after load prints `.../root/someFile.txt`.

On failing_ref `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3`, `ConfigurableFileCollectionCodec.decode` rebuilds with `fileCollectionFactory.configurableFiles()` and does **not** encode `PathToFileResolver`. `ProviderBackedFileCollectionSpec` stores only the `ProviderInternal`. Decode maps that spec to `element.provider` and `fileCollectionFactory.resolving(...)` using the CC isolate factory whose leftover base directory is the root of the build.

In-tree after the repair (not on failing_ref): `RelativePathFilesIntegrationTest` `"provider-backed relative files are resolved relative to their owner"`. Subproject task:

```
incoming.from(project.files(provider { "subFile.txt" }))
incoming.from(project(":other").isolated.projectDirectory.files(provider { "otherFile.txt" }))
incoming.from(layout.settingsDirectory.files(provider { "settingsFile.txt" }))
```

Expected files: `sub/subFile.txt`, `other/otherFile.txt`, `settingsFile.txt`.

Case A — named `files("/abs/sub/someFile.txt")` (already absolute):
  load path equals store path
  no leftover base directory

Case B — named `project.files(provider { "someFile.txt" })` in `:sub` under configuration cache:
  store (config) resolves against `:sub`
  failing_ref load (execution) resolves against leftover root directory
  leftover identity: root-dir FileCollection vs subproject FileCollection

Case C — `fileTree("src").files` queried at configuration time, then `src/file3` is added:
  not this leftover (that is specimen-088 omitted WorkInputs fingerprint)

Case D — named `files("file1", "file2")` then rewrite `file1` contents:
  names stay `[file1, file2]`; contents are not this leftover axis
  same named-files contrast used in specimen-088 case B, not a leftover root dir

The developer wants to know which identity case B actually stored for the named collection after CC load: leftover root-directory resolver (so `root/someFile.txt`), the creating project's resolver (`sub/someFile.txt`), or omitted (no collection restored).
""",
        observed="""# OBSERVED

Public gradle/gradle#30052 (closed 2025-03-03). PR 32359 (alllex) merge `2f46ab737e15c67d3904602fa66c658258c32b66` (parents `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3` + `fa0e3417532e782cc892fcc6cbbf180fb5780038`). Milestone 8.14 RC1. Local Gradle execution was not performed on this lab host.

PR body: CC does not store the base directory for some file collection types. After load, a relative file is resolved against the leftover root-directory-of-the-build because CC injects the file collection factory service with that base. Named `ConfigurableFileCollection` / `ProviderBackedFileCollection` and `ConfigurableFileTree` can still accept relative paths at execution time.

On failing_ref, `ConfigurableFileCollectionCodec`:

```
encodePreservingIdentityOf(value) {
    codec.run { encodeContents(value) }
    writeBoolean(value.isFinalizing)
}
...
val fileCollection = fileCollectionFactory.configurableFiles()
fileCollection.from(contents)
```

No `write(value.resolver)`. `ProviderBackedFileCollectionSpec` is `val provider: ProviderInternal<*>` only. Decode: `is ProviderBackedFileCollectionSpec -> element.provider`.

`RelativePathFilesIntegrationTest` is **absent** on `92fc31994d51f16cf8f172ca1118e2b33b2ea4c3`. The class is added by PR 32359.

Not this packet: specimen-088 (ConfigurableFileTree `.files` query omitted from CC fingerprint / Honor-KILL treeid). specimen-076 (unused system-property snapshot). specimen-042 (script class compiler HashMap race). specimen-051 (nested ValueSource deadlock).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
# ConfigurableFileCollectionCodec.kt encode/decode
# FileCollectionCodec.kt ProviderBackedFileCollectionSpec
# RelativePathFilesIntegrationTest.groovy (on the PR, not failing_ref)

# public shape (named files, relative provider, subproject):
# project.files(provider { "someFile.txt" })
# store: .../subproject/someFile.txt
# failing load: .../root/someFile.txt
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""gradle/gradle
  platforms/core-configuration/core-serialization-codecs/src/main/kotlin/org/gradle/internal/serialize/codecs/core/ConfigurableFileCollectionCodec.kt
  platforms/core-configuration/core-serialization-codecs/src/main/kotlin/org/gradle/internal/serialize/codecs/core/FileCollectionCodec.kt
  platforms/core-configuration/file-collections/src/integTest/groovy/org/gradle/api/file/RelativePathFilesIntegrationTest.groovy
""",
        source="""repository: gradle/gradle
issue: https://github.com/gradle/gradle/issues/30052
pr: https://github.com/gradle/gradle/pull/32359
failing_ref (merge first parent): 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
fixed_ref (merge commit): 2f46ab737e15c67d3904602fa66c658258c32b66
second_parent: fa0e3417532e782cc892fcc6cbbf180fb5780038
merged_at: 2025-03-03T15:44:13Z
merged_by: alllex
pr_author: alllex
changed_files: ConfigurableFileCollectionCodec.kt, ConfigurableFileTreeCodec.kt, FileCollectionCodec.kt, PathToFileResolverCodec.kt, RelativePathFilesIntegrationTest.groovy
pr_title: Fix file collections and file trees with relative files under CC
scout_note: not specimen-088 fileTree query observation. Distinct leftover: named FileCollection / provider relative path omits PathToFileResolver so CC load uses leftover root base dir.
""",
        answer_key="""KNOWN FIX (sealed): gradle/gradle PR 32359 merge 2f46ab737e15c67d3904602fa66c658258c32b66.

failing_ref is merge first parent 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3.

Named ConfigurableFileCollectionCodec decoded via factory.configurableFiles() with no resolver. ProviderBackedFileCollectionSpec stored only the provider. Load resolved relative names against leftover root-directory-of-the-build.

PR repair: PathToFileResolverCodec; encode value.resolver; withResolver(resolver).configurableFiles(); ProviderBackedFileCollectionSpec(resolver, provider). RelativePathFilesIntegrationTest owner-relative named files.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (absolute named files vs provider relative leftover root vs fileTree query fingerprint omit vs named files content rewrite)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — collection contents and the resolver that names them are different identities; CC factory leftover root is not the creating project
ecosystem: gradle / configuration-cache
mechanism_family: leftover-base-dir, named-file-collection, omitted-resolver

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "ConfigurableFileCollectionCodec_failing.kt": """// Reduced excerpt of ConfigurableFileCollectionCodec on failing_ref
// 92fc31994d51f16cf8f172ca1118e2b33b2ea4c3
// Named collection contents are stored. Resolver / base directory is not.

    override suspend fun WriteContext.encode(value: ConfigurableFileCollection) {
        require(value is DefaultConfigurableFileCollection)
        encodePreservingIdentityOf(value) {
            codec.run {
                encodeContents(value)
            }
            writeBoolean(value.isFinalizing)
        }
    }

    override suspend fun ReadContext.decode(): ConfigurableFileCollection {
        return decodePreservingIdentity { id ->
            val contents = codec.run { decodeContents() }
            val fileCollection = fileCollectionFactory.configurableFiles()
            fileCollection.from(contents)
            if (readBoolean()) {
                fileCollection.finalizeValue()
            }
            isolate.identities.putInstance(id, fileCollection)
            fileCollection
        }
    }
""",
            "ProviderBackedFileCollectionSpec_failing.kt": """// Reduced excerpt of FileCollectionCodec on failing_ref
// Provider-backed named collection stores the provider only.
// Decode uses leftover isolate fileCollectionFactory (root base dir).

private
class ProviderBackedFileCollectionSpec(val provider: ProviderInternal<*>)

                    is ProviderBackedFileCollectionSpec -> element.provider

            is ProviderBackedFileCollection -> {
                val provider = fileCollection.provider
                if (provider !is TaskProvider<*>) {
                    elements.add(ProviderBackedFileCollectionSpec(provider))
                    false
                } else {
                    true
                }
            }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  include("sub")
  named collection: project.files(provider { "someFile.txt" })
  CC store then load

Case A (absolute named files):
  path identity unchanged
  no leftover base dir

Case B (named provider relative in :sub, CC load):
  store: .../sub/someFile.txt
  failing_ref load: .../root/someFile.txt
  leftover: root-directory resolver omitted from the collection identity

Case C (fileTree("src").files queried, then src/file3):
  not this leftover (specimen-088 omitted WorkInputs)

Case D (named files("file1","file2"), rewrite file1 bytes):
  names stay; contents not this leftover axis

Not this packet:
  ConfigurableFileTree query observation omitted (specimen-088)
  unused system-property snapshot (specimen-076)
  script class compiler race (specimen-042)
""",
        },
    )


def _claim_job(state, job_id: str, worker: str) -> None:
    job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
    if job is None:
        raise SystemExit(f"{job_id} missing")
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
    elif job.get("status") == "CLAIMED" and job.get("worker") == worker:
        pass
    elif job.get("status") == "DONE":
        pass
    else:
        raise SystemExit(
            f"{job_id} status={job.get('status')} worker={job.get('worker')}"
        )


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


def _complete_and_enqueue(go_id: str, gr_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
        _claim_job(state, JOB_GO, WORKER_GO)
        _claim_job(state, JOB_GR, WORKER_GR)
        job_go = next(j for j in state["ready_jobs"] if j["id"] == JOB_GO)
        job_gr = next(j for j in state["ready_jobs"] if j["id"] == JOB_GR)
        if job_go.get("status") == "CLAIMED" and job_go.get("worker") == WORKER_GO:
            complete(state, JOB_GO, result="ok", artifact=f"specimens/{go_id}")
        if job_gr.get("status") == "CLAIMED" and job_gr.get("worker") == WORKER_GR:
            complete(state, JOB_GR, result="ok", artifact=f"specimens/{gr_id}")
        _register(
            state,
            go_id,
            TRIAL_GO,
            "go work sync leftover replace identity; not 084/083",
        )
        _register(
            state,
            gr_id,
            TRIAL_GR,
            "named FileCollection leftover root dir; not 088/076",
        )
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") in {"READY", "CLAIMED"}:
                complete(state, jid, result="skip", artifact=artifact)
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
                "dream.sh not launched from scout; READY_R1_DREAM enqueued "
                f"trials={TRIAL_GO},{TRIAL_GR}"
            )
        return (go_id, gr_id)

    with_state(fn)
    return note["reason"]


def main() -> None:
    go_id = _claim_id()
    gr_id = _claim_id()
    go_dest = SPECIMENS / go_id
    gr_dest = SPECIMENS / gr_id
    try:
        p1 = emit(packet_go(go_id))
        s1 = write_seed(SPECIMENS / go_id)
        p2 = emit(packet_gradle(gr_id))
        s2 = write_seed(SPECIMENS / gr_id)
        update_index()
        launch_note = _complete_and_enqueue(go_id, gr_id)
        print(p1)
        print(s1)
        print(p2)
        print(s2)
        print(launch_note)
        print(f"ids={go_id},{gr_id} trials={TRIAL_GO},{TRIAL_GR}")
    except Exception:
        for dest in (go_dest, gr_dest):
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
