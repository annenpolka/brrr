# Current situation

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
