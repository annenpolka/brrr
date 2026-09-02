// Reduced excerpt of convertToLockfileObject on failing_ref
// lockfile/fs/src/lockfileFormatConverters.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// Spreads rest.patchedDependencies with no rewrite of object values.

export function convertToLockfileObject (lockfile: LockfileFile): LockfileObject {
  const { importers, ...rest } = lockfile

  const packages: PackageSnapshots = {}
  for (const [depPath, pkg] of Object.entries(lockfile.snapshots ?? {})) {
    const pkgId = removeSuffix(depPath)
    packages[depPath as DepPath] = Object.assign(pkg, lockfile.packages?.[pkgId])
  }
  return {
    ...omit(['snapshots'], rest),
    packages,
    importers: mapValues(importers ?? {}, revertProjectSnapshot),
  }
}
