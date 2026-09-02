CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Jest haste-map can drop the identity of a **manual mock name** after one of several files that claim that name is deleted in watch mode, even though surviving files still provide the mock. `mocks` maps the name to whichever file was processed last. On delete, ChangeQueue removed the name by name alone. The leftover identity is "name gone" until Jest restarts and rebuilds `mocks` from every file.

On failing_ref `1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963`:

```
const mockName = getMockName(filePath);
this._hasteMap.mocks.delete(mockName);
```

The deleted file need not even be the one `mocks` resolved to; deleting a duplicate still clobbers the owner. Claimants are not tracked.

Public report (jestjs/jest#16360). Two files claim the same mock name; delete one in watch mode; leftover missing name until restart. In-tree after the repair: `mockDuplicates` tracks claimants; `_removeMock` promotes a survivor still present in `files`.

Case A — watch, files unchanged:
  cache identity is current
  not leftover-after-delete

Case B — one duplicate mock file deleted, leftover missing name:
  leftover: name dropped / mock unresolved
  survivors omitted from delete path
  watch mode until restart

Case C — Jest restart / full crawl:
  fresh mocks rebuilt from remaining files
  not leftover missing name

Case D — mockDuplicates promote survivor (post-repair shape, not on failing_ref):
  name still resolves after one claimant is deleted
  not leftover missing name

The developer wants to know which identity case B actually used for the mock name after the file delete: leftover dropped-name (survivors omitted), current remaining file, or omitted (no haste map).

# OBSERVED

Public jestjs/jest#16360 (merged 2026-08-17). Squash `47a097e69c758d42b393d8dbed9dc00a89e74250` (parent `1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963`). Local jest was not performed on this lab host.

PR body: a duplicated mock name stops resolving in watch mode when one of its files is deleted. ChangeQueue dropped the name by name alone. Restart hides it because a removal makes buildHasteMap rebuild mocks from every file.

On failing_ref, mocks.delete(mockName) on any matching file delete. mockDuplicates does not exist.

Not this packet: specimen-090 webpack leftover contenthash. specimen-094 vitest leftover cache key. specimen-082 bun leftover peer.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963
# packages/jest-haste-map/src/watchers/ChangeQueue.ts mocks.delete(mockName)

# public shape:
# leftover missing mock name after deleting one duplicate file in watch
# name dropped even when survivors remain
# restart rebuilds mocks from remaining files
```

Source-backed only. Do not execute untrusted checkouts on the host.

jestjs/jest
  packages/jest-haste-map/src/watchers/ChangeQueue.ts

RELEVANT MATERIAL

### changequeue_failing.ts

// Reduced excerpt of ChangeQueue mock delete on failing_ref
// packages/jest-haste-map/src/watchers/ChangeQueue.ts
// 1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963
// mock name dropped by name alone. survivors omitted.

const mockName = getMockName(filePath);
this._hasteMap.mocks.delete(mockName);
// leftover missing name until restart

### leftover_identity_split.txt

Registry / fixture:
  jest-haste-map mocks Map
  leftover missing mock name after deleting one duplicate file

Case A (watch, files unchanged):
  current cache identity
  not leftover-after-delete

Case B (one duplicate mock file deleted, leftover missing name):
  leftover: name dropped / mock unresolved
  survivors omitted from delete path
  watch mode until restart

Case C (Jest restart / full crawl):
  fresh mocks from remaining files
  not leftover missing name

Case D (mockDuplicates promote survivor):
  name still resolves after one claimant is deleted
  not leftover missing name

Not this packet:
  webpack leftover contenthash (specimen-090)
  vitest leftover cache key (specimen-094)

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
