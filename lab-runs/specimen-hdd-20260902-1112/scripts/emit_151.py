#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets 151-152.

Packed (unique vs 001-150; 075 not overwritten; not bazel#29298):
1) objectionary/eo#7628 / PR 7675:
   leftover transpile cache after -Deo.trackSteps=true because
   Transpilation.version() folded locations()/coverage/superclass and
   omitted tracking.steps(); cache HIT of previous no-step-files result.
2) bazel-contrib/rules_distroless#237:
   leftover apt facts/packages after snapshot URL upgrade because
   pkg_fact_key was dist/component/architecture/Packages and omitted
   snapshot URLs. Distinct from bazel#29298 env_inherit local vs remote.

SKIP (claimed 0638-0642 this tick; no unique leftover-identity pair):
- job-0638 podman leftover image vs digest: no merged leftover-HIT
  omitted-digest pair; not 066 (healthcheck timer) / 144 (skaffold).
- job-0639 turbo leftover cache vs env: #548/#4645 closed without PR;
  #10690 closed not_planned. not inventing refs; not 140.
- job-0640 sbt leftover zinc vs analysis: duplicate of 117 (#9195 /
  PR 9207 last-write Analysis). #9546 OPEN; #7969 extra-clear on clean.
- job-0641 lerna leftover package cache vs version: no merged leftover-
  identity pair. not inventing refs; not 004.
- job-0642 rye leftover venv vs lock: no merged leftover-identity pair;
  sccache#2798 still OPEN. not inventing refs; not 022/125.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 151
