# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# COMMANDS

```
# in-tree, not executed on this lab host

# case A — parent 60d3a328bc047c211f75936d54003323ee7ee245
# pnpm install with patchedDependencies: { 'is-positive@1.0.0': <patchPath> }
# lockfile.patchedDependencies['is-positive@1.0.0'] is
#   { path: <relative posix path>, hash: <patchFileHash> }

# case B — 223b9b2e993fcd8766fb0681fc03a349462f1916 write
# same install; lockfile.patchedDependencies['is-positive@1.0.0'] is <patchFileHash>
# pkg-manager/core/test/install/patch.ts expects the bare string

# case C — 223b9b2 read of a case A lockfile
# convertToLockfileObject spreads rest.patchedDependencies with no rewrite
# groupPatchedDependencies: const hash = patchedDependencies[key]
# getOutdatedLockfileSetting: ramda.equals leftover object vs current hash strings

# case D — selector omitted, patch file still on disk
```

Not executed on this lab host.

pnpm/pnpm
  lockfile/fs/src/lockfileFormatConverters.ts
  lockfile/settings-checker/src/calcPatchHashes.ts
  lockfile/settings-checker/src/getOutdatedLockfileSetting.ts
  lockfile/types/src/index.ts
  patching/types/src/index.ts
  patching/config/src/groupPatchedDependencies.ts
  pkg-manager/core/test/install/patch.ts
  lockfile/fs/test/sortLockfileKeys.test.ts

RELEVANT MATERIAL

### calc_patch_hashes_failing.ts

// Reduced excerpt of calcPatchHashes on failing_ref
// lockfile/settings-checker/src/calcPatchHashes.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// Writer identity: selector → hash string. No lockfileDir. No path field.

export async function calcPatchHashes (patches: Record<string, string>): Promise<Record<string, string>> {
  return pMapValues.default(async (patchFilePath) => {
    return createHexHashFromFile(patchFilePath)
  }, patches)
}

### calc_patch_hashes_parent.ts

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

### convert_to_lockfile_object_failing.ts

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

### get_outdated_patcheddeps.ts

// Reduced excerpt of getOutdatedLockfileSetting on failing_ref
// lockfile/settings-checker/src/getOutdatedLockfileSetting.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// ramda.equals on the whole map. Leftover object vs current hash string → 'patchedDependencies'.

    patchedDependencies?: Record<string, string>

  if (!equals(lockfile.patchedDependencies ?? {}, patchedDependencies ?? {})) {
    return 'patchedDependencies'
  }

### group_patched_dependencies_failing.ts

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

### leftover_lockfile_split.txt

Selector: is-positive@1.0.0
Patch file: patches/is-positive@1.0.0.patch
Hash: <patchFileHash> from createHexHashFromFile

Case A (parent 60d3a328bc047c211f75936d54003323ee7ee245 write):
  patchedDependencies:
    is-positive@1.0.0:
      path: patches/is-positive@1.0.0.patch
      hash: <patchFileHash>
  in-tree patch.ts expects that object
  snapshot: is-positive@1.0.0(patch_hash=${patchFileHash})

Case B (223b9b2e993fcd8766fb0681fc03a349462f1916 write):
  patchedDependencies:
    is-positive@1.0.0: <patchFileHash>
  in-tree patch.ts expects the bare string
  PatchFile type gone; PatchInfo is { hash: string }

Case C (223b9b2 read of case A yaml):
  convertToLockfileObject spreads rest.patchedDependencies
  no rewrite of { path, hash } values to strings
  groupPatchedDependencies: const hash = patchedDependencies[key]
  getOutdatedLockfileSetting ramda.equals leftover object vs current hash strings

Case D:
  selector omitted from patchedDependencies; patch file still on disk

Not this identity:
  #4961 / PR 4969 — hash of patch-file bytes, CRLF vs LF, same object shape
  #8366 — merger drops the whole patchedDependencies field

### lockfile_types_failing.ts

// Reduced excerpt of LockfileBase on failing_ref
// lockfile/types/src/index.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// PatchFile export removed. Field is hash-only.

export interface LockfileBase {
  lockfileVersion: string
  overrides?: Record<string, string>
  packageExtensionsChecksum?: string
  patchedDependencies?: Record<string, string>
  pnpmfileChecksum?: string
  settings?: LockfileSettings
  time?: Record<string, string>
}

### patch_file_type_parent.ts

// Reduced excerpt of patching/types on failing parent
// patching/types/src/index.ts
// 60d3a328bc047c211f75936d54003323ee7ee245

export interface PatchFile {
  path: string
  hash: string
}

export interface PatchInfo {
  file: PatchFile
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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
