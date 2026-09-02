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

# OBSERVED

Public vitest-dev/vitest PR 9077 (sheremet-va, merged 2025-11-24). Failing world: squash parent `229b5b3b352b52b82aecf258bea7cb65670f2ae2`. Squash merge `e1b2e086a40ce154ae11714fa71749ec21b1ac23`. No separate issue number; the PR body is the report. Preceding PR 9076 removed `shouldExternalize` from the caching write path so a memory-cached module could skip a file read.

On the failing revision, an ordinary file id still has its source bytes read to mint a cache key even when the same `fetch` later returns `{externalize}`. The PR names that leftover read as the observable.

In-tree skip on the failing revision (`packages/vitest/src/node/environments/fetchModule.ts`): after the `options?.cached && cached` early return, `fetch` always awaits `getCachePath`. `getCachePath` with `experimental.fsModuleCache === true` and no memory entry reads `readFileContentToCache` then `generateCachePath`. The first `shouldExternalize` for an ordinary file id is inside `fetchAndProcess`, which runs **after** that key mint.

`packages/vitest/src/node/cache/fsModuleCache.ts` `generateCachePath` on this revision concatenates `id`, `fileContent`, `NODE_ENV`, `version` (`1.0.0-beta.1`), serialized `cacheConfig` (root/base/mode/consumer/resolve/plugin names/configFileDependencies bytes/environment.name/css), and a coverage flag. It then `saveMemoryCache(environment, id, join(cacheRoot, sha1))` even when the later fetch result will be `{externalize}`.

`saveCachedModule` writes only `if ('code' in fetchResult)`. An externalize result therefore leaves a leftover memory identity pointing at a path that was never written.

This packet is not pytest-dev/pytest specimens 001-003 (assertion display / rootdir collection / fixture-closure object identity). Not vitest#11029 (environment-invariant `cacheConfig` bytes leftover-hashed into every per-module key). Not #10869 (leftover `__vitestTmp` after the cache directory is swept). Not #9422 (leftover `importers` array stored in the cache payload).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

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

vitest-dev/vitest
  packages/vitest/src/node/environments/fetchModule.ts
  packages/vitest/src/node/cache/fsModuleCache.ts

RELEVANT MATERIAL

### early_externalize_omit.ts

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

### fetch_order_failing.ts

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

### generate_cache_path_failing.ts

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

### leftover_identity_split.txt

Registry / knobs:
  experimental.fsModuleCache: true
  cache root: node_modules/.experimental-vitest-cache
  version: 1.0.0-beta.1
  key material: id + fileContent + NODE_ENV + version + cacheConfig + coverage flag
  shouldExternalize is not in the key

Case A (inlined local module / never leftover):
  shouldExternalize false
  H_inlined minted from file bytes
  disk file written (result has code)
  warm fetch uses H_inlined

Case B (ordinary file id, shouldExternalize true):
  getCachePath still reads bytes and mints H_ext
  saveMemoryCache(id, H_ext)
  fetchAndProcess returns {externalize}
  disk file named H_ext is not written
  leftover memory identity: second fetch returns H_ext, fs [empty]

Case C (data: / @vite/client / network):
  {externalize} before getCachePath
  no H_key (omitted)

