#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet specimen-087 (pnpm leftover path field).

Not specimen-068 (pnpm/pacquet Unix node env-hop dropping kebab-case names).
Not specimen-082 / Honor-KILL peerleft (bun.lock leftover packages vs mention).
Not specimen-085 (DERIVED yaml object vs hash-string fixture of the same PR,
fixture refs, no git pins). Not specimen-086 (rust-lang/cargo rustc fingerprint).
Distinct leftover: after 223b9b2 writers store selector→hash, convertToLockfileObject
still spreads a leftover {path,hash} object when reading an old lockfile.
Related-not-this: #4961 CRLF hash of patch-file bytes; #8366 merger drops the
whole patchedDependencies field.
"""
from __future__ import annotations

from emit_specimen import emit
from compile_seed import write_seed
from paths import SPECIMENS
from update_index import main as update_index

SPEC_ID = "specimen-087"


packet = dict(
    id=SPEC_ID,
    manifest="""
id: specimen-087
kind: REAL_SOURCE_BACKED
repository: pnpm/pnpm
failing_ref: 223b9b2e993fcd8766fb0681fc03a349462f1916
fixed_ref: fabf694a81b55f3a572c5a511d8f0651dcb495c8
source_issue: https://github.com/pnpm/pnpm/issues/10911
source_pr: https://github.com/pnpm/pnpm/pull/10911
mechanism_tags:
  - leftover-path-field
  - patchedDependencies-hash-only
  - lockfile-format-migrate
ecosystem: pnpm
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

pnpm lockfile `patchedDependencies` for a selector used to be a `{ path, hash }` object. Commit `223b9b2e993fcd8766fb0681fc03a349462f1916` changed the writer to a bare hash string. An existing lockfile can still carry the leftover `path` field.

Selector `is-positive@1.0.0`, patch file `patches/is-positive@1.0.0.patch`, content hash `patchFileHash` (hex from `createHexHashFromFile`).

Case A — write on parent `60d3a328bc047c211f75936d54003323ee7ee245` (`calcPatchHashes` still returns `PatchFile`):

```
patchedDependencies:
  is-positive@1.0.0:
    path: patches/is-positive@1.0.0.patch
    hash: <patchFileHash>
```

In-tree `pkg-manager/core/test/install/patch.ts` on that parent expects exactly that object (`path` is `path.relative(cwd, patchPath)` with `\\` folded to `/`). Snapshot key is `is-positive@1.0.0(patch_hash=${patchFileHash})`.

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
""",
    observed="""# OBSERVED

Public pnpm/pnpm#10911 (merged 2026-03-08T18:26:48Z, merge `aeb06caae9585d14a51afdfd97e8494b31d72383`, milestone v11.0). First commit `223b9b2e993fcd8766fb0681fc03a349462f1916` (parent `60d3a328bc047c211f75936d54003323ee7ee245`) retitled the lockfile field from `Record<string, { path: string, hash: string }>` to `Record<string, string>` (selector → hash). Commit message: the path was never consumed from the lockfile; patch file paths come from user config (`opts.patchedDependencies`).

Writer on the parent (`lockfile/settings-checker/src/calcPatchHashes.ts`):

