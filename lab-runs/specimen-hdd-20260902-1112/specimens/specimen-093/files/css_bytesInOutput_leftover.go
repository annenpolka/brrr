// Reduced excerpt of generateChunkCSS on failing_ref
// internal/bundler/linker.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
// bytesInOutput = len(compileResult.CSS) while CSS still contains uniqueKey.
// jsonMetadataChunkCallback only patches the outer "bytes" after substitution.

            // Include this file in the metadata
            if c.options.NeedsMetafile {
                if isFirstMeta {
                    isFirstMeta = false
                } else {
                    jMeta.AddString(",")
                }
                jMeta.AddString(fmt.Sprintf("\n        %s: {\n          \"bytesInOutput\": %d\n        }",
                    helpers.QuoteForJSON(c.graph.Files[compileResult.sourceIndex].InputFile.Source.PrettyPath, c.options.ASCIIOnly),
                    len(compileResult.CSS)))
            }

    // End the metadata lazily. The final output size is not known until the
    // final import paths are substituted into the output pieces generated below.
    if c.options.NeedsMetafile {
        chunk.jsonMetadataChunkCallback = func(finalOutputSize int) helpers.Joiner {
            if !isFirstMeta {
                jMeta.AddString("\n      ")
            }
            jMeta.AddString(fmt.Sprintf("},\n      \"bytes\": %d\n    }", finalOutputSize))
            return jMeta
        }
    }
