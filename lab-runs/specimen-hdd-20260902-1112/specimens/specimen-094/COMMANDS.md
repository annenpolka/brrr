# COMMANDS

```
# in-tree on failing_ref 229b5b3b352b52b82aecf258bea7cb65670f2ae2
# (not executed on this lab host)

# knobs
# experimental.fsModuleCache = true
# cache root: node_modules/.experimental-vitest-cache
# FileSystemModuleCache.version = 1.0.0-beta.1
# DEBUG=vitest:cache:fs,vitest:cache:memory

# case A — inlined local module
# import ./sum.js from a test; shouldExternalize false
# fetch: getCachePath then fetchAndProcess
# memory [write] generated a cache in H_inlined
# disk file join(cacheRoot, H_inlined) exists (result has code)
# warm fetch: memory [read] H_inlined; disk hit

# case B — ordinary file id that shouldExternalize
# e.g. node_modules dep not in server.deps.inline
# fetch still calls getCachePath first
# leftover: file bytes read; H_ext minted; saveMemoryCache(id, H_ext)
# fetchAndProcess then returns {externalize, type:'module'}
# disk file named H_ext is not written ('code' not in result)
# second fetch: memory leftover H_ext; fs [empty] H_ext doesn't exist

# case C — data: / @vite/client / network URL
# fetch returns {externalize} before getCachePath
# no H_key; file-content identity omitted

# case D — import.meta.glob( in source
# generateCachePath bails; saveMemoryCache(id, null)
# omitted (bail), not a content hash

# case E — experimental.fsModuleCache !== true
# getCachePath returns null without reading bytes for a key
```

Not executed on this lab host.
