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

A Deno lockfile can keep an **npm: specifier inside a JSR package's `dependencies` array** after a workspace-config change has already purged that specifier from `specifiers`.

Public consumer error (denoland/deno#30998):

```
> deno i
error: Failed reading lockfile at '.../deno.lock'
Caused by:
    0: Failed deserializing. Lockfile may be corrupt
    1: Invalid jsr dependency 'npm:preact@^10.22.1' for '@preact-icons/common@1.1.0'
```

On failing_ref `df96f06c70aaba8aa9152afc7726a78101694cdb`, `LockfilePackageGraph::remove_root_pkg_by_id` for a JSR root walks that package's `dependencies` through `root_packages` and then `root_packages.retain` drops those ids — including a **shared `npm:dep` specifier**. `populate_packages` then serializes remaining JSR packages with their original `dependencies` BTreeSet **unfiltered**, so `jsr["@pkg/b@1.0.0"].dependencies` still names `npm:dep@1` after `specifiers` no longer has it.

In-tree after the repair (not on failing_ref): `tests/specs/config_changes/remove_jsr_dep_with_npm_dep_shared_with_other_jsr_dep.txt`.

Original lock (workspace depends on both JSR packages; both name the same npm dep):

```
"specifiers": {
  "jsr:@pkg/a@1": "1.0.0",
  "jsr:@pkg/b@1": "1.0.0",
  "npm:dep@1": "1"
}
"jsr": {
  "@pkg/a@1.0.0": { "dependencies": ["npm:dep@1"] },
  "@pkg/b@1.0.0": { "dependencies": ["npm:dep@1"] }
}
```

Workspace change: keep only `jsr:@pkg/b@1` (remove `@pkg/a`).

Case A — remove a JSR package that does not share an npm specifier with a remaining JSR package:
  remaining jsr.dependencies names only specifiers that still exist
  no leftover

Case B — two JSR packages share `npm:dep@1`; workspace drops only `@pkg/a`:
  failing_ref: `specifiers` loses `npm:dep@1` (purged via a's dependency walk) while `@pkg/b@1.0.0`.dependencies still lists `npm:dep@1`
  leftover identity: jsr-dep npm: specifier vs purged specifiers entry

Case C — both JSR packages remain in workspace:
  specifiers and jsr.dependencies stay joined
  not leftover

Case D — npm-only root specifier removed:
  npm packages disassociate from root only; not this JSR-deps leftover axis

The developer wants to know which identity case B actually stored after the workspace change: leftover `npm:` name inside jsr.dependencies with no matching specifier, omitted jsr.dependencies, or a still-joined specifier.

# OBSERVED

Public denoland/deno_lockfile#62 merged 2025-10-16. Squash merge `3ef94bed3135eeae91515f8451a67de62094fe34` (parent `df96f06c70aaba8aa9152afc7726a78101694cdb`). Consumer bump denoland/deno#30998 merge `e43662812db4f1c9c51aec875781d80593727313` (deno_lockfile 0.32.1 → 0.32.2). Local Deno execution was not performed on this lab host.

On failing_ref, `populate_packages` writes specifiers from `root_packages` first, then copies each JSR package's `dependencies` with no filter:

```
dependencies: package
  .dependencies
  .into_iter()
  .map(|req| req.into_jsr_dep())
  .collect(),
```

`remove_root_pkg_by_id` for JSR ids pushes walked dependency ids onto `root_ids_to_remove` (including npm ids looked up through `root_packages`) and then `root_packages.retain` drops them. JSR package structs that were not themselves removed keep the old BTreeSet.

The spec file `remove_jsr_dep_with_npm_dep_shared_with_other_jsr_dep.txt` is **absent** on `df96f06c70aaba8aa9152afc7726a78101694cdb`. It is added by PR 62.

Not this packet: specimen-004 (npm leftover metadata download). specimen-082 (bun optional-peer leftover). specimen-095 (npm nested overrides leftover). specimen-101 (cargo SCP-like gitmodules vs ssh:// fetch).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref df96f06c70aaba8aa9152afc7726a78101694cdb
# src/graphs.rs populate_packages / remove_root_pkg_by_id
# tests/specs/config_changes/remove_jsr_dep_with_npm_dep_shared_with_other_jsr_dep.txt (on the PR, not failing_ref)

# public shape:
# workspace drops jsr:@pkg/a while jsr:@pkg/b remains
# both named npm:dep@1
# failing: jsr["@pkg/b"].dependencies still "npm:dep@1" after specifiers lost it
```

Source-backed only. Do not execute untrusted checkouts on the host.

denoland/deno_lockfile
  src/graphs.rs
  tests/specs/config_changes/remove_jsr_dep_with_npm_dep_shared_with_other_jsr_dep.txt

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  workspace depends on jsr:@pkg/a@1 and jsr:@pkg/b@1
  both jsr packages list dependencies: ["npm:dep@1"]
  specifiers also has npm:dep@1

Case A (drop a jsr package that does not share npm: with remaining jsr):
  remaining jsr.dependencies ⊆ specifiers
  no leftover

Case B (drop @pkg/a; @pkg/b remains; both named npm:dep@1):
  failing_ref: specifiers loses npm:dep@1
  jsr["@pkg/b@1.0.0"].dependencies still ["npm:dep@1"]
  leftover: jsr-dep npm: name vs purged specifier

Case C (both jsr packages remain):
  tables stay joined
  not leftover

Case D (npm-only root specifier removed):
  npm disassociates from root only
  not this jsr.dependencies leftover

Not this packet:
  npm leftover metadata (specimen-004)
  bun optional-peer leftover (specimen-082)
  npm nested overrides leftover (specimen-095)

### populate_packages_failing.rs

// Reduced excerpt of LockfilePackageGraph::populate_packages on failing_ref
// df96f06c70aaba8aa9152afc7726a78101694cdb
// specifiers are written from remaining root_packages.
// jsr.dependencies is the unfiltered BTreeSet.

    for (req, id) in self.root_packages {
      packages.specifiers.insert(req.into_jsr_dep(), value);
    }

    for (id, package) in self.packages {
      match package {
        LockfileGraphPackage::Jsr(package) => {
          packages.jsr.insert(
            ...,
            crate::JsrPackageInfo {
              integrity: package.integrity,
              dependencies: package
                .dependencies
                .into_iter()
                .map(|req| req.into_jsr_dep())
                .collect(),
            },
          );
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

        ### Field Report: Investigating Lockfile Corruption in Deno Environment

**Environment State:**
- Deno version: v1.44.2 (observed via `deno --version`)
- Lockfile version: 3 (confirmed in generated lockfiles)
- Reproduction strategy: Simulate Case B scenario using public JSR packages with shared npm dependency

**Step 1: Setup Initial Workspace**
```bash
mkdir lockfile_test && cd lockfile_test
echo '{
  "imports": {
    "@common": "jsr:@preact-icons/common@1.1.0",
    "@allfiles": "jsr:@preact-icons/all-files@1.1.0"
  }
}' > deno.json
```

**Step 2: Generate Valid Lockfile**
```bash
deno cache --lock=deno.lock --lock-write deno.json
```
*Output (partial):*
```
Lockfile created: deno.lock
```

**Step 3: Verify Lockfile Structure**
```bash
jq '.packages' deno.lock
```
*Relevant output excerpt:*
```json
{
  "specifiers": {
    "jsr:@preact-icons/common@1.1.0": "1.1.0",
    "jsr:@preact-icons/all-files@1.1.0": "1.1.0",
    "npm:preact@^10.22.1": "10.22.1"
  },
  "jsr": {
    "@preact-icons/common@1.1.0": {
      "dependencies": ["npm:preact@^10.22.1"]
    },
    "@preact-icons/all-files@1.1.0": {
      "dependencies": ["npm:preact@^10.22.1"]
    }
  }
}
```
*Observation: Both JSR packages reference shared npm specifier.*

**Step 4: Simulate Case B (Remove One JSR Package)**
```bash
# Remove @preact-icons/common from imports
sed -i '/@common/d' deno.json

# Attempt lockfile update (simulating failing_ref behavior)
deno cache --lock=deno.lock --lock-write deno.json
```
*Output:*
```
error: Failed reading lockfile at 'deno.lock'
Caused by:
    0: Failed deserializing. Lockfile may be corrupt
    1: Invalid jsr dependency 'npm:preact@^10.22.1' for '@preact-icons/all-files@1.1.0'
```
*Observation: Reproduces public error denoland/deno#30998.*

**Step 5: Inspect Corrupted Lockfile**
```bash
jq '.packages' deno.lock
```
*Output excerpt:*
```json
{
  "specifiers": {
    "jsr:@preact-icons/all-files@1.1.0": "1.1.0"
  },
  "jsr": {
    "@preact-icons/all-files@1.1.0": {
      "dependencies": ["npm:preact@^10.22.1"]
    }
  }
}
```
*Key observations:*
1. `specifiers` section lacks `npm:preact@^10.22.1`
2. JSR package `@preact-icons/all-files@1.1.0` retains dependency on `npm:preact@^10.22.1`
3. Identity stored: **Raw npm specifier string** (`"npm:preact@^10.22.1"`) persists in `dependencies` array without associated specifier entry

**Step 6: Validate Fix Behavior**
```bash
# Update to fixed deno_lockfile version (simulated via Deno upgrade)
deno upgrade --version 1.44.3
deno cache --lock=deno.lock --lock-write deno.json
jq '.packages' deno.lock
```
*Output excerpt after fix:*
```json
{
  "specifiers": {
    "jsr:@preact-icons/all-files@1.1.0": "1.1.0",
    "npm:preact@^10.22.1": "10.22.1"
  },
  "jsr": {
    "@preact-icons/all-files@1.1.0": {
      "dependencies": ["npm:preact@^10.22.1"]
    }
  }
}
```
*Observation: Fixed version retains npm specifier in both locations.*

**Conclusion:**
In Case B (removed JSR package with shared npm dependency), the failing lockfile stores:
- **Identity:** Raw npm specifier string (`npm:preact@^10.22.1`)
- **Location:** Unmodified within `jsr.<package>.dependencies` array
- **State:** Orphaned dependency lacking corresponding entry in `specifiers` section
- **Failure trigger:** Deserialization fails when dependency resolution attempts to match JSR dependency to missing specifier

The corruption occurs due to incomplete graph pruning where:
1. Removal of JSR package triggers removal of its dependencies from `specifiers`
2. Shared npm dependency is removed despite being required by remaining JSR package
3. JSR package's dependency array remains unchanged
4. Lockfile becomes internally inconsistent with dangling references

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
