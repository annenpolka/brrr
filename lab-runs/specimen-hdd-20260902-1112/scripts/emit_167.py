#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 167+.

Packed (unique vs 001-166; 075 not overwritten; not bazel#29298):
1) swc-project/swc#12166:
   leftover optimizer env replacements after a second compile with a
   different explicit `globals.envs` map, because GlobalPassOption::build
   keyed the process-wide DashMap by `self.vars` and omitted the envs map.

SKIP claimed jobs without a matching leftover-HIT pair this tick.
"""
from __future__ import annotations

import os
import subprocess

from compile_seed import write_seed
from emit_specimen import emit
from paths import HDD_ROOT, RUN_DIR, SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 167
WORKER = "scout-coord-2238"
SKIP_JOBS = {
    "job-0701": (
        "skip swc leftover cache vs moved file: no merged leftover-HIT after-move "
        "pair this tick. packed swc#12166 omitted-envs cache key instead (not "
        "moved-file). not 090/156"
    ),
    "job-0722": (
        "skip biome leftover module graph vs close eviction: same PR 11409 as "
        "specimen-166 files-map; not a unique leftover-HIT this tick. not 166"
    ),
    "job-0717": (
        "skip rust leftover foo.rs vs foo/mod.rs: no merged leftover-HIT pair "
        "this tick. not inventing refs; not 075"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: swc leftover cache vs moved file identity not 090/167",
        "unique swc leftover if pinned",
    ),
    (
        "public OSS: esbuild leftover define cache vs env identity not 156/167",
        "unique esbuild leftover if pinned",
    ),
]


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 210):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_swc(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: swc-project/swc
failing_ref: c5235516340959f703c02d91a79ba40df897eb9c
fixed_ref: c0b6f12fe4c3b1d0235a64496560941751e21bd8
source_issue: https://github.com/swc-project/swc/pull/12166
source_pr: https://github.com/swc-project/swc/pull/12166
mechanism_tags:
  - leftover-optimizer-env
  - omitted-envs-cache-key
  - process-wide-dashmap
ecosystem: swc
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

SWC `GlobalPassOption::build` can keep the identity of **previous optimizer environment replacements** after a second in-process compile with a different explicit `jsc.transform.optimizer.globals.envs` map, because the process-wide DashMap cache key is built from `self.vars` and omits the configured `envs` map.

On failing_ref `c5235516340959f703c02d91a79ba40df897eb9c`:

```
GlobalInliningPassEnvs::Map(map) => {
    static CACHE: Lazy<DashMap<Vec<(Atom, Atom)>, ValuesMap, FxBuildHasher>> =
        Lazy::new(Default::default);

    let cache_key = self
        .vars
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect::<Vec<_>>();
    if let Some(v) = CACHE.get(&cache_key) {
        (*v).clone()
    } else {
        let map = mk_map(
            cm,
            handler,
            map.iter().map(|(k, v)| (k.clone(), v.clone())),
            false,
        );
        CACHE.insert(cache_key, map.clone());
        map
    }
}
```

Two compilations with the same `vars` (often empty) and different explicit `envs` collide. The later compile reuses leftover replacements from the earlier one. `process.env.REPRO_VALUE` stays `'first'` after the second compile asked for `'second'`.

Public report (swc-project/swc#12166). Follow-up of #12129 (cached-span source-map). Same source compiled twice in one process with different explicit environment values.

In-tree after the repair (not on failing_ref): cache key is the configured `envs` map, sorted so equivalent maps match regardless of iteration order.

Case A — same vars and same envs, second compile:
  cache identity is current
  not leftover-after-env-change

Case B — same vars, different explicit envs, leftover replacements:
  leftover: previous ValuesMap (`'first'`)
  envs map omitted from the key
  process-wide DashMap HIT

Case C — new process / empty CACHE:
  fresh mk_map of current envs
  not leftover previous replacements

Case D — key is the envs map (post-repair shape, not on failing_ref):
  second compile emits `'second'`
  not leftover previous envs

The developer wants to know which identity case B actually used for `process.env.REPRO_VALUE` on the second compile: leftover previous-envs (vars-only key), current envs map, or omitted (no cache).
""",
        observed="""# OBSERVED

Public swc-project/swc#12166 (merged 2026-09-01). Squash `c0b6f12fe4c3b1d0235a64496560941751e21bd8` (parent `c5235516340959f703c02d91a79ba40df897eb9c`). Local swc was not performed on this lab host.

PR title: fix(swc): key optimizer env cache by configured values. Cache key was built from `globals.vars`. Same vars + different explicit envs collided. Later compile reused leftover environment replacements.

On failing_ref, `GlobalInliningPassEnvs::Map` keys DashMap by `self.vars`. The `map` used to build ValuesMap is omitted from the key.

Not this packet: specimen-156 bun define-table omitted from runtime-transpile hash. specimen-090 webpack persistent cache. specimen-082 bun optional-peer.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref c5235516340959f703c02d91a79ba40df897eb9c
# crates/swc/src/config/mod.rs GlobalPassOption::build Map arm

# public shape:
# leftover optimizer env replacements after second compile
# cache key is self.vars; configured envs map omitted
# new process / miss writes current envs
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""swc-project/swc
  crates/swc/src/config/mod.rs
  crates/swc/tests/simple.rs
""",
        source="""repository: swc-project/swc
issue: https://github.com/swc-project/swc/pull/12166
pr: https://github.com/swc-project/swc/pull/12166
failing_ref (parent of squash): c5235516340959f703c02d91a79ba40df897eb9c
fixed_ref (cache key is configured envs map, sorted): c0b6f12fe4c3b1d0235a64496560941751e21bd8
merged_at: 2026-09-01T05:52:37Z
pr_author: davidmurdoch
merged_by: kdy1
changed_files: crates/swc/src/config/mod.rs, crates/swc/tests/simple.rs, .changeset/fix-optimizer-env-cache-key.md
pr_title: fix(swc): key optimizer env cache by configured values
scout_note: not 082/090/156. leftover optimizer envs after second compile because key was vars. unique vs 001-166.
""",
        answer_key="""KNOWN FIX (sealed): swc-project/swc PR 12166 squash c0b6f12fe4c3b1d0235a64496560941751e21bd8.

failing_ref is parent c5235516340959f703c02d91a79ba40df897eb9c.

GlobalPassOption::build Map arm keyed the process-wide DashMap by self.vars and omitted the configured envs map. Second compile with different envs HIT leftover replacements.

PR repair: build the cache key from the configured environment map and sort entries.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (same-envs current vs leftover after env change vs new process vs envs-keyed)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — vars-only key JOINs two different envs maps; two greps cannot replace
ecosystem: swc / optimizer globals
mechanism_family: leftover-optimizer-env, omitted-envs-cache-key, process-wide-dashmap

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "global_pass_envs_failing.rs": """// Reduced excerpt of GlobalPassOption::build Map arm on failing_ref
// crates/swc/src/config/mod.rs
// c5235516340959f703c02d91a79ba40df897eb9c
// cache key is self.vars; configured envs map omitted.

