#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 128.

Packed (unique vs 001-127; 075 not overwritten; not bazel#29298):
1) dart-lang/pub#4863 / dart-lang/sdk#61950: leftover
   .dart_tool/package_config.json identity after a workspace member is
   added, because isPackagePathsMappingUpToDateWithLockfile only rejects
   extra mappings and never requires missing workspace packages.
   isLockFileUpToDate only checks root.immediateDependencies, so a
   member pubspec change is also omitted. Distinct from 103 go-work
   leftover replace graph and 121 swift registry TTL.

SKIP (claimed this tick; no unique leftover-identity pair):
- job-0536 conan leftover package_id vs recipe revision: #18954/#20175/
  #17134 still OPEN; #19740 MERGED is alias removal not leftover
  package_id vs recipe revision. not inventing refs.
- job-0537 mill leftover zinc vs 117: mill#4642 is reproducible out/
  absolute-path serialization (cache sharing), not leftover previous
  zinc Analysis after identity-relevant change. 117 remains sbt
  last-write Analysis vs file size+mtime. not inventing refs.
- job-0539 homebrew leftover bottle vs formula rebuild: #20936 is
  formula_auditor revision/compatibility_version, not leftover bottle
  identity vs rebuild. not inventing refs.
- job-0540 cocoapods leftover Pods vs Podfile.lock: no merged leftover
  checksum/sandbox pair distinct from 122/102. not inventing refs.
- job-0541 opam leftover switch vs lock: no merged leftover-identity
  pair. not inventing refs.
- job-0547 mix compile leftover .beam: elixir#14189 CLOSED not_planned
  no PR; #13298 CLOSED completed no PR. not inventing refs.
