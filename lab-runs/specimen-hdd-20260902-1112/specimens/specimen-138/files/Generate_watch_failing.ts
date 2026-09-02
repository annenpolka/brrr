// Reduced excerpt of Generate.ts watch loop on failing_ref
// packages/cli/src/Generate.ts
// 23e865c5601534f14cfe5fbc097c2eb1cf4f342e
// schemaContext loaded once. Watch generate reuses leftover object.

    const schemaResult = await getSchemaForGenerate(args['--schema'], config.schema, cwd, Boolean(postinstallCwd))
    const schemaContext = await processSchemaResult({ schemaResult, ignoreEnvVarErrors: !args['--sql'] })
    const directoryConfig = inferDirectoryConfig(schemaContext)
    // first generate uses schemaContext
    const watcher = new Watcher(schemaContext.schemaRootDir)
    for await (const changedPath of watcher) {
      logUpdate(`Change in ${path.relative(process.cwd(), changedPath)}`)
      // no getSchemaForGenerate here
      generatorsWatch = await getGenerators({
        schemaContext,
        printDownloadProgress: !watchMode,
        version: enginesVersion,
        generatorNames: args['--generator'],
        typedSql,
        registry: defaultRegistry.toInternal(),
      })
      await this.runGenerate({ generators: generatorsWatch })
    }
