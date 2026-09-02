// Reduced excerpt of getOutdatedLockfileSetting on failing_ref
// lockfile/settings-checker/src/getOutdatedLockfileSetting.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// ramda.equals on the whole map. Leftover object vs current hash string → 'patchedDependencies'.

    patchedDependencies?: Record<string, string>

  if (!equals(lockfile.patchedDependencies ?? {}, patchedDependencies ?? {})) {
    return 'patchedDependencies'
  }
