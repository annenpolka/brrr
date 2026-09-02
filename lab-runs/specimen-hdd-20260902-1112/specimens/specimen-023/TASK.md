# TASK

A project uses hatch-vcs for a dynamic version and tells uv to rebuild
when git HEAD moves:

```toml
[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true, tags = true } }]
```

This is used from a *linked git worktree* (`git worktree add`), where
`.git` is a file `gitdir: <repo>/.git/worktrees/<name>` rather than a
directory.

`uv sync` / `uv run` should rebuild the editable install when the
worktree's current commit changes, the same way a regular clone does.
