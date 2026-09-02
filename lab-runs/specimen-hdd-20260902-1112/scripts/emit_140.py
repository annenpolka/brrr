#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 140.

Packed (unique vs 001-139; 075 not overwritten; not bazel#29298):
1) microsoft/rushstack#4400 / PR 4476: leftover rush build cache for a
   downstream phase after an upstream phase CLI flag / dependsOnEnvVars /
   dependsOnAdditionalFiles change because _getCacheIdAsync walked
   npm dependencyProjects, not the operation graph. Downstream cache
   identity omitted those upstream operation inputs.

SKIP (this tick; no unique leftover-identity pair):
- job-0596 nx leftover cache vs env/.env: #28576 PR 28741 CLOSED unmerged;
  #31067 leftover .env PR 32007 CLOSED; merged #35172 is warm-cache
  performance not leftover-identity. not inventing refs.
- job-0597 cmake leftover cache vs compiler: no merged leftover-identity pair.
- job-0598 vite leftover dep cache vs config: hits OPEN (9499/22303).
- job-0599 ccache leftover object vs compiler flags: hits OPEN (false-miss
  / coverage), no leftover-HIT omitted-key pair.
- job-0602 drizzle leftover query cache vs schema: #4677 closed without PR.
- job-0603 golangci leftover cache vs config: no merged leftover-identity pair.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 140
WORKER = "scout-coord-2003"
SKIP_JOBS = {
    "job-0596": (
        "skip nx leftover cache vs env/.env identity: #28576 PR 28741 CLOSED "
        "unmerged; #31067 leftover .env PR 32007 CLOSED; merged #35172 is "
        "warm-cache performance not leftover-identity. not inventing refs"
    ),
    "job-0597": (
        "skip cmake leftover cache vs compiler identity: no merged leftover-"
        "identity pair this tick. not inventing refs; not 127"
    ),
    "job-0598": (
        "skip vite leftover dep cache vs config identity: vite#9499/#22303 "
        "OPEN. not inventing refs; not 090"
    ),
    "job-0599": (
        "skip ccache leftover object vs compiler flags identity: no merged "
        "leftover-HIT omitted-key pair; hits OPEN. not inventing refs; not 075"
    ),
    "job-0602": (
        "skip drizzle leftover query cache vs schema identity: drizzle#4677 "
        "closed without PR. not inventing refs; not 041/043"
    ),
    "job-0603": (
        "skip golangci leftover cache vs config identity: no merged leftover-"
        "identity pair this tick. not inventing refs; not 132/133"
    ),
}
TRIAL = "hdd-rushop"
NEXT_SCOUTS = [
    (
        "public OSS: scons leftover signature vs env identity not 075",
        "unique scons leftover if pinned",
    ),
    (
        "public OSS: sccache leftover object vs CPATH identity if #2798 merges",
        "unique sccache leftover if pinned",
    ),
    (
        "public OSS: please leftover cache vs config identity not 075",
        "unique please leftover if pinned",
    ),
    (
        "public OSS: tox leftover venv vs extras identity not 067",
        "unique tox extras leftover if pinned pair",
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


def packet_rush(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: microsoft/rushstack
failing_ref: 300fcd107dea176ef503ffa073776bff47ee17a1
fixed_ref: 3530cb21a03927ec8b06072ee89a91466dc6beb3
source_issue: https://github.com/microsoft/rushstack/issues/4400
source_pr: https://github.com/microsoft/rushstack/pull/4476
mechanism_tags:
  - leftover-build-cache
  - omitted-operation-graph
  - project-deps-not-phase-deps
ecosystem: rush
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Rush `build` cache can keep the identity of a **previous downstream phase output** after an upstream phase CLI flag / `dependsOnEnvVars` / `dependsOnAdditionalFiles` should have been a different hash. `ProjectBuildCache._getCacheIdAsync` walks `projectToProcess.dependencyProjects` (npm project graph). The runtime operation graph is omitted, so `_phase:second` reuses leftover cache after `_phase:first` identity changed.

On failing_ref `300fcd107dea176ef503ffa073776bff47ee17a1`:

```
const projectsToProcess: Set<RushConfigurationProject> = new Set();
projectsToProcess.add(project);
for (const projectToProcess of projectsToProcess) {
  const projectState = await projectChangeAnalyzer._tryGetProjectStateHashAsync(...);
  projectStates.push(projectState);
  for (const dependency of projectToProcess.dependencyProjects) {
    projectsToProcess.add(dependency);
  }
}
```

Public report (microsoft/rushstack#4400). Two phases; `--some-flag-for-first` only on `_phase:first`; leftover `_phase:second` cache ID unchanged.

In-tree after the repair (not on failing_ref): cache hash computed in `CacheableOperationPlugin` `beforeExecuteOperations` from the runtime operation graph (upstream operation cache IDs included).

Case A — second `rush build` with unchanged flags/env/files:
  cache identity is current
  not leftover-after-upstream-phase-change

Case B — upstream phase flag/env/file flipped, leftover downstream cache:
  leftover: previous `_phase:second` outputs
  operation-graph inputs omitted (npm project deps only)
  downstream cache hit

Case C — empty cache / rebuild:
  fresh cache identity
  not leftover previous downstream phase

Case D — operation-graph cache IDs (post-repair shape, not on failing_ref):
  cache miss after upstream phase identity change
  not leftover previous downstream outputs

The developer wants to know which identity case B actually used for `_phase:second` after the upstream phase change: leftover previous-downstream results (operation graph omitted), current operation-graph identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public microsoft/rushstack#4400 (closed 2024-10-17). PR 4476 merge `3530cb21a03927ec8b06072ee89a91466dc6beb3` (parent `300fcd107dea176ef503ffa073776bff47ee17a1`). Local rush was not performed on this lab host.

Issue body: `dependsOnEnvVars`, `dependsOnAdditionalFiles`, and CLI parameters that affect some phases do not affect cache keys of dependent operations. Cache key computed from project dependencies, not operation dependencies.

On failing_ref, `_getCacheIdAsync` walks `dependencyProjects`. Runtime operation graph is **not** in that walk. PR 4476 moves hash computation onto the operation graph.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-134 moon leftover .env inputs. nx leftover .env (no merged leftover-identity pair this run).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 300fcd107dea176ef503ffa073776bff47ee17a1
# libraries/rush-lib/src/logic/buildCache/ProjectBuildCache.ts _getCacheIdAsync

# public shape:
# leftover _phase:second cache after _phase:first CLI/env/file change
# cache ID walks npm dependencyProjects; operation graph omitted
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""microsoft/rushstack
  libraries/rush-lib/src/logic/buildCache/ProjectBuildCache.ts
  libraries/rush-lib/src/logic/operations/CacheableOperationPlugin.ts
  A/config/rush-project.json
""",
        source="""repository: microsoft/rushstack
issue: https://github.com/microsoft/rushstack/issues/4400
pr: https://github.com/microsoft/rushstack/pull/4476
failing_ref (parent of merge on main): 300fcd107dea176ef503ffa073776bff47ee17a1
fixed_ref (operation-graph cache hashes): 3530cb21a03927ec8b06072ee89a91466dc6beb3
merged_at: 2024-10-17T20:13:49Z
pr_author: dmichon-msft
merged_by: iclanton
changed_files: ProjectBuildCache.ts, CacheableOperationPlugin.ts, InputsSnapshot.ts, ProjectChangeAnalyzer.ts, others
pr_title: [rush] Split ProjectChangeAnalyzer, fix build cache hashes
scout_note: not 136 pants process cache. not 134 moon .env. Distinct leftover: npm project-dep walk omits operation-graph inputs so leftover downstream phase cache stayed current. unique vs 001-139.
""",
        answer_key="""KNOWN FIX (sealed): microsoft/rushstack PR 4476 merge 3530cb21a03927ec8b06072ee89a91466dc6beb3.

failing_ref is parent 300fcd107dea176ef503ffa073776bff47ee17a1.

_getCacheIdAsync walked npm dependencyProjects and omitted the runtime operation graph, so leftover downstream phase cache after upstream CLI/env/file change stayed current.

PR repair: compute cache hashes in CacheableOperationPlugin beforeExecuteOperations from the operation graph.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged flags vs leftover downstream cache after upstream phase identity vs empty cache vs operation-graph hashes)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — project graph and operation graph are different identities; downstream cache omitted upstream phase inputs
ecosystem: rush / phased build cache
mechanism_family: leftover-build-cache, omitted-operation-graph, project-deps-not-phase-deps

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "get_cache_id_failing.ts": """// Reduced excerpt of ProjectBuildCache._getCacheIdAsync on failing_ref
// libraries/rush-lib/src/logic/buildCache/ProjectBuildCache.ts
// 300fcd107dea176ef503ffa073776bff47ee17a1
// Walks npm dependencyProjects. Operation graph omitted.

const projectStates: string[] = [];
const projectsToProcess: Set<RushConfigurationProject> = new Set();
projectsToProcess.add(project);

for (const projectToProcess of projectsToProcess) {
  const projectState: string | undefined = await projectChangeAnalyzer._tryGetProjectStateHashAsync(
    projectToProcess,
    terminal
  );
  if (!projectState) {
    return undefined;
  } else {
    projectStates.push(projectState);
    for (const dependency of projectToProcess.dependencyProjects) {
      projectsToProcess.add(dependency);
    }
  }
}
// no walk of operation.dependencies / upstream phase cache IDs
""",
            "leftover_identity_split.txt": """Registry / fixture:
  two phases _phase:first -> _phase:second
  leftover downstream cache after upstream CLI/env/file change

Case A (second rush build, same flags):
  current cache identity
  not leftover-after-upstream-phase-change

Case B (upstream phase flag/env/file flipped, leftover downstream cache):
  leftover: previous _phase:second outputs
  operation-graph inputs omitted (npm project deps only)
  downstream cache hit

Case C (empty cache / rebuild):
  fresh cache identity
  not leftover previous downstream phase

Case D (operation-graph cache IDs):
  cache miss after upstream phase identity change
  not leftover previous downstream outputs

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  moon leftover .env task inputs (specimen-134)
  nx leftover .env (no merged leftover-identity pair this run)
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
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") == "READY":
                _claim_job(state, jid, WORKER)
                complete(state, jid, result="skip", artifact=artifact)
            elif job.get("status") == "CLAIMED":
                old = job.get("worker")
                if old in {None, WORKER} or str(old).startswith("scout-coord-"):
                    complete(state, jid, result="skip", artifact=artifact)
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
                priority_reason=(
                    "rush leftover downstream phase cache omits operation graph; "
                    "not 134/136"
                ),
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
        path = emit(packet_rush(spec_id))
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
