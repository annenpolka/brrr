#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 148.

Packed (unique vs 001-147; 075 not overwritten; not bazel#29298):
1) job-0637 containers/buildah#4522 / PR 4526:
   leftover RUN --mount=from=stage layer after the source stage was
   rebuilt, because cache lookup did not record whether the mounted
   stage actually executed this build (DidExecute omitted).

Did not steal scout-leftover-2119 jobs 0634-0636 (conan/nomad/dagger).
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 148
WORKER = "scout-coord-2126"
TRIAL = "hdd-budmount"
PACK_JOB = "job-0637"
NEXT_SCOUTS = [
    (
        "public OSS: kaniko leftover snapshot vs digest identity not 066/148",
        "unique kaniko leftover if pinned",
    ),
    (
        "public OSS: buildkit leftover mount-from-stage if not 148",
        "unique buildkit leftover if pinned distinct from 148",
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


def packet_buildah(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: containers/buildah
failing_ref: 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4
fixed_ref: 3f805bcd8cd2fa522d6d2fd9ecfacf71da6aa5f9
source_issue: https://github.com/containers/buildah/issues/4522
source_pr: https://github.com/containers/buildah/pull/4526
mechanism_tags:
  - leftover-mount-stage
  - omitted-did-execute
  - run-mount-from-stage-cache
ecosystem: buildah
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Buildah `RUN --mount=type=bind,from=dependencies` can keep the identity of a **previous mounted stage** after that source stage was rebuilt and the copied file should have been different. The RUN layer is reused from cache. The mount-stage map stores `MountPoint` only. Whether the source stage actually executed this build is not part of cache identity.

On failing_ref `4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4`:

```
if otherStage, ok := s.executor.stages[from]; ok && otherStage.index < s.index {
    stageMountPoints[from] = internal.StageMountDetails{IsStage: true, MountPoint: otherStage.mountPoint}
}
// later: cache lookup for this RUN proceeds even if otherStage was rebuilt
```

`StageMountDetails` has `IsStage` and `MountPoint` only. `DidExecute` does not exist.

Public report (containers/buildah#4522). First stage writes `/build/version` `v1`; second stage `RUN --mount=from=dependencies` copies it. Change `v1` to `v2`; second build still prints `Using cache` for the RUN --mount layer and the image still contains leftover `v1`.

In-tree after the repair (not on failing_ref): `DidExecute` on `StageMountDetails` / `StageExecutor`; if any mounted stage `DidExecute`, `avoidLookingCache = true`.

Case A — second build, source stage unchanged:
  cache identity is current
  not leftover-after-source-stage-change

Case B — source stage rebuilt, leftover RUN --mount cache:
  leftover: previous `/version` / previous mounted stage
  DidExecute omitted from cache identity
  `Using cache` on the copy step

Case C — `--no-cache` / `--layers=false`:
  fresh stage identity
  not leftover previous mount

Case D — avoid cache when mounted stage DidExecute (post-repair shape, not on failing_ref):
  new `/version` after source stage change
  not leftover previous mount

The developer wants to know which identity case B actually used for the RUN --mount layer after the source stage change: leftover previous-cache layer (DidExecute omitted), current mounted-stage identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public containers/buildah#4522 (closed 2023-01-18). PR 4526 merge `3f805bcd8cd2fa522d6d2fd9ecfacf71da6aa5f9` (first parent `4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4`). Local buildah was not performed on this lab host.

Issue body: RUN --mount=from=otherstage reused from cache even though otherstage changed; resulting image still prints leftover `v1`.

On failing_ref, `runStageMountPoints` records only MountPoint. Cache lookup for the RUN step does not know the source stage was freshly executed.

Not this packet: specimen-066 moby leftover. specimen-144 skaffold leftover remote digest. specimen-097 buildkit leftover git-dir cache key omitting ref.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4
# imagebuildah/stage_executor.go runStageMountPoints / Execute cache lookup

# public shape:
# leftover RUN --mount layer after source stage rebuilt
# StageMountDetails has MountPoint only; DidExecute omitted
# --no-cache yields the new version file
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""containers/buildah
  imagebuildah/stage_executor.go
  internal/types.go
""",
        source="""repository: containers/buildah
issue: https://github.com/containers/buildah/issues/4522
pr: https://github.com/containers/buildah/pull/4526
failing_ref (first parent of merge): 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4
fixed_ref (DidExecute avoidLookingCache): 3f805bcd8cd2fa522d6d2fd9ecfacf71da6aa5f9
merged_at: 2023-01-18T13:38:19Z
pr_author: flouthoc
merged_by: openshift-merge-robot
changed_files: imagebuildah/stage_executor.go, internal/types.go, tests/bud.bats
pr_title: stage_executor: while mounting stages make sure freshly built stage is used
scout_note: not 066 moby / not 144 skaffold / not 097 buildkit git-dir. leftover RUN --mount from-stage after source rebuilt. unique vs 001-147.
""",
        answer_key="""KNOWN FIX (sealed): containers/buildah PR 4526 merge 3f805bcd8cd2fa522d6d2fd9ecfacf71da6aa5f9.

failing_ref is first parent 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4.

RUN --mount=from=stage reused leftover previous layer after the source stage was rebuilt. StageMountDetails stored MountPoint only; whether that stage executed this build was omitted from cache identity.

PR repair: DidExecute on StageMountDetails; if any mounted stage DidExecute, avoidLookingCache.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged source stage vs leftover RUN --mount after rebuild vs --no-cache vs DidExecute avoid cache)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — mountpoint path and whether the source stage executed this build are different identities; leftover RUN layer stayed current
ecosystem: buildah / layer cache
mechanism_family: leftover-mount-stage, omitted-did-execute, run-mount-from-stage-cache

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "stage_mount_failing.go": """// Reduced excerpt of RUN --mount from-stage cache on failing_ref
// imagebuildah/stage_executor.go
// 4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4
// StageMountDetails has MountPoint only. DidExecute omitted.
// leftover RUN --mount cache after source stage rebuilt.

if otherStage, ok := s.executor.stages[from]; ok && otherStage.index < s.index {
	stageMountPoints[from] = internal.StageMountDetails{IsStage: true, MountPoint: otherStage.mountPoint}
}
// cache lookup for this RUN proceeds even if otherStage was rebuilt
""",
            "leftover_identity_split.txt": """Registry / fixture:
  buildah --layers RUN --mount=from=stage
  leftover /version after source stage rebuilt

Case A (second build, source stage unchanged):
  current cache identity
  not leftover-after-source-stage-change

Case B (source stage rebuilt, leftover RUN --mount):
  leftover: previous /version
  DidExecute omitted
  Using cache on the copy step

Case C (--no-cache):
  fresh stage identity
  not leftover previous mount

Case D (avoid cache when mounted stage DidExecute):
  new /version after source change
  not leftover previous mount

Not this packet:
  moby leftover (specimen-066)
  skaffold leftover remote digest (specimen-144)
  buildkit leftover git-dir cache key omitting ref (specimen-097)
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
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
        _claim_job(state, PACK_JOB, WORKER)
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == PACK_JOB), None)
        if job is not None and job.get("status") in {"READY", "CLAIMED"}:
            complete(state, PACK_JOB, result="ok", artifact=f"specimens/{spec_id}")
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
                input_ref=f"seeds/{spec_id}.md trial={TRIAL}",
                expected_output="0001-dreamer.md",
                kill_condition="15m",
                estimated_cost="r1",
                priority_reason="buildah leftover RUN --mount from-stage omits DidExecute; not 066/144/097",
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
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
        note["reason"] = f"READY_R1_DREAM enqueued trial={TRIAL} specimen={spec_id}"
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_buildah(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(launch_note)
        print(f"ids={spec_id} trial={TRIAL} worker={WORKER} at={now_jst()}")
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
