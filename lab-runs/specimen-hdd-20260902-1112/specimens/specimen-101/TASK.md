# TASK

A git dependency's `.gitmodules` names a submodule with an **SCP-like** URL (`git@github.com:foo/bar.git`). That form is not a WHATWG URL. Cargo still has to build a `SourceId` (which requires `Url`) and then fetch.

On failing_ref `843a683fef61e9b3f9607ab637b72b0774241513`, `absolute_submodule_url` parses the child URL with `gix` and, when `serialize_alternative_form && scheme == Ssh`, turns alternative form **off** and serializes `ssh://git@host/path`. `update_submodule` then does `child_remote_url.into_url()` and `GitSource::new(source_id)`. `GitRemote` stores a `Url`. Fetch and user-facing messages therefore use the converted `ssh://` identity.

SCP-like `git@host:path` is relative to the user's home (`~/path`). `ssh://git@host/path` is absolute from `/path`. For GitHub/GitLab the two are intercepted the same; for a self-hosted server they are not.

In-tree `dep_with_scp_like_submodule_url` (`tests/testsuite/git.rs`): dependency `dep1` has submodule `submod` with `url = git@github.com:foo/bar.git`. `cargo fetch` with `GIT_SSH_COMMAND=false`. On this revision the `[UPDATING] git submodule` line and `failed to fetch submodule` line name `ssh://git@github.com/foo/bar.git`.

Case A — submodule URL is already `https://` or `ssh://host/path` (WHATWG):
  `into_url` succeeds without conversion
  fetch identity equals `.gitmodules` identity
  no leftover

Case B — submodule URL is SCP-like `git@github.com:foo/bar.git`:
  `absolute_submodule_url` emits `ssh://git@github.com/foo/bar.git`
  `GitSource::new` fetches that `Url`
  `.gitmodules` still names `git@github.com:foo/bar.git`
  leftover: converted ssh:// is the live fetch identity

Case C — relative submodule `./` / `../` against an SCP-like parent:
  failing_ref tests in `absolute_submodule_url` expect the converted `ssh://..././` form
  leftover conversion applies to the joined string

Case D — GitHub/GitLab host (both forms intercepted):
  fetch may succeed with either spelling
  leftover identity is still the ssh:// rewrite; path semantics happen to match

The developer wants to know, for case B, which identity `GitRemote` / fetch used: leftover `ssh://` converted from SCP-like, the original `.gitmodules` SCP-like string, or omitted.
