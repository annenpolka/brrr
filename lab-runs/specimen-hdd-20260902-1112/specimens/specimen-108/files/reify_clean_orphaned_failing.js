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
