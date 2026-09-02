# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

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

# COMMANDS

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

oven-sh/bun
  src/install/lockfile/Package.rs
  src/install/lockfile.rs
  src/install/lockfile/Tree.rs
  src/install/PackageManager/PackageManagerEnqueue.rs
  src/install_types/resolver_hooks.rs
  test/cli/install/bun-lock.test.ts

RELEVANT MATERIAL

### behavior_optional_peer.rs

# Reduced excerpt of Behavior flags on failing_ref
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

### enqueue_optional_peer.rs

# Reduced excerpt of enqueue_dependency_with_main_and_success_fn on failing_ref
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

### hoist_optional_peer.rs

# Reduced excerpt of Tree hoist on failing_ref
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

### leftover_lockfile_split.txt

Registry fixtures (Verdaccio):
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

### package_clone_failing.rs

# Reduced excerpt of Package::clone on failing_ref
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

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
