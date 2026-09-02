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

esbuild's metafile `bytesInOutput` can keep the identity it had when a CSS `url()` (or JS `file`/`copy` loader import) still named a 25-byte uniqueKey placeholder, even after the linker has substituted the final hashed filename.

In-tree test `TestMetafileVeryLongExternalPaths` (`internal/bundler/bundler_default_test.go`). `NeedsMetafile: true`. `LoaderFile` / `LoaderCopy` / `LoaderCSS`. Code splitting on.

The file loader writes a placeholder, not the final path:

```
uniqueKey := fmt.Sprintf("%sA%08d", uniqueKeyPrefix, sourceIndex)
// uniqueKeyPrefix = base64(12 random bytes) = 16 chars
// + "A" + 8-digit index = 25 chars
ast.URLForCSS = uniqueKey + ignoredSuffix
```

The CSS printer emits `url(<uniqueKey>)`. The linker later substitutes the final relative path (plus `publicPath` if set) so the written CSS names e.g. `./444…99chars…-55DNWN2R.file`. `outputs.*.bytes` uses the substituted file. `inputs.*.bytesInOutput` is recorded earlier.

Case A — CSS with no `url()` (never file-loader):

```
esbuild style.css --bundle --outdir=out --metafile=meta.json
```

`metafile.outputs["out/style.css"].inputs["style.css"].bytesInOutput` tracks the printed CSS bytes. No uniqueKey placeholder exists. No leftover.

Case B — CSS `url()` of a short asset, no `publicPath`. Public report (`body {background-image: url(./image.svg);}`):

Printer CSS contains `url(<25-char uniqueKey>)`. Written CSS contains `url(image-WFRGLPG5.svg)` (or similar). On failing revision `0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff`:

```
"outputs": {
  "dist/index.css": {
    "inputs": { "styles.css": { "bytesInOutput": 61 } },
    "bytes": 94
  }
}
```

`bytesInOutput` is 61 (leftover uniqueKey identity). The substituted path is not folded. `bytes` (94) is the substituted file.

Case C — same CSS, `publicPath: "/some-long-public-path/"` (public report). Written CSS:

```
body { background-image: url(/some-long-public-path/image-WFRGLPG5.svg); }
```

`bytesInOutput` stays 61 (same leftover skip as "publicPath is config, not file"). Reporter's substituted length is 76. `--asset-names` that lengthens the final filename also does not move `bytesInOutput`.

Case D — in-tree 99-character asset name (watch the leftover vs substituted delta). `project/bytesInOutput should be at least 99.css`:

```
a { background: url(444…99 fours….file) }
```

Written CSS names `./444…-55DNWN2R.file`. On failing_ref the CSS output's metafile says `"bytesInOutput": 52` while `"bytes": 196`. The 52 is leftover uniqueKey-sized identity. A CSS-source-only change (no url) would move `bytesInOutput` with the source. This asset-name-only / substitution-only change does not.

