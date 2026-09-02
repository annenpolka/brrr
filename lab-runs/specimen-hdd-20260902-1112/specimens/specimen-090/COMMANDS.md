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
