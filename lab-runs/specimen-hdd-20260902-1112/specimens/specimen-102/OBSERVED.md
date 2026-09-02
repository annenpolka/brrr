# OBSERVED

Public astral-sh/uv issue 19152 (benniekiss, closed 2026-05-05) and PR 19269 (charliermarsh, merged 2026-05-05, squash `a1c90c1fa12c95485f3d6a210daa4e6cc7466a90`). Failing world pinned on squash first parent `77f271063993020770ee785469226e33324576be`. Local uv execution was not performed on this lab host.

Issue body: locking a git fork of DeepFilterNet whose Poetry metadata has `child = { path = "../child" }` wrote `source = { directory = "/Users/.../.cache/uv/git-v0/checkouts/.../pyDF" }`. Sync on another machine failed.

Failing_ref: `from_project_maybe_workspace` falls back to `from_metadata23` when no uv project workspace is found. `from_metadata23` does `Requirement::from` with no git context. `LoweredRequirement::from_requirement` with `sources == None` also returns `Requirement::from(requirement)` and never consults `git_member`. `path_source` already has a git_member branch for `tool.uv.sources` paths.

The in-tree Poetry git-path lock test is **not** on the failing revision. `sync_git_path_dependency` (uv-native path inside git) is a different path.

Not this packet: specimen-006/022/023 uv cache fingerprints. uv.lock vs pylock.toml. specimen-091 cargo git PathBuf. specimen-098 pip extras-on-link.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