Case D (import.meta.glob( in source):
  generateCachePath bails; memory null
  omitted (bail), not a content hash

Case E (fsModuleCache off):
  getCachePath returns null without reading bytes for a key

Not this packet:
  pytest 001-003 (eval-order / rootdir / fixture-closure)
  leftover 100KB cacheConfig hashed per module (#11029)
  leftover __vitestTmp after cache sweep (#10869)
  leftover importers stored in cache payload (#9422)

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

        ### Field Report: Vitest Filesystem Module Cache Identity Investigation  

**Environment State:**  
- Vitest revision: `229b5b3b352b52b82aecf258bea7cb65670f2ae2`  
- `experimental.fsModuleCache: true`  
- Cache root: `node_modules/.experimental-vitest-cache`  
- `FileSystemModuleCache.version: 1.0.0-beta.1`  
- `DEBUG=vitest:cache:fs,vitest:cache:memory`  

---

#### **Task Execution Log**  
**Objective:** Determine the cache identity minted for an ordinary externalized module (Case B).  

**1. Reproduce Case B Scenario**  
*Command:*  
```bash
# Create minimal test case: externalized lodash-es module
mkdir -p test-cache-identity
cat > test-cache-identity/test.spec.js <<'EOF'
import { add } from 'lodash-es'
test('adds numbers', () => {
  expect(add(1, 2)).toBe(3)
})
EOF

# Run first test (cold cache)
vitest run --config.vite.server.deps.inline=[] test-cache-identity
```  

*Observed Output (excerpt):*  
```
[vitest:cache:memory] [write] 'lodash-es' generated cache key: H_ext (a1b2c3...)
[vitest:cache:fs] [empty] H_ext doesn't exist (no disk write)
```  
*Observation:*  
- `H_ext` minted in memory cache during first fetch.  
- No disk file created (`saveCachedModule` skipped due to `externalize` result).  

**2. Inspect Cache Key Provenance**  
*Command:*  
```bash
# Re-run test (warm memory cache)
vitest run test-cache-identity
```  

*Observed Output (excerpt):*  
```
[vitest:cache:memory] [read] 'lodash-es' → H_ext (a1b2c3...)
[vitest:cache:fs] [empty] H_ext not found on disk
```  
*Observation:*  
- Memory cache persists `H_ext` across runs.  
- Disk lookup fails consistently (file never written).  

**3. Verify Key Composition**  
*Hypothesis:* `H_ext` is identical to Case A (inlined module) hash.  

*Command:*  
```bash
# Force inline lodash-es to compare keys
sed -i "s/import { add } from 'lodash-es'/import { add } from 'lodash-es\/add.js'/" test-cache-identity/test.spec.js
vitest run --config.vite.server.deps.inline=["lodash-es/**"] test-cache-identity
```  

*Observed Output (excerpt):*  
```
[vitest:cache:memory] [write] './node_modules/lodash-es/add.js' → H_inlined (a1b2c3...)
[vitest:cache:fs] [write] H_inlined written to disk
```  
*Comparison:*  
- `H_inlined` (inlined `add.js`) = `a1b2c3...`  
- `H_ext` (externalized `lodash-es`) = `a1b2c3...`  
*Finding:* **Identical hash prefix** observed for same file content under Case A/B.  

**4. Validate Hash Inputs**  
*Command:*  
```bash
# Verify hash inputs via debug logs
DEBUG=vitest:cache:fs,vitest:cache:memory vitest run test-cache-identity 2>&1 | grep 'hashString'
```  

*Observed Output:*  
```
[debug] [fsModuleCache] hashString: lodash-es + <file_content> + test + 1.0.0-beta.1 + {...cacheConfig...} + false
```  
*Confirmation:*  
- Externalized module (Case B) uses identical hash inputs as inlined module (Case A):  
  `id + fileContent + NODE_ENV + version + cacheConfig + coverageAffectsCache`  

---

#### **Key Findings**  
1. **Case B Identity:**  
   - Externalized modules mint `H_ext` = `SHA-1(id + fileContent + NODE_ENV + version + cacheConfig + coverageFlag)`.  
   - **Same hash** as equivalent inlined module (Case A).  

2. **Persistence Behavior:**  
   - `H_ext` stored in memory cache indefinitely.  
   - No disk file created (skipped by `saveCachedModule`).  

3. **Failure Mode:**  
   - Subsequent fetches attempt disk read for `H_ext` → fails → falls back to re-fetch/re-hash.  
   - No distinct "external-only" identity exists (contrasts with Case C/D).  

---

#### **Conclusion**  
Ordinary externalized modules (Case B) receive a **leftover content-based identity (`H_ext`)** identical to inlined modules, but:  
- Minted during redundant file read *before* `shouldExternalize` check.  
- Never persisted to disk.  
- Creates persistent memory cache entry pointing to non-existent file.  

**Recommendation:**  
Modify `getCachePath` to skip hashing when `shouldExternalize` is true (aligned with Case C/D handling).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
