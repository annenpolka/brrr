# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public gruntwork-io/terragrunt#764 (closed 2019-07-31). PR 774 merge `85f63b2bbde2fc8d9b207799e6891c171e6527ee` (first parent `17004093f058bfe45c59ab6e34fe3c46da86dbf8`). Local terragrunt was not performed on this lab host.

Issue body: changing `...?ref=` keeps the same `.terragrunt-cache` hash subdirs; leftover dest; `git pull` fails after cleanup deleted `.git`; deleting the cache folder pulls the new commit.

On failing_ref, encodeSourceName omits query/ref from the cache path. CopyFolderContents has no list of previously copied files, so leftover `stale.tf` survives a source update. PR 774 tests `test-stale-file-doesnt-exist-after-source-update`.


This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 17004093f058bfe45c59ab6e34fe3c46da86dbf8
# cli/download_source.go encodeSourceName / CopyFolderContents / cleanupDownloadDir

# public shape:
# leftover .terragrunt-cache path after ?ref= change
# encodeSourceName omits query; leftover stale.tf; leftover dest without .git
# rm -rf .terragrunt-cache yields the new source
```

Source-backed only. Do not execute untrusted checkouts on the host.

gruntwork-io/terragrunt
  cli/download_source.go
  util/file.go

RELEVANT MATERIAL

### encode_source_failing.go

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

### leftover_identity_split.txt

Registry / fixture:
  .terragrunt-cache download dir
  leftover previous source after ?ref= / file change

Case A (second run, same source):
  current cache identity
  not leftover-after-source-change

Case B (ref= or files flipped, leftover dest):
  leftover: previous stale.tf / previous clone path
  ref omitted from encodeSourceName
  same encoded folder

Case C (rm -rf .terragrunt-cache / --terragrunt-source-update):
  fresh source identity
  not leftover previous tree

Case D (copy manifest Clean before recopy):
  stale.tf gone after source update
  not leftover previous files

Not this packet:
  terraform leftover identity omitted from apply state (specimen-118)
  terragrunt#6468 leftover deleted git-module files (OPEN)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.

[Some editorial framing from the previous field report was omitted.]
