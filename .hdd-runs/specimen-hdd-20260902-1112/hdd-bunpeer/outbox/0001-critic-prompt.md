# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Lockfile Behavior with Optional Peer Dependencies  
**Environment:** Bun v1.0.0 (commit `c08f665`), Verdaccio registry fixtures (`optional-peer-deps@1.0.0`, `no-deps@1.0.0`, `one-dep@1.0.0`)  

#### **Step 1: Reproduce Case A (Never Install Peer)**  
```bash
# Initialize project
echo '{"name":"foo","version":"1.0.0"}' > package.json

# Add optional-peer-deps without installing peer
bun add -D optional-peer-deps@1.0.0
```  
**Observation:**  
- `bun.lock` contains metadata for `optional-peer-deps` including `peerDependencies` and `optionalPeers` for `no-deps`.  
- **No `packages` entry** for `no-deps` (confirmed via `grep '"no-deps": \["no-deps@' bun.lock` → no match).  

---

#### **Step 2: Reproduce Case B (Add → Remove Direct Dependency)**  
```bash
# Add no-deps explicitly
bun add no-deps@1.0.0

# Verify lockfile state post-add
grep '"no-deps": \["no-deps@' bun.lock  # Returns match → package entry exists

# Remove no-deps
bun remove no-deps
```  
**Observations:**  
1. `package.json` confirms `no-deps` removed.  
2. `bun.lock` **retains `packages` entry** for `no-deps`:  
   ```json
   "packages": {
     "no-deps": ["no-deps@1.0.0", "...", {}, "sha512-..."],
     "optional-peer-deps": ["optional-peer-deps@1.0.0", "...", {
       "peerDependencies": { "no-deps": "*" },
       "optionalPeers": ["no-deps"]
     }, "sha512-..."]
   }
   ```  
3. `node_modules/no-deps` directory remains present (verified via `ls node_modules`).  

**Conflict with Case A:**  
- Lockfile does **not** revert to Case A state (no `packages` entry). Entry persists identically to post-`bun add` state.  

---

#### **Step 3: Reproduce Case C (Hard Dependency Remains)**  
```bash
# Reset environment
rm -rf node_modules bun.lock package.json.lock

# Setup with hard dependency
echo '{
  "name": "foo",
  "version": "1.0.0",
  "dependencies": {
    "optional-peer-deps": "1.0.0",
    "one-dep": "1.0.0"
  }
}' > package.json
bun install

# Add/remove no-deps
bun add no-deps@1.0.1
bun remove no-deps
```  
**Observation:**  
- `bun.lock` retains `packages` entry for `no-deps` (as expected, since `one-dep@1.0.0` requires `no-deps@1.0.1`).  

---

#### **Step 4: Test Case D (Edit package.json + Install)**  
```bash
# Start from Case A state (never installed peer)
rm -rf node_modules bun.lock
echo '{"name":"foo","version":"1.0.0"}' > package.json
bun add -D optional-peer-deps@1.0.0

# Manually add no-deps to package.json
echo '{
  "name": "foo",
  "version": "1.0.0",
  "devDependencies": {
    "optional-peer-deps": "1.0.0",
    "no-deps": "1.0.0"
  }
}' > package.json

# Run install (simulates Case D path)
bun install

# Remove no-deps from package.json and re-install
sed -i '/"no-deps"/d' package.json
bun install
```  
**Observation:**  
- Identical to Case B: `bun.lock` retains `"no-deps": ["no-deps@...` entry.  

---

#### **Key Findings**  
1. **Lockfile State Post-Remove:**  
   - For optional peers with no hard dependencies (Cases B/D), `bun.lock` retains the `packages` entry after removal.  
   - Metadata (`peerDependencies`, `optionalPeers`) remains unchanged from initial install.  
   - **Byte comparison:** Lockfile **does not match Case A** (never-installed state).  

2. **Behavior Root Cause:**  
   - During `Lockfile::clean_with_logger`, `Package::clone` iterates all resolution slots (including optional peers).  
   - Optional-peer slots filled via hoisting (during `bun add no-deps`) retain their `PackageID` mapping.  
   - Since no cleanup occurs for these slots when the direct dependency is removed, the `packages` entry persists.  

3. **Comparison with npm/Yarn:**  
   - As reported in #8662, npm/Yarn revert lockfile to pre-add state. Bun diverges here.  

---

#### **Unresolved Questions**  
- Why does `Package::clone` retain unmapped optional-peer slots instead of discarding them?  
- Does `PendingResolution` in `clone_queue` ever resolve to `invalid_package_id` in this scenario? (Code inspection suggests no.)  

**Recommendation:**  
Modify `Package::clone` to skip resolution slots where `dependency.behavior.is_optional_peer()` is `true` if `old_resolution` is unmapped. This would align with fresh-resolve behavior (which ignores optional peers).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
