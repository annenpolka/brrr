// Reduced excerpt of groupPatchedDependencies on failing_ref
// patching/config/src/groupPatchedDependencies.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// Map value is stored as hash with no string check.

export function groupPatchedDependencies (patchedDependencies: Record<string, string>): PatchGroupRecord {
  const result: PatchGroupRecord = {}
  // getGroup omitted
  for (const key in patchedDependencies) {
    const hash = patchedDependencies[key]
    const { name, version, nonSemverVersion } = dp.parse(key)

    if (name && version) {
      getGroup(name).exact[version] = { hash, key }
      continue
    }
    // range / all branches also store { hash, key }
  }
  return result
}
