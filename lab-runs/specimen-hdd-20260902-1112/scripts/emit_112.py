#!/usr/bin/env python3
"""Emit two sealed REAL_SOURCE_BACKED leftover-identity packets.

1) sbt/sbt#9195 / PR 9207: leftover extra zinc Analysis identity in
   last-write cache vs current analysis-file identity (size+mtime).
   Unique vs 001-111 (no sbt). Distinct from gradle CC leftover 088/104.
2) hashicorp/terraform#37396: leftover resource identity omitted from
   state after apply (destroy error + mark-only update). Unique vs 081
   leftover IdentityJSON vs nil schema Decode.

job-0470 poetry lock leftover vs extras: no unique leftover lock vs extras
identity with merged pair distinct from extraedge/080/098/021.
job-0471 yarn pnp leftover vs 089: #6724 closed without merged PR.
job-0472 helm leftover vs 079: #30819 leftover labels unfixed not_planned.
job-0474 go sumdb leftover vs 083/084: leftover unauthenticated hashes is
084; leftover zip vs mod is 083.
job-0475 maven shade leftover not 096: no merged leftover-identity pair.
job-0476 docker layer leftover vs 066/097: buildkit#5789 closed without
merged PR. Factory starvation rather than inventing refs.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 112
WORKER = "scout-leftover-0469"
JOB_SBT = "job-0469"
JOB_TF = "job-0473"
TRIAL_SBT = "hdd-zincanal"
TRIAL_TF = "hdd-tfomitid"
SKIP_STARVE = {
    "job-0470": (
        "Factory starvation: poetry lock leftover vs extras identity — no "
        "merged pinned leftover-lock-vs-extras pair distinct from extraedge/"
        "080/098/021. poetry#9345 leftover extras in venv vs lock presence "
        "is not lock leftover vs extras. Not inventing refs."
    ),
    "job-0471": (
        "Factory starvation: yarn pnp leftover unique vs 089 — yarn#6724 "
        "duplicate virtual packages closed without merged PR. leftover "
        "storedBuildState after unplugged remove is already specimen-089. "
        "Not inventing refs."
    ),
    "job-0472": (
        "Factory starvation: helm leftover unique vs 079 — helm#30819 leftover "
        "labels after upgrade closed not_planned (unfixed). helm#7542 leftover "
        "CHARTNAME is leftover template placeholder. helm#31285 leftover debug "
        "print. Not inventing refs."
    ),
    "job-0474": (
        "Factory starvation: go sumdb leftover unique vs 083/084 — leftover "
        "unauthenticated tree extension is specimen-084; leftover zip vs "
        "mod-only is specimen-083. No unique leftover-identity merged pair. "
        "Not inventing refs."
    ),
    "job-0475": (
        "Factory starvation: maven shade leftover identity not 096 — no merged "
        "pinned leftover-identity pair distinct from specimen-096 "
        "processorpath. Not inventing refs."
    ),
    "job-0476": (
        "Factory starvation: docker layer leftover unique vs 066/097 — "
        "buildkit#5789 leftover layers after retag closed without merged PR. "
        "066 is healthcheck timer; 097 is keep-git-dir cache key. Not inventing refs."
    ),
}


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


def packet_sbt(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: sbt/sbt
failing_ref: c491f035f832a62843d69364b55237dc29c99e7d
fixed_ref: 49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef
source_issue: https://github.com/sbt/sbt/issues/9195
source_pr: https://github.com/sbt/sbt/pull/9207
mechanism_tags:
  - leftover-extra-analysis
  - last-write-cache-vs-file-identity
  - zinc-analysis-gz-switch
ecosystem: sbt-zinc
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

sbt 2.x can keep leftover **extra zinc Analysis identity** after the analysis gz file under a cache path has switched. The leftover identity is the last-write Analysis still sitting in `MixedAnalyzingCompiler.staticCachedStore`, even though the current analysis-file identity (size + last-modified) is a different gz.

On failing_ref `c491f035f832a62843d69364b55237dc29c99e7d`, `Defaults.analysisStore` is:

```
private inline def analysisStore(inline analysisFile: TaskKey[File]): AnalysisStore =
  MixedAnalyzingCompiler.staticCachedStore(
    analysisFile = analysisFile.value.toPath,
    useTextAnalysis = false,
  )
```

That two-arg overload hard-codes `cacheLast = true`. Zinc then wraps the file store:

```
val store1 =
  if cacheLast then AnalysisStore.getCachedStore(fileStore)
  else fileStore
staticCache(analysisFile, AnalysisStore.getThreadSafeStore(store1))
```

`getCachedStore` keys only on last write through that store. It does not include file size or timestamp. sbt 2.x remote/local caching can replace the gz bytes under the same path. The extra leftover Analysis identity remains.

Public report (sbt/sbt#9195) scripted fixture `cache/discoveredMainClasses`:

```
scalaVersion := "2.13.18"
object Main { def main(args: Array[String]): Unit = () }

> checkDiscoveredMainClasses
# actual == Seq("example.Main")
$ copy-file src/main/scala/Main.scala tmp/Main.scala
$ delete src
-> checkDiscoveredMainClasses
$ copy-file tmp/Main.scala src/main/scala/Main.scala
> checkDiscoveredMainClasses
# expect success but failure
```

Workaround recorded on the issue: `cleanFull`.

Case A — first compile, analysis gz written through this store:
  last-write Analysis identity matches the file
  `discoveredMainClasses` is `Seq("example.Main")`
  no leftover extra Analysis

Case B — sbt 2.x cache restores a different gz under the same analysis path:
  leftover: extra last-write Analysis identity
  current file identity (size + mtime) is the restored gz
  last-write cache does not see the switch

Case C — delete `src`, then restore `Main.scala` (issue 9195):
  leftover extra Analysis identity from B (or from the prior write)
  `checkDiscoveredMainClasses` fails after restore
  not a missing-source case (sources are back)

Case D — `cleanFull` then compile:
  leftover Analysis cache dropped
  not this leftover (wipe, not last-write vs file identity)

The developer wants to know which identity case B/C actually used for zinc Analysis: leftover extra last-write Analysis (file identity ignored), current gz file identity (size+mtime), or omitted (no Analysis store at all).
""",
        observed="""# OBSERVED

Public sbt/sbt#9195 (closed 2026-05-11). PR 9207 merge `49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef` (parents `c491f035f832a62843d69364b55237dc29c99e7d` + `e69e23aae14240d2c6b63e2c5ff356ccc154e784`). Local sbt/zinc was not performed on this lab host.

Issue body: `discoveredMainClasses` after delete+restore of `src` expects success and fails. Notes `.triggeredBy(compile)` plus global cache. Workaround `cleanFull`.

PR body: MixedAnalyzingCompiler analysis cache caches using the last write, assuming all writing happens via it. That does not work with sbt 2.x caching where the gz file under the path can switch. Repair keys local analysis caching on file size and timestamp (caffeine), and calls zinc `staticCachedStore(..., cacheLast = false)`.

On failing_ref, `analysisStore` uses the two-arg zinc overload (`cacheLast = true`). Zinc `getCachedStore` is last-write. File size / last-modified are **not** part of that identity.

Not this packet: specimen-088 / specimen-104 (gradle configuration-cache leftover). specimen-075 (rustc incremental). specimen-078 (derived gocache). specimen-111 (tsbuildinfo leftover signature). No sbt specimen in 001-111.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref c491f035f832a62843d69364b55237dc29c99e7d
# main/src/main/scala/sbt/Defaults.scala analysisStore
# zinc MixedAnalyzingCompiler.staticCachedStore cacheLast=true

# public shape (sbt 2.x scripted cache/discoveredMainClasses):
# first checkDiscoveredMainClasses ok
# delete src; restore Main.scala
# leftover: extra last-write Analysis identity
# checkDiscoveredMainClasses fails
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""sbt/sbt
  main/src/main/scala/sbt/Defaults.scala
  main/src/main/scala/sbt/internal/BuildDef.scala
sbt/zinc
  zinc/src/main/scala/sbt/internal/inc/MixedAnalyzingCompiler.scala
""",
        source="""repository: sbt/sbt
issue: https://github.com/sbt/sbt/issues/9195
pr: https://github.com/sbt/sbt/pull/9207
failing_ref (merge first parent): c491f035f832a62843d69364b55237dc29c99e7d
fixed_ref (merge commit): 49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef
second_parent: e69e23aae14240d2c6b63e2c5ff356ccc154e784
merged_at: 2026-05-11T14:20:27Z
pr_author: eed3si9n
merged_by: eed3si9n
changed_files: main/src/main/scala/sbt/Defaults.scala, main/src/main/scala/sbt/internal/BuildDef.scala, project/Dependencies.scala, scripted tests
pr_title: [2.x] fix: Fixes cache restoration of incremental compilation state (Analysis)
scout_note: not specimen-088/104 gradle CC leftover. not 075 rustc incremental. Distinct leftover: extra last-write zinc Analysis identity vs current analysis-file identity (size+mtime) after gz switch. job-0469 unique vs 001-111 (no sbt).
""",
        answer_key="""KNOWN FIX (sealed): sbt/sbt PR 9207 merge 49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef.

failing_ref is merge first parent c491f035f832a62843d69364b55237dc29c99e7d.

analysisStore used MixedAnalyzingCompiler.staticCachedStore two-arg overload (cacheLast=true). Zinc getCachedStore kept leftover extra Analysis identity after sbt 2.x switched the gz under the same path.

PR repair: BuildDef.cachedAnalysisStore keys caffeine cache on VirtualFileRef + lastModified + sizeBytes; zinc staticCachedStore(..., cacheLast=false). previousCompile / compileTask / early analysis all go through that store.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (first compile last-write matches file vs leftover extra Analysis after gz switch vs delete+restore discoveredMainClasses fail vs cleanFull)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — last-write Analysis identity and analysis-file identity (size+mtime) are different objects; leftover extra Analysis blocked discoveredMainClasses
ecosystem: sbt / zinc
mechanism_family: leftover-extra-analysis, last-write-cache, omitted-file-identity

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "analysis_store_failing.scala": """# Reduced excerpt of Defaults.analysisStore + zinc staticCachedStore on failing_ref
# sbt main/src/main/scala/sbt/Defaults.scala
# c491f035f832a62843d69364b55237dc29c99e7d
# Last-write Analysis identity is the cache. File size/mtime are omitted.

  private inline def analysisStore(inline analysisFile: TaskKey[File]): AnalysisStore =
    MixedAnalyzingCompiler.staticCachedStore(
      analysisFile = analysisFile.value.toPath,
      useTextAnalysis = false,
    )