```
export async function calcPatchHashes (patches: Record<string, string>, lockfileDir: string): Promise<Record<string, PatchFile>> {
  return pMapValues.default(async (patchFilePath) => {
    return {
      hash: await createHexHashFromFile(patchFilePath),
      path: path.relative(lockfileDir, patchFilePath).replaceAll('\\\\', '/'),
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
""",
    commands="""# COMMANDS

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
""",
    tree="""pnpm/pnpm
  lockfile/fs/src/lockfileFormatConverters.ts
  lockfile/settings-checker/src/calcPatchHashes.ts
  lockfile/settings-checker/src/getOutdatedLockfileSetting.ts
  lockfile/types/src/index.ts
  patching/types/src/index.ts
  patching/config/src/groupPatchedDependencies.ts
  pkg-manager/core/test/install/patch.ts
  lockfile/fs/test/sortLockfileKeys.test.ts
""",
    source="""repository: pnpm/pnpm
pr: https://github.com/pnpm/pnpm/pull/10911
issue: https://github.com/pnpm/pnpm/issues/10911
related_issue_crlf_hash: https://github.com/pnpm/pnpm/issues/4961
related_pr_crlf_hash: https://github.com/pnpm/pnpm/pull/4969
related_issue_merger_drop: https://github.com/pnpm/pnpm/issues/8366
failing_ref (format-change commit, no read migrate): 223b9b2e993fcd8766fb0681fc03a349462f1916
failing_parent (old {path,hash} writer): 60d3a328bc047c211f75936d54003323ee7ee245
fixed_ref (migrate old format on read): fabf694a81b55f3a572c5a511d8f0651dcb495c8
head_sha: 0b305324f8c0f22c3a747e77ef0da13ba0b1ae28
merge_commit_sha: aeb06caae9585d14a51afdfd97e8494b31d72383
merged_at: 2026-03-08T18:26:48Z
merged_by: zkochan
milestone: v11.0
pr_title: refactor: simplify patchedDependencies lockfile format
changed_files: lockfile/fs/src/lockfileFormatConverters.ts, lockfile/settings-checker/src/calcPatchHashes.ts, lockfile/types/src/index.ts, patching/types/src/index.ts, patching/config/src/groupPatchedDependencies.ts, pkg-manager/core/test/install/patch.ts
scout_note: not specimen-068 (pacquet Unix node env-hop). not specimen-082/peerleft (bun leftover packages vs mention). not specimen-085 (derived yaml object vs string fixture, no git pins). not specimen-086 (cargo rustc fingerprint). Distinct leftover: path field still present in LockfileObject after 223b9b2 when reading a parent-format lockfile, vs hash-only string after fabf694.
""",
    answer_key="""KNOWN FIX (sealed): pnpm/pnpm PR 10911 commit fabf694a81b55f3a572c5a511d8f0651dcb495c8.

223b9b2 changed lockfile patchedDependencies from Record<string,{path,hash}> to Record<string,string> and stopped writing path, but convertToLockfileObject still spread rest.patchedDependencies unchanged. Reading a pre-change lockfile left leftover {path,hash} objects in LockfileObject; groupPatchedDependencies then stored that object as PatchInfo.hash; getOutdatedLockfileSetting ramda.equals compared leftover objects to current hash strings. Repair: convertToLockfileObject calls migratePatchedDependencies, which maps each value to the string itself or value.hash.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (parent write {path,hash} vs 223b9b2 write hash-only vs 223b9b2 read of leftover object vs omitted; not CRLF byte-hash #4961; not merger drop #8366; not bun leftover packages; not 085 yaml fixture; not 086 cargo rustc fingerprint)
reproducibility: source-backed PR + pinned format-change and migrate commits; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — writer and type dropped path, reader still spread leftover objects; tests only cover fresh writes
ecosystem: pnpm / node
mechanism_family: leftover-path-field, patchedDependencies-hash-only, lockfile-format-migrate

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "convert_to_lockfile_object_failing.ts": """// Reduced excerpt of convertToLockfileObject on failing_ref
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
""",
        "calc_patch_hashes_parent.ts": """// Reduced excerpt of calcPatchHashes on failing parent
// lockfile/settings-checker/src/calcPatchHashes.ts
// 60d3a328bc047c211f75936d54003323ee7ee245
// Writer identity: selector → { path, hash }.

export async function calcPatchHashes (patches: Record<string, string>, lockfileDir: string): Promise<Record<string, PatchFile>> {
  return pMapValues.default(async (patchFilePath) => {
    return {
      hash: await createHexHashFromFile(patchFilePath),
      path: path.relative(lockfileDir, patchFilePath).replaceAll('\\\\', '/'),
    }
  }, patches)
}
""",
        "calc_patch_hashes_failing.ts": """// Reduced excerpt of calcPatchHashes on failing_ref
// lockfile/settings-checker/src/calcPatchHashes.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// Writer identity: selector → hash string. No lockfileDir. No path field.

export async function calcPatchHashes (patches: Record<string, string>): Promise<Record<string, string>> {
  return pMapValues.default(async (patchFilePath) => {
    return createHexHashFromFile(patchFilePath)
  }, patches)
}
""",
        "group_patched_dependencies_failing.ts": """// Reduced excerpt of groupPatchedDependencies on failing_ref
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
""",
        "get_outdated_patcheddeps.ts": """// Reduced excerpt of getOutdatedLockfileSetting on failing_ref
// lockfile/settings-checker/src/getOutdatedLockfileSetting.ts
// 223b9b2e993fcd8766fb0681fc03a349462f1916
// ramda.equals on the whole map. Leftover object vs current hash string → 'patchedDependencies'.

    patchedDependencies?: Record<string, string>

  if (!equals(lockfile.patchedDependencies ?? {}, patchedDependencies ?? {})) {
    return 'patchedDependencies'
  }
""",
        "patch_file_type_parent.ts": """// Reduced excerpt of patching/types on failing parent
// patching/types/src/index.ts
// 60d3a328bc047c211f75936d54003323ee7ee245

export interface PatchFile {
  path: string
  hash: string
}

export interface PatchInfo {
  file: PatchFile
}
""",
        "lockfile_types_failing.ts": """// Reduced excerpt of LockfileBase on failing_ref
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
""",
        "leftover_lockfile_split.txt": """Selector: is-positive@1.0.0
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
""",
    },
)


if __name__ == "__main__":
    dest = SPECIMENS / SPEC_ID
    try:
        dest.mkdir(parents=True)
    except FileExistsError:
        raise SystemExit(f"{dest} already exists; refusing to overwrite")
    path = emit(packet)
    seed = write_seed(SPECIMENS / SPEC_ID)
    print(path)
    print(seed)
    update_index()
