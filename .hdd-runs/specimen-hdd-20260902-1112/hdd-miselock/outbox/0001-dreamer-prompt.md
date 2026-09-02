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

`mise upgrade` of **one tracked project** can drop the install identity still named by **another tracked project's lockfile**.

Two sibling dirs, both `dummy = "latest"`, both `mise.lock` pin `1.0.0`:

```
tracked-upgrade/foo/{mise.toml,mise.lock}   dummy @ 1.0.0
tracked-upgrade/bar/{mise.toml,mise.lock}   dummy @ 1.0.0
```

On failing_ref `2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c`, after `cd bar && mise upgrade dummy@2.0.0`, cleanup calls `get_versions_needed_by_tracked_configs(config, false, false)` — `use_locked_version=false` for **every** tracked config. Foo's lock still names `1.0.0`. The keep-set does not. `1.0.0` is uninstalled. Foo's lock identity is leftover against a missing install.

In-tree after the repair (not on failing_ref): `e2e/cli/test_upgrade` block "upgrading one tracked project should preserve versions pinned by another tracked lockfile". After bar upgrades to `2.0.0`: `mise ls --installed dummy` still contains `1.0.0` and `2.0.0`; foo's lock stays `1.0.0`; bar's lock is `2.0.0` and not `1.0.0`.

Case A — single tracked project, upgrade dummy 1.0.0 → 2.0.0:
  old 1.0.0 is this project's stale lock
  uninstall of 1.0.0 is intended
  no leftover sibling pin

Case B — two tracked projects, both locked 1.0.0; upgrade only bar to 2.0.0:
  failing_ref keep-set ignores foo's lock
  leftover identity: foo lock pin 1.0.0 vs missing install
  bar lock 2.0.0 vs installed 2.0.0 stay joined

Case C — `mise prune` (not upgrade) with lockfiles enabled:
  prune already passed `use_locked_version=true`
  not this upgrade leftover

Case D — two projects share the same lockfile path:
  one pin, not sibling leftover

The developer wants to know which identity case B actually kept after bar's upgrade: leftover missing install for foo's still-pinned 1.0.0, both pins installed, or omitted foo lock.

# OBSERVED

Public jdx/mise#10114 merged 2026-05-28. Squash merge `f38bab024878162972660d16935ac5cc8340a582` (parent `2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c`). Discussion #9978. Local mise execution was not performed on this lab host.

On failing_ref, `Upgrade` cleanup after rebuild_for_toolset:

```
let versions_needed_by_tracked =
    get_versions_needed_by_tracked_configs(config, false, false).await?;
```

Comment on failing_ref: upgrade passes false because it checks what tracked configs resolve to after an upgrade, before their lockfiles have been updated. That false is applied to **all** tracked configs, including siblings whose lockfiles were not the upgrade target.

`get_versions_needed_by_tracked_configs` only reads `Lockfile::read` when `use_locked_version` is true. Foo's `[[tools.dummy]] version = "1.0.0"` is therefore not in the keep-set. Cleanup uninstalls `dummy@1.0.0` if bar's upgrade succeeded.

The e2e sibling-lock block is **absent** on `2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c`. It is added by PR 10114.

Not this packet: specimen-006/022/023/102 (uv git vs directory source kinds). specimen-078 (go testcache omits buildid). specimen-089 (yarn PnP leftover locator).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c
# src/cli/upgrade.rs get_versions_needed_by_tracked_configs(config, false, false)
# src/toolset/mod.rs Lockfile::read gated on use_locked_version
# e2e/cli/test_upgrade sibling tracked lock block (on the PR, not failing_ref)

# public shape:
# foo and bar both dummy=latest locked 1.0.0
# cd bar && mise upgrade dummy@2.0.0
# failing: foo lock still 1.0.0, install of 1.0.0 gone
```

Source-backed only. Do not execute untrusted checkouts on the host.

jdx/mise
  src/cli/upgrade.rs
  src/toolset/mod.rs
  e2e/cli/test_upgrade

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  foo and bar both dummy = latest
  both mise.lock pin dummy 1.0.0

Case A (single project upgrade 1.0.0 → 2.0.0):
  stale lock of this project
  uninstall intended
  no sibling leftover

Case B (upgrade only bar to 2.0.0):
  failing_ref keep-set ignores foo lock
  leftover: foo pin 1.0.0 vs missing install
  bar 2.0.0 stays joined

Case C (mise prune, not upgrade):
  already use_locked_version=true
  not this leftover

Case D (shared lockfile path):
  one pin
  not sibling leftover

Not this packet:
  uv git vs directory (006/022/023/102)
  go testcache omits buildid (078)

### upgrade_failing.rs

// Reduced excerpt of Upgrade cleanup on failing_ref
// 2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c
// use_locked_version=false is applied to every tracked config.

        let versions_needed_by_tracked =
            get_versions_needed_by_tracked_configs(config, false, false).await?;

        for (o, tv) in to_remove {
            if successful_versions.iter().any(|v| v.ba() == o.tool_version.ba()) {
                let version_key = (
                    o.tool_version.ba().short.to_string(),
                    o.tool_version.tv_pathname(),
                );
                if versions_needed_by_tracked.contains(&version_key) {
                    continue;
                }
                // uninstall old version
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
