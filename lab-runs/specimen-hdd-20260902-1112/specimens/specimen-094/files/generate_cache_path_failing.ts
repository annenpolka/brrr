// Reduced excerpt of FileSystemModuleCache.generateCachePath
// packages/vitest/src/node/cache/fsModuleCache.ts
// 229b5b3b352b52b82aecf258bea7cb65670f2ae2
// version 1.0.0-beta.1. resolver is passed in and is not part of hashString.

    hashString += id
      + fileContent
      + (process.env.NODE_ENV ?? '')
      + this.version
      + cacheConfig
      + coverageAffectsCache

    const cacheKey = hash('sha1', hashString, 'hex')
    const fsResultPath = join(cacheRoot, cacheKey)
    this.saveMemoryCache(environment, id, fsResultPath)
    return fsResultPath

  async saveCachedModule(cachedFilePath, fetchResult, importers = [], mappings = false) {
    if ('code' in fetchResult) {
      await atomicWriteFile(cachedFilePath, `${fetchResult.code}${cacheComment}${this.toBase64(result)}`)
    }
  }
