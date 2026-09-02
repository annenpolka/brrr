# TASK

Vitest's experimental filesystem module cache can still name a hashed identity for a module that the run then treats as external, even though other externalize paths never mint that identity at all.

In-tree on failing_ref `229b5b3b352b52b82aecf258bea7cb65670f2ae2`. `experimental.fsModuleCache: true`. Cache root is `node_modules/.experimental-vitest-cache` (or `experimental.fsModuleCachePath`). `FileSystemModuleCache.version` is `'1.0.0-beta.1'`.

```
DEBUG=vitest:cache:fs,vitest:cache:memory vitest run
```

`ModuleFetcher.fetch` (ordinary file URL, not `data:` / `@vite/client` / network):

1. `environment.moduleGraph.ensureEntryFromUrl`
2. `getCachePath(environment, moduleGraphModule)` — always, when the option is on
3. later `fetchAndProcess` → `resolver.shouldExternalize(moduleGraphModule.id)`

`getCachePath` on this revision:

```
const fileContent = await this.readFileContentToCache(...)
return this.fsCache.generateCachePath(this.config, environment, this.resolver, id, fileContent)
```

`generateCachePath` SHA-1s:

```
hashString += id + fileContent + (process.env.NODE_ENV ?? '') + this.version + cacheConfig + coverageAffectsCache
cacheKey = hash('sha1', hashString, 'hex')
join(cacheRoot, cacheKey)  // H_key
saveMemoryCache(environment, id, H_key)
```

`resolver` is an argument of `generateCachePath` and is not concatenated into `hashString`. `shouldExternalize` is not an input to the key.

Case A — inlined local module (not externalized). First fetch:

```
# e.g. ./sum.js imported by a test, server.deps does not externalize it
```

`H_inlined` is minted from those bytes. `saveCachedModule` writes `join(cacheRoot, H_inlined)` because the fetch result has `code`. `DEBUG=vitest:cache:memory` logs `[write] ${id} generated a cache in ${H_inlined}`. Warm fetch: memory hit, disk file exists, `[read]`.

Case B — `shouldExternalize` is true for an ordinary file id (typical: a `node_modules` package not listed in `server.deps.inline`). Same `fetch` order as case A.

On this revision `getCachePath` still reads the file and still mints `H_ext` from those leftover bytes, then `saveMemoryCache(id, H_ext)`. `fetchAndProcess` then returns `{ externalize, type: 'module' }`. `cacheResult` only writes when `'code' in result`, so the disk file named `H_ext` is never created. Public PR 9077 report of the leftover: vitest still reads file content to generate the cache key. Second fetch of the same id: `getMemoryCachePath` returns leftover `H_ext`; `getCachedModule` looks for a file that is not there (`DEBUG=vitest:cache:fs` `[empty] ${H_ext} doesn't exist`).

Case C — `data:` URL, `@vite/client`, or non-file `isExternalUrl`. `fetch` returns `{externalize}` **before** `getCachePath`. No `H_key`. File-content identity is omitted from any cache key.

Case D — source contains `import.meta.glob(`. `generateCachePath` bails, `saveMemoryCache(id, null)`, returns `null`. Omitted (bail identity), not a content hash.

Case E — `experimental.fsModuleCache` is not `true`. `getCachePath` returns `null` without reading bytes for a key.

The developer wants to know which identity an ordinary externalized module (case B) actually contained after `fetch`: leftover already-hashed `H_ext` from file content (same mint path as case A, unused on disk), omitted (same as case C / E), or a distinct external-only identity that never hashed those bytes.
