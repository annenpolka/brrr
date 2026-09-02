#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet specimen-082 (bun leftover optional-peer lockfile identity).

Not npm/cli specimen-004 (unmet optional-peer packument fetch). Repo oven-sh/bun
is absent from SPECIMEN_INDEX.
"""
from __future__ import annotations

from emit_specimen import emit
from compile_seed import write_seed
from paths import SPECIMENS
from update_index import main as update_index

SPEC_ID = "specimen-082"


packet = dict(
    id=SPEC_ID,
    manifest="""
id: specimen-082
kind: REAL_SOURCE_BACKED
repository: oven-sh/bun
failing_ref: c08f665367451debfc9a71799f1f29eba776e4a3
fixed_ref: bbe3f6a2629adf808adbd0da199ae8c94a3c0d47
source_issue: https://github.com/oven-sh/bun/issues/8662
source_pr: https://github.com/oven-sh/bun/pull/35681
mechanism_tags:
  - optional-peer-leftover
  - lockfile-resolution-slot
  - clone-carries-optional-peer
ecosystem: bun
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

`bun remove` of a package that also satisfied an optional peer does not return `bun.lock` to the identity it had before that package was ever added.

Registry fixtures (Verdaccio `optional-peer-deps@1.0.0` declares optional peer `no-deps@*`; `no-deps@1.0.0` has no dependencies):

Case A — never install the peer:

```
package.json: { name: "foo", version: "1.0.0" }
bun add -D optional-peer-deps@1.0.0
```

`bun.lock` on oven-sh/bun `c08f665367451debfc9a71799f1f29eba776e4a3` has no `packages` entry whose serialized prefix is `"no-deps": ["no-deps@`. The name `no-deps` still appears inside `optional-peer-deps`'s `peerDependencies` / `optionalPeers` metadata.

Case B — add then remove the peer as a direct dependency:

```
bun add -D optional-peer-deps@1.0.0
bun add no-deps@1.0.0
bun remove no-deps
```

After step 2, `bun.lock` contains a `packages` identity:

```
"packages": {
  "no-deps": ["no-deps@1.0.0", "...", {}, "sha512-..."],
  "optional-peer-deps": ["optional-peer-deps@1.0.0", "...", { "peerDependencies": { "no-deps": "*" }, "optionalPeers": ["no-deps"] }, "sha512-..."]
}
```

After step 3, `package.json` no longer lists `no-deps`. `Package::clone` (the lockfile clean walk) still iterates every resolution slot, including the optional-peer slot hoist filled during step 2, and if that slot's `PackageID` is unmapped it pushes `PendingResolution` onto `clone_queue`.

Case C — same as B, except `one-dep@1.0.0` (hard dependency on `no-deps@1.0.1`) remains in `package.json` through the add/remove pair. After remove, `bun.lock` still contains a `packages` entry for `no-deps`.

Case D — case B via editing `package.json` + `bun install` instead of `bun remove` (the other path into `Lockfile::clean_with_logger`).

