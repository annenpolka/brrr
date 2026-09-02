// Reduced excerpt of calcPatchHashes on failing parent
// lockfile/settings-checker/src/calcPatchHashes.ts
// 60d3a328bc047c211f75936d54003323ee7ee245
// Writer identity: selector → { path, hash }.

export async function calcPatchHashes (patches: Record<string, string>, lockfileDir: string): Promise<Record<string, PatchFile>> {
  return pMapValues.default(async (patchFilePath) => {
    return {
      hash: await createHexHashFromFile(patchFilePath),
      path: path.relative(lockfileDir, patchFilePath).replaceAll('\\', '/'),
    }
  }, patches)
}
