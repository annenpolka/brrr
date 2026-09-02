#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet (npm nested-overrides leftover identity).

npm/cli#5850 / PR 8089. Nested override honored on a first install (no lockfile,
no node_modules) but a later `npm install` with those stores present returns
the original (non-overridden) lockfile identity. In-tree: Edge.detach /
reload delete the incoming edge without updating the target OverrideSet, so
the leftover rule stays on the node and its out-edges.

Not specimen-004 / 033 (optional-peer packument fetch, npm/cli#9876 / PR 9877).
Not Honor-KILL bun specimen-082 leftover packages vs optionalPeers mention
after bun remove. Not #8986 leftover overridden versions after deleting the
overrides field (open, no fixed_ref). Not #9359 leftover generic OverrideSet
forwarded through a Link with no matching rule.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, with_state
from update_index import main as update_index

JOB_ID = "job-0335"
WORKER = "scout-job-0335"
TRIAL = "hdd-overleft"
START_N = 95


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
    raise SystemExit("no free specimen id in 095-199")


def packet_for(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: npm/cli
failing_ref: e345cc58ecad0e1e18eefc00638d7fa32966c2b7
fixed_ref: b9225e524074239bd8db9a27f3e9ab72f2b5c09e
source_issue: https://github.com/npm/cli/issues/5850
source_pr: https://github.com/npm/cli/pull/8089
mechanism_tags:
  - leftover-override-set
  - nested-override-lockfile-identity
  - edge-detach-skips-override-update
ecosystem: npm
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

A nested npm `overrides` rule is honored on a first install and ignored on the next install against the same tree. The lockfile identity of the overridden package does not return to the identity it had on the first install, and it also does not match a tree that never declared the nested override.

Public fixture (npm/cli#5850, npm@8.19.2 class; same shape still reported on npm 9/10):

```
{
  "name": "test",
  "version": "1.0.0",
  "engines": { "npm": ">=8.3.0" },
  "dependencies": { "json-server": "^0.17.0" },
  "overrides": {
    "json-server": {
      "package-json": "7.0.0"
    }
  }
}
```

`json-server` declares a dependency on `package-json`. The override is nested under `json-server`, not a top-level `"package-json": "7.0.0"`.

Case A — never nested-overridden (same `json-server` range, no `overrides` field):

```
npm install
```

`package-lock.json` records whatever `package-json` `json-server` actually asked for. `npm audit` reports the vulnerabilities of that original identity. There is no `"overridden"` annotation for `package-json`.

Case B — first install with the nested override, empty stores:

```
rm -rf node_modules package-lock.json
npm install
```

On npm/cli `e345cc58ecad0e1e18eefc00638d7fa32966c2b7`, this is the only install that honors the nested rule. `npm audit` reports 0 vulnerabilities. The lockfile identity of `package-json` is `7.0.0`.

Case C — second `npm install` with lockfile and `node_modules` still present (package.json still contains the nested override; this is not deleting the `overrides` field):

```
npm install
```

`npm audit` reports 5 vulnerabilities. The lockfile identity of `package-json` is no longer `7.0.0`; it matches the original (case A) identity, not case B.

Related public observations on the same failing world:

```
npm update                          # 0 vulnerabilities (override applied again)
rm -rf node_modules && npm install  # 5 vulnerabilities (lockfile leftover)
rm package-lock.json && npm install # 5 vulnerabilities (node_modules leftover)
```

A top-level (non-nested) override `"package-json": "7.0.0"` does **not** show this second-install leftover; only the nested form does.

Case D — in-tree Arborist graph, no registry. Root has `overrides: { baz: "1.0.0" }`, child `bar` depends on `baz`, `baz` depends on `buzz`. After the `bar → baz` edge is detached (the override-carrying incoming edge is gone; `baz` remains in the tree via another path, or is about to be re-linked):

On the failing revision, `baz.overrides` is still the rule copied from that edge (`addEdgeIn` did `this.overrides = edge.overrides`). `Edge.detach` / `reload` only run `this.#to.edgesIn.delete(this)`. `baz.edgesOut.get("buzz").overrides` still names the leftover rule.

The developer wants to know which identity the lockfile / Arborist node actually contained for `package-json` (public) or `baz` (in-tree) after case C / the detach: leftover original / leftover OverrideSet (same as case A, or the stale nested rule), omitted (never-overridden), or the first-install overridden identity (`7.0.0` / `baz@1.0.0`).
""",
        observed="""# OBSERVED

Public npm/cli#5850 (lukekarrys, 2022-11-12) / PR 8089. Failing world: npm@8.19.2 and later 9.x/10.x reports; pinned checkout `e345cc58ecad0e1e18eefc00638d7fa32966c2b7` (merge parent of the squash).

Issue reproduction (nested override only honored on a cold first install):

```
# package.json as in TASK (json-server ^0.17.0, nested package-json 7.0.0)
npm install                         # 0 vulnerabilities
npm install                         # 5 vulnerabilities
npm update                          # 0 vulnerabilities
rm -rf node_modules && npm install  # 5 vulnerabilities
rm package-lock.json && npm install # 5 vulnerabilities
rm -rf node_modules package-lock.json && npm install  # 0 vulnerabilities
```

Expected after every `npm install` while the nested override remains in package.json: lockfile identity of `package-json` stays `7.0.0`; audit stays at 0.

Saw: only the empty-store first install and `npm update` apply the nested rule. Any later `npm install` that can read the existing lockfile or `node_modules` returns the original `package-json` identity. Collaborator note (bnbdr): the same tree with a **top-level** `"package-json": "7.0.0"` override does apply on subsequent installs.

In-tree leftover on the failing revision (`workspaces/arborist/lib/node.js` `addEdgeIn`):

```
  addEdgeIn (edge) {
    if (edge.overrides) {
      this.overrides = edge.overrides
    }

    this.edgesIn.add(edge)
    ...
  }
```

That assignment overwrites `this.overrides` with the incoming edge's set. It does not walk `this.edgesOut`. `get overridden` is `!!(this.overrides && this.overrides.value && this.overrides.name === this.name)` — a leftover set still reports overridden.

`Edge.reload` / `detach` on the failing revision (`workspaces/arborist/lib/edge.js`):

```
    if (newTo !== this.#to) {
      if (this.#to) {
        this.#to.edgesIn.delete(this)
      }
      ...
    }
...
  detach () {
    ...
    if (this.#to) {
      this.#to.edgesIn.delete(this)
    }
    this.#from.edgesOut.delete(this.#name)
    ...
  }
```

`edgesIn.delete` does not recompute the target's OverrideSet from remaining incoming edges. After the override-carrying edge is gone, the leftover set on the node and its out-edges is unchanged.

Parent attach on the failing revision still copies `parent.overrides.getNodeRule(this)` onto the child when a parent is set. That is a different copy path from the incoming-edge leftover.

PR 8089 later added `workspaces/arborist/test/node.js` cases `updateOverridesEdgeInRemoved uses findSpecificOverrideSet for multiple edgesIn` and `should propagate the new override set to the target node`. Those names are not on the failing revision.

This packet is not optional-peer packument fetch of unmet peers (npm/cli#9876), not bun.lock leftover `packages` vs `optionalPeers` mention after `bun remove`, and not leftover overridden versions after deleting the `overrides` field from package.json (#8986, still open).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""# COMMANDS

```
# in-tree on failing_ref e345cc58ecad0e1e18eefc00638d7fa32966c2b7
# (not executed on this lab host)

# case A — never nested-overridden
# package.json dependencies: json-server ^0.17.0; no overrides
npm install
# lockfile identity of package-json is json-server's original range
# npm audit reports that original identity's vulnerabilities
# no overridden annotation for package-json

# case B — first install, empty stores, nested override present
# package.json overrides.json-server.package-json = 7.0.0
rm -rf node_modules package-lock.json
npm install
# npm audit: 0 vulnerabilities
# lockfile identity of package-json is 7.0.0

# case C — leftover original identity; nested override still in package.json
npm install
# npm audit: 5 vulnerabilities
# lockfile identity of package-json matches case A, not 7.0.0

# public #5850 variants
# npm update                          → 0 vulnerabilities
# rm -rf node_modules && npm install  → 5 vulnerabilities
# rm package-lock.json && npm install → 5 vulnerabilities

# case D — in-tree: detach the override-carrying incoming edge
# baz.overrides still the leftover set
# baz.edgesOut.get('buzz').overrides still names that set
# Edge.detach only ran edgesIn.delete

# unit tests live in workspaces/arborist/test/node.js
# production paths: workspaces/arborist/lib/node.js (addEdgeIn)
#                   workspaces/arborist/lib/edge.js (reload, detach)
```

Not executed on this lab host.
""",
        tree="""npm/cli
  workspaces/arborist/lib/node.js
  workspaces/arborist/lib/edge.js
  workspaces/arborist/lib/override-set.js
  workspaces/arborist/test/node.js
""",
        source="""repository: npm/cli
issue: https://github.com/npm/cli/issues/5850
pr: https://github.com/npm/cli/pull/8089
related_pr: https://github.com/npm/cli/pull/7025
failing_ref (squash merge parent): e345cc58ecad0e1e18eefc00638d7fa32966c2b7
fixed_ref (squash merge commit): b9225e524074239bd8db9a27f3e9ab72f2b5c09e
head_sha: 9feb44c99f06bb4ca83abbefa3174e5e1654227f
merged_at: 2025-02-26T17:12:42Z
merged_by: wraithgar
changed_files: workspaces/arborist/lib/dep-valid.js, workspaces/arborist/lib/edge.js, workspaces/arborist/lib/node.js, workspaces/arborist/lib/override-set.js, workspaces/arborist/tap-snapshots/test/edge.js.test.cjs, workspaces/arborist/test/edge.js, workspaces/arborist/test/node.js, workspaces/arborist/test/override-set.js
pr_title: fix: resolve override conflicts and apply correct versions
scout_note: not specimen-004/033 optional-peer packument fetch (npm/cli#9876). not specimen-082/Honor-KILL peerleft (bun.lock leftover packages vs optionalPeers mention after bun remove). not #8986 leftover overridden lockfile identity after deleting the overrides field (open, no fixed_ref). not #9359 leftover generic OverrideSet forwarded through a Link with no matching rule. Distinct leftover: nested override json-server.package-json=7.0.0 honored only on empty-store first install / npm update; subsequent npm install returns original package-json identity. In-tree: addEdgeIn overwrites this.overrides; detach/reload delete the incoming edge without recomputing the target OverrideSet, so out-edges keep the leftover rule.
""",
        answer_key="""KNOWN FIX (sealed): npm/cli PR 8089 squash merge b9225e524074239bd8db9a27f3e9ab72f2b5c09e.

failing_ref is squash-merge parent e345cc58ecad0e1e18eefc00638d7fa32966c2b7.

addEdgeIn assigned `this.overrides = edge.overrides` and did not walk edgesOut. Edge.detach / reload removed the incoming edge with `edgesIn.delete` and left the target OverrideSet in place, so nested override identity leaked onto later installs from the leftover lockfile / node_modules graph (public: json-server nested package-json@7.0.0 honored only on first empty-store install; subsequent npm install restored the original package-json identity and 5 audit hits).

Repair: Node.deleteEdgeIn calls updateOverridesEdgeInRemoved (recompute from remaining edgesIn, then recalculateOutEdgesOverrides). addEdgeIn / updateOverridesEdgeInAdded pick the more specific OverrideSet via OverrideSet.findSpecificOverrideSet instead of last-write. Edge.reload propagates a changed override set to the target even when `newTo === this.#to`. node.overridden now requires an incoming edge whose override value equals this.version and is not equal to edge.from.overrides. Tests added in workspaces/arborist/test/node.js cover EdgeInRemoved / EdgeInAdded / reload propagation.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (never-overridden original identity vs first-install 7.0.0 vs subsequent leftover original vs npm-update re-apply vs top-level override that does not leftover vs in-tree leftover OverrideSet after edge detach)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two stores (package.json nested override vs lockfile/node_modules identity) disagree after a no-op second install; leftover is the OverrideSet on the node after the carrying edge is gone, not a missing first-install
ecosystem: npm / node
mechanism_family: leftover-override-set, nested-override-lockfile-identity, edge-detach-skips-override-update

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "add_edge_in_failing.js": """// Reduced excerpt of Node.addEdgeIn on failing_ref
// workspaces/arborist/lib/node.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// Incoming override set overwrites this.overrides. Out-edges are not walked.

  addEdgeIn (edge) {
    if (edge.overrides) {
      this.overrides = edge.overrides
    }

    this.edgesIn.add(edge)

    // try to get metadata from the yarn.lock file
    if (this.root.meta) {
      this.root.meta.addEdge(edge)
    }
  }
""",
            "reload_detach_failing.js": """// Reduced excerpt of Edge.reload / detach on failing_ref
// workspaces/arborist/lib/edge.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// Target OverrideSet is not recomputed when the incoming edge is dropped.

  reload (hard = false) {
    this.#explanation = null
    if (this.#from.overrides) {
      this.overrides = this.#from.overrides.getEdgeRule(this)
    } else {
      delete this.overrides
    }
    const newTo = this.#from.resolve(this.#name)
    if (newTo !== this.#to) {
      if (this.#to) {
        this.#to.edgesIn.delete(this)
      }
      this.#to = newTo
      this.#error = null
      if (this.#to) {
        this.#to.addEdgeIn(this)
      }
    } else if (hard) {
      this.#error = null
    }
  }

  detach () {
    this.#explanation = null
    if (this.#to) {
      this.#to.edgesIn.delete(this)
    }
    this.#from.edgesOut.delete(this.#name)
    this.#to = null
    this.#error = 'DETACHED'
    this.#from = null
  }
""",
            "overridden_failing.js": """// Reduced excerpt of Node.overridden on failing_ref
// workspaces/arborist/lib/node.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// A leftover OverrideSet with name+value still reports overridden.

  get overridden () {
    return !!(this.overrides && this.overrides.value && this.overrides.name === this.name)
  }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  json-server@^0.17.0 (public #5850)
  nested override: json-server.package-json = 7.0.0
  in-tree: root overrides baz=1.0.0; bar depends on baz; baz depends on buzz

Case A (never nested-overridden):
  npm install
  package-json lockfile identity = json-server's original range
  npm audit reports that original identity
  no overridden annotation for package-json
  in-tree: baz.overrides undefined (or parent generic set with no baz value)

Case B (first install, empty stores, nested override present):
  rm -rf node_modules package-lock.json && npm install
  package-json lockfile identity = 7.0.0
  npm audit: 0 vulnerabilities
  in-tree: baz.overridden true when version is 1.0.0

Case C (second install; nested override still in package.json):
  npm install
  leftover original package-json identity (matches case A, not 7.0.0)
  npm audit: 5 vulnerabilities
  rm -rf node_modules && npm install  → still leftover (lockfile)
  rm package-lock.json && npm install → still leftover (node_modules)
  npm update                          → 7.0.0 again

Case D (in-tree detach of the override-carrying incoming edge):
  Edge.detach / reload: edgesIn.delete only
  leftover: baz.overrides still the copied set
  leftover: baz.edgesOut.get('buzz').overrides still names that set
  Node.overridden still true if name+value match

Not this packet:
  optional-peer packument fetch of unmet peers (specimen-004 / 033, npm/cli#9876)
  bun.lock leftover packages vs optionalPeers mention after bun remove (specimen-082)
  leftover overridden versions after deleting the overrides field (#8986, unfixed)
  leftover generic OverrideSet forwarded through a Link with no matching rule (#9359)
  top-level (non-nested) override, which does apply on subsequent installs
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == JOB_ID), None)
        if job is None:
            raise SystemExit(f"{JOB_ID} missing")
        if job.get("status") == "CLAIMED" and job.get("worker") == WORKER:
            complete(state, JOB_ID, result="ok", artifact=f"specimens/{spec_id}")
        elif job.get("status") == "DONE" and job.get("artifact") == f"specimens/{spec_id}":
            pass
        else:
            raise SystemExit(
                f"{JOB_ID} status={job.get('status')} worker={job.get('worker')} artifact={job.get('artifact')}"
            )
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
                priority_reason="npm nested-overrides leftover identity; not 004/033/082",
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if len(claimed_r1) >= 2:
            note["reason"] = (
                "dream.sh not launched; 2+ R1 already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        else:
            note["reason"] = (
                "dream.sh not launched from scout; READY_R1_DREAM enqueued "
                f"trial={TRIAL} (coordinator owns dreamer slots)"
            )
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_for(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(f"enqueued READY_R1_DREAM trial={TRIAL} specimen={spec_id}")
        print(launch_note)
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
