KNOWN FIX (sealed): evanw/esbuild commit a375b372f5a4947c3e7d2af68301190a88bf83cd (closes PR 2091 / issue 2071).

bytesInOutput used len(compileResult.CSS) / len(compileResult.JS) while those slices still contained uniqueKey placeholders (fmt.Sprintf("%sA%08d", prefix, sourceIndex), 25 bytes). Path substitution for cyclic references happened later; only outputs.*.bytes was remapped. Repair: keep per-input output pieces, then accurateFinalByteCount walks pieces and adds len(final importPath) for asset/chunk substitutions (same paths as substituteFinalPaths, including publicPath). CSS and JS jsonMetadataChunkCallback now call that after finalRelPath is known. Snapshot TestMetafileVeryLongExternalPaths: CSS bytesInOutput 52 -> 142; JS file-loader 45 -> 135.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
