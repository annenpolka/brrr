# OBSERVED

Public vitest-dev/vitest PR 9077 (sheremet-va, merged 2025-11-24). Failing world: squash parent `229b5b3b352b52b82aecf258bea7cb65670f2ae2`. Squash merge `e1b2e086a40ce154ae11714fa71749ec21b1ac23`. No separate issue number; the PR body is the report. Preceding PR 9076 removed `shouldExternalize` from the caching write path so a memory-cached module could skip a file read.

On the failing revision, an ordinary file id still has its source bytes read to mint a cache key even when the same `fetch` later returns `{externalize}`. The PR names that leftover read as the observable.

In-tree skip on the failing revision (`packages/vitest/src/node/environments/fetchModule.ts`): after the `options?.cached && cached` early return, `fetch` always awaits `getCachePath`. `getCachePath` with `experimental.fsModuleCache === true` and no memory entry reads `readFileContentToCache` then `generateCachePath`. The first `shouldExternalize` for an ordinary file id is inside `fetchAndProcess`, which runs **after** that key mint.

`packages/vitest/src/node/cache/fsModuleCache.ts` `generateCachePath` on this revision concatenates `id`, `fileContent`, `NODE_ENV`, `version` (`1.0.0-beta.1`), serialized `cacheConfig` (root/base/mode/consumer/resolve/plugin names/configFileDependencies bytes/environment.name/css), and a coverage flag. It then `saveMemoryCache(environment, id, join(cacheRoot, sha1))` even when the later fetch result will be `{externalize}`.

`saveCachedModule` writes only `if ('code' in fetchResult)`. An externalize result therefore leaves a leftover memory identity pointing at a path that was never written.

This packet is not pytest-dev/pytest specimens 001-003 (assertion display / rootdir collection / fixture-closure object identity). Not vitest#11029 (environment-invariant `cacheConfig` bytes leftover-hashed into every per-module key). Not #10869 (leftover `__vitestTmp` after the cache directory is swept). Not #9422 (leftover `importers` array stored in the cache payload).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
