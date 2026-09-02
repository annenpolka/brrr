#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 133.

Packed (unique vs 001-132; 075 not overwritten; not bazel#29298):
1) stylelint/stylelint#2908 / PR 6356: leftover .stylelintcache after
   a config-file change because standalone hashed
   JSON.stringify(config || {}) before cosmiconfig resolution, so CLI
   config:undefined became "{}". Distinct from 132 eslint plugin-meta
   omitted from toJSON, 114 ruff nested pyproject, 107 pytest cache-dir.

SKIP (this tick; no unique leftover-identity pair):
- job-0570 prettier leftover cache vs plugin metadata: #17260 still
  OPEN, no PR. not inventing refs.
- job-0571 golangci-lint leftover cache vs config: no merged leftover-
  identity pair (#5313 invalid config ignored; #5871 stats; #4220 CI
  time). not inventing refs.
- job-0572 nuget leftover packages.lock vs assets: Home leftover issues
  still OPEN. not inventing refs.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 133
WORKER = "scout-coord-1858"
JOB_PACK = "job-0569"
TRIAL = "hdd-slcache"
SKIP_JOBS = {
    "job-0570": (
        "skip prettier leftover cache vs plugin metadata: prettier#17260 "
        "still OPEN no PR (optional plugin meta for cache key). not "
        "inventing refs; not 132"
    ),
    "job-0571": (
        "skip golangci-lint leftover cache vs config identity: no merged "
        "leftover-identity pair. #5313 invalid config silently ignored; "
        "#5871 cache stats 0; #4220 CI time. not inventing refs"
    ),
    "job-0572": (
        "skip nuget leftover packages.lock vs assets file identity: "
        "NuGet/Home leftover issues still OPEN. not inventing refs"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: biome leftover cache vs config identity not 132/133",
        "unique biome cache leftover",
    ),
    (
        "public OSS: oxc leftover cache vs config identity not 132/133",
        "unique oxc/oxlint cache leftover",
    ),
    (
        "public OSS: sqlc leftover generated vs schema identity not 041/043",
        "unique sqlc generate leftover",
    ),
    (
        "public OSS: prettier leftover cache vs plugin metadata if #17260 merges",
        "unique prettier plugin-cache leftover if pinned",
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


def packet_stylelint(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: stylelint/stylelint
failing_ref: 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
fixed_ref: 5be33b779b93761d86cb871dfd70f34686b5f6c5
source_issue: https://github.com/stylelint/stylelint/issues/2908
source_pr: https://github.com/stylelint/stylelint/pull/6356
mechanism_tags:
  - leftover-stylelint-cache
  - omitted-resolved-config
  - hashed-empty-cli-config
ecosystem: stylelint
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

stylelint `--cache` can keep the identity of a **previous lint result** after a config-file change should have been a different cache object. `standalone` hashed `JSON.stringify(config || {})` before cosmiconfig resolution. When the CLI config object is undefined (config loaded from `.stylelintrc.json`), that hash is stylelintVersion plus "{}". Resolved file config is omitted.

On failing_ref `3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66`:

```
const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);
fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);
absoluteFilePaths = absoluteFilePaths.filter(fileCache.hasFileChanged.bind(fileCache));
```

Public report (stylelint/stylelint#2908). `.stylelintrc.json` with `block-no-empty: null` then change to `true`; leftover `.stylelintcache` still skips `a.css`.

In-tree after the repair (not on failing_ref): `lintSource` calls `calcHashOfConfig(config)` after `getConfigForFile`; test `cache is discarded when a config file is changed`.

Case A — second `stylelint --cache` with unchanged `.stylelintrc.json`:
  cache identity is current
  not leftover-after-config-change

Case B — config file rule flipped, leftover `.stylelintcache`:
  leftover: previous config's lint results
  resolved file config omitted from hash (`config || {}` is `{}`)
  new-rule warnings not reported

Case C — delete `.stylelintcache` then lint:
  fresh cache identity
  not leftover previous config

Case D — hash resolved config after getConfigForFile (post-repair shape, not on failing_ref):
  cache miss after config-file change
  not leftover previous results

The developer wants to know which identity case B actually used for `.stylelintcache` after the config-file change: leftover previous-config results (resolved config omitted), current config-file identity, or omitted (no cache file).
""",
        observed="""# OBSERVED

Public stylelint/stylelint#2908 (closed 2022-09-27). PR 6356 squash `5be33b779b93761d86cb871dfd70f34686b5f6c5` (parent `3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66`). Local stylelint was not performed on this lab host.

Issue body: a config change is not detected when using `--cache`.

On failing_ref, standalone hashes the CLI `config` argument (often undefined when a file config is used) and filters paths before `lintSource`. `calcHashOfConfig` on the resolved config is **not** on the failing revision. It is added by PR 6356.

Not this packet: specimen-132 eslint leftover cache plugin name@version omitted from toJSON. specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
# lib/standalone.js hash(`${stylelintVersion}_${JSON.stringify(config || {})}`)

# public shape:
# leftover .stylelintcache after .stylelintrc.json block-no-empty null -> true
# resolved file config omitted from hash (CLI config undefined -> {})
# new-rule warnings not reported
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""stylelint/stylelint
  lib/standalone.js
  lib/utils/FileCache.js
  lib/lintSource.js
  lib/__tests__/standalone-cache.test.js
  .stylelintcache
  .stylelintrc.json
""",
        source="""repository: stylelint/stylelint
issue: https://github.com/stylelint/stylelint/issues/2908
pr: https://github.com/stylelint/stylelint/pull/6356
failing_ref (parent of squash on main): 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
fixed_ref (Fix cache refresh when config is changed): 5be33b779b93761d86cb871dfd70f34686b5f6c5
merged_at: 2022-09-27T17:37:48Z
pr_author: kimulaco
merged_by: jeddy3
changed_files: lib/standalone.js, lib/utils/FileCache.js, lib/lintSource.js, lib/createStylelint.js, lib/__tests__/standalone-cache.test.js
pr_title: Fix cache refresh when config is changed
scout_note: not 132 eslint plugin-meta toJSON. not 114 ruff nested pyproject. Distinct leftover: standalone hashed empty CLI config so leftover .stylelintcache after cosmiconfig file change is treated as current. job-0569 unique vs 001-132.
""",
        answer_key="""KNOWN FIX (sealed): stylelint/stylelint PR 6356 squash 5be33b779b93761d86cb871dfd70f34686b5f6c5.

failing_ref is parent 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66.

standalone hashed JSON.stringify(config || {}) before cosmiconfig resolution, so leftover cache after a config-file change kept previous-config lint results.

PR repair: calcHashOfConfig on the resolved config inside lintSource after getConfigForFile.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged file config vs leftover cache after flip vs wipe vs resolved-config hash)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — CLI config object and cosmiconfig-resolved file config are different identities; empty {} hash omitted the file so leftover cache stayed current
ecosystem: stylelint / css lint cache
mechanism_family: leftover-stylelint-cache, omitted-resolved-config, hashed-empty-cli-config

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "standalone_hash_failing.js": """// Reduced excerpt of standalone cache identity on failing_ref
// lib/standalone.js
// 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
// CLI config (often undefined when using a file config) is hashed.
// Resolved cosmiconfig config is omitted.

		const stylelintVersion = pkg.version;
		const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);

		fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);
		absoluteFilePaths = absoluteFilePaths.filter(fileCache.hasFileChanged.bind(fileCache));
""",
            "leftover_identity_split.txt": """Registry / fixture:
  .stylelintrc.json block-no-empty: null
  leftover .stylelintcache after flipping to true

Case A (second lint, same config file):
  current cache identity
  not leftover-after-config-change

Case B (config file flipped, leftover cache):
  leftover: previous config results
  resolved file config omitted (hash of {})
  new-rule warnings not reported

Case C (delete .stylelintcache):
  fresh cache identity
  not leftover previous config

Case D (hash resolved config after getConfigForFile):
  cache miss after file change
  not leftover previous results

Not this packet:
  eslint leftover plugin name@version omitted from toJSON (specimen-132)
  ruff leftover cache vs nested pyproject (specimen-114)
  pytest leftover cache-dir supporting files (specimen-107)
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
                    "stylelint leftover cache hashes empty CLI config; "
                    "resolved file config omitted; not 132/114/107"
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
        path = emit(packet_stylelint(spec_id))
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
