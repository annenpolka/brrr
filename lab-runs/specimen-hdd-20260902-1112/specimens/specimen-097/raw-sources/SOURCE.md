repository: moby/buildkit
issue: https://github.com/moby/buildkit/issues/4446
pr: https://github.com/moby/buildkit/pull/5444
failing_ref (merge first parent): bc6f7be35057d15f8384c91ed500a610ab7e2a87
fixed_ref (merge commit): 94f0ff8a0c85f4491ce7fd5ffc942e7f58a01ff9
pr_head: 44b1aca26a97107190c6b89e8277183e12ad17a0
second_parent: 44b1aca26a97107190c6b89e8277183e12ad17a0
merged_at: 2024-10-28T16:42:24Z
merged_by: tonistiigi
pr_author: tonistiigi
changed_files: source/git/source.go, source/git/source_test.go
pr_title: git: fix caching git commit through multiple refs
milestone: v0.17.0
scout_note: not specimen-066 (moby healthcheck timers). not specimen-007 libgit2. not specimen-091 cargo RecursivePathSource PathBuf. Distinct leftover: keep-git-dir cache key omitted the named ref so two tags at one SHA reused a .git without the second ref.
