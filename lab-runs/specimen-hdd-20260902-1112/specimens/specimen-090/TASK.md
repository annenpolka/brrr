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
