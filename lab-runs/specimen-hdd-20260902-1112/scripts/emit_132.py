#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 132.

Packed (unique vs 001-131; 075 not overwritten; not bazel#29298):
1) eslint/eslint#16284 / PR 16992: leftover lint cache after plugin
   upgrade because FlatConfigArray toJSON serialized plugins as
   Object.keys(plugins) only — plugin name@version omitted from cache
   identity. Distinct from 114 ruff nested pyproject cache and 107
   pytest cache-dir supporting files.

SKIP (this tick; no unique leftover-identity pair):
- job-0565 nuget leftover packages.lock vs assets: NuGet/Home#10056/
  #14015/#10456/#9372 still OPEN. not inventing refs.
- job-0566 cabal leftover unit-id: haskell/cabal#6488 still OPEN, no PR.
  not inventing refs.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 132
WORKER = "scout-coord-1848"
JOB_PACK = None  # packed from leftover hunt after 0555 was other-worker SKIP
TRIAL = "hdd-eslplug"
SKIP_JOBS = {
    "job-0565": (
        "skip nuget leftover packages.lock vs assets file identity: "
        "NuGet/Home#10056/#14015/#10456/#9372 still OPEN. not inventing refs"
    ),
    "job-0566": (
        "skip cabal leftover store unit-id vs library identity: "
        "haskell/cabal#6488 still OPEN no PR. not inventing refs"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: stylelint leftover cache vs config identity not 132/114/107",
        "unique stylelint cache leftover",
    ),
    (
        "public OSS: prettier leftover cache vs plugin metadata not 132",
        "unique prettier plugin-cache leftover if pinned",
    ),
    (
        "public OSS: golangci-lint leftover cache vs config identity not 114",
        "unique golangci cache leftover",
    ),
    (
        "public OSS: nuget leftover packages.lock vs assets if Home leftover merges",
        "unique nuget lock leftover if pinned",
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


def packet_eslint(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: eslint/eslint
failing_ref: b3634f695ddab6a82c0a9b1d8695e62b60d23366
fixed_ref: 1665c029acb92bf8812267f1647ad1a7054cbcb4
source_issue: https://github.com/eslint/eslint/issues/16284
source_pr: https://github.com/eslint/eslint/pull/16992
mechanism_tags:
  - leftover-eslint-cache
  - omitted-plugin-meta
  - flat-config-serialization
ecosystem: eslint
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

ESLint's `--cache` can keep the identity of a **previous lint result** after a plugin upgrade should have been a different cache object. Flat config serialization used as the cache identity listed plugins as namespaces only. Plugin `name@version` / `meta.name`+`meta.version` are omitted, so leftover cache after `eslint-plugin-react` 7.37.1 → 7.37.7 still hits.

On failing_ref `b3634f695ddab6a82c0a9b1d8695e62b60d23366`, `FlatConfigArray` `toJSON` does:

```
plugins: Object.keys(plugins),
```

Parser/processor objects already used `getObjectId` (name@version). Plugins did not.

Public report (eslint/eslint#16284): upgrade eslint-plugin-react; leftover cache suppresses new-rule offenses.

In-tree after the repair (not on failing_ref): serialize each plugin as `namespace:name@version` via `getObjectId`; tests convert config with plugin name/version and plugin meta into normalized JSON.

Case A — second `eslint --cache` with unchanged plugin version:
  cache identity is current
  not leftover-after-plugin-upgrade

Case B — plugin upgrade, leftover cache:
  leftover: previous plugin version's lint results
  plugin name@version omitted from serialized config identity
  new-rule offenses not reported

Case C — delete `.eslintcache` then lint:
  fresh cache identity
  not leftover previous plugin

Case D — plugin meta in serialized config (post-repair shape, not on failing_ref):
  cache miss after plugin upgrade
  not leftover previous plugin results

The developer wants to know which identity case B actually used for the ESLint cache after the plugin upgrade: leftover previous-plugin results (meta omitted), current plugin-version identity, or omitted (no cache file).
""",
        observed="""# OBSERVED

Public eslint/eslint#16284 (closed 2023-03-23). PR 16992 squash `1665c029acb92bf8812267f1647ad1a7054cbcb4` (parent `b3634f695ddab6a82c0a9b1d8695e62b60d23366`). Local ESLint was not performed on this lab host.

Issue body: leftover cache after eslint-plugin-react upgrade hid new-rule offenses. Related eslintrc#88 is not this packet (legacy eslintrc cache).

On failing_ref, `toJSON` serializes plugins as `Object.keys(plugins)` only. `getObjectId` for plugins is **not** on the failing revision. It is added by PR 16992.

Not this packet: specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files. specimen-128 dart leftover package_config missing workspace member.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref b3634f695ddab6a82c0a9b1d8695e62b60d23366
# lib/config/flat-config-array.js FlatConfigArray toJSON plugins: Object.keys(plugins)

# public shape:
# leftover .eslintcache after eslint-plugin-react 7.37.1 -> 7.37.7
# plugin name@version omitted from serialized config identity
# new-rule offenses not reported
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""eslint/eslint
  lib/config/flat-config-array.js
  tests/lib/config/flat-config-array.js
  docs/src/extend/plugins.md
  .eslintcache
""",
        source="""repository: eslint/eslint
issue: https://github.com/eslint/eslint/issues/16284
pr: https://github.com/eslint/eslint/pull/16992
failing_ref (parent of squash on main): b3634f695ddab6a82c0a9b1d8695e62b60d23366
fixed_ref (Use plugin metadata for flat config serialization): 1665c029acb92bf8812267f1647ad1a7054cbcb4
merged_at: 2023-03-23T19:47:52Z
pr_author: nzakas
merged_by: mdjermanovic
changed_files: lib/config/flat-config-array.js, tests/lib/config/flat-config-array.js, docs/src/extend/plugins.md
pr_title: feat: Use plugin metadata for flat config serialization
scout_note: not 114 ruff nested pyproject. not 107 pytest cache-dir files. Distinct leftover: serialized flat config omits plugin name@version so leftover cache after plugin upgrade is treated as current. job-0555 was other-worker SKIP; this pair is leftover plugin-meta vs cache identity.
""",
        answer_key="""KNOWN FIX (sealed): eslint/eslint PR 16992 squash 1665c029acb92bf8812267f1647ad1a7054cbcb4.

failing_ref is parent b3634f695ddab6a82c0a9b1d8695e62b60d23366.

toJSON serialized plugins as Object.keys(plugins) only, so leftover cache after plugin upgrade kept previous-plugin lint results.

PR repair: serialize plugins as namespace:getObjectId(plugin) (name@version / meta.name+meta.version).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged plugin vs leftover cache after upgrade vs wipe vs meta in identity)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — plugin identity and serialized config identity are different objects; name@version omitted so leftover cache stayed current
ecosystem: eslint / js lint cache
mechanism_family: leftover-eslint-cache, omitted-plugin-meta, flat-config-serialization

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "flat_config_tojson_failing.js": """// Reduced excerpt of FlatConfigArray toJSON on failing_ref
// lib/config/flat-config-array.js
// b3634f695ddab6a82c0a9b1d8695e62b60d23366
// Plugins serialized as namespaces only. Plugin name@version omitted.

                return {
                    ...this,
                    plugins: Object.keys(plugins),
                    languageOptions: {
                        ...languageOptions,
                        parser: parserName
                    },
                    processor: processorName
                };
""",
            "leftover_identity_split.txt": """Registry / fixture:
  eslint --cache with eslint-plugin-react 7.37.1
  leftover .eslintcache after upgrade to 7.37.7

Case A (second lint, same plugin version):
  current cache identity
  not leftover-after-plugin-upgrade

Case B (plugin upgrade, leftover cache):
  leftover: previous plugin version results
  plugin name@version omitted from serialized config
  new-rule offenses not reported

Case C (delete .eslintcache):
  fresh cache identity
  not leftover previous plugin

Case D (plugin meta in serialized config):
  cache miss after upgrade
  not leftover previous plugin results

Not this packet:
  ruff leftover cache vs nested pyproject (specimen-114)
  pytest leftover cache-dir supporting files (specimen-107)
  dart leftover package_config missing workspace member (specimen-128)
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
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if not already:
            enqueue(
                state,
                "READY_R1_DREAM",
                input_ref=f"seeds/{spec_id}.md trial={TRIAL}",
                expected_output="0001-dreamer.md",
                kill_condition="15m",
                estimated_cost="r1",
                priority_reason=(
                    "eslint leftover cache omits plugin name@version from "
                    "serialized flat config; not 114/107/128"
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
        path = emit(packet_eslint(spec_id))
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
