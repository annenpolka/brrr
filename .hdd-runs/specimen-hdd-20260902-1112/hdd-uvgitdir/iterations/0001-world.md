# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public astral-sh/uv issue 19152 (benniekiss, closed 2026-05-05) and PR 19269 (charliermarsh, merged 2026-05-05, squash `a1c90c1fa12c95485f3d6a210daa4e6cc7466a90`). Failing world pinned on squash first parent `77f271063993020770ee785469226e33324576be`. Local uv execution was not performed on this lab host.

Issue body: locking a git fork of DeepFilterNet whose Poetry metadata has `child = { path = "../child" }` wrote `source = { directory = "/Users/.../.cache/uv/git-v0/checkouts/.../pyDF" }`. Sync on another machine failed.

Failing_ref: `from_project_maybe_workspace` falls back to `from_metadata23` when no uv project workspace is found. `from_metadata23` does `Requirement::from` with no git context. `LoweredRequirement::from_requirement` with `sources == None` also returns `Requirement::from(requirement)` and never consults `git_member`. `path_source` already has a git_member branch for `tool.uv.sources` paths.

The in-tree Poetry git-path lock test is **not** on the failing revision. `sync_git_path_dependency` (uv-native path inside git) is a different path.

Not this packet: specimen-006/022/023 uv cache fingerprints. uv.lock vs pylock.toml. specimen-091 cargo git PathBuf. specimen-098 pip extras-on-link.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 77f271063993020770ee785469226e33324576be
# crates/uv-distribution/src/metadata/requires_dist.rs from_metadata23
# crates/uv-distribution/src/metadata/lowering.rs from_requirement sources==None
# crates/uv/tests/it/sync.rs lock_git_poetry_path_dependency (on the PR, not failing_ref)

# public shape:
# git source subdirectory=root; Poetry path = "../child"
# uv lock --no-cache
# failing: child source.directory = absolute git checkout path
```

Source-backed only. Do not execute untrusted checkouts on the host.

astral-sh/uv
  crates/uv-distribution/src/metadata/requires_dist.rs
  crates/uv-distribution/src/metadata/lowering.rs
  crates/uv/tests/it/sync.rs

RELEVANT MATERIAL

### from_metadata23_failing.rs

// Reduced excerpt of from_metadata23 / from_project_maybe_workspace on failing_ref
// crates/uv-distribution/src/metadata/requires_dist.rs
// 77f271063993020770ee785469226e33324576be
// No uv workspace (Poetry layout) -> Requirement::from with no git_member.

    pub fn from_metadata23(metadata: uv_pypi_types::RequiresDist) -> Self {
        Self {
            name: metadata.name,
            requires_dist: Box::into_iter(metadata.requires_dist)
                .map(Requirement::from)
                .collect(),
            provides_extra: metadata.provides_extra,
            dependency_groups: BTreeMap::default(),
            dynamic: metadata.dynamic,
        }
    }

        let Some(project_workspace) =
            ProjectWorkspace::from_maybe_project_root(install_path, &discovery, cache).await?
        else {
            return Ok(Self::from_metadata23(metadata));
        };

### from_requirement_no_sources_failing.rs

// Reduced excerpt of LoweredRequirement::from_requirement on failing_ref
// crates/uv-distribution/src/metadata/lowering.rs
// When tool.uv.sources has no entry, git_member is not consulted.

        let Some(sources) = sources else {
            return Either::Left(std::iter::once(Ok(Self(Requirement::from(requirement)))));
        };

### leftover_identity_split.txt

Fixture:
  git repo with root/ (Poetry, path = "../child") and child/
  consumer: root = { git = "<repo>", subdirectory = "root" }
  uv lock --no-cache

Case A (uv workspace / tool.uv.sources path inside fetch_root):
  path_source sees git_member
  lock source is git + subdirectory
  no leftover directory

Case B (Poetry path inside the git checkout, no uv workspace):
  from_metadata23 / Requirement::from
  lock source is directory = absolute cache checkout path
  leftover: machine-specific directory identity
  live package is the git tree (same commit, subdirectory=child)

Case C (path not under fetch_root):
  real directory dependency
  not leftover git identity

Case D (git root package itself):
  consumer already git+subdirectory=root
  leftover is only the transitive path child

Not this packet:
  uv cache fingerprints (006/022/023)
  uv.lock vs pylock.toml
  cargo PathBuf .. (091)
  pip extras-on-link (098)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
