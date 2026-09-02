#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets from 125.

Never overwrite specimen-123/124 (earthly CACHE --id, 124==123 class).
075 not overwritten. Not bazel#29298.

Packed (unique vs 001-124):
1) astral-sh/uv#11479 / PR 11513: leftover extras conflict-marker
   identity simplified to true in uv.lock. Distinct from extraedge/
   080/098/006/102/106. Coord skipped job-0528 citing uv#20078 (not
   leftover previous extras object); this pair is leftover extras
   marker vs lock identity.
2) npm/cli#9659 / PR 9671: leftover original identity because a nested
   root override never crosses a file:/workspace Link. Distinct from
   004/033 and 095 (subsequent-install OverrideSet). Coord skipped
   job-0530 as already 095; this is a different leftover nested axis.
3) gradle/gradle#36392 / PR 38432: leftover CC named-file absolute
   paths after copy/move because cache identity omits build location.
   Distinct from 104 ccnamed leftover root base dir and 088 fileTree.
   Coord skipped job-0531 as already 104; this is a unique CC axis.

SKIP hunts (no merged leftover-identity pair this tick):
- go work leftover use vs replace: already 084/103; #54264 open
- sccache leftover vs command identity: mozilla/sccache#2798 CPATH open
- ccache leftover vs compiler identity: ccache#958 open
- cabal store leftover: no merged pair
- mix compile leftover: job-0517 was mix.lock; elixir#13298 no PR;
  #14189 leftover .beam still open
