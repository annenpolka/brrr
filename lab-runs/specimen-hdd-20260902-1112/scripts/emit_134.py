#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 134.

Packed (unique vs 001-133; 075 not overwritten; not bazel#29298):
1) moonrepo/moon#481 / PR 482: leftover task cache after a `.env`
   change because expand_env loaded env vars but omitted the env file
   from task.inputs, and get_file_hashes skipped gitignored paths.
   Distinct from 119 pixi leftover args, 115 go-task leftover MATCH,
   turbo leftover env (no merged pair this run).

SKIP (this tick; no unique leftover-identity pair):
- job-0574 biome leftover cache vs config: no merged leftover-identity
  pair found.
- job-0575 oxc leftover cache vs config: no merged leftover-identity
  pair (oxc#25133 is gitignore walk, not leftover cache identity).
- job-0576 sqlc leftover generated vs schema: no merged leftover-
  identity pair distinct from 041/043 protobuf.
- job-0577 prettier leftover plugin-cache: #17260 still OPEN no PR.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 134
WORKER = "scout-coord-1908"
TRIAL = "hdd-moonenv"
SKIP_JOBS = {
    "job-0574": (
        "skip biome leftover cache vs config identity: no merged leftover-"
        "identity pair. not inventing refs; not 132/133"
    ),
    "job-0575": (
        "skip oxc leftover cache vs config identity: no merged leftover-"
        "identity pair. oxc#25133 is gitignore walk. not inventing refs"
    ),
    "job-0576": (
        "skip sqlc leftover generated vs schema identity: no merged leftover-"
        "identity pair distinct from 041/043. not inventing refs"
    ),
    "job-0577": (
        "skip prettier leftover cache vs plugin metadata: prettier#17260 "
        "still OPEN no PR. not inventing refs; not 132"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: dprint leftover incremental cache vs config identity not 132/133",
        "unique dprint cache leftover",
    ),
    (
        "public OSS: pants leftover process cache vs env identity not 075",
        "unique pants env leftover",
    ),
    (
        "public OSS: prisma leftover generated client vs schema identity not 041/043",
        "unique prisma generate leftover",
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


def packet_moon(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: moonrepo/moon
failing_ref: 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
fixed_ref: 2959d6f0bcc9dbe12fb3f35e54186d245b44586a
source_issue: https://github.com/moonrepo/moon/issues/481
source_pr: https://github.com/moonrepo/moon/pull/482
mechanism_tags:
  - leftover-task-cache
  - omitted-env-file-input
  - gitignored-hash-skip
ecosystem: moon
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

moon can keep the identity of a **previous task cache** after a `.env` file change should have been a different hash. `expand_env` loads env vars from the file but omits the env file from `task.inputs`. `get_file_hashes` then skips gitignored paths, so even an explicit `.env` input is omitted from the cache identity.

On failing_ref `5468dd6fb24ee98cbf6e4c05e3421e6a17e73199`:

```
// expand_env loads dotenv into self.env
// does not push env_file onto self.inputs

for file in files {
    if !self.is_file_ignored(file) {
        objects.push(file.clone());
    }
}
```

Public report (moonrepo/moon#481). Task lists `.env` as an input and `envFile: true`. Change `.env` FOO=123 → FOO=456; leftover cache is reused.

In-tree after the repair (not on failing_ref): `self.inputs.push(env_file)`; `get_file_hashes(files, allow_ignored=true)` for task inputs; test `tracks_input_changes_for_env_files`.

Case A — second `moon run` with unchanged `.env`:
  cache identity is current
  not leftover-after-env-change

Case B — `.env` contents flipped, leftover task cache:
  leftover: previous env file's task output
  env file omitted from inputs and/or skipped as gitignored
  cached output reused

Case C — delete the moon cache then run:
  fresh hash identity
  not leftover previous env

Case D — env file hashed as an input even if gitignored (post-repair shape, not on failing_ref):
  cache miss after `.env` change
  not leftover previous output

The developer wants to know which identity case B actually used for the task cache after the `.env` change: leftover previous-env output (env file omitted), current env-file identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public moonrepo/moon#481 (closed 2022-11-30). PR 482 squash `2959d6f0bcc9dbe12fb3f35e54186d245b44586a` (parent `5468dd6fb24ee98cbf6e4c05e3421e6a17e73199`). Local moon was not performed on this lab host.

Issue body: `.env` listed as an input does not break cache; leftover cached output is reused after the file changes.

On failing_ref, `expand_env` does not add `env_file` to `inputs`. `Git::get_file_hashes` skips `is_file_ignored`. `allow_ignored` is **not** on the failing revision. It is added by PR 482.

Not this packet: specimen-119 pixi leftover task cache filename omitting args. specimen-115 go-task leftover wildcard MATCH. turbo leftover env (no merged leftover-identity pair this run). specimen-133 stylelint leftover cache hashing empty CLI config.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
# crates/core/task/src/task.rs expand_env
# crates/core/vcs/src/git.rs get_file_hashes skips is_file_ignored

# public shape:
# leftover moon task cache after .env FOO=123 -> FOO=456
# env file omitted from inputs; gitignored paths skipped from hash
# cached output reused
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""moonrepo/moon
  crates/core/task/src/task.rs
  crates/core/vcs/src/git.rs
  crates/core/runner/src/actions/run_target.rs
  crates/cli/tests/run_test.rs
  .env
""",
        source="""repository: moonrepo/moon
issue: https://github.com/moonrepo/moon/issues/481
pr: https://github.com/moonrepo/moon/pull/482
failing_ref (parent of squash on master): 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
fixed_ref (Fix an issue where .env is not considered an input): 2959d6f0bcc9dbe12fb3f35e54186d245b44586a
merged_at: 2022-11-30T23:58:31Z
pr_author: milesj
merged_by: milesj
changed_files: crates/core/task/src/task.rs, crates/core/vcs/src/git.rs, crates/core/runner/src/actions/run_target.rs, crates/cli/tests/run_test.rs
pr_title: fix: Fix an issue where `.env` is not considered an input.
scout_note: not 119 pixi leftover args. not 115 go-task leftover MATCH. Distinct leftover: env file omitted from task.inputs and skipped when gitignored so leftover cache after .env change is treated as current.
""",
        answer_key="""KNOWN FIX (sealed): moonrepo/moon PR 482 squash 2959d6f0bcc9dbe12fb3f35e54186d245b44586a.

failing_ref is parent 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199.

expand_env loaded dotenv into env vars but omitted the env file from inputs; get_file_hashes skipped gitignored paths, so leftover cache after a .env change kept previous-env task output.

PR repair: push env_file onto inputs; hash task inputs with allow_ignored=true.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged .env vs leftover cache after flip vs wipe vs gitignored file hashed)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — env var values and env-file identity are different objects; gitignore skip omitted .env so leftover cache stayed current
ecosystem: moon / task cache
mechanism_family: leftover-task-cache, omitted-env-file-input, gitignored-hash-skip

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "expand_env_failing.rs": """// Reduced excerpt of expand_env + get_file_hashes on failing_ref
// crates/core/task/src/task.rs expand_env
// crates/core/vcs/src/git.rs get_file_hashes
// 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
// env file loaded into env vars. Not pushed onto inputs.
// Gitignored paths omitted from hash objects.

    pub fn expand_env(&mut self, data: &ResolverData) -> Result<(), TaskError> {
        if let Some(env_file) = &self.options.env_file {
            let env_path = data.project_root.join(env_file);
            // no self.inputs.push(env_file)
            for entry in dotenvy::from_path_iter(&env_path).map_err(error_handler)? {
                let (key, value) = entry.map_err(error_handler)?;
                self.env.entry(key).or_insert(value);
            }
        }
        Ok(())
    }

    async fn get_file_hashes(&self, files: &[String]) -> VcsResult<BTreeMap<String, String>> {
        let mut objects = vec![];
        for file in files {
            if !self.is_file_ignored(file) {
                objects.push(file.clone());
            }
        }
        // hash-object --stdin-paths on objects only
    }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  moon.yml envFile: true, inputs include .env
  leftover task cache after FOO=123 -> FOO=456

Case A (second moon run, same .env):
  current cache identity
  not leftover-after-env-change

Case B (.env flipped, leftover cache):
  leftover: previous env file's task output
  env file omitted from inputs and/or skipped as gitignored
  cached output reused

Case C (delete moon cache):
  fresh hash identity
  not leftover previous env

Case D (env file hashed even if gitignored):
  cache miss after .env change
  not leftover previous output

Not this packet:
  pixi leftover task cache filename omitting args (specimen-119)
  go-task leftover wildcard MATCH (specimen-115)
  stylelint leftover cache hashing empty CLI config (specimen-133)
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
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
                    "moon leftover task cache omits gitignored .env from inputs; "
                    "not 119/115/133"
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
        path = emit(packet_moon(spec_id))
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
