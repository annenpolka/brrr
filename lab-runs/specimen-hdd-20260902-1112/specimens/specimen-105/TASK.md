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
