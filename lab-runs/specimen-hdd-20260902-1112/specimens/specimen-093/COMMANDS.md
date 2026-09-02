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
