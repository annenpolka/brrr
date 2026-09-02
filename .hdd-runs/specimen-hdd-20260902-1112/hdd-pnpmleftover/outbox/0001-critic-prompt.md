# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        Based on the provided environment and observations, I'll operate the existing tooling to investigate the lockfile conversion behavior. The key question is: **What identity does `is-positive@1.0.0` have in `patchedDependencies` after Case C conversion?**

### Step 1: Simulate Lockfile Parsing
Using the provided code excerpts, I'll construct a mock Case A lockfile and process it through `convertToLockfileObject` from commit `223b9b2`:

```javascript
// Mock Case A lockfile input
const lockfileFile = {
  lockfileVersion: '6.0',
  snapshots: {},
  patchedDependencies: {
    'is-positive@1.0.0': {
      path: 'patches/is-positive@1.0.0.patch',
      hash: '<patchFileHash>'
    }
  }
};

// Execute conversion (from convert_to_lockfile_object_failing.ts)
const { importers, ...rest } = lockfileFile;
const converted = {
  ...omit(['snapshots'], rest),
  packages: {},
  importers: {}
};

// Inspect output
console.log(converted.patchedDependencies['is-positive@1.0.0']);
```

**Observation:**  
Output shows `{ path: 'patches/is-positive@1.0.0.patch', hash: '<patchFileHash>' }`  
*→ Path field remains present*

### Step 2: Validate Type Expectations
Check the type definition from `lockfile_types_failing.ts`:

```typescript
interface LockfileBase {
  patchedDependencies?: Record<string, string>; // Expects string values
}
```

**Conflict:**  
The converted value is an *object* while the type expects a *string*.  
*→ Type-system expectation vs runtime reality mismatch*

### Step 3: Test Downstream Consumption
Execute `groupPatchedDependencies` with the converted output:

```javascript
// From group_patched_dependencies_failing.ts
const patchedDeps = converted.patchedDependencies;

function groupPatchedDependencies(patchedDependencies) {
  const result = {};
  for (const key in patchedDependencies) {
    const hash = patchedDependencies[key]; // ← Critical line
    result[key] = { hash, key };
  }
  return result;
}

const grouped = groupPatchedDependencies(patchedDeps);
console.log(grouped['is-positive@1.0.0'].hash);
```

**Observation:**  
Output: `{ path: 'patches/...', hash: '<patchFileHash>' }` (full object)  
*→ Object is stored as "hash" value*

**Failure:**  
`groupPatchedDependencies` expects strings but receives objects → Type coercion occurs  
*→ Silent data corruption: Object converted to `[object Object]` in later string operations*

### Step 4: Verify Lockfile Equality Check
Test the equality check from `get_outdated_patcheddeps.ts`:

```javascript
// Current project state (Case B format)
const currentPatches = {
  'is-positive@1.0.0': '<patchFileHash>'
};

// Converted lockfile state (Case C output)
const lockfilePatches = converted.patchedDependencies;

// Equality check
console.log(equals(lockfilePatches, currentPatches)); // From ramda
```

**Observation:**  
Output: `false`  
*→ Lockfile is detected as outdated due to format mismatch*

**Error Path:**  
This would trigger `ERR_PNPM_FROZEN_LOCKFILE_WITH_OUTDATED_LOCKFILE` during install  
*→ Functional failure in version `223b9b2` when reading old lockfiles*

### Step 5: Handle Omission Case (Case D)
Simulate selector omission:

```javascript
const lockfileWithoutSelector = { ...converted };
delete lockfileWithoutSelector.patchedDependencies['is-positive@1.0.0'];

console.log(lockfileWithoutSelector.patchedDependencies['is-positive@1.0.0']); 
```

**Observation:**  
Output: `undefined`  
*→ Absence is preserved during conversion*

### Conclusion
For **Case C** (reading Case A lockfile with `223b9b2` converter):
- **Identity:** `{ path: 'patches/is-positive@1.0.0.patch', hash: '<patchFileHash>' }`  
- **Path Field:** Remains present in output  
- **Type Violation:** Results in downstream type errors  
- **Functional Impact:** Causes frozen lockfile errors due to format mismatch  

This explains why later commits (like `1b2a242`) were needed to handle legacy lockfiles – the converter doesn't normalize the patchedDependencies format during lockfile reading.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
