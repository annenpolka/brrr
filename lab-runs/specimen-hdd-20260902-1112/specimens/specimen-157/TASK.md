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
