#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 141.

Packed (unique vs 001-140; 075 not overwritten; not bazel#29298):
1) spack/spack#51553 / PR 51931: leftover concretizer cache after a
   package.py change because the cache stored fully-finalized specs
   (hashes baked in) and omitted re-running post-processing /
   _finalize_concretization on cache hit. Distinct from 136 pants
   process cache / 140 rush operation graph.

SKIP (this tick; no unique leftover-identity pair):
- job-0608 scons leftover signature vs env: #1521 is extra rebuilds
  after cache hits (false miss), tigris-era no pinned GitHub PR.
- job-0609 sccache leftover CPATH: #2798 still OPEN, PR 2799 OPEN.
- job-0610 please leftover cache vs config: #2978 OPEN extra-hash;
  #677 exclude-vars not leftover-identity.
- job-0611 tox leftover venv vs extras: #793 closed "fixed in tox 4"
  without PR; #1105 extras ignored at install, not leftover cache.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 141
WORKER = "scout-coord-2016"
TRIAL = "hdd-spackconc"
SKIP_JOBS = {
    "job-0608": (
        "skip scons leftover signature vs env identity: scons#1521 is extra "
        "rebuilds after cache hits (false miss), tigris-era no pinned GitHub "
        "PR. not inventing refs; not 075"
    ),
    "job-0609": (
        "skip sccache leftover object vs CPATH identity: sccache#2798 still "
        "OPEN, PR 2799 OPEN. not inventing refs"
    ),
    "job-0610": (
        "skip please leftover cache vs config identity: please#2978 OPEN "
        "(visibility extra-hash); #677 exclude-vars not leftover-identity. "
        "not inventing refs; not 075"
    ),
    "job-0611": (
        "skip tox leftover venv vs extras identity: tox#793 closed without "
        "PR (tox 4 rewrite); #1105 extras ignored at install not leftover "
        "cache. not inventing refs; not 067"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: ansible leftover inventory cache vs file identity not 136",
        "unique ansible leftover if pinned",
    ),
    (
        "public OSS: skaffold leftover artifact cache vs input identity not 097",
        "unique skaffold leftover if pinned",
    ),
    (
        "public OSS: terragrunt leftover cache vs source identity not 118",
        "unique terragrunt leftover if pinned",
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


def packet_spack(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: spack/spack
failing_ref: 194e0da658190ae0219bd9576bd7ce1099ce1e0b
fixed_ref: 525775aa9b3e9500f661508456902c7634c23655
source_issue: https://github.com/spack/spack/issues/51553
source_pr: https://github.com/spack/spack/pull/51931
mechanism_tags:
  - leftover-concretizer-cache
  - omitted-package-hash-recompute
  - post-finalization-store
ecosystem: spack
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Spack `concretizer:concretization_cache` can keep the identity of a **previous spec hash** after a `package.py` change should have been a different dag_hash. The cache stores fully-finalized specs (hashes baked in). On a cache hit, `_finalize_concretization` / package-hash post-processing is omitted, so leftover `mo2ogtq` is reused after commenting `install()` in bzip2.

On failing_ref `194e0da658190ae0219bd9576bd7ce1099ce1e0b`:

```
cache_key = self._make_cache_key(problem, control_file_paths)
if conc_cache_enabled and self._conc_cache:
    result, concretization_stats = self._conc_cache.fetch(cache_key)
if not result:
    result = self._run_clingo(...)
    self._conc_cache.store(cache_key, result, self.control.statistics)
# later, on the stored Result:
root._finalize_concretization()
```

`_make_cache_key` hashes ASP problem + control files. Cached `Result.to_dict()` already has concrete hashes. Cache hit skips re-finalization.

Public report (spack/spack#51553). `spack spec -l bzip2` with cache on; edit package.py; leftover previous hash until cache disabled.

In-tree after the repair (not on failing_ref): cache write immediately after solve, before finalization; cache hits re-run `post_process_concretization_result()`.

Case A — second `spack spec` with unchanged package.py:
  cache identity is current
  not leftover-after-package-change

Case B — package.py flipped, leftover concretizer cache:
  leftover: previous dag_hash / fully-finalized spec
  package-hash recompute omitted on cache hit
  same `mo2ogtq`

Case C — cache disabled / `spack clean -m`:
  fresh hash identity
  not leftover previous spec

Case D — cache stores pre-finalization, re-finalize on hit (post-repair shape, not on failing_ref):
  cache miss / new hash after package.py change
  not leftover previous dag_hash

The developer wants to know which identity case B actually used for the spec hash after the package.py change: leftover previous-finalized results (re-finalization omitted), current package identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public spack/spack#51553 (closed 2026-06-16). PR 51931 merge `525775aa9b3e9500f661508456902c7634c23655` (parent `194e0da658190ae0219bd9576bd7ce1099ce1e0b`). Local spack was not performed on this lab host.

Issue body: concretizer cache returns previous bzip2 hash after package.py install() comment; disabling the cache yields a new hash.

On failing_ref, cache stores the Result after the solve and later finalizes hashes into that object. Cache hits reuse leftover finalized hashes. PR 51931 moves the store before finalization and re-runs post-processing on hits.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-140 rush leftover downstream phase vs operation graph.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 194e0da658190ae0219bd9576bd7ce1099ce1e0b
# lib/spack/spack/solver/asp.py PyclingoDriver cache store / _make_cache_key

# public shape:
# leftover concretizer cache after package.py change
# fully-finalized spec hashes stored; re-finalization omitted on hit
# spack spec -l bzip2 keeps previous dag_hash until cache off
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""spack/spack
  lib/spack/spack/solver/asp.py
  repos/spack_repo/builtin/packages/bzip2/package.py
""",
        source="""repository: spack/spack
issue: https://github.com/spack/spack/issues/51553
pr: https://github.com/spack/spack/pull/51931
failing_ref (parent of merge on develop): 194e0da658190ae0219bd9576bd7ce1099ce1e0b
fixed_ref (cache after solve, re-finalize on hit): 525775aa9b3e9500f661508456902c7634c23655
merged_at: 2026-05-29T07:23:46Z
pr_author: tgamblin
merged_by: tgamblin
changed_files: lib/spack/spack/solver/asp.py, lib/spack/spack/spec.py, tests, concretizer.yaml
pr_title: solver: cache concretization results immediately after solve
scout_note: not 136 pants process cache. not 140 rush operation graph. Distinct leftover: fully-finalized spec hashes stored so leftover dag_hash after package.py change stayed current. unique vs 001-140.
""",
        answer_key="""KNOWN FIX (sealed): spack/spack PR 51931 merge 525775aa9b3e9500f661508456902c7634c23655.

failing_ref is parent 194e0da658190ae0219bd9576bd7ce1099ce1e0b.

Concretization cache stored fully-finalized specs and omitted re-running _finalize_concretization on cache hit, so leftover dag_hash after package.py change stayed current.

PR repair: store immediately after solve, before finalization; re-run post_process_concretization_result on cache hits.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged package.py vs leftover cache after edit vs cache off vs re-finalize on hit)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — ASP problem key and package.py hash are different identities; leftover finalized hashes stayed current
ecosystem: spack / concretizer cache
mechanism_family: leftover-concretizer-cache, omitted-package-hash-recompute, post-finalization-store

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "asp_cache_failing.py": """# Reduced excerpt of PyclingoDriver solve cache on failing_ref
# lib/spack/spack/solver/asp.py
# 194e0da658190ae0219bd9576bd7ce1099ce1e0b
# Stores Result after clingo; later _finalize_concretization bakes hashes.
# Cache hit reuses leftover finalized hashes. package.py recompute omitted.

cache_key = self._make_cache_key(problem, control_file_paths)
result, concretization_stats = None, None
if conc_cache_enabled and self._conc_cache:
    result, concretization_stats = self._conc_cache.fetch(cache_key)
if not result:
    result = self._run_clingo(specs, setup, problem_repr, control_file_paths, timer)
    self._conc_cache.store(cache_key, result, self.control.statistics)
# later on Result specs:
#   root._finalize_concretization()
# cache hit skips that recompute
""",
            "leftover_identity_split.txt": """Registry / fixture:
  concretizer:concretization_cache enable
  leftover spec hash after package.py change

Case A (second spack spec, same package.py):
  current cache identity
  not leftover-after-package-change

Case B (package.py flipped, leftover cache):
  leftover: previous dag_hash / fully-finalized spec
  package-hash recompute omitted on cache hit
  same mo2ogtq

Case C (cache disabled / spack clean -m):
  fresh hash identity
  not leftover previous spec

Case D (store before finalization, re-finalize on hit):
  new hash after package.py change
  not leftover previous dag_hash

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  rush leftover downstream phase cache (specimen-140)
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
                    "spack leftover concretizer cache omits package-hash recompute; "
                    "not 136/140"
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
        path = emit(packet_spack(spec_id))
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
