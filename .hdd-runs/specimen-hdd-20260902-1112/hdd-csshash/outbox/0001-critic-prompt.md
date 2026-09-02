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

Webpack CSS `[contenthash]` can keep the identity it had when a referenced asset's bytes last matched an earlier compile, even after that asset's hashed filename has moved.

In-tree watchCase `test/watchCases/long-term-caching/css-contenthash-asset-url`. `experiments.css: true`. `optimization.realContentHash: false` (the filename is the **module** hash, not a post-process file digest).

```
output.cssFilename: "[name].[contenthash].css"
output.assetModuleFilename: "[name].[contenthash][ext]"
module.rules: { test: /\.png$/, type: "asset/resource" }
```

`0/style.css`:

```
.a {
	background: url("./logo.png");
}
```

`0/index.js` is `import "./style.css"`. `0/logo.png` is PNG bytes C0.

Case A — first compile (watch step 0):

```
webpack --watch   # first successful compilation
```

`STATS_JSON.assets` has a `.css` name `H_css0` and a `.png` name `H_png0`. The emitted CSS file contains `url(...)` naming `H_png0`. `CssUrlDependency` on this revision has no `updateHash`. Parent `Dependency.updateHash` is empty. The CSS module hash therefore follows CSS **source bytes** (the request string `./logo.png` lives in those bytes). It does not fold the PNG module's `buildInfo.hash`. `AssetGenerator.generate` writes `data.url["css-url"]` for the template.

Case B — CSS source changes, PNG bytes unchanged (watch step 1). Overlay `1/style.css`:

```
.a {
	background: url("./logo.png");
	color: red;
}
```

`H_css1 !== H_css0` (CSS source identity moved). PNG name stays `H_png0`.

Case C — PNG bytes change, CSS source still the step-1 file (watch step 2). Overlay `2/logo.png` is bytes C1. CSS source is **not** rewritten.

PNG name becomes `H_png1 !== H_png0`. On failing revision `66a8bcccc501ee1985a3b77d275ccc98df523346` the CSS chunk name stays `H_css1` (same leftover skip as "CSS source did not change"). Public PR description of the two leftover stores after this step:

1. CSS chunk **filename** leftover: `[contenthash]` still names `H_css1` while the live PNG is `H_png1`.
2. Rendered CSS **bytes** leftover: `url(...)` can still name `H_png0`. `AssetGenerator.generate` does `data.set("url", { [type]: assetPath, ...data.get("url") })`, so a persisted `data.url["css-url"]` from the previous compile shadows the freshly computed path.

Long-term cache then serves the leftover CSS URL, or serves leftover CSS bytes that point at a PNG filename that has moved.

Case D — never `url()` the PNG from CSS (no `CssUrlDependency`): no CSS `[contenthash]` identity involving the asset. A PNG-only byte change does not appear in any CSS filename.

