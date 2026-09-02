// Reduced excerpt of ChangeQueue mock delete on failing_ref
// packages/jest-haste-map/src/watchers/ChangeQueue.ts
// 1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963
// mock name dropped by name alone. survivors omitted.

const mockName = getMockName(filePath);
this._hasteMap.mocks.delete(mockName);
// leftover missing name until restart
