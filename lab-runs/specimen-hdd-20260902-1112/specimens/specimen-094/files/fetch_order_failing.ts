// Reduced excerpt of ModuleFetcher.fetch / getCachePath / fetchAndProcess
// packages/vitest/src/node/environments/fetchModule.ts
// 229b5b3b352b52b82aecf258bea7cb65670f2ae2
// Ordinary file ids mint a cache key before shouldExternalize.

    if (options?.cached && cached) {
      return { cache: true }
    }

    const cachePath = await this.getCachePath(
      environment,
      moduleGraphModule,
    )
    // ... later, after a miss:
    const result = await this.fetchAndProcess(environment, url, importer, moduleGraphModule, options)

  private async getCachePath(environment, moduleGraphModule) {
    if (!this.fsCacheEnabled) {
      return null
    }
    const memoryCacheKey = this.fsCache.getMemoryCachePath(environment, moduleId)
    if (memoryCacheKey !== undefined) {
      return memoryCacheKey
    }
    const fileContent = await this.readFileContentToCache(environment, moduleGraphModule)
    return this.fsCache.generateCachePath(
      this.config,
      environment,
      this.resolver,
      moduleGraphModule.id!,
      fileContent,
    )
  }

  private async fetchAndProcess(...) {
    const externalize = await this.resolver.shouldExternalize(moduleGraphModule.id!)
    if (externalize) {
      return { externalize, type: 'module' }
    }
    // fetchModule(...)
  }
