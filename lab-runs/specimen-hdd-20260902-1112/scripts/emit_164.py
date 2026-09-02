#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 164+.

Packed (unique vs 001-163; 075 not overwritten; not bazel#29298):
1) job-0708 biomejs/biome#11409:
   leftover parsed-source map after close_file, because close removed
   documents/node_cache and omitted db_remove_file / files-map eviction.

SKIP claimed jobs without a merged leftover-HIT pair this tick.
"""
from __future__ import annotations

import os
import subprocess

from compile_seed import write_seed
from emit_specimen import emit
from paths import HDD_ROOT, RUN_DIR, SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 164
WORKER = "scout-coord-2228"
SKIP_JOBS = {
    "job-0707": (
        "skip dune leftover source digest vs omitted ctime: #15490/#15494 are "
        "tests reproducing stale digest; #15495 is digest-cache STATS only, not "
        "a leftover-HIT key fix. not inventing refs; not 154"
    ),
    "job-0710": (
        "skip zig leftover cache vs include path: #23645 is miss-path hasher "
        "using unhit before bin_digest populated (false-miss), not leftover-HIT "
        "after include-path change. not inventing refs; not 075"
    ),
    "job-0711": (
        "skip oxc leftover parse cache vs source: no merged leftover-HIT "
        "omitted-source-hash pair this tick. not inventing refs; not 090"
    ),
    "job-0712": (
        "skip php leftover opcache vs same-mtime replace: no merged leftover-HIT "
        "pair this tick (hits open or file_cache_only). not inventing refs; not 110"
    ),
    "job-0713": (
        "skip node leftover compile cache vs strip-types: #63705 is sourceURL "
        "reporting; #65326 is package.json lookup memo. not leftover-HIT omitted "
        "strip-types hash. not inventing refs; not 082/090"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: biome leftover module graph vs close eviction not 164",
        "unique biome leftover if pinned",
    ),
    (
        "public OSS: ruff leftover cache vs config identity not 114",
        "unique ruff leftover if pinned",
    ),
    (
        "public OSS: pants leftover cache vs env identity",
        "unique pants leftover if pinned",
    ),
    (
        "public OSS: buck2 leftover action cache vs omitted dep identity",
        "unique buck2 leftover if pinned",
    ),
]


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 200):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_biome(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: biomejs/biome
failing_ref: 7dbf9d84125b51c4177a899f8638d54b01cd065c
fixed_ref: 405dedb0ff65dd29927faf587f6542e3c29db248
source_issue: https://github.com/biomejs/biome/pull/11409
source_pr: https://github.com/biomejs/biome/pull/11409
mechanism_tags:
  - leftover-parsed-source
  - omitted-close-eviction
  - workspace-db-file-map
ecosystem: biome
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Biome's workspace database can keep the identity of a **previous parsed source** after `close_file`, because close removed the document and node_cache and omitted eviction of the parsed-source map (`db_remove_file`). The path-keyed parse stays. Memory grows across a long LSP session. A later open of the same path can see leftover previous parse.

On failing_ref `7dbf9d84125b51c4177a899f8638d54b01cd065c`:

```
fn close_file(&self, params: CloseFileParams) -> Result<(), WorkspaceError> {
    let path = params.path.as_path();

    self.documents.pin().remove(path);
    self.node_cache.lock().unwrap().remove(path);

    if self.is_indexed(path) {
        self.scanner.reindex_file(path.to_path_buf());
    }

    Ok(())
}
```

`WorkspaceDbData` clones used by Salsa queries did not carry a `files` map that close could pin-remove. `close_file` never called `db_remove_file`. Closing a project similarly omitted descendant parsed-source eviction from that map.

Public report (biomejs/biome#11409). Open files, close them, memory keeps growing; parsed sources stay. Expected: path gone from the parsed-source map. Actual: leftover previous parse.

In-tree after the repair (not on failing_ref): `WorkspaceDbData` holds `files`; `close_file` calls `db_remove_file`; `unload_path` drops descendant files.

Case A — file still open, content unchanged:
  parse identity is current
  not leftover-after-close

Case B — file closed, leftover parsed source:
  leftover: previous ParsedSource for that path
  documents/node_cache gone; files map omitted from eviction
  path-keyed HIT

Case C — never opened / empty workspace db:
  no parse
  not leftover previous source

Case D — db_remove_file on close (post-repair shape, not on failing_ref):
  path gone from files map
  not leftover previous parse

The developer wants to know which identity case B actually used for the path after close: leftover previous-parse (files map omitted from eviction), current disk, or omitted (no parse).
""",
        observed="""# OBSERVED

Public biomejs/biome#11409 (merged 2026-08-19). Squash `405dedb0ff65dd29927faf587f6542e3c29db248` (parent `7dbf9d84125b51c4177a899f8638d54b01cd065c`). Local biome was not performed on this lab host.

PR title: fix(core): files eviction and project. Closing a file would not evict the parsed-source map from the database. Changeset: LSP memory leak over long editor sessions.

On failing_ref, `close_file` removes `documents` and `node_cache` only. Parsed-source map stays. Project close unloads documents under the root but omitted descendant files-map eviction.

Not this packet: specimen-157 jest haste mock-name delete. specimen-159 gleam leftover cache files after move+restore.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 7dbf9d84125b51c4177a899f8638d54b01cd065c
# crates/biome_service/src/workspace/server.rs close_file
# crates/biome_service/src/db/mod.rs WorkspaceDbData

# public shape:
# leftover parsed source after close_file
# documents/node_cache removed; files map omitted from eviction
# never-opened / db_remove_file drops the path
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""biomejs/biome
  crates/biome_service/src/workspace/server.rs
  crates/biome_service/src/db/mod.rs
  crates/biome_service/src/db/state.rs
  crates/biome_service/src/workspace/server.tests.rs
""",
        source="""repository: biomejs/biome
issue: https://github.com/biomejs/biome/pull/11409
pr: https://github.com/biomejs/biome/pull/11409
failing_ref (parent of squash): 7dbf9d84125b51c4177a899f8638d54b01cd065c
fixed_ref (db_remove_file on close; files map on WorkspaceDbData): 405dedb0ff65dd29927faf587f6542e3c29db248
merged_at: 2026-08-19T18:25:28Z
pr_author: ematipico
merged_by: ematipico
changed_files: crates/biome_service/src/db/mod.rs, crates/biome_service/src/db/state.rs, crates/biome_service/src/workspace/server.rs, crates/biome_service/src/workspace/server.tests.rs, .changeset/fix-workspace-db-file-cache-eviction.md
pr_title: fix(core): files eviction and project
scout_note: not 157/159. leftover parsed source after close because files map omitted from eviction. unique vs 001-163.
""",
        answer_key="""KNOWN FIX (sealed): biomejs/biome PR 11409 squash 405dedb0ff65dd29927faf587f6542e3c29db248.

failing_ref is parent 7dbf9d84125b51c4177a899f8638d54b01cd065c.

close_file removed documents and node_cache and omitted db_remove_file. Parsed-source map kept leftover previous parse for the path.

PR repair: put files on WorkspaceDbData; remove_file on close; unload_path drops descendant files.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (still-open current vs leftover parse after close vs never-opened vs db_remove_file)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — path-keyed parse JOINs previous close; two greps cannot replace
ecosystem: biome / LSP workspace db
mechanism_family: leftover-parsed-source, omitted-close-eviction, workspace-db-file-map

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "close_file_failing.rs": """// Reduced excerpt of close_file on failing_ref
// crates/biome_service/src/workspace/server.rs
// 7dbf9d84125b51c4177a899f8638d54b01cd065c
// documents/node_cache removed; parsed-source map omitted from eviction.

fn close_file(&self, params: CloseFileParams) -> Result<(), WorkspaceError> {
    let path = params.path.as_path();

    self.documents.pin().remove(path);
    self.node_cache.lock().unwrap().remove(path);

    if self.is_indexed(path) {
        self.scanner.reindex_file(path.to_path_buf());
    }

    Ok(())
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  Biome workspace close_file / WorkspaceDb parsed-source map
  leftover ParsedSource after close

Case A (file still open, content unchanged):
  current parse identity
  not leftover-after-close

Case B (file closed, leftover parsed source):
  leftover: previous ParsedSource for that path
  documents/node_cache gone; files map omitted from eviction

Case C (never opened / empty workspace db):
  no parse
  not leftover previous source

Case D (db_remove_file on close):
  path gone from files map
  not leftover previous parse

Not this packet:
  jest haste mock-name delete (specimen-157)
  gleam leftover cache after move+restore (specimen-159)
""",
        },
    )


PACKETS = [
    ("job-0708", "hdd-biomevict", packet_biome,
     "biome leftover parsed source after close omitted files-map eviction; not 157/159"),
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
