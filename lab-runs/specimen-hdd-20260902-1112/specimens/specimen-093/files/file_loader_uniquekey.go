// Reduced excerpt of LoaderFile on failing_ref
// internal/bundler/bundler.go
// 0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff
// uniqueKeyPrefix is 16 chars (base64 of 12 random bytes).
// "%sA%08d" => 25-byte placeholder. CSS printer emits this, not the final path.

    case config.LoaderFile:
        uniqueKey := fmt.Sprintf("%sA%08d", args.uniqueKeyPrefix, args.sourceIndex)
        uniqueKeyPath := uniqueKey + source.KeyPath.IgnoredSuffix
        expr := js_ast.Expr{Data: &js_ast.EString{Value: helpers.StringToUTF16(uniqueKeyPath)}}
        ast := js_parser.LazyExportAST(args.log, source, js_parser.OptionsFromConfig(&args.options), expr, "")
        ast.URLForCSS = uniqueKeyPath
        result.file.inputFile.Repr = &graph.JSRepr{AST: ast}
        result.ok = true
        result.file.inputFile.UniqueKeyForAdditionalFile = uniqueKey
