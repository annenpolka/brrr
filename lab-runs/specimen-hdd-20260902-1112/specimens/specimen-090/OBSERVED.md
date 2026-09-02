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