WORKER = "scout-coord-2127"
SKIP_JOBS = {
    "job-0638": (
        "skip podman leftover image cache vs digest identity: no merged "
        "leftover-HIT omitted-digest pair this tick. not inventing refs; "
        "not 066/144"
    ),
    "job-0639": (
        "skip turbo leftover cache vs env identity: turborepo#548/#4645 "
        "closed without PR; #10690 closed not_planned. not inventing refs; "
        "not 140"
    ),
    "job-0640": (
        "skip sbt leftover zinc cache vs analysis identity: duplicate of "
        "117 sbt#9195 / PR 9207 last-write Analysis. #9546 OPEN; #7969 "
        "extra-clear on clean. not inventing refs; not 075"
    ),
    "job-0641": (
        "skip lerna leftover package cache vs version identity: no merged "
        "leftover-identity pair this tick. not inventing refs; not 004"
    ),
    "job-0642": (
        "skip rye leftover venv cache vs lock identity: no merged leftover-"
        "identity pair this tick; sccache#2798 still OPEN. not inventing "
        "refs; not 022/125"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: hex leftover cache vs checksum identity not 074",
        "unique hex leftover if pinned",
    ),
    (
        "public OSS: mix leftover compile vs source identity not 054",
        "unique mix leftover if pinned",
    ),
    (
        "public OSS: kustomize leftover inventory vs resource identity not 052",
        "unique kustomize leftover if pinned",
    ),
    (
        "public OSS: flux leftover artifact vs digest identity not 144",
        "unique flux leftover if pinned",
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


def packet_eo(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: objectionary/eo
failing_ref: 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
fixed_ref: 34df04c9a5eb26c6718c9512d930c4653627d70f
source_issue: https://github.com/objectionary/eo/issues/7628
source_pr: https://github.com/objectionary/eo/pull/7675
mechanism_tags:
  - leftover-transpile-cache
  - omitted-tracksteps-from-cache-key
  - diagnostic-flag-on-cache-hit
ecosystem: eolang
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

EOLANG `Transpilation.version()` can keep the identity of a **previous transpile-cache result** after `-Deo.trackSteps=true` should have written the intermediate XMIRs of the transpile train. The cache-key fingerprint folds plugin version, bundled XSL fingerprint, `trackLocations`, `coverage`, and superclass. `tracking.steps()` is not part of that key. A later build with the flag on takes the leftover previous no-step-files result.

On failing_ref `09ba1e478be7e2ef4fd1293828512ef9d05f38e6`:

```
String version() {
    return String.format(
        "%s-%s-%b-%b-%s",
        this.version,
        new Fingerprint(
            Stream.concat(
                Arrays.stream(Transpilation.XSLS), Arrays.stream(Transpilation.IMPORTS)
            ).toArray(String[]::new)
        ).get(),
        this.tracking.locations(), this.coverage, this.superclass
    );
}
```

`TrSpy` (the writer of step XMIRs) lives inside the transform that only runs on a cache miss. `locations()` is already in the key two fields away. `steps()` is not.

Public report (objectionary/eo#7628). Run 1 default: step files 0. Run 2 `-Deo.trackSteps=true` with shared cache: step files 0. Control with a private cache: step files 10. Warm cache of the previous no-steps identity stays current.

In-tree after the repair (not on failing_ref): `version()` folds `this.tracking.steps()` as a third boolean in the key.

Case A — second transpile, same flags, same XSL fingerprint:
  cache identity is current
  not leftover-after-flag

Case B — trackSteps flipped on, leftover cache hit:
  leftover: previous no-step-files transpile result
  steps() omitted from version() key
  shared cache

Case C — private cache / cache miss:
  fresh step XMIRs
  not leftover previous result

Case D — steps() in the cache key (post-repair shape, not on failing_ref):
  new key after trackSteps change
  not leftover previous result

The developer wants to know which identity case B actually used for the transpile output after the flag change: leftover previous-cache result (steps omitted), current step-writing transform, or omitted (no cache).
""",
        observed="""# OBSERVED

Public objectionary/eo#7628 (closed 2026-08-26). PR 7675 merge `34df04c9a5eb26c6718c9512d930c4653627d70f` (first parent `09ba1e478be7e2ef4fd1293828512ef9d05f38e6`). Local eo was not performed on this lab host.

Issue body: `-Deo.trackSteps=true` writes intermediate XMIRs only on a cache miss; the flag is not part of the cache key. A build that had it off leaves a cached result that a later build with it on takes as it is, producing no step files. Shared-cache BUILD B step files 0; private-cache CONTROL step files 10.

On failing_ref, `Transpilation.version()` formats plugin version, XSL fingerprint, locations(), coverage, superclass. `tracking.steps()` is read only when constructing the Xsline, after the cache lookup.

Not this packet: specimen-117 sbt leftover last-write zinc Analysis. specimen-075 rustc incremental fingerprint. specimen-148 buildah leftover RUN --mount from-stage.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
# eo-maven-plugin Transpilation.version / tracking.steps

# public shape:
# leftover transpile cache after -Deo.trackSteps=true
# version() key omits steps(); locations() is present
# private cache / miss writes the step XMIRs
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""objectionary/eo
  eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java
""",
        source="""repository: objectionary/eo
issue: https://github.com/objectionary/eo/issues/7628
pr: https://github.com/objectionary/eo/pull/7675
failing_ref (first parent of merge on master): 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
fixed_ref (fold tracking.steps into version()): 34df04c9a5eb26c6718c9512d930c4653627d70f
merged_at: 2026-08-26T05:36:55Z
pr_author: morphqdd
merged_by: yegor256
changed_files: eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java, eo-maven-plugin/src/test/java/org/eolang/maven/TranspilationTest.java
pr_title: #7628: fold trackSteps into the transpile cache key
scout_note: not 117 zinc last-write / not 075 rustc fingerprint / not 148 buildah mount-stage. leftover transpile result after trackSteps because steps() omitted from version(). unique vs 001-150.
""",
        answer_key="""KNOWN FIX (sealed): objectionary/eo PR 7675 merge 34df04c9a5eb26c6718c9512d930c4653627d70f.

failing_ref is first parent 09ba1e478be7e2ef4fd1293828512ef9d05f38e6.

Transpilation.version() keyed plugin version + XSL fingerprint + locations() + coverage + superclass. Rotating -Deo.trackSteps=true kept leftover previous no-step-files cache HIT. steps() was not part of the key.

PR repair: fold this.tracking.steps() into version() as a third boolean.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged flags vs leftover no-step-files after trackSteps vs private cache vs steps in key)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — locations() already in the key while steps() was omitted; leftover HIT skipped the writer
ecosystem: eolang / maven transpile cache
mechanism_family: leftover-transpile-cache, omitted-tracksteps-from-cache-key, diagnostic-flag-on-cache-hit

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "transpile_failing.java": """// Reduced excerpt of Transpilation.version cache key on failing_ref
// eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java
// 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
// version() folds locations()/coverage/superclass. steps() omitted.
// leftover previous no-step-files result after -Deo.trackSteps=true.

String version() {
    return String.format(
        "%s-%s-%b-%b-%s",
        this.version,
        new Fingerprint(
            Stream.concat(
                Arrays.stream(Transpilation.XSLS), Arrays.stream(Transpilation.IMPORTS)
            ).toArray(String[]::new)
        ).get(),
        this.tracking.locations(), this.coverage, this.superclass
    );
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  EOLANG Transpilation.version() global transpile cache
  leftover no-step-files result after trackSteps=true

Case A (second transpile, same flags, same XSL fingerprint):
  current cache identity
  not leftover-after-flag

Case B (trackSteps flipped on, leftover cache hit):
  leftover: previous no-step-files transpile result
  steps() omitted from version() key
  shared cache

Case C (private cache / cache miss):
  fresh step XMIRs
  not leftover previous result

Case D (steps() in the cache key):
  new key after trackSteps change
  not leftover previous result

Not this packet:
  sbt leftover last-write zinc Analysis (specimen-117)
  rustc incremental fingerprint (specimen-075)
  buildah leftover RUN --mount from-stage (specimen-148)
""",
        },
    )


def packet_distroless(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: bazel-contrib/rules_distroless
failing_ref: 42dd9a20c5c761e4131325a2cf594a753ffffa2d
fixed_ref: 52a250a1135cd35440a3ff6616fc4f6ebd4819a0
source_issue: https://github.com/bazel-contrib/rules_distroless/pull/237
source_pr: https://github.com/bazel-contrib/rules_distroless/pull/237
mechanism_tags:
  - leftover-apt-facts
  - omitted-snapshot-url-from-fact-key
  - stale-packages-after-snapshot-upgrade
ecosystem: bazel-distroless
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

bazel-contrib `rules_distroless` apt extension can keep the identity of **previous snapshot facts / packages** after the snapshot URL was upgraded and the package index should have been different. The facts cache key is `dist/component/architecture/Packages` (and Contents). Snapshot URLs are not part of that key. Upgrading the snapshot while leaving dist/component/arch the same still returns leftover previous integrity facts and stale packages.

On failing_ref `42dd9a20c5c761e4131325a2cf594a753ffffa2d`:

```
pkg_fact_key = dist + "/" + component + "/" + architecture + "/Packages"
cnt_fact_key = dist + "/" + component + "/" + architecture + "/Contents"
```

`mctx.facts` then serves `glock.facts().get(pkg_fact_key)` as the integrity for a cache HIT. The URL of the snapshot is not in the key.

Public report (bazel-contrib/rules_distroless#237). Same dist/component/arch; snapshot URL flipped from `.../20251001T023456Z` to `.../20240210T223313Z`; leftover previous facts and stale packages. Rolling suites were already filtered; snapshot suites reused the omitted-URL key.

In-tree after the repair (not on failing_ref): `util.index_fact_key(dist, component, architecture, index_type, urls)` appends a sorted-deduplicated URL token; unused previous-URL facts are pruned.

Case A — second fetch, same snapshot URLs, same dist/component/arch:
  cache identity is current
  not leftover-after-upgrade

Case B — snapshot URL upgraded, leftover facts hit:
  leftover: previous integrity / stale packages
  snapshot URL omitted from fact key
  same dist/component/arch

Case C — facts empty / first fetch / rolling suite not cached:
  fresh index identity
  not leftover previous facts

Case D — snapshot URLs in the fact key (post-repair shape, not on failing_ref):
  new facts after snapshot upgrade
  not leftover previous packages

The developer wants to know which identity case B actually used for the package index after the snapshot URL change: leftover previous-facts packages (URL omitted), current snapshot index, or omitted (no facts cache).
""",
        observed="""# OBSERVED

Public bazel-contrib/rules_distroless#237 (merged 2026-07-28). Squash `52a250a1135cd35440a3ff6616fc4f6ebd4819a0` (parent `42dd9a20c5c761e4131325a2cf594a753ffffa2d`). Local rules_distroless was not performed on this lab host.

PR body: the URL of the snapshot was not part of the cache key for facts. Upgrading the snapshot (everything else the same) yielded stale facts and stale packages. Repair bakes snapshot source URLs into the facts key and prunes facts from unused URLs.

On failing_ref, `_fetch_and_parse_sources` builds `pkg_fact_key` from dist/component/architecture only, then `glock.facts().get(pkg_fact_key)` on snapshot suites.

Not this packet: bazel#29298 `env_inherit` action cache local vs remote (SKIP unfixed). specimen-064/070 nix leftover. specimen-136 pants leftover vcs_version.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 42dd9a20c5c761e4131325a2cf594a753ffffa2d
# apt/extensions.bzl pkg_fact_key / mctx.facts

# public shape:
# leftover snapshot facts after snapshot URL upgrade
# fact key is dist/component/arch/Packages; URL omitted
# empty facts / URL in key yields the new index
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""bazel-contrib/rules_distroless
  apt/extensions.bzl
  apt/private/util.bzl
""",
        source="""repository: bazel-contrib/rules_distroless
issue: https://github.com/bazel-contrib/rules_distroless/pull/237
pr: https://github.com/bazel-contrib/rules_distroless/pull/237
failing_ref (parent of squash on main): 42dd9a20c5c761e4131325a2cf594a753ffffa2d
fixed_ref (snapshot URL in facts key): 52a250a1135cd35440a3ff6616fc4f6ebd4819a0
merged_at: 2026-07-28T18:35:23Z
pr_author: blorente
merged_by: thesayyn
changed_files: apt/extensions.bzl, apt/private/util.bzl, apt/tests/BUILD.bazel, apt/tests/facts_test.bzl
pr_title: fix: Add snapshot URL to facts keys
scout_note: not bazel#29298 env_inherit / not 064/070 nix / not 136 pants vcs. leftover apt facts after snapshot URL upgrade because URL omitted from fact key. unique vs 001-150.
""",
        answer_key="""KNOWN FIX (sealed): bazel-contrib/rules_distroless PR 237 squash 52a250a1135cd35440a3ff6616fc4f6ebd4819a0.

failing_ref is parent 42dd9a20c5c761e4131325a2cf594a753ffffa2d.

pkg_fact_key was dist/component/architecture/Packages with snapshot URL omitted. Upgrading the snapshot kept leftover previous facts and stale packages.

PR repair: index_fact_key appends sorted-deduplicated snapshot URLs; prune facts whose keys are not in this run's used_keys.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged snapshot vs leftover facts after URL upgrade vs empty facts vs URL in key)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — dist/component/arch and snapshot URL are different identities; leftover facts stayed current
ecosystem: bazel-distroless / apt facts cache
mechanism_family: leftover-apt-facts, omitted-snapshot-url-from-fact-key, stale-packages-after-snapshot-upgrade

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "facts_failing.bzl": """# Reduced excerpt of apt facts key on failing_ref
# apt/extensions.bzl
# 42dd9a20c5c761e4131325a2cf594a753ffffa2d
# pkg_fact_key is dist/component/arch/Packages. snapshot URL omitted.
# leftover previous integrity after snapshot URL upgrade.

pkg_fact_key = dist + "/" + component + "/" + architecture + "/Packages"
cnt_fact_key = dist + "/" + component + "/" + architecture + "/Contents"
cached_pkg_format = formats.get(pkg_fact_key)
# glock.facts().get(pkg_fact_key) is the leftover integrity on HIT
""",
            "leftover_identity_split.txt": """Registry / fixture:
  rules_distroless apt mctx.facts
  leftover snapshot facts after URL upgrade

Case A (second fetch, same snapshot URLs):
  current cache identity
  not leftover-after-upgrade

Case B (snapshot URL upgraded, leftover facts hit):
  leftover: previous integrity / stale packages
  snapshot URL omitted from fact key
  same dist/component/arch

Case C (facts empty / rolling suite):
  fresh index identity
  not leftover previous facts

Case D (snapshot URLs in the fact key):
  new facts after snapshot upgrade
  not leftover previous packages

Not this packet:
  bazel#29298 env_inherit local vs remote (SKIP unfixed)
  nix leftover (specimen-064/070)
  pants leftover vcs_version (specimen-136)
""",
        },
    )


PACKETS = [
    (None, "hdd-eotrack", packet_eo,
     "eo leftover transpile cache omits trackSteps from version(); not 117/075/148"),
    (None, "hdd-snapurl", packet_distroless,
     "distroless leftover apt facts omit snapshot URL from key; not bazel#29298 / 064/136"),
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
        if old not in {None, worker} and not str(old).startswith("scout-coord-"):
            raise SystemExit(f"{job_id} status=CLAIMED worker={old}")
        job["worker"] = worker
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


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
                if old in {None, WORKER} or str(old).startswith("scout-coord-"):
                    complete(state, jid, result="skip", artifact=artifact)
                else:
                    print(f"not skipping {jid} worker={old}")
        ids = {s.get("id") for s in state.get("specimens") or []}
        reasons = []
        for job_id, spec_id, trial, priority_reason in packed:
            if spec_id not in ids:
                state.setdefault("specimens", []).append({"id": spec_id})
                ids.add(spec_id)
            if job_id is not None:
                job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
                if job is not None and job.get("status") in {"READY", "CLAIMED"}:
                    if job.get("status") == "READY":
                        _claim_job(state, job_id, WORKER)
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
            write_seed(SPECIMENS / spec_id)
            packed.append((job_id, spec_id, trial, priority_reason))
        update_index()
        launch_note = _complete_and_enqueue(packed)
        for job_id, spec_id, trial, _ in packed:
            print(SPECIMENS / spec_id)
            print(f"seed=seeds/{spec_id}.md trial={trial} job={job_id}")
        print(launch_note)
        print(f"ids={[p[1] for p in packed]} worker={WORKER} at={now_jst()}")
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
