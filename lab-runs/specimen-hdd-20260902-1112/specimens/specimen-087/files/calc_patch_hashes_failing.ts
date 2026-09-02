// Reduced excerpt of calcPatchHashes on failing_ref
// lockfile/settings-checker/src/calcPatchHashes.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// Writer identity: selector → hash string. No lockfileDir. No path field.

export async function calcPatchHashes (patches: Record<string, string>): Promise<Record<string, string>> {
  return pMapValues.default(async (patchFilePath) => {
    return createHexHashFromFile(patchFilePath)
  }, patches)
}
