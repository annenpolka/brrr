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
