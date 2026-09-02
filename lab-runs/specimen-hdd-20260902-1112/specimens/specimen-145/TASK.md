# TASK

Terragrunt `.terragrunt-cache` can keep the identity of a **previous source tree** after `terraform { source = "...?ref=..." }` changed. Two leftovers share one download folder:

1. `encodeSourceName` hashes the source URL **without the query string**. Different `ref=` values reuse `QM1-63WWHsRnztH6ooxLgsdRMGg/tieM-yGmC7c1rfHpXzt3T9uRVsA`. Version lives only in `.terragrunt-source-version`.
2. `CopyFolderContents` copies into that folder with **no manifest**. After source update, leftover `stale.tf` from the previous tree stays. `cleanupDownloadDir` then deletes leftover dest contents including `.git`, so go-getter `git pull` fails (`pathspec 'master' did not match`).

On failing_ref `17004093f058bfe45c59ab6e34fe3c46da86dbf8`:

```
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
```

Public report (gruntwork-io/terragrunt#764). Change `?ref=` from `6e30e8a` to `c7f82af`; same cache path; leftover dest; delete `.terragrunt-cache` to get the new commit. In-tree test after the repair: `test-stale-file-exists` then `test-stale-file-doesnt-exist-after-source-update`.

In-tree after the repair (not on failing_ref): `.terragrunt-module-manifest` / `.terragrunt-source-manifest`; `CopyFolderContents(..., manifestFile)` Clean() previous copies; `cleanupDownloadDir` removed.

Case A — second run, same `source` / same files:
  cache identity is current
  not leftover-after-source-change

Case B — `ref=` or local files flipped, leftover dest:
  leftover: previous `stale.tf` / previous clone path
  ref omitted from cache-path identity
  same encoded folder

Case C — `rm -rf .terragrunt-cache` / `--terragrunt-source-update`:
  fresh source identity
  not leftover previous tree

Case D — copy manifest Clean() before recopy (post-repair shape, not on failing_ref):
  stale.tf gone after source update
  not leftover previous files

The developer wants to know which identity case B actually used for the working dir after the source change: leftover previous-copy (no manifest; ref omitted from path), current source identity, or omitted (no cache).
