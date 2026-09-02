// Reduced excerpt of CacheKey on failing_ref
// source/git/source.go
// After ls-remote picks a SHA, key is shaToCacheKey(sha) with no usedRef.
// Commit-SHA identifier also keys only on the SHA.

	if ref := gs.src.Ref; ref != "" && gitutil.IsCommitSHA(ref) {
		cacheKey := gs.shaToCacheKey(ref)
		gs.cacheKey = cacheKey
		return cacheKey, ref, nil, true, nil
	}
	// ...
	cacheKey := gs.shaToCacheKey(sha)
	gs.cacheKey = cacheKey
	return cacheKey, sha, nil, true, nil
