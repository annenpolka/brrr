# TASK

pnpm lockfile `patchedDependencies` for a selector used to be a `{ path, hash }` object. Commit `223b9b2e993fcd8766fb0681fc03a349462f1916` changed the writer to a bare hash string. An existing lockfile can still carry the leftover `path` field.

Selector `is-positive@1.0.0`, patch file `patches/is-positive@1.0.0.patch`, content hash `patchFileHash` (hex from `createHexHashFromFile`).

Case A — write on parent `60d3a328bc047c211f75936d54003323ee7ee245` (`calcPatchHashes` still returns `PatchFile`):

```
patchedDependencies:
  is-positive@1.0.0:
    path: patches/is-positive@1.0.0.patch
    hash: <patchFileHash>
```

In-tree `pkg-manager/core/test/install/patch.ts` on that parent expects exactly that object (`path` is `path.relative(cwd, patchPath)` with `\` folded to `/`). Snapshot key is `is-positive@1.0.0(patch_hash=${patchFileHash})`.

Case B — write on `223b9b2e993fcd8766fb0681fc03a349462f1916` (`calcPatchHashes` returns `Record<string, string>`, no `lockfileDir`):

```
patchedDependencies:
  is-positive@1.0.0: <patchFileHash>
```

The same test file on that commit expects the bare string. `LockfileBase.patchedDependencies` is typed `Record<string, string>`. `PatchFile` (`{ path, hash }`) is gone from `patching/types`.

Case C — *read* a Case A lockfile with the Case B converter. `convertToLockfileObject` on `223b9b2` is:

```
return {
  ...omit(['snapshots'], rest),
  packages,
  importers: mapValues(importers ?? {}, revertProjectSnapshot),
}
```

`rest.patchedDependencies` is whatever YAML parsed. There is no rewrite of object values to strings. `groupPatchedDependencies` on that same commit does `const hash = patchedDependencies[key]` and stores `{ hash, key }`. `getOutdatedLockfileSetting` does `equals(lockfile.patchedDependencies ?? {}, patchedDependencies ?? {})` where the right-hand side is Case B hash strings from a fresh `calcPatchHashes`.

Case D — selector omitted from `patchedDependencies` while `patches/is-positive@1.0.0.patch` still exists on disk.

Case E (not this identity) — pnpm#4961 / PR 4969: same `{ path, hash }` object shape, but `hash` of the patch file bytes differs Windows CRLF vs POSIX LF (`ERR_PNPM_FROZEN_LOCKFILE_WITH_OUTDATED_LOCKFILE` on Windows CI).

Case F (not this identity) — pnpm#8366: `@pnpm/lockfile.merger` copies only `lockfileVersion` / `importers` / `packages` and drops `patchedDependencies` entirely.

The developer wants to know which identity `convertToLockfileObject` actually produced for `is-positive@1.0.0` in Case C on `223b9b2`: leftover `{ path, hash }` object (path field still present), hash-only string, empty string, or omitted.
