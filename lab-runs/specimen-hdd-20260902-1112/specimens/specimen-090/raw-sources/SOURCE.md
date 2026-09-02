repository: webpack/webpack
issue: none (PR body is the report)
pr: https://github.com/webpack/webpack/pull/20938
failing_ref (squash parent): 66a8bcccc501ee1985a3b77d275ccc98df523346
fixed_ref (squash merge commit): c030e725c8c533f2838ff8424ae6444c23ef196a
head_sha: fa1e7a03d7c9d5033e9284042c80d3d7d14f6c85
merged_at: 2026-05-09T14:22:42Z
merged_by: alexander-akait
changed_files: .changeset/css-contenthash-asset-url.md, lib/asset/AssetGenerator.js, lib/dependencies/CssUrlDependency.js, test/configCases/css/public-path/__snapshots__/ConfigCacheTest.snap, test/configCases/css/public-path/__snapshots__/ConfigTest.snap, test/watchCases/long-term-caching/css-contenthash-asset-url/{webpack.config.js,0/index.js,0/logo.png,0/style.css,1/index.js,1/style.css,2/index.js,2/logo.png}
pr_title: fix: invalidate css [contenthash] when a referenced asset url changes
scout_note: not #20710/#20724 leftover runtime-chunk hash after watch rebuild (hashing order of entry vs runtime). not #11339/#9520 RealContentHashPlugin file digest (watchCase realContentHash false — this is module [contenthash]). not #21018 HTML referenced-module updateHash. not specimen-089 leftover storedBuildState after unplugged remove. Distinct leftover: CSS module [contenthash] still names H_css1 after PNG contenthash moved, plus persisted data.url css-url leftover vs freshly computed assetPath.