# zinc MixedAnalyzingCompiler.scala two-arg overload (cacheLast = true):

  def staticCachedStore(analysisFile: Path, useTextAnalysis: Boolean): AnalysisStore =
    staticCachedStore(
      analysisFile = analysisFile,
      useTextAnalysis = useTextAnalysis,
      useConsistent = false,
      cacheLast = true,
      mappers = ReadWriteMappers.getEmptyMappers(),
      reproducible = true,
      parallelism = Runtime.getRuntime.availableProcessors(),
    )

    val store1 =
      if cacheLast then AnalysisStore.getCachedStore(fileStore)
      else fileStore
    staticCache(analysisFile, AnalysisStore.getThreadSafeStore(store1))
""",
            "leftover_identity_split.txt": """Registry / fixture:
  sbt 2.x analysis gz path
  MixedAnalyzingCompiler.staticCachedStore cacheLast=true
  scripted cache/discoveredMainClasses

Case A (first compile, write through this store):
  last-write Analysis identity matches file
  no leftover extra Analysis

Case B (sbt 2.x cache restores a different gz under same path):
  leftover: extra last-write Analysis identity
  current file identity is size+mtime of restored gz

Case C (delete src then restore Main.scala):
  leftover extra Analysis identity
  checkDiscoveredMainClasses fails after restore

