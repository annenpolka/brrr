# TASK

`uv lock` of a **git** dependency whose metadata (Poetry `path =` or a PEP 508 path URL) points at another directory **inside the same git checkout** can serialize that child as a local directory instead of as the git source.

On failing_ref `77f271063993020770ee785469226e33324576be`, `RequiresDist::from_project_maybe_workspace` discovers a uv `ProjectWorkspace`. If that discovery misses (Poetry-only layout, no uv workspace), it returns `from_metadata23`, which maps each `requires_dist` entry through `Requirement::from` with **no** `git_member`. A path URL becomes `RequirementSource::Directory { install_path }` whose `install_path` is the cache checkout on this machine.

`path_source` on the same revision, when `tool.uv.sources` *does* apply and `git_member` is set, already rewrites a directory inside `fetch_root` to `RequirementSource::Git { subdirectory }`. The Poetry-path / no-workspace path never reaches that function.

Public lock snippet (#19152):

```
[[package]]
name = "deepfilterlib"
version = "0.5.7"
source = { directory = "/Users/benniekiss/.cache/uv/git-v0/checkouts/e42607f483442963/ba2260b/pyDF" }
```

In-tree after the repair: `lock_git_poetry_path_dependency` (`crates/uv/tests/it/sync.rs`). Repo layout:

```
repository/
  root/pyproject.toml     tool.poetry; child = { path = "../child" }
  child/pyproject.toml    [project] name = "child"
consumer pyproject.toml   root = { git = "<repo>", subdirectory = "root" }
```

Case A — uv workspace / `tool.uv.sources` path inside the same git checkout:
  `path_source` sees `git_member`
  lock source is git + subdirectory
  no leftover directory

Case B — Poetry `path = "../child"` inside the git checkout, no uv workspace:
  `from_metadata23` / `Requirement::from`
  lock source is `directory = "<absolute checkout>/child"`
  leftover: machine-specific path identity while the live package is a git tree

Case C — path that does **not** sit under `fetch_root`:
  even with `git_member`, it is a real directory dep
  not leftover git identity

Case D — the git root itself (`subdirectory = "root"`):
  consumer source is already git
  the leftover is only the **transitive** path child

The developer wants to know, for case B, which identity `uv.lock` stored for `child`: leftover absolute directory of the git checkout, git+subdirectory of the same repo, or omitted.