- job-0548 cabal store leftover unit-id: no unique leftover store
  unit-id pair (#9464 is per-component coverage). not inventing refs.
- job-0549 sccache leftover CPATH: mozilla/sccache#2798 still OPEN.
  not 075/086. not inventing refs.
- job-0550 buck2 leftover action cache: facebook/buck2#976 still OPEN.
  skip bazel#29298. not inventing refs.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 128
WORKER = "scout-coord-1827"
JOB_PACK = "job-0538"
TRIAL = "hdd-pubws"
SKIP_JOBS = {
    "job-0536": (
        "skip conan leftover package_id vs recipe revision: #18954 OPEN "
        "full lockfiles with prev; #20175 OPEN package_ids in lockfiles; "
        "#17134 OPEN package revisions in lockfiles; #19740 MERGED is "
        "alias removal not leftover package_id vs recipe revision. not "
        "inventing refs; not 001-127"
    ),
    "job-0537": (
        "skip mill leftover zinc analysis vs 117: mill#4642 is "
        "reproducible out/ absolute-path serialization for cache sharing, "
        "not leftover previous zinc Analysis after identity-relevant "
        "change. specimen-117 remains sbt last-write Analysis vs file "
        "size+mtime. not inventing refs"
    ),
    "job-0539": (
        "skip homebrew leftover bottle vs formula rebuild: Homebrew#20936 "
        "is formula_auditor revision/compatibility_version, not leftover "
        "bottle identity vs rebuild number. not inventing refs"
    ),
    "job-0540": (
        "skip cocoapods leftover Pods vs Podfile.lock: no merged leftover "
        "checksum/sandbox identity pair distinct from 122/102. not "
        "inventing refs"
    ),
    "job-0541": (
        "skip opam leftover switch vs lock identity: no merged leftover-"
        "identity pair. not inventing refs"
    ),
    "job-0547": (
        "skip mix compile leftover .beam vs manifest: elixir#14189 CLOSED "
        "not_planned no PR (cover relies on leftover .beam); #13298 CLOSED "
        "completed no PR (mtime @external_resource). not mix.lock 074. "
        "not inventing refs"
    ),
    "job-0548": (
        "skip cabal store leftover unit-id vs library identity: no unique "
        "leftover store unit-id merged pair; #9464 is per-component "
        "coverage. not inventing refs"
    ),
    "job-0549": (
        "skip sccache leftover cache vs command identity CPATH: "
        "mozilla/sccache#2798 still OPEN. not 075/086. not inventing refs"
    ),
    "job-0550": (
        "skip buck2 action cache leftover vs command identity: "
        "facebook/buck2#976 still OPEN. skip bazel#29298. not inventing refs"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: eslint leftover cache vs config identity not 114/107",
        "unique eslint cache leftover",
    ),
    (
        "public OSS: turbo leftover cache hash omitting env not 119/115",
        "unique turbo env leftover",
    ),
    (
        "public OSS: nx leftover runtime cache inputs not 119/115",
        "unique nx runtime leftover",
    ),
    (
        "public OSS: ninja leftover depfile vs command identity not 075/086",
        "unique ninja depfile leftover",
    ),
    (
        "public OSS: hatch leftover env vs pyproject identity not 106/021",
        "unique hatch env leftover",
    ),
    (
        "public OSS: coursier leftover artifact vs checksum not 074/021",
        "unique coursier leftover",
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


def packet_pub(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: dart-lang/pub
failing_ref: 425174668513d0696a637e62c683ec5885999914
fixed_ref: 0382a52acba89ff0080d559bb22f4017962bbd1d
source_issue: https://github.com/dart-lang/sdk/issues/61950
source_pr: https://github.com/dart-lang/pub/pull/4863
mechanism_tags:
  - leftover-package-config
  - omitted-workspace-member
  - lock-up-to-date-root-only
ecosystem: dart-pub
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

dart pub can keep the identity of a **previous `.dart_tool/package_config.json`** after a workspace membership change should have been a different mapping. `isPackagePathsMappingUpToDateWithLockfile` only rejects extra mappings. Missing workspace packages are omitted, so leftover package_config without the new member is treated as up-to-date.

On failing_ref `425174668513d0696a637e62c683ec5885999914`, `isLockFileUpToDate` checks only `root.immediateDependencies`. A workspace member's pubspec change is omitted. Workspace packages are never listed in `pubspec.lock` `packages`, and the mapping check never requires every `workspaceRoot.transitiveWorkspace` name.

Public report (dart-lang/sdk#61950 / dart-lang/pub#4863). Workspace:

```
# pubspec.yaml
name: myapp
workspace: [sub]

# sub/pubspec.yaml
name: sub
resolution: workspace
```

After `dart run sub:tool`, add workspace member `pkg_b` without `pub get`. On failing_ref the leftover package_config (no `pkg_b`) is still treated as current. Same PR: `isLockFileUpToDate` does not see a new dependency on member `sub`.

In-tree after the repair (not on failing_ref): require every workspace package in `packagePathsMapping`; check `immediateDependencies` for every `transitiveWorkspace` package; tests `Invalidates resolution when new package added to workspace` and `Invalidates resolution when workspace member dependency is modified`.

Case A — second `dart run sub:tool` with unchanged workspace:
  package_config is the current mapping
  not leftover-after-workspace-add

Case B — add workspace member `pkg_b` without `pub get`, leftover package_config:
  leftover: package_config without pkg_b
  missing workspace member omitted from identity
  treated as up-to-date on failing_ref

Case C — delete `.dart_tool/package_config.json` + `pubspec.lock` then `pub get`:
  fresh mapping including pkg_b
  not leftover missing member

Case D — missing workspace member invalidates (post-repair shape, not on failing_ref):
  package_config is not leftover without pkg_b
  resolution runs again

The developer wants to know which identity case B actually used for `.dart_tool/package_config.json` after adding `pkg_b`: leftover mapping without pkg_b (treated as current), current mapping including pkg_b, or omitted (no package_config).
""",
        observed="""# OBSERVED

Public dart-lang/sdk#61950 (closed 2026-09-01). dart-lang/pub PR 4863 squash `0382a52acba89ff0080d559bb22f4017962bbd1d` (parent `425174668513d0696a637e62c683ec5885999914`). Local pub was not performed on this lab host.

Issue body: `dart run` from a subdirectory with an outdated lock fails looking for pubspec.yaml in the subdirectory. PR also adds workspace-member invalidation: leftover package_config after adding a workspace package, leftover lock after a member pubspec change.

On failing_ref, `isPackagePathsMappingUpToDateWithLockfile` checks extra mappings and lockfile packages only. Missing `workspaceRoot.transitiveWorkspace` names are **not** required. `isLockFileUpToDate` uses `root.immediateDependencies` only. Those checks are **not** on the failing revision. They are added by PR 4863.

Not this packet: specimen-103 go work leftover replace graph. specimen-121 swift registry metadata TTL inverted. specimen-126 npm leftover original across file: Link. specimen-125 uv leftover extras marker simplified to true.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 425174668513d0696a637e62c683ec5885999914
# lib/src/entrypoint.dart isLockFileUpToDate / isPackagePathsMappingUpToDateWithLockfile

# public shape:
# leftover .dart_tool/package_config.json after workspace: [sub, pkg_b]
# missing pkg_b omitted from up-to-date check
# dart run pkg_b:tool treated leftover mapping as current
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""dart-lang/pub
  lib/src/entrypoint.dart
  lib/src/executable.dart
  test/embedding/get_executable_for_command.dart
  .dart_tool/package_config.json
  pubspec.lock
""",
        source="""repository: dart-lang/pub
issue: https://github.com/dart-lang/sdk/issues/61950
pr: https://github.com/dart-lang/pub/pull/4863
failing_ref (parent of squash on master): 425174668513d0696a637e62c683ec5885999914
fixed_ref (Use workspace root when constructing Entrypoint): 0382a52acba89ff0080d559bb22f4017962bbd1d
merged_at: 2026-09-01T13:49:04Z
pr_author: sigurdm
merged_by: sigurdm
changed_files: lib/src/entrypoint.dart, lib/src/executable.dart, test/embedding/get_executable_for_command.dart
pr_title: Use workspace root when constructing Entrypoint in getExecutableForCommand and ensureUpToDate
scout_note: not specimen-103 go-work leftover replace. not 121 swift registry TTL. Distinct leftover: package_config identity omits missing workspace members so leftover mapping without pkg_b is treated as current. job-0538 unique vs 001-127 (no dart-lang/pub).
""",
        answer_key="""KNOWN FIX (sealed): dart-lang/pub PR 4863 squash 0382a52acba89ff0080d559bb22f4017962bbd1d.

failing_ref is parent 425174668513d0696a637e62c683ec5885999914.

isPackagePathsMappingUpToDateWithLockfile omitted missing workspace packages, so leftover package_config without a newly added member was treated as current. isLockFileUpToDate checked only root.immediateDependencies.

PR repair: require every transitiveWorkspace name in packagePathsMapping; check immediateDependencies for every workspace package; construct Entrypoint from workspace root.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged workspace vs leftover mapping after add vs wipe vs missing-member invalidates)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — package_config mapping identity and workspace pubspec identity are different objects; missing members omitted so leftover mapping stayed current
ecosystem: dart / pub
mechanism_family: leftover-package-config, omitted-workspace-member, lock-up-to-date-root-only

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "entrypoint_failing.dart": """// Reduced excerpt of isLockFileUpToDate + mapping check on failing_ref
// lib/src/entrypoint.dart
// 425174668513d0696a637e62c683ec5885999914
// Missing workspace members are omitted from identity.

      if (!root.immediateDependencies.values.every(isDependencyUpToDate)) {
        final pubspecPath = p.normalize(p.join(dir, 'pubspec.yaml'));
        log.fine(
          'The $pubspecPath file has changed since the $lockFilePath file '
          'was generated.',
        );
        return false;
      }

      bool isPackagePathsMappingUpToDateWithLockfile(
        Map<String, String> packagePathsMapping, {
        required String lockFilePath,
        required String packageConfigPath,
      }) {
        // extra mappings only — missing workspace packages omitted
        final hasExtraMappings =
            !packagePathsMapping.keys.every((packageName) {
              return workspaceRoot.transitiveWorkspace.any(
                    (p) => p.name == packageName,
                  ) ||
                  lockFile.packages.containsKey(packageName);
            });
        if (hasExtraMappings) {
          return false;
        }
        return lockFile.packages.values.every((lockFileId) {
          final packagePath = packagePathsMapping[lockFileId.name];
          return packagePath != null;
        });
      }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  workspace myapp with member sub
  leftover .dart_tool/package_config.json without pkg_b

Case A (second dart run, unchanged workspace):
  current mapping
  not leftover-after-workspace-add

Case B (add workspace member pkg_b, leftover package_config):
  leftover: mapping without pkg_b
  missing workspace member omitted from identity
  treated as up-to-date

Case C (delete package_config + lock then pub get):
  fresh mapping including pkg_b
  not leftover missing member

Case D (missing member invalidates):
  not leftover mapping without pkg_b

Not this packet:
  go work leftover replace graph (specimen-103)
  swift registry TTL inverted (specimen-121)
  npm leftover original across file: Link (specimen-126)
  uv leftover extras marker simplified to true (specimen-125)
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
                    "dart leftover package_config omits missing workspace member; "
                    "not 103/121/126"
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
                "dream.sh not launched from emit; READY_R1_DREAM already in flight: "
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
        path = emit(packet_pub(spec_id))
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