Public report (oven-sh/bun#8662 comment 3379529330, `@tanstack/router-plugin` optional peer `@tanstack/react-router`): after add-then-remove, `bun.lock` differed from the never-installed state and the package remained under `node_modules`. npm and yarn 1.22.22 returned the lockfile to the pre-add state.

The developer wants to know which identity `bun.lock` actually contained for `no-deps` after case B's remove: leftover `packages` entry (same bytes as after step 2, or a rewritten leftover), omitted (byte-identical to case A), or `optionalPeers` metadata only without a `packages` identity.
""",
    observed="""# OBSERVED

Public oven-sh/bun PR 35681 / issue 8662. Failing world in `src/install/lockfile/Package.rs` around squash-merge parent `c08f665367451debfc9a71799f1f29eba776e4a3`.

`Behavior` marks optional peers as both OPTIONAL and PEER:

```
pub fn is_optional(self) -> bool {
    self.contains(Self::OPTIONAL) && !self.contains(Self::PEER)
}
pub fn is_optional_peer(self) -> bool {
    self.contains(Self::OPTIONAL) && self.contains(Self::PEER)
}
```

Fresh resolve does not populate an optional-peer slot on its own. `enqueue_dependency_with_main_and_success_fn` on that revision:

```
if dependency.behavior.is_optional_peer() {
    return Ok(());
}
```

Hoist (`src/install/lockfile/Tree.rs`) can still bind an optional-peer slot to a sibling already in the tree. When `pkg_id == invalid_package_id` and `dependency.behavior.is_optional_peer()`, it calls `Tree::hoist_dependency` rather than skipping the edge. A later hoist walk that finds a matching name with a real `res_id` returns `HoistDependencyResult::Resolve(res_id)`.

`Lockfile::clean_with_logger` rebuilds the package list by cloning from the root. `Package::clone` on that revision copies every resolution slot, including optional-peer slots, with no `is_optional_peer` guard:

```
for (i, (old_resolution, resolution)) in old_resolutions
    .iter()
    .zip(resolutions.iter_mut())
    .enumerate()
{
    if *old_resolution >= max_package_id {
        *resolution = invalid_package_id;
        continue;
    }

    let mapped = package_id_mapping[*old_resolution as usize];
    if mapped < max_package_id {
        *resolution = mapped;
    } else {
        cloner.clone_queue.push(PendingResolution {
            old_resolution: *old_resolution,
            resolve_id: new_package.resolutions.off
                + PackageID::try_from(i).expect("int cast"),
        });
    }
}
```

Package comment on the same revision: `resolutions[i]` is the resolved package ID for `dependencies[i]`; `invalid_package_id` means that dependency is not resolved.

A `packages` entry for `no-deps` serializes as `"no-deps": ["no-deps@...`. The literal `no-deps` also appears inside `optional-peer-deps`'s `peerDependencies` / `optionalPeers` metadata, so presence of a packages identity is the `"no-deps": ["no-deps@` prefix, not a substring match on the name.

In-tree `test/cli/install/bun-lock.test.ts` on that revision has no add/remove optional-peer leftover cases. PR 35681 later added four tests; the first two (`bun remove` of a package that was only otherwise an optional peer; `bun install` after deleting it from `package.json`) fail on the released build with the leftover `"no-deps": ["no-deps@` entry quoted above. The control (hard dependency elsewhere still pulls `no-deps`) passes on that build: lockfile byte-identical before and after the add/remove pair.

This packet does not include a local clone; treat the snippets and lockfile split as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
# in-tree on failing_ref c08f665367451debfc9a71799f1f29eba776e4a3
# (not executed on this lab host)
# registry fixtures: optional-peer-deps@1.0.0, no-deps@1.0.0 (Verdaccio test registry)

# case A
bun add -D optional-peer-deps@1.0.0
# bun.lock has no packages entry prefix "no-deps": ["no-deps@"

# case B
bun add no-deps@1.0.0
# bun.lock now contains "no-deps": ["no-deps@
bun remove no-deps
# package.json no longer lists no-deps
# Package::clone still walks the optional-peer resolution slot hoist filled in step 2
# and may push PendingResolution onto clone_queue

# case C (control)
# package.json already has optional-peer-deps@1.0.0 and one-dep@1.0.0 (hard dep no-deps@1.0.1)
bun add no-deps@1.0.1
bun remove no-deps
# bun.lock still contains a packages entry for no-deps
```

Not executed on this lab host.
""",
    tree="""oven-sh/bun
  src/install/lockfile/Package.rs
  src/install/lockfile.rs
  src/install/lockfile/Tree.rs
  src/install/PackageManager/PackageManagerEnqueue.rs
  src/install_types/resolver_hooks.rs
  test/cli/install/bun-lock.test.ts
""",
    source="""repository: oven-sh/bun
pr: https://github.com/oven-sh/bun/pull/35681
issue: https://github.com/oven-sh/bun/issues/8662
issue_comment: https://github.com/oven-sh/bun/issues/8662#issuecomment-3379529330
failing_ref (squash-merge parent): c08f665367451debfc9a71799f1f29eba776e4a3
fixed_ref (squash merge commit): bbe3f6a2629adf808adbd0da199ae8c94a3c0d47
head_sha: 01366fd66e9086b5c87b028163098e3d46df82a3
merged_at: 2026-07-30T16:51:10Z
merged_by: dylan-conway
changed_files: src/install/lockfile/Package.rs, test/cli/install/bun-lock.test.ts
pr_title: install: drop packages held only by optional-peer resolution slots from bun.lock
scout_note: not npm/cli specimen-004 (unmet optional-peer packument fetch). Distinct leftover: bun.lock packages identity held only by an optional-peer resolution slot after remove.
""",
    answer_key="""KNOWN FIX (sealed): oven-sh/bun PR 35681 squash merge bbe3f6a2629adf808adbd0da199ae8c94a3c0d47.

Package::clone copied every resolution slot, including optional-peer slots hoist had filled, so a package that had once satisfied an optional peer stayed reachable through clean_with_logger after the only non-peer edge was removed. Fresh resolve never populated those slots independently (enqueue_dependency_with_main_and_success_fn returns Ok(()) for is_optional_peer). Repair: in Package::clone, write invalid_package_id to an optional-peer resolution slot instead of mapping/enqueuing the old target; Cloner::flush re-runs resolve()/hoist(), which re-binds the slot only when some non-optional-peer edge still keeps the target alive. Added bun-lock.test.ts cases expect bun.lock after remove to be byte-identical to the never-installed state.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (never-installed optional peer vs leftover after add/remove vs still-reachable via hard dep; bun.lock packages identity vs optionalPeers metadata substring; bun remove vs package.json edit + bun install)
reproducibility: source-backed PR + pinned squash parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — optional-peer resolution slots are skipped on fresh enqueue but carried through lockfile clone once hoist has filled them
ecosystem: bun / node
mechanism_family: optional-peer-leftover, lockfile-resolution-slot, clone-carries-optional-peer

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "package_clone_failing.rs": """# Reduced excerpt of Package::clone on failing_ref
# src/install/lockfile/Package.rs
# Lockfile::clean_with_logger rebuilds packages by cloning from the root.
# resolutions[i] is the resolved package ID for dependencies[i].

        let resolutions: &mut [PackageID] =
            &mut new.buffers.resolutions[prev_len as usize..end as usize];
        debug_assert_eq!(old_resolutions.len(), resolutions.len());
        for (i, (old_resolution, resolution)) in old_resolutions
            .iter()
            .zip(resolutions.iter_mut())
            .enumerate()
        {
            if *old_resolution >= max_package_id {
                *resolution = invalid_package_id;
                continue;
            }

            let mapped = package_id_mapping[*old_resolution as usize];
            if mapped < max_package_id {
                *resolution = mapped;
            } else {
                cloner.clone_queue.push(PendingResolution {
                    old_resolution: *old_resolution,
                    resolve_id: new_package.resolutions.off
                        + PackageID::try_from(i).expect("int cast"),
                });
            }
        }
""",
        "enqueue_optional_peer.rs": """# Reduced excerpt of enqueue_dependency_with_main_and_success_fn on failing_ref
# src/install/PackageManager/PackageManagerEnqueue.rs
# Fresh resolve does not populate an optional-peer slot independently.

pub fn enqueue_dependency_with_main_and_success_fn(
    this: &mut PackageManager,
    id: DependencyID,
    dependency: &Dependency,
    resolution: PackageID,
    install_peer: bool,
    success_fn: SuccessFn,
    fail_fn: Option<FailFn>,
    is_root: bool,
) -> crate::Result<()> {
    if dependency.behavior.is_optional_peer() {
        return Ok(());
    }
    // ... remaining enqueue omitted ...
}
""",
        "behavior_optional_peer.rs": """# Reduced excerpt of Behavior flags on failing_ref
# src/install_types/resolver_hooks.rs

impl Behavior {
    /// Peer-optionals are reported separately.
    pub fn is_optional(self) -> bool {
        self.contains(Self::OPTIONAL) && !self.contains(Self::PEER)
    }
    pub fn is_optional_peer(self) -> bool {
        self.contains(Self::OPTIONAL) && self.contains(Self::PEER)
    }
    pub fn is_peer(self) -> bool {
        self.contains(Self::PEER)
    }
}
""",
        "hoist_optional_peer.rs": """# Reduced excerpt of Tree hoist on failing_ref
# src/install/lockfile/Tree.rs
# When an optional-peer slot is still invalid, hoist looks for a sibling
# already in the tree rather than skipping the edge.

                if pkg_id == invalid_package_id {
                    if dependency.behavior.is_optional_peer() {
                        break 'hoisted Tree::hoist_dependency::<true, METHOD>(
                            next_id,
                            hoist_root_id,
                            pkg_id,
                            dep_id,
                            builder,
                        )?;
                    }

                    // skip unresolvable dependencies
                    continue 'dep;
                }

            if package_id == invalid_package_id {
                debug_assert!(dependency.behavior.is_optional_peer());
                debug_assert!(res_id != invalid_package_id);
                // resolve optional peer to builder.resolutions[dep_id]
                return Ok(HoistDependencyResult::Resolve(res_id));
            }
""",
        "leftover_lockfile_split.txt": """Registry fixtures (Verdaccio):
  optional-peer-deps@1.0.0
    peerDependencies: { no-deps: "*" }
    optionalPeers: ["no-deps"]
  no-deps@1.0.0
    no dependencies
  one-dep@1.0.0
    hard dependency no-deps@1.0.1

Case A (never install the peer):
  bun add -D optional-peer-deps@1.0.0
  bun.lock has NO packages entry prefix "no-deps": ["no-deps@"
  name no-deps still appears inside optional-peer-deps metadata

Case B (add then remove as a direct dep):
  after bun add no-deps@1.0.0:
    bun.lock contains
      "no-deps": ["no-deps@1.0.0", "...", {}, "sha512-..."]
      "optional-peer-deps": [..., { peerDependencies: { no-deps: "*" }, optionalPeers: ["no-deps"] }, ...]
  after bun remove no-deps:
    package.json no longer lists no-deps
    Package::clone walks every resolution slot including the optional-peer slot
    unmapped slots are pushed onto clone_queue as PendingResolution

Case C (hard dep remains):
  package.json: optional-peer-deps@1.0.0 and one-dep@1.0.0
  bun add no-deps@1.0.1 then bun remove no-deps
  bun.lock still contains a packages entry for no-deps
  lockfile is byte-identical to the pre-add baseline on the released build

Case D:
  same leftover path as B, via editing package.json + bun install
  (other entry into Lockfile::clean_with_logger)

Public #8662 comment 3379529330:
  @tanstack/router-plugin optional peer @tanstack/react-router
  after add-then-remove, bun.lock differed from step-1; package remained in node_modules
  npm and yarn 1.22.22 returned lockfile to pre-add state
""",
    },
)


if __name__ == "__main__":
    dest = SPECIMENS / SPEC_ID
    if dest.exists():
        raise SystemExit(f"{dest} already exists; refusing to overwrite")
    path = emit(packet)
    seed = write_seed(SPECIMENS / SPEC_ID)
    print(path)
    print(seed)
    update_index()
