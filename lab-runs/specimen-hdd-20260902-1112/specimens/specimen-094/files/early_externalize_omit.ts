// Reduced excerpt of fetch early returns that never mint a cache key
// packages/vitest/src/node/environments/fetchModule.ts
// 229b5b3b352b52b82aecf258bea7cb65670f2ae2
// Contrast with ordinary shouldExternalize, which runs after getCachePath.

    if (url.startsWith('data:')) {
      return { externalize: url, type: 'builtin' }
    }
    if (url === '/@vite/client' || url === '@vite/client') {
      return { externalize: '/@vite/client', type: 'module' }
    }
    if (isExternalUrl(url) && !isFileUrl) {
      return { externalize: url, type: 'network' }
    }
