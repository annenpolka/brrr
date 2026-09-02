// Reduced excerpt of updateShapeSignature on failing_ref
// tsc/internal/execute/incremental/affectedfileshandler.go
// 5739027c9a7df24e27123f453a50c011b37717b6
// JSON files have no declaration output. Empty dts is the shape signature.
// Later JSON content changes look shape-equivalent.

	info, _ := h.program.snapshot.fileInfos.Load(file.Path())
	prevSignature := info.signature
	if !file.IsDeclarationFile && !useFileVersionAsSignature {
		update.signature = h.computeDtsSignature(file)
	}
	// Default is to use file version as signature
