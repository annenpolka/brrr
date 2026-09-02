// Reduced excerpt of cache-path identity + copy on failing_ref
// cli/download_source.go / util/file.go
// 17004093f058bfe45c59ab6e34fe3c46da86dbf8
// encodeSourceName omits query/ref. CopyFolderContents has no manifest.

func encodeSourceName(sourceUrl *url.URL) (string, error) {
	sourceUrlNoQuery, err := parseSourceUrl(sourceUrl.String())
	sourceUrlNoQuery.RawQuery = ""
	return util.EncodeBase64Sha1(sourceUrlNoQuery.String()), nil
}

func CopyFolderContents(source string, destination string) error {
	return CopyFolderContentsWithFilter(source, destination, func(path string) bool {
		return !PathContainsHiddenFileOrFolder(path)
	})
}
// leftover previous files in destination after source change