GlobalInliningPassEnvs::Map(map) => {
    static CACHE: Lazy<DashMap<Vec<(Atom, Atom)>, ValuesMap, FxBuildHasher>> =
        Lazy::new(Default::default);

    let cache_key = self
        .vars
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect::<Vec<_>>();
    if let Some(v) = CACHE.get(&cache_key) {
        (*v).clone()
    } else {
        let map = mk_map(
            cm,
            handler,
            map.iter().map(|(k, v)| (k.clone(), v.clone())),
            false,
        );
        CACHE.insert(cache_key, map.clone());
        map
    }
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  SWC GlobalPassOption::build envs Map cache
  leftover optimizer env replacements after second compile

Case A (same vars and same envs):
  current cache identity
  not leftover-after-env-change

Case B (same vars, different explicit envs, leftover replacements):
  leftover: previous ValuesMap ('first')
  envs map omitted from the key

Case C (new process / empty CACHE):
  fresh mk_map of current envs
  not leftover previous replacements

Case D (key is the envs map):
  second compile emits 'second'
  not leftover previous envs

Not this packet:
  bun define-table omitted from runtime-transpile hash (specimen-156)
  webpack persistent cache (specimen-090)
  bun optional-peer (specimen-082)
""",
        },
    )


PACKETS = [
    (None, "hdd-swcenv", packet_swc,
     "swc leftover optimizer envs omitted from cache key (vars-only); not 082/090/156"),
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
        if old not in {None, worker} and not str(old).startswith("scout-"):
            raise SystemExit(f"{job_id} status=CLAIMED worker={old}")
        job["worker"] = worker
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


def _init_trial(trial: str, seed: str) -> None:
    script = RUN_DIR / "scripts" / "init_trial.sh"
    subprocess.run([str(script), trial, seed], check=True, cwd=str(RUN_DIR))


def _complete_and_enqueue(packed: list[tuple[str | None, str, str, str]]) -> str:
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
                if old in {None, WORKER} or str(old).startswith("scout-"):
                    complete(state, jid, result="skip", artifact=artifact)
        ids = {s.get("id") for s in state.get("specimens") or []}
        reasons = []
        for job_id, spec_id, trial, priority_reason in packed:
            if spec_id not in ids:
                state.setdefault("specimens", []).append({"id": spec_id})
                ids.add(spec_id)
            if job_id:
                job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
                if job is not None and job.get("status") in {"READY", "CLAIMED"}:
                    if job.get("status") == "READY":
                        _claim_job(state, job_id, WORKER)
                    old = job.get("worker")
                    if old in {None, WORKER} or str(old).startswith("scout-"):
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
    packed: list[tuple[str | None, str, str, str]] = []
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
