CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public prisma/prisma#27128 (closed 2025-05-28). PR prisma/orm#27279 squash `8d06a847ea4e84c70c84469b2a845e568f454e14` (parent `23e865c5601534f14cfe5fbc097c2eb1cf4f342e`). Local prisma generate was not performed on this lab host.

Issue body: `prisma generate --watch` runs once correctly, then produces the same generated client regardless of schema.prisma changes. A second terminal `prisma generate` (no watch) writes the current client; the watch process then reverts it to the leftover first-load client.

On failing_ref, `schemaContext` is built once before the watcher. The watch loop does **not** call `getSchemaForGenerate`. That reload is added by PR 27279.

Not this packet: specimen-041 protobuf JSON unknown-fields. specimen-043 protobuf CI generated-code-drift. specimen-136 pants leftover vcs_version process cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 23e865c5601534f14cfe5fbc097c2eb1cf4f342e
# packages/cli/src/Generate.ts watch loop reuses leftover schemaContext

# public shape:
# leftover generated client after schema.prisma appends model B
# watch generate identity is first-load schemaContext
# generated/models stays ['A.ts'] until non-watch prisma generate
```

Source-backed only. Do not execute untrusted checkouts on the host.

prisma/orm
  packages/cli/src/Generate.ts
  packages/cli/src/generate/Watcher.ts
  packages/client/tests/e2e/27128-generate-watch/prisma/schema.prisma
  packages/client/tests/e2e/27128-generate-watch/tests/main.mts

RELEVANT MATERIAL

### Generate_watch_failing.ts

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

### leftover_identity_split.txt

Registry / fixture:
  prisma generate --watch
  leftover generated client after schema.prisma appends model B

Case A (second watch tick, same schema.prisma):
  current generated client identity
  not leftover-after-schema-change

Case B (schema.prisma appends model B, leftover schemaContext):
  leftover: previous schema's generated client (A.ts only)
  current schema file omitted from watch generate identity
  B.ts missing

Case C (prisma generate without --watch):
  current schema identity
  not leftover previous client

Case D (reload schema inside watch loop):
  generated client includes B.ts
  not leftover previous schema

Not this packet:
  protobuf JSON unknown-fields (specimen-041)
  protobuf CI generated-code-drift (specimen-043)
  pants leftover vcs_version process cache (specimen-136)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