Case D (cleanFull then compile):
  leftover Analysis dropped
  not this leftover

Not this packet:
  gradle configuration-cache leftover (specimen-088 / specimen-104)
  rustc incremental (specimen-075)
  derived gocache (specimen-078)
  tsbuildinfo leftover signature (specimen-111)
""",
        },
    )


def packet_tf(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: hashicorp/terraform
failing_ref: dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3
fixed_ref: 28cb1307393a2a6a0d1600955e17cd585e1aa7b8
source_issue: none
source_pr: https://github.com/hashicorp/terraform/pull/37396
mechanism_tags:
  - leftover-identity-omitted-from-state
  - destroy-error-drops-identity
  - mark-only-update-drops-identity
ecosystem: terraform
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Terraform apply can drop leftover **resource identity** from state even when the provider still returned that identity (or the prior state still had it). Two apply paths copy value/private/status and omit `Identity`.

On failing_ref `dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3`, `NodeAbstractResourceInstance.apply` (`internal/terraform/node_resource_abstract_instance.go`):

Mark-only update (values equal, sensitivity marks differ; provider is not called):

```
if change.Action == plans.Update && eq && !marks.MarksEqual(beforePaths, afterPaths) {
    newState := &states.ResourceInstanceObject{
        CreateBeforeDestroy: state.CreateBeforeDestroy,
        Dependencies:        state.Dependencies,
        Private:             state.Private,
        Status:              state.Status,
        Value:               change.After,
    }
    return newState, diags
}
```

Destroy/apply error when the provider returns a non-null new value:

```
case diags.HasErrors() && !newVal.IsNull():
    newState := &states.ResourceInstanceObject{
        Status:              state.Status,
        Value:               newVal,
        Private:             resp.Private,
        CreateBeforeDestroy: createBeforeDestroy,
    }
    return newState, diags
```

The non-error success path already sets `Identity: resp.NewIdentity`. `testDiffFn` on that revision does not copy `PriorIdentity` into `PlannedIdentity`.

In-tree after the repair (not on failing_ref): `TestContext2Apply_errorDestroyWithIdentity` — destroy apply fails, provider returns `NewState` `{id:"baz"}` and `NewIdentity` `{id:"baz"}`, prior `IdentityJSON` was `{"id":"baz"}`; expects identity still present. `TestContext2Apply_SensitivityChangeWithIdentity` — mark-only update, prior `IdentityJSON` `{"id":"baz"}`; expects the same identity bytes after apply.

Case A — successful apply, non-null new value, no diagnostics:
  `Identity: resp.NewIdentity` written
  no leftover omitted identity

Case B — destroy apply errors, provider returns non-null `NewState` + `NewIdentity`:
  leftover: identity omitted from the new state object
  value/private/status kept
  prior IdentityJSON `{"id":"baz"}` is gone after encode

Case C — update where unmarked before==after and only sensitivity marks change:
  leftover: identity omitted (copy previous state, changing only Value)
  provider is not called
  prior IdentityJSON dropped

Case D — apply error and provider returns null new value:
  `state.DeepCopy()` returned
  not this leftover (prior identity kept via copy)

The developer wants to know which identity case B (and C) actually left in state after apply: leftover omitted identity (IdentityJSON absent), identity present (`{"id":"baz"}`), or typed null identity.
""",
        observed="""# OBSERVED

Public hashicorp/terraform PR 37396 (merged 2025-08-05). Squash `28cb1307393a2a6a0d1600955e17cd585e1aa7b8` (single parent `dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3`). Changelog: "Fixes resource identity being dropped from state in certain cases". Local terraform was not performed on this lab host.

PR body: two apply paths incorrectly remove resource identity from state. (1) Destroy errors when the provider returns a new non-null state: identity from the provider response is not included. (2) State values do not change during an update, but marks (sensitive) do: Terraform does not call the provider and identity is missing from the copied object.

On failing_ref, the mark-only update object has CreateBeforeDestroy / Dependencies / Private / Status / Value and no Identity field. The error-and-non-null object has Status / Value / Private / CreateBeforeDestroy and no Identity. The success non-null path already has Identity.

`change.AfterIdentity` / `resp.NewIdentity` assignment on those two paths is **not** on the failing revision.

Not this packet: specimen-081 leftover IdentityJSON vs nil identity schema on Decode (PR 37709). specimen-081 is encode/decode of leftover JSON against a nil schema. This packet is identity omitted from the apply-time state object while value remains.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3
# internal/terraform/node_resource_abstract_instance.go apply

# public shape (destroy error, provider returns NewIdentity):
# leftover: Identity omitted from new state object
# value still present
# IdentityJSON absent after encode

# public shape (mark-only sensitivity update):
# leftover: Identity omitted from copied state object
# provider not called
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""hashicorp/terraform
  internal/terraform/node_resource_abstract_instance.go
  internal/terraform/context_apply2_test.go
  internal/terraform/context_test.go
""",
        source="""repository: hashicorp/terraform
issue: none
pr: https://github.com/hashicorp/terraform/pull/37396
failing_ref (squash parent): dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3
fixed_ref (squash merge): 28cb1307393a2a6a0d1600955e17cd585e1aa7b8
merged_at: 2025-08-05T10:00:31Z
pr_author: dbanck
merged_by: dbanck
changed_files: internal/terraform/node_resource_abstract_instance.go, internal/terraform/context_apply2_test.go, internal/terraform/context_test.go, .changes/v1.13/BUG FIXES-20250804-162137.yaml
pr_title: Fix resource identity being dropped from state in certain cases
scout_note: not specimen-081 leftover IdentityJSON vs nil schema Decode. Distinct leftover: apply omits Identity from state object on destroy-error and mark-only update. job-0473 unique vs 081 tfident.
""",
        answer_key="""KNOWN FIX (sealed): hashicorp/terraform PR 37396 squash 28cb1307393a2a6a0d1600955e17cd585e1aa7b8.

failing_ref is squash parent dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3.

Mark-only update copied previous state and set only Value, omitting Identity. Destroy/apply error with non-null newVal built a new object without Identity even when the provider returned NewIdentity.

PR repair: mark-only path sets Identity: change.AfterIdentity. Error non-null path sets Identity: resp.NewIdentity. testDiffFn copies PriorIdentity to PlannedIdentity.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (success apply keeps identity vs destroy-error omits vs mark-only omits vs error-null DeepCopy keeps)
reproducibility: source-backed PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — value identity and resource identity are different objects; leftover omitted identity after apply while value remains
ecosystem: terraform / go
mechanism_family: leftover-identity-omitted, apply-drops-identity, mark-only-update

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "apply_omit_identity_failing.go": """// Reduced excerpt of NodeAbstractResourceInstance.apply on failing_ref
// internal/terraform/node_resource_abstract_instance.go
// dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3
// Mark-only update and destroy-error non-null paths omit Identity.

