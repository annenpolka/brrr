# FIX (sealed)

Issue: https://github.com/astral-sh/uv/issues/19705
  title: `cache-keys` git commit is never detected in linked git worktrees
PR: https://github.com/astral-sh/uv/pull/19706
  title: Fix Git cache keys for worktrees and packed refs
failing_ref: 6feeacc622b8d1a644397fe7d2b8af6d5c3dafcf
fixed_ref: 5c6189b2cc52fe06385a89f173c4e6e889141f7d

Root cause (two layers):

1. `git_head()` for a `.git` *file* returned the worktree git dir path
   without appending `HEAD`, so `read_to_string` tried to read a
   directory and the commit became null.
2. Even with HEAD, `git_dir.join("refs/heads/main")` looked beside the
   `.git` file / worktree dir. Branch refs and packed-refs live in the
   common git directory. Tags walked loose `refs/tags` only.

Fix: resolve `.git` files and `commondir`; read loose refs from the
worktree dir then the common dir; fall back to `packed-refs`. Loose
refs override packed entries. Regression test
`commit_and_tags_from_linked_worktree` plus
`invalidate_path_on_worktree_packed_commit`.
