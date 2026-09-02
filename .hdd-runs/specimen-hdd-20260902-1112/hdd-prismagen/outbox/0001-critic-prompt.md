# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        Based on the provided material and operating constraints, I'll investigate the identity case for scenario B using only the installed Prisma CLI tool and observed behaviors. Here's my field report:

**Experiment Setup**
```
$ mkdir watch_identity_test && cd watch_identity_test
$ npm init -y
$ npm install @prisma/client
$ cat > schema.prisma <<'EOF'
generator client {
  provider = "prisma-client-js"
}
model A {
  id Int @id
}
EOF
```

**Initial Baseline Observation**
```
$ prisma generate
✔ Generated Prisma Client (v5.12.1) to ./node_modules/@prisma/client in 112ms

$ ls -1 node_modules/.prisma/client/
index.d.ts
index.js
libquery_engine-linux-arm64-openssl-3.0.x.so.node
package.json
schema.prisma
```

**Scenario B Execution (schema change during watch)**
```
# Terminal 1 - Start watch process
$ prisma generate --watch
✔ Generated Prisma Client (v5.12.1) to ./node_modules/@prisma/client in 98ms
Watching...  

# Terminal 2 - Modify schema
$ cat >> schema.prisma <<'EOF'
model B {
  id Int @id
}
EOF

# Terminal 1 Output After Change
Change detected in schema.prisma
✔ Generated Prisma Client (v5.12.1) to ./node_modules/@prisma/client in 86ms
```

**Post-Change Artifact Inspection**
```
$ ls -1 node_modules/.prisma/client/
index.d.ts
index.js
libquery_engine-linux-arm64-openssl-3.0.x.so.node
package.json
schema.prisma  # Contains ONLY model A
```

**Contrast with Scenario C (non-watch generate)**
```
$ prisma generate
✔ Generated Prisma Client (v5.12.1) to ./node_modules/@prisma/client in 104ms

$ grep 'model' node_modules/.prisma/client/schema.prisma
model A {
model B {
```

**Key Findings**
1. The watch process regenerates client artifacts after schema changes (output confirms generation occurred)
2. Generated artifacts retain the **leftover first-load schemaContext** (client schema.prisma lacks model B)
3. Manual regeneration without watch uses **current schema identity** (includes model B)
4. Watch process output claims successful generation but delivers stale artifacts

**Identity Confirmation**
For case B (schema.prisma append during watch):
- ✅ Uses leftover first-load schemaContext
- ❌ Omits current schema file identity
- ❌ Does not skip generation (process executes but uses stale context)

**Observed Behavioral Paradox**
The CLI reports successful generation after schema changes but delivers artifacts inconsistent with the current schema file. This matches public report prisma/prisma#27128 where the watch process "reverts" manually generated updates.

**Recommended Next Investigation**
1. Add debug output to `getGenerators()` to log schema hash before generation:
```typescript
console.debug(`Schema hash: ${schemaContext.schema?.hash}`)
```
2. Compare hashes between:
   - Initial watch load
   - Post-change watch generation
   - Non-watch generation
3. Verify if hash changes correlate with artifact updates

**Unresolved Contradiction**
The tool claims regeneration occurs but delivers stale artifacts. This suggests either:
a) SchemaContext isn't invalidated after file changes, or
b) Artifact writing silently fails when schemaContext is stale

No filesystem errors were observed during testing, pointing to schemaContext reuse as root cause per failing_ref behavior.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
