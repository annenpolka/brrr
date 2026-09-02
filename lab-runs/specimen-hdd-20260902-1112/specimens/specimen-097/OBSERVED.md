# OBSERVED

Public moby/buildkit PR 5444 (tonistiigi, merged 2024-10-28, merge `94f0ff8a0c85f4491ce7fd5ffc942e7f58a01ff9`). Related discussion: #4446 (keep-git-dir detached HEAD / missing refs). Failing world pinned on merge first parent `bc6f7be35057d15f8384c91ed500a610ab7e2a87`. Local BuildKit execution was not performed on this lab host.

PR body: when keep-git-dir is true, a Git commit accessed through different refs (or a ref added after the commit was already pulled) reused a cache key that was only the git commit. The previous `.git` directory can be reused without the later ref inside. keep-git-dir false is unchanged: two refs at one commit yield identical tree content. A raw SHA identifier still does not add a named ref to the key.

In-tree test added on the PR (`TestMultipleTagAccessKeepGitDir`): two tags on the same commit; keep-git-dir true requires `key1 != key2` while `pin1 == pin2`; keep-git-dir false requires `key1 == key2`. That test is **not** on the failing revision.

`CacheKey` on failing_ref: if `gs.src.Ref` is already a commit SHA, `shaToCacheKey(ref)` (no extra ref). Otherwise `git ls-remote origin <ref> <ref>^{}` picks a SHA from HEAD/tag/partial lines, then `shaToCacheKey(sha)` with no usedRef.

Not this packet: specimen-066 (moby healthcheck StartPeriod vs StartInterval). specimen-007 (libgit2). specimen-091 (cargo git checkout PathBuf `..`). cargo#17289 (checkout short-id vs core.abbrev).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
