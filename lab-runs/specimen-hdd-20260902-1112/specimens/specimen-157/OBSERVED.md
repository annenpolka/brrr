# OBSERVED

Public jestjs/jest#16360 (merged 2026-08-17). Squash `47a097e69c758d42b393d8dbed9dc00a89e74250` (parent `1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963`). Local jest was not performed on this lab host.

PR body: a duplicated mock name stops resolving in watch mode when one of its files is deleted. ChangeQueue dropped the name by name alone. Restart hides it because a removal makes buildHasteMap rebuild mocks from every file.

On failing_ref, mocks.delete(mockName) on any matching file delete. mockDuplicates does not exist.

Not this packet: specimen-090 webpack leftover contenthash. specimen-094 vitest leftover cache key. specimen-082 bun leftover peer.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
