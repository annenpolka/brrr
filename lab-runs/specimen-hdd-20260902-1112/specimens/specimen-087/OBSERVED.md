# OBSERVED

Public pnpm/pnpm#10911 (merged 2026-03-08T18:26:48Z, merge `aeb06caae9585d14a51afdfd97e8494b31d72383`, milestone v11.0). First commit `223b9b2e993fcd8766fb0681fc03a349462f1916` (parent `60d3a328bc047c211f75936d54003323ee7ee245`) retitled the lockfile field from `Record<string, { path: string, hash: string }>` to `Record<string, string>` (selector → hash). Commit message: the path was never consumed from the lockfile; patch file paths come from user config (`opts.patchedDependencies`).

Writer on the parent (`lockfile/settings-checker/src/calcPatchHashes.ts`):

```
export async function calcPatchHashes (patches: Record<string, string>, lockfileDir: string): Promise<Record<string, PatchFile>> {
  return pMapValues.default(async (patchFilePath) => {
    return {
      hash: await createHexHashFromFile(patchFilePath),
      path: path.relative(lockfileDir, patchFilePath).replaceAll('\\', '/'),
    }
  }, patches)
}
```

Writer on `223b9b2`:

```
export async function calcPatchHashes (patches: Record<string, string>): Promise<Record<string, string>> {
  return pMapValues.default(async (patchFilePath) => {
    return createHexHashFromFile(patchFilePath)
  }, patches)
}
```

`patching/types` on the parent still has `PatchFile { path, hash }` and `PatchInfo { file: PatchFile }`. On `223b9b2`, `PatchInfo` is `{ hash: string }` only.

`groupPatchedDependencies` on the parent stored `{ file, key }` where `file` was the `PatchFile` object. On `223b9b2` it stores `{ hash, key }` with `hash = patchedDependencies[key]` (the map value, unvalidated).

`getOutdatedLockfileSetting` on `223b9b2` still uses ramda `equals` on the whole `patchedDependencies` map. A leftover object vs a current hash string is not equal, so the changed field is `'patchedDependencies'`. Frozen install surfaces that as lockfile-config mismatch.

`convertToLockfileObject` on `223b9b2` does not walk `patchedDependencies`. It spreads `rest` after omitting `snapshots`. YAML that still has:

```
patchedDependencies:
  is-positive@1.0.0:
    path: patches/is-positive@1.0.0.patch
    hash: <patchFileHash>
```

therefore becomes an in-memory value whose `path` field is still present, even though the type and the writer now say hash-only.

In-tree `pkg-manager/core/test/install/patch.ts` was updated in the same commit to expect the bare string. Those tests write a fresh lockfile; they do not read a parent-format lockfile through `convertToLockfileObject`. `lockfile/fs/test/sortLockfileKeys.test.ts` likewise swapped `{ path: 'foo', hash: 'bar' }` for `'bar'`.

Later PR commits (not this packet's failing/fixed pair): `1b2a242` restored a runtime `patchFilePath` that `223b9b2` had also dropped from `PatchInfo` (broke `applyPatchToDir`); `cdaf08b` updated remaining `PatchFile` readers. Related-not-this: #4961 is hash-of-bytes CRLF vs LF; #8366 is merger dropping the whole field.

This packet does not include a local clone. Do not execute untrusted checkouts on the host. Not specimen-068 (Unix node env-hop). Not specimen-082 (bun leftover `packages` row). Not specimen-085 (owned two-shape yaml fixture of object vs string vs empty vs omitted, no git pins). Not specimen-086 (cargo rustc fingerprint).
