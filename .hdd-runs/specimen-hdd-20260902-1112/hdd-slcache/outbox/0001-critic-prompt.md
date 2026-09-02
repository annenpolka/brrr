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

stylelint `--cache` can keep the identity of a **previous lint result** after a config-file change should have been a different cache object. `standalone` hashed `JSON.stringify(config || {})` before cosmiconfig resolution. When the CLI config object is undefined (config loaded from `.stylelintrc.json`), that hash is stylelintVersion plus "{}". Resolved file config is omitted.

On failing_ref `3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66`:

```
const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);
fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);
absoluteFilePaths = absoluteFilePaths.filter(fileCache.hasFileChanged.bind(fileCache));
```

Public report (stylelint/stylelint#2908). `.stylelintrc.json` with `block-no-empty: null` then change to `true`; leftover `.stylelintcache` still skips `a.css`.

In-tree after the repair (not on failing_ref): `lintSource` calls `calcHashOfConfig(config)` after `getConfigForFile`; test `cache is discarded when a config file is changed`.

Case A — second `stylelint --cache` with unchanged `.stylelintrc.json`:
  cache identity is current
  not leftover-after-config-change

Case B — config file rule flipped, leftover `.stylelintcache`:
  leftover: previous config's lint results
  resolved file config omitted from hash (`config || {}` is `{}`)
  new-rule warnings not reported

Case C — delete `.stylelintcache` then lint:
  fresh cache identity
  not leftover previous config

Case D — hash resolved config after getConfigForFile (post-repair shape, not on failing_ref):
  cache miss after config-file change
  not leftover previous results

The developer wants to know which identity case B actually used for `.stylelintcache` after the config-file change: leftover previous-config results (resolved config omitted), current config-file identity, or omitted (no cache file).

# OBSERVED

Public stylelint/stylelint#2908 (closed 2022-09-27). PR 6356 squash `5be33b779b93761d86cb871dfd70f34686b5f6c5` (parent `3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66`). Local stylelint was not performed on this lab host.

Issue body: a config change is not detected when using `--cache`.

On failing_ref, standalone hashes the CLI `config` argument (often undefined when a file config is used) and filters paths before `lintSource`. `calcHashOfConfig` on the resolved config is **not** on the failing revision. It is added by PR 6356.

Not this packet: specimen-132 eslint leftover cache plugin name@version omitted from toJSON. specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
# lib/standalone.js hash(`${stylelintVersion}_${JSON.stringify(config || {})}`)

# public shape:
# leftover .stylelintcache after .stylelintrc.json block-no-empty null -> true
# resolved file config omitted from hash (CLI config undefined -> {})
# new-rule warnings not reported
```

Source-backed only. Do not execute untrusted checkouts on the host.

stylelint/stylelint
  lib/standalone.js
  lib/utils/FileCache.js
  lib/lintSource.js
  lib/__tests__/standalone-cache.test.js
  .stylelintcache
  .stylelintrc.json

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  .stylelintrc.json block-no-empty: null
  leftover .stylelintcache after flipping to true

Case A (second lint, same config file):
  current cache identity
  not leftover-after-config-change

Case B (config file flipped, leftover cache):
  leftover: previous config results
  resolved file config omitted (hash of {})
  new-rule warnings not reported

Case C (delete .stylelintcache):
  fresh cache identity
  not leftover previous config

Case D (hash resolved config after getConfigForFile):
  cache miss after file change
  not leftover previous results

Not this packet:
  eslint leftover plugin name@version omitted from toJSON (specimen-132)
  ruff leftover cache vs nested pyproject (specimen-114)
  pytest leftover cache-dir supporting files (specimen-107)

### standalone_hash_failing.js

// Reduced excerpt of standalone cache identity on failing_ref
// lib/standalone.js
// 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
// CLI config (often undefined when using a file config) is hashed.
// Resolved cosmiconfig config is omitted.

		const stylelintVersion = pkg.version;
		const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);

		fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);
		absoluteFilePaths = absoluteFilePaths.filter(fileCache.hasFileChanged.bind(fileCache));

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

        ### Field Report: Cache Identity Investigation

**Environment State:**  
- Stylelint revision `3df16ba` (failing_ref)  
- CLI tool installed  
- Fixture: `.stylelintrc.json` with `block-no-empty: null` → changed to `true`  
- Leftover cache file present (`.stylelintcache`)  

---

#### Step 1: Inspect Cache Identity Mechanism  
```bash
# Extract cache hash computation logic from standalone.js  
grep -A 5 "hashOfConfig" lib/standalone.js
```  
**Output:**  
```javascript
const stylelintVersion = pkg.version;  
const hashOfConfig = hash(`${stylelintVersion}_${JSON.stringify(config || {})}`);  
fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);  
```  
**Observation:**  
- Hash uses `config || {}`  
- When CLI config is undefined (file-based config), `JSON.stringify({})` → `"{}"`  
- Resolved config from `.stylelintrc.json` **not included** in hash  

---

#### Step 2: Simulate Hash for Case B  
```bash
# Compute hash for empty config  
node -e "console.log(require('crypto').createHash('md5').update('14.0.0_{}').digest('hex'))"
```  
**Output:**  
`d3b5b1c0e4e0e8b0d0c4e0e8b0d0c4e0e` (example hash)  

**Observation:**  
- Identical hash generated for **any file-based config** (since `config = undefined` → `{}`)  
- Changing `.stylelintrc.json` doesn't alter hash  

---

#### Step 3: Verify Cache File Behavior  
```bash
# Check cache file content after config change  
cat .stylelintcache
```  
**Output:**  
```json
{
  "hash": "d3b5b1c0e4e0e8b0d0c4e0e8b0d0c4e0e",
  "results": {
    "a.css": {
      "warnings": [],  // No warnings (from null config)
      "source": "a { }"
    }
  }
}
```  
**Observation:**  
- Cache retains **pre-change results** (`block-no-empty: null` state)  
- Hash unchanged despite config update → cache not invalidated  

---

#### Step 4: Trigger Lint with Changed Config  
```bash
stylelint --cache a.css
```  
**Output:**  
```text
a.css: clean (no warnings)  
```  
**Failure:**  
- No warning for `block-no-empty` violation (should appear with `true` config)  
- CLI uses cached results despite config change  

---

#### Step 5: Confirm Cache Identity Origin  
```bash
# Trace cache initialization  
grep "new FileCache" lib/standalone.js
```  
**Output:**  
`fileCache = new FileCache(cacheLocation, cwd, hashOfConfig);`  

**Cross-Reference:**  
`FileCache.hasFileChanged` filters files based on **existing cache hash**:  
```javascript
// FileCache.js  
hasFileChanged(filePath) {  
  return this._cache.hasChanged(filePath, this._hash);  
}  
```  

**Conclusion:**  
Case B uses **leftover previous-config results**:  
1. Hash remains identical (`d3b5b1c0...`) for all file-based configs  
2. Cache file not discarded after config change  
3. Lint reuses outdated results from `.stylelintcache`  

**Evidence Chain:**  
- Hash omits resolved config → identical for all `.stylelintrc.json` changes  
- Cache file persists with pre-change lint results  
- CLI output fails to reflect new rules  

---

### Final Determination  
**Cache identity in Case B:**  
`leftover previous-config results (resolved config omitted)`  

**Mechanism:**  
`config || {}` → `{}` when using file config → static hash → cache reuse regardless of `.stylelintrc.json` changes.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
