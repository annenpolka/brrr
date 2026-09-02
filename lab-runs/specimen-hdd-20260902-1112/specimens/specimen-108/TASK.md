# TASK

Under npm `install-strategy=linked`, `npm uninstall <pkg>` can leave leftover **bin-shim identity** in `node_modules/.bin` after the package's top-level symlink and `.store` entry are gone. The leftover shim is a dangling link (POSIX) or a leftover `.cmd`/`.ps1` file (Windows). A later `npm install` does not heal it.

On failing_ref `696801574984ad19ffaa9a7200d7e752920a018d`, linked reify builds the actual tree for the diff from the ideal tree (`#buildLinkedActualForDiff`), so a removed dependency is never compared against disk and the diff emits no action to drop its bin shim. Post-reify `#cleanOrphanedStoreEntries` sweeps `.store` keys and top-level links. The top-level sweep **skips dot-entries**:

```
// skip npm-managed entries (.bin, .store, .package-lock.json, etc)
if (ent.name.startsWith('.')) {
    continue
}
```

There is no `#cleanStaleBinLinks`. `#cleanOrphanedStoreEntries` does not record `package.bin` names.

Public report (npm/cli#9613), `install-strategy=linked`:

```
package.json dependencies: rimraf@3.0.2, minimatch@3.0.4
npm install
ls node_modules/.bin                 # rimraf
npm uninstall rimraf
ls -l node_modules/.bin/rimraf
# node_modules/.bin/rimraf -> ../rimraf/bin.js   (dangling; ../rimraf gone)
```

Hoisted strategy removes the `.bin` entry.

In-tree after the repair (not on failing_ref): `t.test('removes stale .bin shims after uninstall, keeps surviving ones')` in `workspaces/arborist/test/arborist/reify.js`. Adds rimraf+semver linked, uninstalls rimraf, expects rimraf / rimraf.cmd / rimraf.ps1 gone and semver shims kept.

Case A — hoisted `npm uninstall rimraf` (no linked):
  diff sees the on-disk tree
  `.bin/rimraf` removed
  no leftover shim identity

Case B — linked `npm uninstall rimraf` while `semver` remains:
  top-level `rimraf` symlink and `.store` entry removed
  leftover: `.bin/rimraf` (and `.cmd`/`.ps1`) still named rimraf
  surviving `.bin/semver` should stay

Case C — linked first install (never installed rimraf):
  no leftover uninstall shim
  not this leftover

Case D — linked uninstall then `rm -rf node_modules && npm install`:
  fresh tree
  not leftover identity (wipe, not sweep)

The developer wants to know which identity case B actually left in `node_modules/.bin`: leftover rimraf shim (dangling / stale name), both shims removed, or omitted (no `.bin` directory).
