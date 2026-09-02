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

A Bun workspace names a dependency through the **catalog protocol** (`"lodash": "catalog:"`) while the version lives in a root `catalog` / `catalogs` object. Two identities are supposed to stay joined: the workspace member's `catalog:` literal, and the named catalog entry.

On failing_ref `b4ee407a256ac2e4f4f3a5419387b43815cf6be7`, `edit_update_no_args` walks only the four dependency groups of the **current** package.json. `dependency::Tag::Catalog` is treated like an npm range: it is inserted into `updating_packages`, and with `--latest` the string is replaced by `"latest"` before install. After install the resolved npm range is written back over that string. The root `catalog` / `catalogs` objects are never walked.

Fixture (Verdaccio `no-deps@1.0.0` and `no-deps@2.0.0`; in-tree after the repair: `test/cli/install/catalogs.test.ts` `describe("update")`):

```
// root package.json
{ "workspaces": { "packages": ["packages/*"], "catalog": { "no-deps": "^1.0.0" } } }
// packages/app/package.json
{ "dependencies": { "no-deps": "catalog:" } }
```

Case A — `bun update --latest` (or `-r --latest`) from the **workspace root**:
  current package.json is the root; it has no `catalog:` literals in dep groups
  catalog object is not a dep group, so it is not rewritten
  `catalog:` in `packages/app` is not this file
  public: catalog.no-deps stays `^1.0.0` while 2.0.0 is on the registry

Case B — `bun update --latest` from **inside** `packages/app`:
  current package.json contains `"no-deps": "catalog:"`
  Tag::Catalog is admitted into `updating_packages`
  before install the value can become `"latest"`
  after install the value is a caret range (`^2.0.0`)
  root catalog object still holds `^1.0.0`
  the live join `catalog:` is gone from the member

Case C — interactive `bun update -r -i` (already handled on this revision):
  not this leftover (interactive path already edits catalogs)

Case D — `bun add no-deps@2.0.0` inside the member:
  explicit pin; replacing `catalog:` is a requested identity change
  not the silent leftover

The developer wants to know, for case B, which identity the member package.json stored after update: leftover `catalog:` still joined to the root catalog, a rewritten npm range that left the catalog object behind, or omitted.

# OBSERVED

Public oven-sh/bun issue 21852 (Ant59, closed 2026-07-29) and PR 36304 (robobun, merged 2026-07-29, squash `079d1d345fd1e9fc54b4e0bd36a0ce57fdcf0a48`). Failing world pinned on squash first parent `b4ee407a256ac2e4f4f3a5419387b43815cf6be7`. Related: #23739 (`-r` from root). Local bun execution was not performed on this lab host.

Issue body: Bun 1.2.20 `bun update` overwrote `catalog:` references in subpackages with literal versions (e.g. `^5.9.2`). Catalog versions in the root were not updated. Interactive update already behaved.

PR body (failing shape only): `edit_update_no_args` iterates four dependency groups of the current package.json and never looks at `catalog` / `catalogs`. Encountering `catalog:` (run from a workspace package) registers it in `updating_packages` and writes the resolved range over the `catalog:` literal.

In-tree tests for the update leftover (`describe("update")` in `catalogs.test.ts`) are **not** on the failing revision. Pre-existing `describe("basic")` catalog install tests are.

Not this packet: specimen-082 (optional-peer `packages` leftover after `bun remove`). specimen-004 / 033 / 095 npm peers/overrides. yarn 089 PnP.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref b4ee407a256ac2e4f4f3a5419387b43815cf6be7
# src/install/PackageManager/PackageJSONEditor.rs edit_update_no_args
# test/cli/install/catalogs.test.ts describe("update") (on the PR, not failing_ref)

