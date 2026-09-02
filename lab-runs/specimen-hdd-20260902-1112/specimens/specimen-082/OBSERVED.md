# OBSERVED

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
