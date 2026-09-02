// Reduced excerpt of shaToCacheKey on failing_ref
// source/git/source.go
// bc6f7be35057d15f8384c91ed500a610ab7e2a87
// Key is commit SHA. KeepGitDir adds ".git". Named ref is not in the key.

func (gs *gitSourceHandler) shaToCacheKey(sha string) string {
	key := sha
	if gs.src.KeepGitDir {
		key += ".git"
	}
	if gs.src.Subdir != "" {
		key += ":" + gs.src.Subdir
	}
	return key
}