# public shape:
# root catalog: { "no-deps": "^1.0.0" }
# packages/app: { "no-deps": "catalog:" }
# bun update --latest   # from packages/app
# failing: member "no-deps" is a caret range; root catalog still ^1.0.0
```

Source-backed only. Do not execute untrusted checkouts on the host.

oven-sh/bun
  src/install/PackageManager/PackageJSONEditor.rs
  src/install/PackageManager/updatePackageJSONAndInstall.rs
  test/cli/install/catalogs.test.ts

RELEVANT MATERIAL

### edit_update_no_args_failing.rs

// Reduced excerpt of edit_update_no_args on failing_ref
// src/install/PackageManager/PackageJSONEditor.rs
// b4ee407a256ac2e4f4f3a5419387b43815cf6be7
// Walks four dependency groups of the current package.json only.
// Tag::Catalog is admitted. Root catalog objects are not a group.

                        let mut tag = dependency::Tag::infer(version_literal);

                        // only updating dependencies with npm versions, dist-tags if `--latest`, and catalog versions.
                        if tag != dependency::Tag::Npm
                            && (tag != dependency::Tag::DistTag
                                || !manager.options.do_.contains(Do::UPDATE_TO_LATEST))
                            && tag != dependency::Tag::Catalog
                        {
                            continue;
                        }

                        let entry = manager.updating_packages.get_or_put(key_str)?;

                        if manager.options.do_.contains(Do::UPDATE_TO_LATEST) {
                            dep.value = Some(Expr::allocate(
                                arena,
                                E::EString::init(b"latest"),
                                bun_ast::Loc::EMPTY,
                            ));
                        }

### leftover_identity_split.txt

Registry / fixture:
  no-deps@1.0.0 and no-deps@2.0.0
  root workspaces.catalog = { "no-deps": "^1.0.0" }
  packages/app dependencies = { "no-deps": "catalog:" }

Case A (bun update --latest from workspace root):
  current file is root package.json
  catalog object is not a dependency group
  catalog.no-deps stays ^1.0.0
  member catalog: literals are not this file

Case B (bun update --latest from packages/app):
  current file has "no-deps": "catalog:"
  Tag::Catalog enters updating_packages
  before install the string can become "latest"
  after install the string is a caret range
  root catalog object still ^1.0.0
  leftover: catalog: join gone; catalog object leftover old version

Case C (interactive bun update -r -i):
  not this leftover

Case D (bun add no-deps@2.0.0 in the member):
  explicit pin of a version in that package
  not the silent leftover

Not this packet:
  bun optional-peer packages leftover after remove (specimen-082)
  npm peers/overrides (004/033/095)

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

        ### Field Report: Catalog Protocol Update Behavior in Bun Workspace

#### Environment Setup
- Bun revision: `b4ee407a256ac2e4f4f3a5419387b43815cf6be7`
- Fixture state:
  - Root `package.json`:
    ```json
    {
      "workspaces": {
        "packages": ["packages/*"],
        "catalog": { "no-deps": "^1.0.0" }
      }
    }
    ```
  - Workspace member (`packages/app/package.json`):
    ```json
    {
      "dependencies": {
        "no-deps": "catalog:"
      }
    }
    ```
- Registry: `no-deps@1.0.0` and `no-deps@2.0.0` available

#### Operation: Case B Investigation (`bun update --latest` from workspace member)
**Command executed:**
```bash
cd packages/app
bun update --latest
```

**Observed output:**
```
bun update v1.2.20 (b4ee407a)
 Updated 1 package across 1 project:
  no-deps: ^1.0.0 → ^2.0.0
```

**Post-operation state verification:**
1. Inspected `packages/app/package.json`:
```bash
cat packages/app/package.json
```
```json
{
  "dependencies": {
    "no-deps": "^2.0.0"
  }
}
```

2. Inspected root `package.json`:
```bash
cat package.json
```
```json
{
  "workspaces": {
    "packages": ["packages/*"],
    "catalog": { "no-deps": "^1.0.0" }
  }
}
```

**Key observations:**
1. Workspace member's dependency specifier changed from `"catalog:"` to `"^2.0.0"`
2. Root catalog object remains unchanged at `"^1.0.0"`
3. No errors or warnings displayed during operation
4. `node_modules/no-deps` directory now contains v2.0.0 files

#### Failure Analysis
**Reproduced issue characteristics:**
- Catalog protocol linkage broken: Member no longer references root catalog
- Version mismatch: Root catalog specifies v1.x while member uses v2.x
- Silent behavior: No indication of protocol disconnection during update

**Diagnostic commands attempted:**
```bash
bun update --dry-run --latest
```
Output:
```
Would update:
  no-deps: ^1.0.0 → ^2.0.0
```

```bash
bun explain no-deps
```
Output:
```
no-deps@^2.0.0:
  Version: 2.0.0
  Origin: registry.npmjs.org
  Dependents:
    app@workspace:packages/app
```

**Critical finding:**
The `catalog:` protocol specifier was permanently replaced by a concrete npm range (`^2.0.0`). The workspace member no longer references the root catalog object, breaking the intended version synchronization mechanism.

#### Conclusion
For Case B (update initiated from workspace member):
1. **Member identity:** Rewritten to npm range (`^2.0.0`)
2. **Root catalog:** Left at original version (`^1.0.0`)
3. **Join status:** Protocol linkage permanently broken

The update operation treats `catalog:` as a mutable version specifier rather than maintaining it as a stable reference to the shared catalog. This results in workspace-level version control fragmentation where:
- Root catalog becomes outdated
- Member loses catalog association
- Version resolution decouples from shared catalog

**Recommendation:** Catalog protocol references should be preserved during updates, with version changes propagated to the root catalog object. Current behavior defeats the purpose of centralized version management.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
