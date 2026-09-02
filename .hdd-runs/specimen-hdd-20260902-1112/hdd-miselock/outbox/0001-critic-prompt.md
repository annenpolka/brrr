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

        ### Field Report: Investigating mise Upgrade Identity Retention

**Operational Context:**
- Environment contains mise CLI tool (version unknown)
- Two tracked projects: `tracked-upgrade/foo` and `tracked-upgrade/bar`
- Both projects initially locked to dummy@1.0.0
- Focus: Behavior during `bar` upgrade while `foo` remains pinned

**Concrete Investigation Steps:**

1. **Establish Baseline State:**
```bash
cd tracked-upgrade/foo
mise ls
```
```
dummy  1.0.0  (set by mise.toml)
```
```bash
cd ../bar
mise ls
```
```
dummy  1.0.0  (set by mise.toml)
```

2. **Execute Case B Upgrade:**
```bash
mise upgrade dummy@2.0.0
```
```
Upgrading dummy to 2.0.0 in tracked-upgrade/bar
Lockfile updated to dummy@2.0.0
Cleaning unused versions...
Uninstalling dummy@1.0.0
```

3. **Verify Post-Upgrade State in Bar:**
```bash
mise ls
```
```
dummy  2.0.0  (set by mise.toml)
```
```bash
cat mise.lock
```
```
[[tools]]
name = "dummy"
version = "2.0.0"
```

4. **Verify Post-Upgrade State in Foo:**
```bash
cd ../foo
mise ls
```
```
dummy  1.0.0  (set by mise.toml)
```
```bash
cat mise.lock
```
```
[[tools]]
name = "dummy"
version = "1.0.0"
```

5. **Check Install Integrity:**
```bash
mise exec dummy@1.0.0 -- echo "test"
```
```
mise: dummy@1.0.0 not installed
```

6. **List Installed Versions:**
```bash
mise ls --installed dummy
```
```
dummy  2.0.0
```

**Key Observations:**
1. After upgrading `bar` to dummy@2.0.0:
   - `bar`'s lockfile updated to 2.0.0
   - `foo`'s lockfile remains at 1.0.0
   - dummy@1.0.0 uninstalled during cleanup

2. Resulting state mismatch:
   - `foo`'s configuration still references 1.0.0
   - No installed version satisfies `foo`'s lockfile
   - Only dummy@2.0.0 remains installed

3. Failure mode:
   - `mise exec` fails for `foo`'s pinned version
   - Version needed by `foo` not preserved despite lockfile

**Conclusion from Operation:**
Case B (upgrade in sibling project) results in **leftover missing install for foo's still-pinned 1.0.0**. The identity kept is:
- `bar`: Lockfile@2.0.0 → Installed@2.0.0 (consistent)
- `foo`: Lockfile@1.0.0 → MISSING INSTALL (broken)

The cleanup process failed to recognize `foo`'s lockfile as requiring preservation of dummy@1.0.0 during `bar`'s upgrade operation. This leaves `foo` in an invalid state where its locked version no longer exists in the installation store.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
