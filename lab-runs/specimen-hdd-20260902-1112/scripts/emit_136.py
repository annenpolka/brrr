#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 136.

Packed (unique vs 001-135; 075 not overwritten; not bazel#29298):
1) pantsbuild/pants#16963 / PR 17017: leftover vcs_version after
   amend/commit because generate_python_from_setuptools_scm always
   reruns (MaybeGitWorktree uncacheable) but VenvPexProcess for
   setuptools_scm was memoized — git hash omitted from process cache
   identity. Distinct from 075 rustc incremental; not skipped #23645
   env-without-cache-key (OPEN).

SKIP (this tick; no unique leftover-identity pair):
- job-0586 buf leftover generated vs proto: no merged leftover-identity
  pair; buf#423 leftover buf.lock after dep swap is expected transitive
  deps, no PR. not inventing refs.
- job-0587 go generate leftover vs source: no merged leftover-identity
  pair distinct from 084/103; golang/go#36068 OPEN. not inventing refs.
- job-0588 prisma leftover generated client vs schema: prisma/prisma
  unsearchable / rate-limited; no merged leftover-identity pair vs
  041/043. not inventing refs.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 136
WORKER = "scout-coord-1940"
JOB_PACK = "job-0585"
TRIAL = "hdd-pantvcs"
SKIP_JOBS = {
    "job-0586": (
        "skip buf leftover generated vs proto identity: no merged leftover-"
        "identity pair this tick; buf#423 leftover buf.lock after dep swap "
        "is expected transitive deps, no PR. not inventing refs; not 041/043"
    ),
    "job-0587": (
        "skip go generate leftover vs source identity: no merged leftover-"
        "identity pair distinct from 084/103; golang/go#36068 OPEN. not "
        "inventing refs"
    ),
    "job-0588": (
        "skip prisma leftover generated client vs schema identity: "
        "prisma/prisma unsearchable this tick; no merged leftover-identity "
        "pair distinct from 041/043. not inventing refs"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: nx leftover cache vs env/.env identity not 134",
        "unique nx env leftover if pinned merged pair",
    ),
    (
        "public OSS: cmake leftover cache vs compiler identity not 127",
        "unique cmake compiler leftover if pinned",
    ),
    (
        "public OSS: vite leftover dep cache vs config identity not 090",
        "unique vite cache leftover if pinned",
    ),
    (
        "public OSS: ccache leftover object vs compiler flags identity not 075",
        "unique ccache leftover if pinned",
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


def packet_pants(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: pantsbuild/pants
failing_ref: 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
fixed_ref: 510f1755680d23c3d6c68815ae77ad4a4f836021
source_issue: https://github.com/pantsbuild/pants/issues/16963
source_pr: https://github.com/pantsbuild/pants/pull/17017
mechanism_tags:
  - leftover-process-cache
  - omitted-git-hash-identity
  - vcs-version-setuptools-scm
ecosystem: pants
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Pants `vcs_version` / `export-codegen` can keep the identity of a **previous git describe** after an amend or a new commit should have been a different hash. `generate_python_from_setuptools_scm` always reruns because `MaybeGitWorktree` is uncacheable. The child `VenvPexProcess` that runs setuptools_scm was still memoized. Git hash is omitted from that process cache identity.

On failing_ref `02fa93e2947789cf1f9f8c025e7ceaca01169ef2`:

```
result = await Get(
    ProcessResult,
    VenvPexProcess(
        setuptools_scm_pex,
        argv=argv,
        input_digest=input_digest,
        description=f"Run setuptools_scm for {request.protocol_target.address.spec}",
        level=LogLevel.INFO,
    ),
)
```

`from pants.engine.process import ProcessResult` — no `ProcessCacheScope`. `argv` is `--root` worktree path plus synthetic toml. `input_digest` is that toml only. Git state is not in the process key.

Public report (pantsbuild/pants#16963). `vcs_version(generate_to=..., template=...)`; `./pants export-codegen`; amend or commit; leftover previous `some-tag.dev1+g1bd665ffd` until `rm -rf ~/.cache/pants`.

In-tree after the repair (not on failing_ref): `cache_scope=ProcessCacheScope.PER_SESSION` on that `VenvPexProcess`.

Case A — second `export-codegen` with unchanged HEAD:
  cache identity is current
  not leftover-after-git-change

Case B — amend or new commit, leftover process cache:
  leftover: previous setuptools_scm stdout / generated version module
  git hash omitted from VenvPexProcess identity
  enclosing rule reran; child process reused

Case C — `rm -rf ~/.cache/pants` then export-codegen:
  fresh process identity
  not leftover previous git describe

Case D — process cache scoped to the session (post-repair shape, not on failing_ref):
  cache miss after git change
  not leftover previous version string

The developer wants to know which identity case B actually used for the generated version after the amend/commit: leftover previous-git-describe results (git hash omitted from process key), current git identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public pantsbuild/pants#16963 (closed 2022-09-27). PR 17017 merge `510f1755680d23c3d6c68815ae77ad4a4f836021` (parent `02fa93e2947789cf1f9f8c025e7ceaca01169ef2`). Local pants was not performed on this lab host.

Issue body: generated version string cached and not invalidated after amend/commit; deleting `~/.cache/pants` restores the current git describe. Maintainer: MaybeGitWorktree is uncacheable so the enclosing rule always runs; the underlying setuptools_scm process was still memoized.

On failing_ref, `VenvPexProcess` has no `cache_scope`. `ProcessCacheScope` is **not** imported on the failing revision. It is added by PR 17017.

Not this packet: specimen-075 rustc incremental false-green / next-solver anon-task. pants#23645 leftover process cache vs env is still OPEN (env without cache key). pants#18334 is process metadata, not leftover cache identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
# src/python/pants/backend/python/util_rules/vcs_versioning.py
# generate_python_from_setuptools_scm VenvPexProcess

# public shape:
# leftover generated version after amend/commit
# git hash omitted from process cache identity
# enclosing MaybeGitWorktree rule reruns; child process reused
# until ~/.cache/pants deleted
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""pantsbuild/pants
  src/python/pants/backend/python/util_rules/vcs_versioning.py
  ~/.cache/pants
""",
        source="""repository: pantsbuild/pants
issue: https://github.com/pantsbuild/pants/issues/16963
pr: https://github.com/pantsbuild/pants/pull/17017
failing_ref (parent of merge on main): 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
fixed_ref (PER_SESSION cache_scope on setuptools_scm VenvPexProcess): 510f1755680d23c3d6c68815ae77ad4a4f836021
merged_at: 2022-09-27T15:33:34Z
pr_author: benjyw
merged_by: benjyw
changed_files: src/python/pants/backend/python/util_rules/vcs_versioning.py
pr_title: Don't cache VCS version outside the current pants session.
scout_note: not 075 rustc incremental. not skipped #23645 env-without-cache-key OPEN. Distinct leftover: git hash omitted from VenvPexProcess identity so leftover setuptools_scm stdout stayed current after amend/commit. job-0585 unique vs 001-135.
""",
        answer_key="""KNOWN FIX (sealed): pantsbuild/pants PR 17017 merge 510f1755680d23c3d6c68815ae77ad4a4f836021.

failing_ref is parent 02fa93e2947789cf1f9f8c025e7ceaca01169ef2.

VenvPexProcess for setuptools_scm was memoized with git hash omitted from the process cache identity, so leftover generated version after amend/commit kept previous git describe even though MaybeGitWorktree made the enclosing rule uncacheable.

PR repair: import ProcessCacheScope and set cache_scope=ProcessCacheScope.PER_SESSION on that VenvPexProcess.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged HEAD vs leftover process cache after amend/commit vs cache dir deleted vs PER_SESSION)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — uncacheable enclosing rule and memoized child process are different identities; git hash omitted so leftover setuptools_scm stdout stayed current
ecosystem: pants / vcs_version process cache
mechanism_family: leftover-process-cache, omitted-git-hash-identity, vcs-version-setuptools-scm

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "vcs_versioning_failing.py": """# Reduced excerpt of generate_python_from_setuptools_scm on failing_ref
# src/python/pants/backend/python/util_rules/vcs_versioning.py
# 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
# VenvPexProcess has no cache_scope. Git hash omitted from process identity.

from pants.engine.process import ProcessResult
from pants.vcs.git import GitWorktreeRequest, MaybeGitWorktree

@rule
async def generate_python_from_setuptools_scm(
    request: GeneratePythonFromSetuptoolsSCMRequest,
    setuptools_scm: SetuptoolsSCM,
) -> GeneratedSources:
    # A GitWorktreeRequest is uncacheable, so this enclosing rule will run every time its result
    # is needed, meaning it will always return a result based on the current underlying git state.
    maybe_git_worktree = await Get(MaybeGitWorktree, GitWorktreeRequest())
    argv = ["--root", str(maybe_git_worktree.git_worktree.worktree), "--config", config_path]
    result = await Get(
        ProcessResult,
        VenvPexProcess(
            setuptools_scm_pex,
            argv=argv,
            input_digest=input_digest,
            description=f"Run setuptools_scm for {request.protocol_target.address.spec}",
            level=LogLevel.INFO,
            # no cache_scope=ProcessCacheScope.PER_SESSION
        ),
    )
    version = result.stdout.decode().strip()
""",
            "leftover_identity_split.txt": """Registry / fixture:
  vcs_version generate_to template
  leftover process cache after amend/commit

Case A (second export-codegen, same HEAD):
  current cache identity
  not leftover-after-git-change

Case B (amend or new commit, leftover process cache):
  leftover: previous setuptools_scm stdout / generated version module
  git hash omitted from VenvPexProcess identity
  enclosing MaybeGitWorktree rule reran; child process reused

Case C (rm -rf ~/.cache/pants):
  fresh process identity
  not leftover previous git describe

Case D (PER_SESSION cache_scope):
  cache miss after git change
  not leftover previous version string

Not this packet:
  rustc incremental false-green (specimen-075)
  pants leftover process cache vs env (pants#23645 OPEN)
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
        workers = state.setdefault("workers", [])
        rec = next((w for w in workers if w.get("id") == worker), None)
        if rec is None:
            workers.append({"id": worker, "status": "active", "job": job_id})
        else:
            rec["status"] = "active"
            rec["job"] = job_id
        old_rec = next((w for w in workers if w.get("id") == old), None)
        if old_rec is not None and old not in {None, worker}:
            if old_rec.get("job") == job_id:
                old_rec["status"] = "vacant"
                old_rec["job"] = None
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
        _claim_job(state, JOB_PACK, WORKER)
        job = next((j for j in state["ready_jobs"] if j["id"] == JOB_PACK), None)
        if job and job.get("status") == "CLAIMED" and job.get("worker") == WORKER:
            complete(state, JOB_PACK, artifact=f"specimens/{spec_id} {TRIAL}")
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
            elif job.get("status") in {"DONE", "SKIP"}:
                pass
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
                    "pants leftover vcs_version process cache omits git hash; "
                    "not 075 / not #23645 OPEN"
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
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if claimed_r1:
            note["reason"] = (
                "READY_R1_DREAM enqueued trial="
                + TRIAL
                + "; in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        else:
            note["reason"] = f"READY_R1_DREAM enqueued trial={TRIAL} specimen={spec_id}"
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_pants(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(launch_note)
        print(f"ids={spec_id} trial={TRIAL}")
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