if change.Action == plans.Update && eq && !marks.MarksEqual(beforePaths, afterPaths) {
    newState := &states.ResourceInstanceObject{
        CreateBeforeDestroy: state.CreateBeforeDestroy,
        Dependencies:        state.Dependencies,
        Private:             state.Private,
        Status:              state.Status,
        Value:               change.After,
    }
    return newState, diags
}

case diags.HasErrors() && !newVal.IsNull():
    newState := &states.ResourceInstanceObject{
        Status:              state.Status,
        Value:               newVal,
        Private:             resp.Private,
        CreateBeforeDestroy: createBeforeDestroy,
    }
    return newState, diags

case !newVal.IsNull():
    newState := &states.ResourceInstanceObject{
        Status:              states.ObjectReady,
        Value:               newVal,
        Private:             resp.Private,
        CreateBeforeDestroy: createBeforeDestroy,
        Identity:            resp.NewIdentity,
    }
    return newState, diags
""",
            "leftover_identity_split.txt": """Registry / fixture:
  resource test_resource with identity schema {id}
  prior IdentityJSON {"id":"baz"}

Case A (successful apply, non-null, no error):
  Identity: resp.NewIdentity written
  no leftover omitted identity

Case B (destroy apply errors, provider returns NewState+NewIdentity):
  leftover: Identity omitted from new state object
  value still present
  IdentityJSON absent after encode