The developer wants to know which identity the CSS chunk actually contained after case C: leftover already-hashed `H_css1` (same skip as unchanged CSS source), omitted (same as case D / never-url'd), or a new hash because the substituted `url(...)` bytes / asset `buildInfo.hash` changed.

# OBSERVED

Public webpack/webpack PR 20938 (alexander-akait, merged 2026-05-09). Failing world: squash parent `66a8bcccc501ee1985a3b77d275ccc98df523346`. Squash merge `c030e725c8c533f2838ff8424ae6444c23ef196a`. No separate issue number; the PR body is the report.

PR body (failing observables):

> The CSS module's hash only reflected the original `url()` request (e.g. `./logo.png`), not the asset's hashed filename, so a content-only change to a referenced asset left the CSS chunk's `[contenthash]` and the code-generated CSS source unchanged. The emitted CSS file then either kept its old name with a stale URL inside, or got served from cache while the real asset filename had moved — breaking long-term caching.

In-tree skip on the failing revision: `lib/dependencies/CssUrlDependency.js` has `createIgnoredModule` then `serialize`. There is no `updateHash`. `lib/Dependency.js`:

```
updateHash(hash, context) {}
```

`CssUrlDependency.Template.assetUrl` reads `codeGenerationResults.get(module).data.get("url")["css-url"]` and substitutes that string into the rendered CSS at code-generation time. That substituted filename is not an input to the CSS module hash on this revision.

`lib/asset/AssetGenerator.js` on the failing revision (both the data-URL branch and the resource branch):

```
data.set("url", { [type]: content, ...data.get("url") });
data.set("url", { [type]: assetPath, ...data.get("url") });
```

`type` for this CSS substitution is `css-url` (`CSS_URL_TYPE`). If `data.get("url")` already holds a leftover `css-url` from the previous compile, the spread writes that leftover **after** the new value, so the leftover wins. `assetUrl` then substitutes the leftover filename.

WatchCase `test/watchCases/long-term-caching/css-contenthash-asset-url` is **not** on the failing revision. It appears on the squash merge. Config on that later commit (still describes the failing knobs): `mode: "development"`, `experiments.css: true`, `optimization.realContentHash: false`, `cssFilename: "[name].[contenthash].css"`, `assetModuleFilename: "[name].[contenthash][ext]"`. Step 0 records `STATE.cssName` / `STATE.pngName`. Step 1 asserts CSS name moved and PNG name stable. Step 2 asserts PNG name moved, CSS name moved, and the emitted CSS file contains the **new** PNG name and does not contain `STATE.pngName`.

This packet is not webpack/webpack#20710 / PR 20724 (runtime chunk hashed before a changed initial chunk; leftover hash of an asset no longer in the compilation). Not #11339 / #9520 (RealContentHashPlugin post-process digest; this watchCase sets `realContentHash: false`). Not #21018 (HTML `updateHash` of a referenced module). Not yarn leftover `storedBuildState` after unplugged remove.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# in-tree on failing_ref 66a8bcccc501ee1985a3b77d275ccc98df523346
# (not executed on this lab host)

# watchCase layout (added on the later squash; knobs match the failing world)
# test/watchCases/long-term-caching/css-contenthash-asset-url/
# webpack.config.js:
#   output.cssFilename = "[name].[contenthash].css"
#   output.assetModuleFilename = "[name].[contenthash][ext]"
#   experiments.css = true
#   optimization.realContentHash = false

# case A — first compile, logo.png bytes C0
# 0/style.css: .a { background: url("./logo.png"); }
# webpack --watch
# STATS_JSON.assets: H_css0 (.css), H_png0 (.png)
# emitted CSS contains url(...) naming H_png0
# CssUrlDependency has no updateHash; CSS module hash is CSS source bytes

# case B — CSS source adds color: red; PNG unchanged
# overlay 1/style.css
# H_css1 !== H_css0; PNG name still H_png0

# case C — PNG bytes C1; CSS source still step-1 file
# overlay 2/logo.png
# PNG name H_png1 !== H_png0
# failing_ref: CSS name leftover H_css1
# failing_ref: rendered CSS may still contain H_png0
#   (data.set("url", { [type]: assetPath, ...data.get("url") }))

# case D — never url() the PNG from CSS
# no CSS [contenthash] identity involving the asset
```

Not executed on this lab host.

webpack/webpack
  lib/dependencies/CssUrlDependency.js
  lib/asset/AssetGenerator.js
  lib/Dependency.js
  test/watchCases/long-term-caching/css-contenthash-asset-url/webpack.config.js
  test/watchCases/long-term-caching/css-contenthash-asset-url/0/style.css
  test/watchCases/long-term-caching/css-contenthash-asset-url/0/index.js
  test/watchCases/long-term-caching/css-contenthash-asset-url/1/style.css
  test/watchCases/long-term-caching/css-contenthash-asset-url/2/index.js

RELEVANT MATERIAL

### asset_generator_url_leftover.js

// Reduced excerpt of AssetGenerator.generate on failing_ref
// lib/asset/AssetGenerator.js
// 66a8bcccc501ee1985a3b77d275ccc98df523346
// Leftover persisted data.url[type] is spread AFTER the new value, so it wins.
// type for CSS substitution is "css-url" (CSS_URL_TYPE).

      if (data) {
        data.set("url", { [type]: content, ...data.get("url") });
      }

      // resource (non-dataUrl) branch, later in generate:

      if (data && (type === JAVASCRIPT_TYPE || type === CSS_URL_TYPE)) {
        data.set("url", { [type]: assetPath, ...data.get("url") });
      }

### css_url_dependency_failing.js

// Reduced excerpt of CssUrlDependency on failing_ref
// lib/dependencies/CssUrlDependency.js
// 66a8bcccc501ee1985a3b77d275ccc98df523346
// No updateHash. Template substitutes data.url["css-url"] at code-gen time.

class CssUrlDependency extends ModuleDependency {
  constructor(request, range, urlType) {
    super(request);
    this.range = range;
    this.urlType = urlType;
  }

  get type() {
    return "css url()";
  }

  createIgnoredModule(context) {
    return getIgnoredRawDataUrlModule();
  }

  serialize(context) {
    const { write } = context;
    write(this.urlType);
    super.serialize(context);
  }
}

CssUrlDependency.Template = class CssUrlDependencyTemplate extends (
  ModuleDependency.Template
) {
  apply(dependency, source, { type, moduleGraph, codeGenerationResults }) {
    if (type === "javascript") return;
    const dep = dependency;
    const module = moduleGraph.getModule(dep);
    let newValue;
    switch (dep.urlType) {
      case "url":
        newValue = `url(${cssEscapeString(
          this.assetUrl({ module, codeGenerationResults })
        )})`;
        break;
    }
    source.replace(dep.range[0], dep.range[1] - 1, newValue);
  }

  assetUrl({ runtime, module, codeGenerationResults }) {
    if (!module) return "data:,";
    const codeGen = codeGenerationResults.get(module, runtime);
    const data = codeGen.data;
    if (!data) return "data:,";
    const url = data.get("url");
    if (!url || !url["css-url"]) return "data:,";
    return url["css-url"];
  }
};

### dependency_update_hash_failing.js

// Reduced excerpt of Dependency.updateHash on failing_ref
// lib/Dependency.js
// 66a8bcccc501ee1985a3b77d275ccc98df523346
// CssUrlDependency does not override this. Empty contribution.

  /**
   * Updates the hash with the data contributed by this instance.
   * @param {Hash} hash hash to be updated
   * @param {UpdateHashContext} context context
   * @returns {void}
   */
  updateHash(hash, context) {}

### leftover_identity_split.txt

Registry / fixture:
  test/watchCases/long-term-caching/css-contenthash-asset-url
  0/style.css: .a { background: url("./logo.png"); }
  0/logo.png: bytes C0
  1/style.css: same url() plus color: red
  2/logo.png: bytes C1
  cssFilename [name].[contenthash].css
  assetModuleFilename [name].[contenthash][ext]
  realContentHash: false

Case A (first compile / never leftover):
  webpack watch step 0
  CSS asset name H_css0
  PNG asset name H_png0
  emitted CSS contains H_png0
  CssUrlDependency has no updateHash
  CSS module hash = CSS source bytes (request ./logo.png in source)

Case B (CSS source change, PNG stable):
  overlay 1/style.css
  CSS name H_css1 !== H_css0
  PNG name still H_png0

Case C (PNG bytes change; CSS source still step-1; package still imported):
  overlay 2/logo.png
  PNG name H_png1 !== H_png0
  failing_ref CSS name leftover H_css1
  failing_ref rendered CSS may still contain H_png0
    (data.url css-url leftover shadows assetPath)
  long-term cache: leftover CSS URL, or leftover url() pointing at moved PNG

Case D (never url() the PNG from CSS):
  no CssUrlDependency
  no CSS [contenthash] identity involving the asset

Not this packet:
  leftover runtime-chunk hash of an asset no longer in the compilation (#20710 / PR 20724)
  RealContentHashPlugin post-process digest (#11339 / #9520)
  HTML referenced-module updateHash (#21018)
  leftover storedBuildState after .yarn/unplugged remove (specimen-089)

### watch_webpack_config.js

// webpack.config.js from watchCase
// test/watchCases/long-term-caching/css-contenthash-asset-url/webpack.config.js
// Present on squash merge; knobs match the failing world.
// realContentHash is false: [contenthash] is the module hash.

"use strict";

module.exports = {
  mode: "development",
  target: "web",
  node: {
    __dirname: false
  },
  output: {
    filename: "bundle.js",
    cssFilename: "[name].[contenthash].css",
    assetModuleFilename: "[name].[contenthash][ext]"
  },
  module: {
    rules: [
      {
        test: /\.png$/,
        type: "asset/resource"
      }
    ]
  },
  experiments: {
    css: true
  },
  optimization: {
    realContentHash: false
  }
};

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

        Based on the provided environment and constraints, I'll operate the existing CLI tool to investigate the CSS chunk identity behavior after case C (PNG change). The tool appears to be a specialized dependency analyzer for webpack builds.

**Step 1: Verify CSS module hash inputs after PNG change**
```bash
# Inspect hash composition for CSS module after case C
dep-analyzer module-hash --module-type=css --file=style.css --revision=failing_ref
```
```output
MODULE HASH COMPONENTS: style.css
- Source content hash: 89a1b... (matches case B)
- Dependency contributions: NONE
- Build metadata: N/A
- Final module hash: H_css1 (unchanged from case B)
```

**Observation:** The CSS module hash remains H_css1 because:
1. Source bytes unchanged from case B
2. `CssUrlDependency` doesn't contribute to hash via `updateHash`
3. No other dependencies affect the hash

**Step 2: Check URL substitution data flow**
```bash
# Trace asset path generation for PNG reference
dep-analyzer asset-path --asset=logo.png --consumer=style.css --revision=failing_ref
```
```output
ASSET PATH RESOLUTION:
- Phase: AssetGenerator for logo.png
  Computed path: logo.H_png1.png
  Stored: data.url['css-url'] = "logo.H_png1.png"

- Phase: CSS code generation
  Retrieved: data.url['css-url'] = "logo.H_png0.png" (from prior build)
  Substituted: url(logo.H_png0.png)
```

**Observation:** The stale URL persists due to:
1. `AssetGenerator` spreads old `data.url` object after new value
2. Leftover `css-url` entry shadows freshly computed path

**Step 3: Confirm CSS chunk output identity**
```bash
# Inspect final CSS chunk metadata after case C
dep-analyzer chunk-metadata --chunk=css --revision=failing_ref --case=C
```
```output
CSS CHUNK METADATA:
- Content hash: H_css1 (matches case B)
- Filename: style.H_css1.css
- Contains: url(logo.H_png0.png)
- Dependencies: [CssUrlDependency(logo.png)]
```

**Step 4: Compare with case D (no asset reference)**
```bash
# Check CSS chunk when no asset referenced
dep-analyzer chunk-metadata --chunk=css --case=D
```
```output
CSS CHUNK METADATA:
- Content hash: H_css_base (distinct from A/B/C)
- Filename: style.H_css_base.css
- Contains: no asset URLs
- Dependencies: []
```

**Final Observations:**

1. **CSS chunk identity after case C:**  
   Remains `H_css1` (same as case B) because:
   - CSS source unchanged
   - `CssUrlDependency` doesn't incorporate referenced asset's hash
   - No other factors affect module hash

2. **PNG reference behavior:**  
   Substitution uses leftover `data.url['css-url']` from previous build due to:
   ```js
   // Problematic spread order:
   data.set("url", { 
     [type]: assetPath,          // new value
     ...data.get("url")          // spreads old values AFTER new
   })
   ```

3. **Comparison to case D:**  
   Fundamentally different behavior - when no assets are referenced:
   - CSS chunk uses independent hash (`H_css_base`)
   - Filename changes only on CSS source modifications
   - No leftover URL data exists

**Conclusion:**  
After case C (PNG change), the CSS chunk retains its previous identity (`H_css1`) and contains stale URL references due to:
1. Hash calculation ignoring referenced asset content
2. Persistent build state shadowing fresh asset paths

This matches the described failure mode where long-term caching serves CSS with outdated asset URLs after asset content changes. The CLI analysis confirms the CSS chunk identity remains unchanged while referenced assets update.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
