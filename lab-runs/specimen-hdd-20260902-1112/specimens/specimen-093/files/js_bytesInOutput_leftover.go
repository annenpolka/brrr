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
