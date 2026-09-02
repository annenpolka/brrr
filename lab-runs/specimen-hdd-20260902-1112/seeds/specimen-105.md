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