Case C (mark-only sensitivity update, values equal):
  leftover: Identity omitted from copied state object
  provider not called

Case D (apply error, provider returns null new value):
  state.DeepCopy()
  prior identity kept
  not this leftover

Not this packet:
  leftover IdentityJSON vs nil schema Decode (specimen-081)
""",
        },
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


def _note_jobs(state, sbt_id: str, tf_id: str) -> str:
    # Jobs 0469-0476 were CLAIMED then SKIP'd ~46s later (coordinator race).
    # Do not steal SKIP. Packets still land; R1 is enqueued.
    for jid, artifact in SKIP_STARVE.items():
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
        if job is None:
            continue
        if job.get("status") == "READY":
            job["status"] = "CLAIMED"
            job["worker"] = WORKER
            job["claimed_at"] = now_jst()
            from scheduler import complete

            complete(state, jid, result="skip", artifact=artifact)
        elif job.get("status") == "SKIP" and not (job.get("artifact") or "").startswith("Factory starvation"):
            job["artifact"] = artifact
    for jid, packed, reason in (
        (
            JOB_SBT,
            sbt_id,
            f"packed leftover extra zinc Analysis vs file identity as {sbt_id}; unique vs 001-111",
        ),
        (
            JOB_TF,
            tf_id,
            f"packed leftover identity omitted from apply state as {tf_id}; unique vs 081 Decode",
        ),
    ):
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
        if job is None:
            continue
        if job.get("status") == "READY":
            job["status"] = "CLAIMED"
            job["worker"] = WORKER
            job["claimed_at"] = now_jst()
            from scheduler import complete

            complete(
                state,
                jid,
                result="ok",
                artifact=f"specimens/{packed} {reason}",
            )
        elif job.get("status") in {"CLAIMED", "SKIP"}:
            job["artifact"] = f"specimens/{packed} {reason} (status was {job.get('status')})"
    claimed_r1 = [
        j
        for j in state.get("ready_jobs") or []
        if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
    ]
    if claimed_r1:
        return (
            "dream.sh not launched; READY_R1_DREAM already in flight: "
            + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
        )
    return f"dream.sh not launched from scout; READY_R1_DREAM enqueued trials={TRIAL_SBT},{TRIAL_TF}"


def _complete_and_enqueue(sbt_id: str, tf_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
        _register(
            state,
            sbt_id,
            TRIAL_SBT,
            "sbt leftover extra zinc Analysis identity vs file identity; not 088/104/075",
        )
        _register(
            state,
            tf_id,
            TRIAL_TF,
            "terraform leftover identity omitted from apply state; not 081 IdentityJSON vs nil schema",
        )
        note["reason"] = _note_jobs(state, sbt_id, tf_id)
        return (sbt_id, tf_id)

    with_state(fn)
    return note["reason"]


def main() -> None:
    sbt_id = _claim_id()
    tf_id = _claim_id()
    sbt_dest = SPECIMENS / sbt_id
    tf_dest = SPECIMENS / tf_id
    try:
        p1 = emit(packet_sbt(sbt_id))
        s1 = write_seed(SPECIMENS / sbt_id)
        p2 = emit(packet_tf(tf_id))
        s2 = write_seed(SPECIMENS / tf_id)
        update_index()
        launch_note = _complete_and_enqueue(sbt_id, tf_id)
        print(p1)
        print(s1)
        print(p2)
        print(s2)
        print(launch_note)
        print(f"ids={sbt_id},{tf_id} trials={TRIAL_SBT},{TRIAL_TF}")
        print(
            "SKIP starve: job-0470 poetry, job-0471 yarn, job-0472 helm, "
            "job-0474 go sumdb, job-0475 maven shade, job-0476 docker layer"
        )
    except Exception:
        for dest in (sbt_dest, tf_dest):
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