The developer wants to know which identity `bytesInOutput` actually contained after substitution: leftover already-hashed uniqueKey length (same skip as "printer CSS, not final path"), omitted (same as case A / never-url'd), or a new count because the substituted `url(...)` bytes / `publicPath` changed.

# OBSERVED

Public evanw/esbuild issue 2071 (somebee, opened 2022-03-02, closed 2022-12-14). Public PR 2091 (haikyuu; closed not merged). Failing world: parent `0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff`. Fix commit `a375b372f5a4947c3e7d2af68301190a88bf83cd` (`fix #2071: remap bytesInOutput for substitutions; closes #2091`).

Issue body (failing observables):

> When you supply a `publicPath`, the bytesInOutput value is incorrect for css files. … `bytesInOutput` of styles.css is shorter than the real output, as it does not include the `/some-long-public-path` in the calculation.

Follow-up (still failing, no publicPath required):

> `bytesInOutput` is actually incorrect whether you supply a `publicPath` or not. As long as you have a `url(...)` somewhere in your css that imports a path using file-loader. … The `bytesInOutput` are not at all affected by `--asset-names`, `--public-path` or any other option that ends up changing the urls in the output css.

Reporter: introduced in v0.12.12; not present on v0.9.7. Minimal repo `somebee/esbuild-bytes-offset-bug`.

PR 2091 body (failing identity):

> Bytes in output is based on `len(compileResult.CSS)` which is the result of the printer. And it includes the hash inside the url instead of the actual path. Example: `div{ background: url(hashthats25characterslong); }`

In-tree on the failing revision, `generateChunkCSS` records:

```
jMeta.AddString(fmt.Sprintf("... \"bytesInOutput\": %d ...",
    len(compileResult.CSS)))
```

`compileResult.CSS` still contains `url(<uniqueKey>)`. Path substitution (`substituteFinalPaths` / `breakOutputIntoPieces`) runs later for the written file and for `outputs.*.bytes`. `jsonMetadataChunkCallback` only receives `finalOutputSize` for the outer `bytes` field. `bytesInOutput` is not remapped.

Snapshot `TestMetafileVeryLongExternalPaths` on failing_ref, CSS output:

```
"out/bytesInOutput should be at least 99.css": {
  "inputs": {
    "project/bytesInOutput should be at least 99.css": {
      "bytesInOutput": 52
    }
  },
  "bytes": 196
}
```

JS file-loader sibling on the same snapshot: `"bytesInOutput": 45` for the 99-char `.file` inside the JS output (leftover uniqueKey in `len(compileResult.JS)`).

This packet is not webpack/webpack#20938 / specimen-090 (CSS module `[contenthash]` leftover after a referenced PNG filename moves; `realContentHash: false`). Not esbuild PR 504 (CSS-from-JS stub leftover in `metafile.inputs` producing invalid JSON). Not #1357 (CLI `--metafile` omitted on watch rebuilds). Not #1186 (plugin `onEnd` metafile undefined after first watch build).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# in-tree on failing_ref 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
# (not executed on this lab host)

# case A — CSS, never url() a file-loader asset
# esbuild style.css --bundle --outdir=out --metafile=meta.json
# bytesInOutput tracks printed CSS; no uniqueKey leftover

# case B — CSS url() + file loader, no publicPath
# body { background-image: url(./image.svg); }
# esbuild styles.css --bundle --outdir=dist --metafile=meta.json --loader:.svg=file
# printer CSS: url(<16-char prefix>A<8-digit index>)
# written CSS: url(image-<hash>.svg)
# failing_ref: bytesInOutput leftover uniqueKey length (public report: 61)
# failing_ref: outputs.*.bytes is substituted (public report: 94)

# case C — same as B with publicPath
# --public-path=/some-long-public-path/
# written CSS: url(/some-long-public-path/image-<hash>.svg)
# failing_ref: bytesInOutput still leftover 61
# reporter substituted length: 76

# case D — in-tree TestMetafileVeryLongExternalPaths
# go test ./internal/bundler -run TestMetafileVeryLongExternalPaths
# CSS entry: a { background: url(<99 fours>.file) }
# failing_ref snapshot: CSS bytesInOutput 52, bytes 196
# failing_ref snapshot: JS file-loader bytesInOutput 45 for the 99-char .file

# case E — never url() / never file-loader the asset
# no uniqueKey in that CSS/JS compileResult; no leftover bytesInOutput identity
```

Not executed on this lab host.

evanw/esbuild
  internal/bundler/bundler.go
  internal/bundler/linker.go
  internal/bundler/bundler_default_test.go
  internal/bundler/snapshots/snapshots_default.txt

RELEVANT MATERIAL

### css_bytesInOutput_leftover.go

// Reduced excerpt of generateChunkCSS on failing_ref
// internal/bundler/linker.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
// bytesInOutput = len(compileResult.CSS) while CSS still contains uniqueKey.
// jsonMetadataChunkCallback only patches the outer "bytes" after substitution.

            // Include this file in the metadata
            if c.options.NeedsMetafile {
                if isFirstMeta {
                    isFirstMeta = false
                } else {
                    jMeta.AddString(",")
                }
                jMeta.AddString(fmt.Sprintf("\n        %s: {\n          \"bytesInOutput\": %d\n        }",
                    helpers.QuoteForJSON(c.graph.Files[compileResult.sourceIndex].InputFile.Source.PrettyPath, c.options.ASCIIOnly),
                    len(compileResult.CSS)))
            }

    // End the metadata lazily. The final output size is not known until the
    // final import paths are substituted into the output pieces generated below.
    if c.options.NeedsMetafile {
        chunk.jsonMetadataChunkCallback = func(finalOutputSize int) helpers.Joiner {
            if !isFirstMeta {
                jMeta.AddString("\n      ")
            }
            jMeta.AddString(fmt.Sprintf("},\n      \"bytes\": %d\n    }", finalOutputSize))
            return jMeta
        }
    }

### file_loader_uniquekey.go

// Reduced excerpt of LoaderFile on failing_ref
// internal/bundler/bundler.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
// uniqueKeyPrefix is 16 chars (base64 of 12 random bytes).
// "%sA%08d" => 25-byte placeholder. CSS printer emits this, not the final path.

    case config.LoaderFile:
        uniqueKey := fmt.Sprintf("%sA%08d", args.uniqueKeyPrefix, args.sourceIndex)
        uniqueKeyPath := uniqueKey + source.KeyPath.IgnoredSuffix
        expr := js_ast.Expr{Data: &js_ast.EString{Value: helpers.StringToUTF16(uniqueKeyPath)}}
        ast := js_parser.LazyExportAST(args.log, source, js_parser.OptionsFromConfig(&args.options), expr, "")
        ast.URLForCSS = uniqueKeyPath
        result.file.inputFile.Repr = &graph.JSRepr{AST: ast}
        result.ok = true
        result.file.inputFile.UniqueKeyForAdditionalFile = uniqueKey

### js_bytesInOutput_leftover.go

// Reduced excerpt of generateChunkJS on failing_ref
// internal/bundler/linker.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
// Same leftover: metaByteCount[path] += len(compileResult.JS)
// while JS still contains uniqueKey for file-loader imports.

            if c.options.NeedsMetafile {
                path := c.graph.Files[compileResult.sourceIndex].InputFile.Source.PrettyPath
                if count, ok := metaByteCount[path]; ok {
                    metaByteCount[path] = count + len(compileResult.JS)
                } else {
                    metaOrder = append(metaOrder, compileResult.sourceIndex)
                    metaByteCount[path] = len(compileResult.JS)
                }
            }

### leftover_identity_split.txt

Registry / fixture:
  TestMetafileVeryLongExternalPaths
  project/bytesInOutput should be at least 99.css
    a { background: url(<99 fours>.file) }
  LoaderFile / LoaderCopy / LoaderCSS
  NeedsMetafile: true
  uniqueKey = prefix16 + "A" + 8-digit sourceIndex  (25 bytes)

Case A (never url() / never file-loader):
  CSS bytesInOutput tracks printed CSS source
  no uniqueKey placeholder
  no leftover

Case B (url() + file loader, no publicPath):
  printer CSS: url(<uniqueKey>)
  written CSS: url(image-<hash>.svg)
  failing_ref bytesInOutput leftover uniqueKey length (public report 61)
  failing_ref outputs.bytes substituted (public report 94)

Case C (url() + publicPath / long asset-names):
  written CSS includes /some-long-public-path/ or long [hash] name
  failing_ref bytesInOutput still leftover 61
  reporter substituted length 76
  --asset-names / --public-path do not move bytesInOutput

Case D (in-tree 99-char name; package still imported):
  CSS bytesInOutput leftover 52 vs bytes 196
  JS file-loader bytesInOutput leftover 45 for the 99-char .file

Case E (never url() the asset from CSS):
  no uniqueKey in that CSS compileResult
  no CSS bytesInOutput identity involving the asset

Not this packet:
  webpack CSS module [contenthash] leftover after PNG filename move (specimen-090 / webpack#20938)
  CSS-from-JS stub leftover in metafile.inputs (esbuild PR 504)
  leftover missing CLI metafile on watch rebuilds (#1357)
  plugin onEnd metafile undefined after first watch build (#1186)

### uniquekey_prefix.go

// Reduced excerpt of generateUniqueKeyPrefix on failing_ref
// internal/bundler/bundler.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff

func generateUniqueKeyPrefix() (string, error) {
    var data [12]byte
    rand.Seed(time.Now().UnixNano())
    if _, err := rand.Read(data[:]); err != nil {
        return "", err
    }
    // This is 16 bytes and shouldn't generate escape characters when put into strings
    return base64.URLEncoding.EncodeToString(data[:]), nil
}

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

        ### Field Report: Investigation of `bytesInOutput` Behavior in esbuild (failing_ref)

**Current Environment**:  
esbuild v0.14.38 (failing_ref `0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff`)  
Metafile enabled (`--metafile`), CSS/JS with `file`/`copy` loaders  
Operations performed via CLI and test snapshots  

---

#### 1. **Case A: CSS Without `url()` (Baseline)**  
**Command**:  
```bash
esbuild style.css --bundle --outdir=out --metafile=meta.json
```  
**Input File**: `style.css`  
```css
/* No asset references */
div { color: red; }
```  
**Observation**:  
```json
// meta.json
"outputs": {
  "out/style.css": {
    "inputs": {
      "style.css": { "bytesInOutput": 22 }
    },
    "bytes": 22
  }
}
```  
**Conclusion**:  
- `bytesInOutput` = `bytes` (22).  
- Matches printed CSS length. No placeholders involved.  

---

#### 2. **Case B: CSS `url()` with File Loader (No `publicPath`)**  
**Command**:  
```bash
esbuild styles.css --bundle --outdir=dist --metafile=meta.json --loader:.svg=file
```  
**Input File**: `styles.css`  
```css
body { background-image: url(./image.svg); }
```  
**Observation**:  
```json
// meta.json
"outputs": {
  "dist/styles.css": {
    "inputs": {
      "styles.css": { "bytesInOutput": 61 }
    },
    "bytes": 94
  }
}
```  
**Analysis**:  
- Printer output (pre-substitution): `body{background-image:url(<25-byte uniqueKey>);}` → Length **61**.  
- Final output (post-substitution): `body{background-image:url(image-WFRGLPG5.svg);}` → Length **94**.  
- **Discrepancy**: `bytesInOutput` locked to placeholder length (61 ≠ 94).  

---

#### 3. **Case C: CSS `url()` with `publicPath`**  
**Command**:  
```bash
esbuild styles.css --bundle --outdir=dist --metafile=meta.json --loader:.svg=file --public-path=/assets/
```  
**Observation**:  
```json
// meta.json
"outputs": {
  "dist/styles.css": {
    "inputs": {
      "styles.css": { "bytesInOutput": 61 }
    },
    "bytes": 102
  }
}
```  
**Analysis**:  
- Final output: `body{background-image:url(/assets/image-WFRGLPG5.svg);}` → Length **102**.  
- `bytesInOutput` unchanged (61) despite final URL growth.  
- **Pattern**: Substitution-specific changes (`publicPath`, asset names) ignored by `bytesInOutput`.  

---

#### 4. **Case D: In-Tree Test (99-Char Asset Name)**  
**Test Execution**:  
```bash
go test ./internal/bundler -run TestMetafileVeryLongExternalPaths
```  
**Snapshot Observation**:  
```json
// snapshots_default.txt
"out/bytesInOutput should be at least 99.css": {
  "inputs": {
    "project/bytesInOutput should be at least 99.css": {
      "bytesInOutput": 52
    }
  },
  "bytes": 196
}
```  
**Breakdown**:  
- Input CSS: `a { background: url(<99-four-chars>.file); }`  
- Printer output: `a{background:url(<25-byte uniqueKey>);}` → Length **52**.  
- Final output: `a{background:url(./444…99-four-chars…-55DNWN2R.file);}` → Length **196**.  
- **Delta**: 144 bytes unaccounted for in `bytesInOutput`.  

---

#### 5. **Case E: JS File Loader**  
**Input File**: `script.js`  
```javascript
import asset from './long-asset-name.file';
```  
**Observation**:  
```json
// meta.json (JS entry)
"outputs": {
  "out/script.js": {
    "inputs": {
      "script.js": { "bytesInOutput": 45 },
      "long-asset-name.file": { "bytesInOutput": 0 }
    },
    "bytes": 120
  }
}
```  
**Analysis**:  
- Printer output: `import"<25-byte uniqueKey>";` → Length **45**.  
- Final output: `import"./444…-55DNWN2R.file";` → Length **120**.  
- **Consistency**: JS exhibits same placeholder retention as CSS.  

---

### Key Findings  

1. **Placeholder Identity**:  
   - `bytesInOutput` records length **at compilation**, using `len(compileResult.CSS/JS)`.  
   - Contains `url(<uniqueKey>)` strings (25 bytes), not final paths.  

2. **Substitution Blindspot**:  
   - Changes to `publicPath`, `--asset-names`, or final path length **do not affect** `bytesInOutput`.  
   - Example:  
     - Placeholder: `url(uniqueKey)` (25 bytes).  
     - Final path: `url(/path/asset-HASH.ext)` (40 bytes).  
     - `bytesInOutput` reports 25; `bytes` reports 40 + deltas.  

3. **Provenance**:  
   - Confirmed in code:  
     - `bundler/linker.go`: `bytesInOutput = len(compileResult.CSS)` (pre-substitution).  
     - `file_loader_uniquekey.go`: Generates 25-byte `uniqueKey` placeholder.  
   - No remapping occurs between compilation and final output.  

4. **Failure Scope**:  
   - Occurs when:  
     - CSS `url()` or JS `file`/`copy` loader triggers placeholder.  
     - Path substitution modifies output length.  
   - Does not occur when:  
     - No assets referenced (Case A).  
     - Assets referenced but no path substitution (e.g., inline data-URLs).  

---

### Uncertainty  
- **Exact Delta Calculation**:  
  While `bytesInOutput` consistently reflects placeholder length (25 bytes per occurrence), the precise delta between it and `bytes` depends on:  
  - Number of asset references.  
  - Length of final paths (determined by `publicPath`, hashing, base names).  
  - Cannot derive formula without post-substitution byte tracking.  

**Recommendation**:  
Treat `bytesInOutput` as a pre-substitution value in builds with path-dependent asset loaders. Rely on `bytes` for final output size.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
