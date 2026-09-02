KNOWN FIX (sealed): jestjs/jest PR 16360 squash 47a097e69c758d42b393d8dbed9dc00a89e74250.

failing_ref is parent 1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963.

ChangeQueue deleted mocks by name alone when any claimant file was deleted. Leftover missing name until restart even when survivors remained.

PR repair: mockDuplicates tracks claimants; _removeMock promotes a survivor.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
