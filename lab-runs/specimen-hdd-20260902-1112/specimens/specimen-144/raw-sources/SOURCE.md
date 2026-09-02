repository: GoogleContainerTools/skaffold
issue: https://github.com/GoogleContainerTools/skaffold/issues/9248
related_issue: https://github.com/GoogleContainerTools/skaffold/issues/9279
pr: https://github.com/GoogleContainerTools/skaffold/pull/9278
failing_ref (parent of squash on main): 6ea9aeb818b8e371a4386bf044479f86a0a6e885
fixed_ref (lookupRemote compares remote vs cached digest): 9ff4546df8c0d891fde32c24e0d0ef93a8c7404b
merged_at: 2024-01-31T13:29:23Z
pr_author: idsulik
merged_by: ericzzzzzzz
changed_files: pkg/skaffold/build/cache/lookup.go, cache.go, retrieve_test.go, pkg/skaffold/runner/new.go
pr_title: fix(lookupRemote): fixed lookup.go lookupRemote to compare remote and cached digests
scout_note: not 097 buildkit keep-git-dir omitted-ref. leftover remote tag identity after input digest change. unique vs 001-141.
