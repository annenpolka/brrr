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
