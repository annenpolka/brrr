#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 135.

Packed (unique vs 001-134; 075 not overwritten; not bazel#29298):
1) dprint/dprint#1135 / PR 1138: leftover incremental cache after a
   cacheKeyFiles change because incremental_hash hashed the raw plugin
   config map from dprint.jsonc and omitted the plugin's resolved
   Configuration.cache_key (exec plugin folds rustfmt.toml into it).
   Distinct from 132 eslint plugin-meta toJSON, 133 stylelint empty
   CLI config hash, 114 ruff nested pyproject.

SKIP (this tick; no unique leftover-identity pair):
- job-0582 pants leftover process cache vs env: #23645 still OPEN
  (env without cache key); #18334 is process metadata not leftover
  cache identity; #16963 leftover vcs_version closed without PR.
- job-0583 prisma leftover generated client vs schema: prisma/prisma
  not searchable this tick; no merged leftover-identity pair vs 041/043.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 135
WORKER = "scout-coord-1918"
JOB_PACK = "job-0581"
TRIAL = "hdd-dprintck"
SKIP_JOBS = {
    "job-0582": (
        "skip pants leftover process cache vs env identity: pants#23645 "
        "OPEN (env without cache key); #18334 process metadata not leftover "
        "cache; #16963 leftover vcs_version closed without PR. not inventing refs"
    ),
    "job-0583": (
        "skip prisma leftover generated client vs schema identity: "
        "prisma/prisma not searchable this tick; no merged leftover-identity "
        "pair distinct from 041/043. not inventing refs"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: pants leftover vcs_version cache vs git hash identity not 075",
        "unique pants vcs leftover if pinned",
    ),
    (
        "public OSS: buf leftover generated vs proto identity not 041/043",
        "unique buf generate leftover",
    ),
    (
        "public OSS: go generate leftover vs source identity not 084/103",
        "unique go generate leftover",
    ),
    (
        "public OSS: prisma leftover generated client vs schema if searchable",
        "unique prisma generate leftover if pinned",
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


def packet_dprint(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: dprint/dprint
failing_ref: 6fc0a066370e2c3a2a1030c56fbc229918a45cef
fixed_ref: 0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f
source_issue: https://github.com/dprint/dprint/issues/1135
source_pr: https://github.com/dprint/dprint/pull/1138
mechanism_tags:
  - leftover-incremental-cache
  - omitted-resolved-plugin-config
  - cachekeyfiles-hash-omitted
ecosystem: dprint
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

dprint `--incremental` can keep the identity of a **previous format cache** after a file listed in exec-plugin `cacheKeyFiles` should have been a different hash. The host `incremental_hash` hashed the raw plugin config map from `dprint.jsonc`. The plugin's resolved `Configuration.cache_key` (exec plugin folds `rustfmt.toml` contents into it) is omitted.

On failing_ref `6fc0a066370e2c3a2a1030c56fbc229918a45cef`:

```
pub fn incremental_hash(&self, hasher: &mut impl Hasher) {
    hasher.write(self.info().name.as_bytes());
    hasher.write(self.info().version.as_bytes());
    let sorted_config = self.format_config.plugin.iter().collect::<BTreeMap<_, _>>();
    for (key, value) in sorted_config {
        hasher.write(key.as_bytes());
        value.hash(hasher);
    }
    // no hasher.write(serialized_resolved_config)
    self.format_config.global.hash(hasher);
}
```

Public report (dprint/dprint#1135). `cacheKeyFiles: ["./rustfmt.toml"]`; edit rustfmt.toml; leftover incremental cache; `dprint fmt` does not reformat until `dprint clear-cache`.

In-tree after the repair (not on failing_ref): `serialized_resolved_config` from `instance.resolved_config` is hashed; test `incremental_hash_includes_resolved_config`.

Case A — second `dprint fmt` with unchanged rustfmt.toml:
  cache identity is current
  not leftover-after-cacheKeyFiles-change

Case B — rustfmt.toml flipped, leftover incremental cache:
  leftover: previous formatter output
  resolved plugin cache_key omitted (raw dprint.jsonc map only)
  files not reformatted

Case C — `dprint clear-cache` then fmt:
  fresh cache identity
  not leftover previous config

Case D — resolved config in incremental hash (post-repair shape, not on failing_ref):
  cache miss after cacheKeyFiles change
  not leftover previous output

The developer wants to know which identity case B actually used for the incremental cache after the rustfmt.toml change: leftover previous-config results (resolved cache_key omitted), current cacheKeyFiles identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public dprint/dprint#1135 (closed 2026-05-31). PR 1138 squash `0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f` (parent `6fc0a066370e2c3a2a1030c56fbc229918a45cef`). Local dprint was not performed on this lab host.

Issue body: exec plugin `cacheKeyFiles` is hashed into plugin Configuration.cache_key but the host incremental hash uses the raw dprint.jsonc plugin map, so leftover cache after rustfmt.toml change is reused.

On failing_ref, `incremental_hash` hashes `format_config.plugin` only. `serialized_resolved_config` is **not** on the failing revision. It is added by PR 1138.

Not this packet: specimen-132 eslint leftover plugin name@version omitted from toJSON. specimen-133 stylelint leftover cache hashing empty CLI config. specimen-114 ruff leftover cache vs nested pyproject.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 6fc0a066370e2c3a2a1030c56fbc229918a45cef
# crates/dprint/src/resolution.rs PluginWithConfig::incremental_hash

# public shape:
# leftover incremental cache after rustfmt.toml listed in cacheKeyFiles changes
# resolved plugin cache_key omitted; raw dprint.jsonc map hashed
# dprint fmt does not reformat until clear-cache
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""dprint/dprint
  crates/dprint/src/resolution.rs
  crates/dprint/src/plugins/implementations/mod.rs
  dprint.jsonc
  rustfmt.toml
""",
        source="""repository: dprint/dprint
issue: https://github.com/dprint/dprint/issues/1135
pr: https://github.com/dprint/dprint/pull/1138
failing_ref (parent of squash on main): 6fc0a066370e2c3a2a1030c56fbc229918a45cef
fixed_ref (include plugin's resolved config in incremental cache key): 0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f
merged_at: 2026-05-31T16:32:42Z
pr_author: dsherret
merged_by: dsherret
changed_files: crates/dprint/src/resolution.rs, crates/dprint/src/plugins/implementations/mod.rs
pr_title: fix: include plugin's resolved config in incremental cache key
scout_note: not 132 eslint plugin-meta. not 133 stylelint empty CLI hash. Distinct leftover: host incremental hash omits plugin resolved cache_key so leftover cache after cacheKeyFiles change is treated as current. job-0581 unique vs 001-134.
""",
        answer_key="""KNOWN FIX (sealed): dprint/dprint PR 1138 squash 0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f.

failing_ref is parent 6fc0a066370e2c3a2a1030c56fbc229918a45cef.

incremental_hash hashed the raw plugin config map and omitted the plugin's resolved Configuration.cache_key, so leftover incremental cache after a cacheKeyFiles change kept previous formatter output.

PR repair: hash serialized_resolved_config from instance.resolved_config.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged rustfmt.toml vs leftover cache after flip vs clear-cache vs resolved config hashed)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — raw dprint.jsonc plugin map and plugin-resolved cache_key are different identities; cacheKeyFiles contents omitted so leftover cache stayed current
ecosystem: dprint / incremental cache
mechanism_family: leftover-incremental-cache, omitted-resolved-plugin-config, cachekeyfiles-hash-omitted

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "incremental_hash_failing.rs": """// Reduced excerpt of PluginWithConfig::incremental_hash on failing_ref
// crates/dprint/src/resolution.rs
// 6fc0a066370e2c3a2a1030c56fbc229918a45cef
// Raw plugin config map hashed. Resolved cache_key omitted.

  pub fn incremental_hash(&self, hasher: &mut impl Hasher) {
    hasher.write(self.info().name.as_bytes());
    hasher.write(self.info().version.as_bytes());
    let sorted_config = self.format_config.plugin.iter().collect::<BTreeMap<_, _>>();
    for (key, value) in sorted_config {
      hasher.write(key.as_bytes());
      value.hash(hasher);
    }
    // no hasher.write(serialized_resolved_config.as_bytes())
    if let Some(associations) = &self.associations {
      for association in associations {
        hasher.write(association.as_bytes());
      }
    }
    self.format_config.global.hash(hasher);
  }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  dprint.jsonc exec cacheKeyFiles: [./rustfmt.toml]
  leftover incremental cache after rustfmt.toml change

Case A (second dprint fmt, same rustfmt.toml):
  current cache identity
  not leftover-after-cacheKeyFiles-change

Case B (rustfmt.toml flipped, leftover cache):
  leftover: previous formatter output
  resolved plugin cache_key omitted (raw dprint.jsonc map only)
  files not reformatted

Case C (dprint clear-cache):
  fresh cache identity
  not leftover previous config

Case D (resolved config in incremental hash):
  cache miss after cacheKeyFiles change
  not leftover previous output

Not this packet:
  eslint leftover plugin name@version omitted from toJSON (specimen-132)
  stylelint leftover cache hashing empty CLI config (specimen-133)
  ruff leftover cache vs nested pyproject (specimen-114)
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
                    "dprint leftover incremental cache omits plugin resolved cache_key; "
                    "not 132/133/114"
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
        path = emit(packet_dprint(spec_id))
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
