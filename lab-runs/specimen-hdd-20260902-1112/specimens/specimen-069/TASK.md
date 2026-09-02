# TASK

`actions/checkout` v7 on a self-hosted Windows runner writes `includeIf.gitdir:...path` entries pointing at a temp credentials config:

```
includeIf.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
```

Post-job cleanup runs the equivalent of:

```
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\runner\_work\_temp\git-credentials-.config
```

Git prints:

```
error: invalid pattern: C:\runner\_work\_temp\git-credentials-.config
```

The workflow can still conclude successfully. A later checkout on the same worktree sees the leftover `includeIf` and repeats the error.

The developer wants to know which git config *value* cleanup tried to match, whether that value was treated as a regex, and which `includeIf` entries remained.
