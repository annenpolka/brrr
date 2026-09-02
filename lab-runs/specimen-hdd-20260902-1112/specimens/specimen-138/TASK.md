# TASK

`prisma generate --watch` can keep the identity of a **previous generated client** after `schema.prisma` should have been a different schema. The first load builds `schemaContext` once. The watch loop regenerates from that leftover object. Current schema file identity is omitted.

On failing_ref `23e865c5601534f14cfe5fbc097c2eb1cf4f342e`:

```
const schemaResult = await getSchemaForGenerate(...)
const schemaContext = await processSchemaResult({ schemaResult, ... })
const directoryConfig = inferDirectoryConfig(schemaContext)
// ... first generate ...
const watcher = new Watcher(schemaContext.schemaRootDir)
for await (const changedPath of watcher) {
  logUpdate(`Change in ${path.relative(process.cwd(), changedPath)}`)
  generatorsWatch = await getGenerators({
    schemaContext,  // leftover first-load schema
    ...
  })
  await this.runGenerate({ generators: generatorsWatch })
}
```

Public report (prisma/prisma#27128). `prisma generate --watch`; append `model B`; leftover generated client still only `A.ts` until a non-watch `prisma generate`.

In-tree after the repair (not on failing_ref): watch loop re-runs `getSchemaForGenerate` + `processSchemaResult` + `inferDirectoryConfig`. E2E `27128-generate-watch` expects `['A.ts','B.ts']` after the append.

Case A — second watch tick, unchanged schema.prisma:
  generated client identity is current
  not leftover-after-schema-change

Case B — schema.prisma appends model B, leftover schemaContext:
  leftover: previous schema's generated client (A.ts only)
  current schema file omitted from watch generate identity
  B.ts missing

Case C — `prisma generate` without `--watch` after the append:
  current schema identity
  not leftover previous client

Case D — reload schema inside the watch loop (post-repair shape, not on failing_ref):
  generated client includes B.ts
  not leftover previous schema

The developer wants to know which identity case B actually used for the generated client after the schema.prisma change: leftover first-load schemaContext, current schema file identity, or omitted (no generate).