- buck2 action cache leftover: facebook/buck2#976 open
- cargo sparse (#11165 open). terraform omit (081/118). bun catalog
  (082/100). nix narHash (064/070/092).
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 125
WORKER = "scout-leftover-125"
PACKED = [
    (
        None,
        WORKER,
        "hdd-uvxmark",
        "uv leftover extras conflict-marker simplified to true in lock; not extraedge/006/102/106",
    ),
    (
        None,
        WORKER,
        "hdd-overlink",
        "npm leftover original identity: nested override omitted across file: Link; not 004/033/095",
    ),
    (
        None,
        WORKER,
        "hdd-ccreloc",
        "gradle leftover CC named-file abs paths after relocate; location omitted; not 104/088",
    ),
]
NEXT_SCOUTS = [
    (
        "public OSS: mix compile leftover .beam vs manifest identity not mix.lock 074",
        "unique mix compile leftover",
    ),
    (
        "public OSS: cabal store leftover unit-id vs library identity not 001-124",
        "unique cabal store leftover",
    ),
    (
        "public OSS: sccache leftover cache vs command identity CPATH not 075/086 if #2798 merges",
        "unique sccache command leftover if pinned",
    ),
    (
        "public OSS: buck2 action cache leftover vs command identity not bazel#29298",
        "unique buck2 leftover",
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


def packet_uv(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: astral-sh/uv
failing_ref: 2bda549bcca67f06df602901ad9cdf30d35add00
fixed_ref: 91593d42d990397695a15750dcb8453c62a71b7d
source_issue: https://github.com/astral-sh/uv/issues/11479
source_pr: https://github.com/astral-sh/uv/pull/11513
mechanism_tags:
  - leftover-extras-conflict-marker
  - omitted-extra-from-lock-identity
  - simplified-to-true
ecosystem: uv
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

uv's lock can keep the identity of a **previous extra-gated package version as unconditional** after a later extra activation should have been a different lock object. `simplify_conflict_markers` treats extras-known-to-be-enabled inferences as always-true, so an extras conflict marker is omitted (simplified to `true`) from `uv.lock`.

On failing_ref `2bda549bcca67f06df602901ad9cdf30d35add00`, `simplify_conflict_markers` walks every edge and, if all inference sets satisfy the conflict marker, calls `assume_conflict_item` / `assume_not_conflict_item`. Ambiguous edges (two outgoing edges with the same package name, e.g. sympy 1.13.1 and sympy 1.13.3) are **not** skipped.

Public report (astral-sh/uv#11479). `uv sync -p 3.12` installs only `torch==2.5.1`. `uv sync -p 3.12 --extra m3gnet` installs both `torch==2.2.0` and leftover `torch==2.5.1`, plus two sympy versions. Lock excerpt for always-required `e3nn`:

```
[[package]]
name = "e3nn"
dependencies = [
    { name = "sympy", version = "1.13.1", source = { registry = "https://pypi.org/simple" } },
    { name = "sympy", version = "1.13.3", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-4-test-alignn' or extra == 'extra-4-test-m3gnet'" },
    { name = "torch", version = "2.2.0", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-4-test-alignn' or extra == 'extra-4-test-m3gnet'" },
    { name = "torch", version = "2.5.1", source = { registry = "https://pypi.org/simple" } },
]
```

The extras marker for sympy 1.13.1 / torch 2.5.1 was simplified to true. Those versions are leftover unconditional identity.

In-tree after the repair (not on failing_ref): skip simplification when `ambiguous_edges > 1`; test `duplicate_torch_and_sympy_because_of_wrong_inferences`.

Case A — `uv sync` with no extras (production only):
  torch 2.5.1 is the production identity
  not leftover extras-marker identity

Case B — `uv sync --extra m3gnet` with leftover lock that omitted extras markers:
  leftover: torch 2.5.1 / sympy 1.13.1 as unconditional
  extras marker omitted from lock identity
  also installs torch 2.2.0 / sympy 1.13.3 (extra-gated)

Case C — lock written with extras markers kept (post-repair shape, not on failing_ref):
  extra-gated versions stay extra-gated
  not leftover unconditional identity

Case D — delete `uv.lock` then `uv lock` with extras declared as conflicts:
  fresh lock identity
  not leftover simplified-to-true markers

The developer wants to know which identity case B actually left in `uv.lock` for e3nn→torch 2.5.1: leftover unconditional (extras marker omitted), extra-gated marker for m3gnet, or omitted (no torch 2.5.1 edge).
""",
        observed="""# OBSERVED

Public astral-sh/uv#11479 (closed 2025-02-18). PR 11513 rebase tip `91593d42d990397695a15750dcb8453c62a71b7d` (series parent `2bda549bcca67f06df602901ad9cdf30d35add00`). Local uv was not performed on this lab host.

Issue body: `uv sync --extra m3gnet` installs two torch versions and two sympy versions because some e3nn edges have extras conflict markers simplified to true.

On failing_ref, `simplify_conflict_markers` does not skip ambiguous same-name edges. `assume_conflict_item` can drop the extras marker from lock identity. The skip for `ambiguous_edges > 1` is **not** on the failing revision. It is added by PR 11513.

Not this packet: extraedge / specimen-080 / specimen-098 extras CLI. specimen-006 (uv CI cache leftover fingerprints). specimen-102 (uv leftover git vs directory in lock). specimen-106 (pdm extra path URL expanded). specimen-123/124 earthly leftover CACHE --id unexpanded ARG.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 2bda549bcca67f06df602901ad9cdf30d35add00
# crates/uv-resolver/src/graph_ops.rs simplify_conflict_markers

# public shape:
# leftover e3nn -> torch 2.5.1 with extras marker omitted (true)
# uv sync --extra m3gnet installs torch 2.2.0 AND leftover 2.5.1
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""astral-sh/uv
  crates/uv-resolver/src/graph_ops.rs
  crates/uv-resolver/src/resolution/output.rs
  crates/uv/tests/it/lock_conflict.rs
  uv.lock
""",
        source="""repository: astral-sh/uv
issue: https://github.com/astral-sh/uv/issues/11479
pr: https://github.com/astral-sh/uv/pull/11513
failing_ref (parent of first rebased PR commit on main): 2bda549bcca67f06df602901ad9cdf30d35add00
fixed_ref (conflict-marker simplification skip): 91593d42d990397695a15750dcb8453c62a71b7d
test_commit: aaf3429e3f1ef3ba31692b50664409d1b3b6b3c1
merged_at: 2025-02-18T12:45:24Z
pr_author: BurntSushi
merged_by: BurntSushi
changed_files: crates/uv-resolver/src/graph_ops.rs, crates/uv-resolver/src/resolution/output.rs, crates/uv/tests/it/lock_conflict.rs, crates/uv/tests/it/lock.rs
pr_title: fix duplicate packages with multiple conflicting extras declared
scout_note: not extraedge/080/098 extras CLI. not specimen-006/102/106. not 123/124 earthly CACHE --id. Distinct leftover: extras conflict marker simplified to true so leftover extra-gated version is unconditional lock identity. job-0528 was coord-skipped citing uv#20078; this pair is leftover extras-marker vs lock.
""",
        answer_key="""KNOWN FIX (sealed): astral-sh/uv PR 11513 commit 91593d42d990397695a15750dcb8453c62a71b7d.

failing_ref is series parent 2bda549bcca67f06df602901ad9cdf30d35add00.

simplify_conflict_markers applied extras inferences to ambiguous same-name edges and omitted extras markers (simplified to true), so leftover unconditional torch/sympy identity stayed in uv.lock after extra activation.

PR repair: skip conflict-marker simplification when ambiguous_edges > 1 (two outgoing edges with the same package name).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (no-extra sync vs leftover unconditional after extra vs markers kept vs wipe lock)
reproducibility: source-backed issue+PR + pinned parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — extras-marker identity and lock production identity are different objects; leftover true-marker blocked extra-gated isolation
ecosystem: uv / python lock
mechanism_family: leftover-extras-marker, omitted-from-lock, simplified-to-true

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "simplify_conflict_markers_failing.rs": """// Reduced excerpt of simplify_conflict_markers on failing_ref
// crates/uv-resolver/src/graph_ops.rs
// 2bda549bcca67f06df602901ad9cdf30d35add00
// Ambiguous same-name edges are not skipped.
// Extras inferences can simplify a conflict marker to true.

    for edge_index in (0..graph.edge_count()).map(EdgeIndex::new) {
        let (from_index, _) = graph.edge_endpoints(edge_index).unwrap();
        let Some(inference_sets) = inferences.get(&from_index) else {
            continue;
        };
        let all_paths_satisfied = inference_sets.iter().all(|set| {
            graph[edge_index].conflict().evaluate(&extras, &groups)
        });
        if !all_paths_satisfied {
            continue;
        }
        for set in inference_sets {
            for inf in set {
                if inf.included {
                    graph[edge_index].assume_conflict_item(&inf.item);
                } else {
                    graph[edge_index].assume_not_conflict_item(&inf.item);
                }
            }
        }
    }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  pyproject extras chgnet/sevennet/all/alignn/m3gnet with conflicts
  leftover uv.lock e3nn -> torch 2.5.1 / sympy 1.13.1 with extras marker omitted

Case A (uv sync, no extras):
  torch 2.5.1 production identity
  not leftover extras-marker

Case B (uv sync --extra m3gnet, leftover true markers):
  leftover: torch 2.5.1 / sympy 1.13.1 unconditional
  also extra-gated torch 2.2.0 / sympy 1.13.3
  extras marker omitted from lock identity

Case C (extras markers kept on ambiguous edges):
  extra-gated stay extra-gated
  not leftover unconditional

Case D (delete uv.lock then lock):
  fresh identity
  not leftover simplified-to-true

Not this packet:
  extraedge / specimen-080 / specimen-098 extras CLI
  uv CI cache leftover fingerprints (specimen-006)
  uv leftover git vs directory (specimen-102)
  pdm extra path URL expanded (specimen-106)
  earthly leftover CACHE --id unexpanded ARG (specimen-123/124)
""",
        },
    )


def packet_npm(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: npm/cli
failing_ref: ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
fixed_ref: 968e42fbd62eb3a6f446466359c9431f41d76b2b
source_issue: https://github.com/npm/cli/issues/9659
source_pr: https://github.com/npm/cli/pull/9671
mechanism_tags:
  - leftover-override-across-file-link
  - omitted-overrideset-on-link-target
  - nested-transitive-original-identity
ecosystem: npm
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

npm's arborist can keep the identity of a **previous un-overridden transitive package** after a root `overrides` rule should have been a different lock object, when the path to that package crosses a `file:` / workspace Link. A Link and its target are not edge-connected. Override forwarding to the target ran while the target subtree was still unbuilt, so the guard found no matching rule and never forwarded.

On failing_ref `ae6dbeb12a6f4b313a28c99068e34ba834ae91d1`, `#buildDepStep` queues `link.target` without `link.target.updateOverridesEdgeInAdded(link.overrides)`. `#repropagateOverrides` runs after `#transplant`, before the actual tree's edges are fully resolved.

Public report (npm/cli#9659):

```
// package.json
{
  "name": "root",
  "dependencies": { "a": "file:./pkgs/a" },
  "overrides": { "brace-expansion": "2.0.1" }
}

// pkgs/a/package.json
{ "name": "a", "version": "1.0.0", "dependencies": { "glob": "7.2.0" } }
```

After `npm install`, lock/install identity is leftover `brace-expansion@1.1.15` (original), not overridden `2.0.1`. Same under hoisted and linked. The identical override works when `glob` is a direct root dependency (no Link boundary).

In-tree after the repair (not on failing_ref): forward `link.overrides` before the target subtree resolves; `#repropagateOverrides` after `calcDepFlags`; tests `overrides a nested dependency reached through a file: link`.

Case A — override path does not cross a Link (root depends on glob directly):
  lock identity is overridden 2.0.1
  not leftover original

Case B — override path crosses `file:./pkgs/a`, leftover original brace-expansion:
  leftover: 1.1.15 un-overridden identity
  nested override omitted on the Link target
  lock pins leftover original

Case C — delete node_modules + lock then install with no overrides:
  original identity is correct (not leftover of an override)

Case D — override forwarded before subtree resolve (post-repair shape, not on failing_ref):
  lock identity is 2.0.1
  not leftover original

The developer wants to know which identity case B actually left in the lock for brace-expansion: leftover original 1.1.15, overridden 2.0.1, or omitted (no brace-expansion).
""",
        observed="""# OBSERVED

Public npm/cli#9659 (closed 2026-06-26). PR 9671 squash `968e42fbd62eb3a6f446466359c9431f41d76b2b` (parent `ae6dbeb12a6f4b313a28c99068e34ba834ae91d1`). Local npm was not performed on this lab host.

Issue body: root override targeting a transitive dep is silently ignored when the path crosses a file:/workspace link; lock pins the original version; no warning.

On failing_ref, Link target is queued without forwarding OverrideSet. `#repropagateOverrides` exists for store links (#9619) but runs too early for a file: link whose subtree resolves late. Forward-before-queue is **not** on the failing revision. It is added by PR 9671.

Not this packet: specimen-004/033 optional-peer leftover (npm/cli#9876). specimen-095 nested override honored only on empty-store first install; subsequent install leftover original via addEdgeIn overwrite (npm/cli#5850). npm/cli#8986 leftover after deleting overrides (open). specimen-123/124 earthly leftover CACHE --id.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
# workspaces/arborist/lib/arborist/build-ideal-tree.js #buildDepStep
# workspaces/arborist/lib/arborist/load-actual.js #repropagateOverrides

# public shape:
# leftover brace-expansion@1.1.15 across file: link
# overrides { brace-expansion: 2.0.1 } omitted on Link target
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""npm/cli
  workspaces/arborist/lib/arborist/build-ideal-tree.js
  workspaces/arborist/lib/arborist/load-actual.js
  workspaces/arborist/lib/override-set.js
  package-lock.json
""",
        source="""repository: npm/cli
issue: https://github.com/npm/cli/issues/9659
pr: https://github.com/npm/cli/pull/9671
failing_ref (squash parent): ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
fixed_ref (squash merge): 968e42fbd62eb3a6f446466359c9431f41d76b2b
merged_at: 2026-06-26T13:30:43Z
pr_author: manzoorwanijk
merged_by: owlstronaut
changed_files: workspaces/arborist/lib/arborist/build-ideal-tree.js, workspaces/arborist/lib/arborist/load-actual.js, workspaces/arborist/test/arborist/build-ideal-tree.js, workspaces/arborist/test/arborist/load-actual.js
pr_title: fix(arborist): apply overrides across a file:/workspace link boundary
scout_note: not specimen-004/033 optional-peer leftover. not specimen-095 subsequent-install OverrideSet leftover. Distinct leftover: nested root override omitted across file: Link so leftover original transitive identity stays in the lock. job-0530 was coord-skipped as already 095; this axis is leftover original across Link, not leftover OverrideSet after subsequent install.
""",
        answer_key="""KNOWN FIX (sealed): npm/cli PR 9671 squash 968e42fbd62eb3a6f446466359c9431f41d76b2b.

failing_ref is squash parent ae6dbeb12a6f4b313a28c99068e34ba834ae91d1.

Link target was queued without forwarding OverrideSet; nested override never reached descendant edges; leftover original version was locked.

PR repair: updateOverridesEdgeInAdded(link.overrides) before the target subtree resolves; #repropagateOverrides after calcDepFlags.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (direct override vs leftover original across file: Link vs no-override original vs forwarded OverrideSet)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — Link identity and target OverrideSet identity are different objects; leftover original blocked the nested override
ecosystem: npm / arborist
mechanism_family: leftover-override, omitted-overrideset, file-link-boundary

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "build_ideal_link_failing.js": """// Reduced excerpt of #buildDepStep link-target queue on failing_ref
// workspaces/arborist/lib/arborist/build-ideal-tree.js
// ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
// Link target is queued. OverrideSet is not forwarded first.

          !link.target.parent &&
          !link.target.fsParent ||
          unseenLink) {
        this.addTracker('idealTree', link.target.name, link.target.location)
        this.#depsQueue.push(link.target)
      }

// load-actual.js: #repropagateOverrides runs after #transplant,
// before the actual tree's edges are fully resolved for a file: link.
""",
            "leftover_identity_split.txt": """Registry / fixture:
  root overrides { brace-expansion: 2.0.1 }
  a via file:./pkgs/a depends on glob@7.2.0
  leftover lock brace-expansion@1.1.15

Case A (glob is a direct root dep, no Link):
  overridden 2.0.1
  not leftover original

Case B (path crosses file: link, leftover original):
  leftover: 1.1.15 un-overridden
  nested override omitted on Link target

Case C (no overrides field):
  original identity is correct
  not leftover of an override

Case D (OverrideSet forwarded before subtree):
  2.0.1
  not leftover original

Not this packet:
  optional-peer leftover (specimen-004/033)
  nested override subsequent-install leftover OverrideSet (specimen-095)
  leftover after deleting overrides (npm/cli#8986 open)
  earthly leftover CACHE --id (specimen-123/124)
""",
        },
    )


def packet_gradle(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: gradle/gradle
failing_ref: e0ca283b48bc739f14140b8a61565d689758c032
fixed_ref: 24311263532f820ba81399b662ae3d53eebe28b9
source_issue: https://github.com/gradle/gradle/issues/36392
source_pr: https://github.com/gradle/gradle/pull/38432
mechanism_tags:
  - leftover-cc-after-relocation
  - omitted-build-location-from-cc-identity
  - leftover-named-file-absolute-paths
ecosystem: gradle
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Gradle configuration cache can keep the identity of **named files from a previous project location** after the project directory is copied or moved. CC identity omits the build tree root, so a copied `.gradle/configuration-cache` entry is reused. Stored named-file absolute paths still point at the old location.

On failing_ref `e0ca283b48bc739f14140b8a61565d689758c032`, `ConfigurationCacheRepository.Layout.checkFingerprint` registers `rootDirs` as watchable hierarchies and then checks classloader / fingerprint. It does **not** compare `startParameter.buildTreeRootDirectory` against stored `rootDirs`.

Public report (gradle/gradle#36392):

```
gradle init --type java-library --use-defaults
gradle assemble
cp -rf orig copy
# modify a source file in copy
echo broken > lib/src/main/java/org/example/Library.java
cd copy && gradle assemble
```

```
BUILD SUCCESSFUL
Configuration cache entry reused.
```

UP-TO-DATE looks at leftover named source files in `orig`, not `copy`.

In-tree after the repair (not on failing_ref): if `buildTreeRootDirectory !in rootDirs`, return `CheckedFingerprint.Invalid` ("the location of the build has changed from … to …"). Tests copy and move.

Case A — second `gradle assemble` in the original directory:
  CC load is the same location
  named-file paths still match
  not leftover-after-relocate

Case B — copy/move the project including `.gradle/configuration-cache`, then assemble:
  leftover: CC entry + named-file absolute paths from the previous location
  build location omitted from CC identity
  UP-TO-DATE on leftover orig files

Case C — delete `.gradle/configuration-cache` in the copy then assemble:
  fresh CC identity
  not leftover named files from orig

Case D — location included in CC identity (post-repair shape, not on failing_ref):
  "cannot be reused because the location of the build has changed"
  not leftover named-file paths

The developer wants to know which identity case B actually used for named source files: leftover orig absolute paths, copy's current paths, or omitted (no CC entry).
""",
        observed="""# OBSERVED

Public gradle/gradle#36392 (closed 2026-07-13). PR 38432 commit `24311263532f820ba81399b662ae3d53eebe28b9` (parent `e0ca283b48bc739f14140b8a61565d689758c032`). Local Gradle was not performed on this lab host.

Issue body: copy project with configuration-cache entries; assemble in the copy reuses the entry; UP-TO-DATE checks leftover named files in the old location.

On failing_ref, `checkFingerprint` does not invalidate when `buildTreeRootDirectory` is absent from stored `rootDirs`. The location compare is **not** on the failing revision. It is added by PR 38432.

Not this packet: specimen-104 named FileCollection leftover root base dir (PathToFileResolver omitted; gradle#30052 / PR 32359). specimen-088 fileTree query observation omitted. Unique axis vs 104: leftover named-file absolute paths after relocate because CC identity omits build location, not leftover resolver for relative named files at load. specimen-123/124 earthly leftover CACHE --id.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref e0ca283b48bc739f14140b8a61565d689758c032
# DefaultConfigurationCache.kt checkFingerprint(candidateEntry, rootDirs)

# public shape:
# leftover CC entry after cp -rf orig copy
# named source files still orig/... not copy/...
# Configuration cache entry reused
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""gradle/gradle
  platforms/core-configuration/configuration-cache/src/main/kotlin/org/gradle/internal/cc/impl/DefaultConfigurationCache.kt
  platforms/core-configuration/configuration-cache/src/integTest/groovy/org/gradle/internal/cc/impl/ConfigurationCacheDirIntegrationTest.groovy
  .gradle/configuration-cache/
""",
        source="""repository: gradle/gradle
issue: https://github.com/gradle/gradle/issues/36392
pr: https://github.com/gradle/gradle/pull/38432
failing_ref (parent of relocate-check commit on master): e0ca283b48bc739f14140b8a61565d689758c032
fixed_ref (Don't use CC if it's relocated): 24311263532f820ba81399b662ae3d53eebe28b9
merged_at: 2026-07-13T14:26:08Z
pr_author: ov7a
merged_by: ov7a
changed_files: DefaultConfigurationCache.kt, ConfigurationCacheDirIntegrationTest.groovy
pr_title: Don't use CC if it's relocated
scout_note: not specimen-104 ccnamed leftover root base dir (resolver omitted). not specimen-088 fileTree query. Distinct leftover: CC identity omits build location so leftover named-file absolute paths from the previous directory are reused after copy/move. job-0531 was coord-skipped as already 104; this axis is leftover named-file abs paths after relocate, not leftover resolver for relative named files.
""",
        answer_key="""KNOWN FIX (sealed): gradle/gradle PR 38432 commit 24311263532f820ba81399b662ae3d53eebe28b9.

failing_ref is parent e0ca283b48bc739f14140b8a61565d689758c032.

checkFingerprint registered stored rootDirs as watchable but omitted comparing buildTreeRootDirectory, so leftover CC named-file absolute paths from the previous location were reused after copy/move.

PR repair: Invalid when buildTreeRootDirectory is not in rootDirs; tests for copy and move.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (same-dir reload vs leftover named-file abs paths after copy vs wipe CC vs location in identity)
reproducibility: source-backed issue+PR + pinned parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — CC entry identity and named-file path identity are different objects; build location omitted so leftover orig files were identity
ecosystem: gradle / configuration-cache
mechanism_family: leftover-cc-entry, omitted-location, leftover-named-file-paths

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "check_fingerprint_failing.kt": """// Reduced excerpt of checkFingerprint on failing_ref
// DefaultConfigurationCache.kt
// e0ca283b48bc739f14140b8a61565d689758c032
// Stored rootDirs are watchable. Build location is omitted from identity.

    private
    fun ConfigurationCacheRepository.Layout.checkFingerprint(candidateEntry: CandidateEntry, rootDirs: List<File>): CheckedFingerprint {
        // Register all included build root directories as watchable hierarchies,
        // so we can load the fingerprint for build scripts and other files from included builds
        // without violating file system invariants.
        registerWatchableBuildDirectories(rootDirs)

        val classLoaderScopesInvalidationReason = checkClassLoaderScopes()
        if (classLoaderScopesInvalidationReason != null) {
            return CheckedFingerprint.Invalid(buildPath(), classLoaderScopesInvalidationReason)
        }
        // no compare of startParameter.buildTreeRootDirectory against rootDirs
        val systemPropertiesSnapshot = System.getProperties().clone()
        return checkFingerprintAgainstLoadedProperties(candidateEntry).also { result ->
            // ...
        }
    }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  orig/ java-library with .gradle/configuration-cache
  copy/ of orig including CC
  leftover named source files orig/lib/src/main/java/...

Case A (second assemble in orig):
  same location
  not leftover-after-relocate

Case B (assemble in copy, leftover CC):
  leftover: named-file absolute paths from orig
  build location omitted from CC identity
  UP-TO-DATE on leftover orig files

Case C (delete copy/.gradle/configuration-cache):
  fresh CC identity
  not leftover named files

Case D (location in CC identity):
  cannot be reused because location changed
  not leftover named-file paths

Not this packet:
  named FileCollection leftover root base dir (specimen-104)
  fileTree query observation omitted (specimen-088)
  earthly leftover CACHE --id (specimen-123/124)
""",
        },
    )


def _register(state, spec_id: str, trial: str, reason: str) -> None:
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
            input_ref=f"seeds/{spec_id}.md trial={trial}",
            expected_output="0001-dreamer.md",
            kill_condition="15m",
            estimated_cost="r1",
            priority_reason=reason,
            specimen=spec_id,
            lineage=trial,
            phase="cambrian",
            extra={"trial": trial},
        )


def _complete_and_enqueue(ids: list[str]) -> str:
    note = {"reason": ""}
    packets = list(zip(PACKED, ids))

    def fn(state):
        for (job_id, worker, trial, reason), spec_id in packets:
            _register(state, spec_id, trial, reason)
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
            )
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if claimed_r1:
            note["reason"] = (
                "dream.sh not launched; READY_R1_DREAM already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        else:
            note["reason"] = (
                "dream.sh not launched from scout; READY_R1_DREAM enqueued trials="
                + ",".join(t for _, _, t, _ in PACKED)
            )
        return ids

    with_state(fn)
    return note["reason"]


def main() -> None:
    ids = [_claim_id() for _ in PACKED]
    dests = [SPECIMENS / i for i in ids]
    builders = [packet_uv, packet_npm, packet_gradle]
    try:
        for spec_id, builder in zip(ids, builders):
            emit(builder(spec_id))
            write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(ids)
        for spec_id, packed in zip(ids, PACKED):
            print(f"{spec_id} {packed[2]} {packed[0]}")
        print(launch_note)
        print("ids=" + ",".join(ids))
    except Exception:
        for dest in dests:
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
