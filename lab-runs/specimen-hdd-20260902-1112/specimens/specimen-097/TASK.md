# TASK

BuildKit's git source cache key for a checkout can be only the commit SHA (plus `.git` when `keepGitDir` is true). Two identifiers that name the **same commit through different refs** then share one snapshot. With `keepGitDir`, the program later resolves the user-provided ref inside that snapshot's `.git`. The first fetch may have stored a `.git` that does not contain the second ref.

In-tree after the repair: `TestMultipleTagAccessKeepGitDir` (`source/git/source_test.go`). Repo has tags `a/v1.2.3` and `a/v1.2.3-same` on the same initial commit. First identifier uses Ref `a/v1.2.3`; second uses `a/v1.2.3-same`. Same remote. `KeepGitDir` true vs false.

On failing_ref `bc6f7be35057d15f8384c91ed500a610ab7e2a87`, `shaToCacheKey` is:

```
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
```

`CacheKey` after resolving ls-remote always calls `shaToCacheKey(sha)` with no ref. A commit-SHA identifier also keys only on the SHA.

Case A — `KeepGitDir` false, two tags on one commit (`a/v1.2.3` then `a/v1.2.3-same`):
  tree content is identical
  cache keys are equal (SHA only, length 40)
  no leftover `.git` identity (there is no `.git` in the snapshot)

Case B — `KeepGitDir` true, same two tags, same commit:
  pin (resolved SHA) is equal
  failing_ref cache keys are equal (`sha + ".git"`)
  second snapshot can reuse the first keep-git-dir checkout
  that `.git` was fetched for `a/v1.2.3`; `git rev-parse a/v1.2.3-same` inside it can miss the second ref

Case C — `KeepGitDir` true, identifier is a raw 40-char commit SHA (no named ref):
  `shaToCacheKey` still SHA + `.git`
  no named ref is requested in `.git` beyond the SHA fetch
  not the two-tag leftover

Case D — `KeepGitDir` true, two different commits (different SHAs):
  keys differ because SHA differs
  not a leftover-ref problem

The developer wants to know, for case B, which identity `shaToCacheKey` stored: leftover SHA-only (plus `.git`) so two refs collide, SHA#ref so they split, or omitted (no keep-git-dir key).
