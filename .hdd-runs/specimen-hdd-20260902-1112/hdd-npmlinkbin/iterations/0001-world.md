# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public npm/cli#9613 (closed 2026-06-24). PR 9632 merge `981e2498589c83859b3c9e8b92a2cc67562dc06b` (single parent / squash `696801574984ad19ffaa9a7200d7e752920a018d`). Part of #9608 linked-strategy leftovers. Local npm was not performed on this lab host.

PR body: under linked, uninstall removed the top-level symlink and `.store` entry but left the shim in `node_modules/.bin` as a dangling link. The leftover shim can break tools that enumerate `.bin`, shadow a later-installed binary of the same name, and is not healed by a subsequent `npm install`. Hoisted removes the `.bin` entry.

On failing_ref, `#cleanOrphanedStoreEntries` collects valid store keys and valid top-level link names, then `#cleanOrphanedTopLevelLinks` removes orphaned symlinks whose names do not start with `.`. `.bin` is skipped as an npm-managed dot-entry. No `binsByDir` / `#cleanStaleBinLinks`.

`#cleanStaleBinLinks` is **not** on the failing revision. It is added by PR 9632: while collecting valid top-level links, record `child.package.bin` names per `node_modules` dir; then remove `.bin` entries whose base name (after stripping `.cmd`/`.ps1`) is not provided by a surviving package, or which are dangling symlinks.

Not this packet: specimen-004 / specimen-033 (npm optional-peer leftover). specimen-082 (bun optional-peer leftover / Honor-KILL peerleft). specimen-095 (npm nested-override leftover / Honor-KILL overleft). specimen-089 (yarn leftover PnP build state). job-0394/0419 npm peer leftover (duplicate 004/082/095).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 696801574984ad19ffaa9a7200d7e752920a018d
# workspaces/arborist/lib/arborist/reify.js #cleanOrphanedStoreEntries
# workspaces/arborist/test/arborist/reify.js linked stale .bin test (on the PR, not failing_ref)

# public shape (linked):
# npm uninstall rimraf
# leftover: node_modules/.bin/rimraf -> ../rimraf/bin.js (dangling)
# store entry and top-level symlink gone
```

Source-backed only. Do not execute untrusted checkouts on the host.

npm/cli
  workspaces/arborist/lib/arborist/reify.js
  workspaces/arborist/test/arborist/reify.js

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  install-strategy=linked
  deps: rimraf + semver (or minimatch)
  npm uninstall rimraf

Case A (hoisted uninstall):
  .bin/rimraf removed
  no leftover shim

Case B (linked uninstall, semver remains):
  leftover: .bin/rimraf dangling
  store + top-level rimraf gone
  .bin/semver kept

Case C (linked first install, rimraf never present):
  no leftover uninstall shim

Case D (rm -rf node_modules && npm install):
  fresh tree
  not leftover sweep

Not this packet:
  npm optional-peer leftover (specimen-004/033)
  bun optional-peer leftover (specimen-082)
  npm nested-override leftover (specimen-095)
  yarn leftover PnP build state (specimen-089)
  cargo git+ssh vs registry (job-0339: no merged PR)

### reify_clean_orphaned_failing.js

// Reduced excerpt of #cleanOrphanedStoreEntries / top-level sweep on failing_ref
// workspaces/arborist/lib/arborist/reify.js
// 696801574984ad19ffaa9a7200d7e752920a018d
// Store keys and top-level links are swept. .bin is skipped as a dot-entry.
// No binsByDir / #cleanStaleBinLinks.

  async #cleanOrphanedStoreEntries () {
    const nmDir = resolve(this.path, 'node_modules')
    const storeDir = resolve(nmDir, '.store')
    const validKeys = new Set()
    const nmDirs = new Map()
    // ... collect valid store keys and top-level link names from idealTree ...
    for (const [dir, valid] of nmDirs) {
      await this.#cleanOrphanedTopLevelLinks(dir, valid)
    }
  }

    const orphaned = []
    for (const ent of dirents) {
      // skip npm-managed entries (.bin, .store, .package-lock.json, etc)
      if (ent.name.startsWith('.')) {
        continue
      }
      // ... orphaned top-level symlink sweep ...
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
