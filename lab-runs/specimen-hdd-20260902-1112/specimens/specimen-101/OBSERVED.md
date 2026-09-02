# OBSERVED

Public rust-lang/cargo issue 16740 (weihanglo, closed 2026-03-13) and PR 16744 (weihanglo, merged 2026-03-13, merge `cbb9bb8bd0fb272b1be0d63a010701ecb3d1d6d3`). Failing world pinned on merge first parent `843a683fef61e9b3f9607ab637b72b0774241513`. Follow-up of #16727 (SCP-like URLs failed `Url::parse` with `relative URL without a base`). Local cargo execution was not performed on this lab host.

Issue body: after converting SCP-like to `ssh://` for parse, path semantics differ (`git@host:path` vs `ssh://git@host/path`). GitHub/GitLab hide it; a self-hosted `~/repos/foo.git` vs `/repos/foo.git` does not.

Failing_ref `absolute_submodule_url` always rewrites alternative SSH form to `ssh://`. `update_submodule` builds `SourceId::for_git(&child_remote_url.into_url()?)` and `GitSource::new`. `GitRemote.url` is `Url`. In-tree test `dep_with_scp_like_submodule_url` expects submodule lines to show `ssh://git@github.com/foo/bar.git`.

Not this packet: specimen-091 (RecursivePathSource PathBuf `..` duplicate package). specimen-005/024/086 cargo fingerprints. cargo#17289 checkout short-id vs core.abbrev. cargo#16727 (parse failure, not leftover fetch identity).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
