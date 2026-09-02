# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Source: https://github.com/astral-sh/uv/issues/19705 at uv 0.11.16, and
`crates/uv-cache-info/src/git_info.rs` at
`6feeacc622b8d1a644397fe7d2b8af6d5c3dafcf`. Local execution was not
performed.

After `uv sync` in a linked worktree vs a regular clone of the same
commit (timestamps elided):

```jsonc
// linked worktree
{"commit": null, "tags": {"v0.1.0": "c3aff651..."}, "env": {}, "directories": {}}

// regular clone
{"commit": "c3aff651...", "tags": {}, "env": {}, "directories": {}}
```

In the worktree, later `git commit` then `uv sync` keeps the hatch-vcs
version unchanged. In the regular clone, the same sequence rebuilds.

Secondary observation from the same report: after `git pack-refs --all`
in the regular clone, a re-sync records `"commit": null` there too.
Tags in the clone were empty even though `v0.1.0` existed (packed).

Loose-ref layout that *does* invalidate in `invalidate_path_on_commit`
(regular `.git` directory, not a worktree file):

```
.git/HEAD                    -> "ref: refs/heads/main"
.git/refs/heads/main         -> 40-hex commit
```

Changing that loose ref file caused `uv pip install -r requirements.txt`
to re-prepare the editable path dependency.

# COMMANDS

Not executed in this packet. Source-backed only.

Issue 19705 minimal session (macOS/Linux):

```text
git init --bare .bare -b main
git clone .bare seed
# in seed: pyproject with hatch-vcs + cache-keys git commit/tags
git add -A && git commit -m init && git tag v0.1.0
git push origin main v0.1.0
git -C .bare worktree add ../wt main
git clone .bare plain
(cd wt && uv sync && cat .venv/lib/python*/site-packages/cktest-*.dist-info/uv_cache.json)
(cd plain && uv sync && cat .venv/lib/python*/site-packages/cktest-*.dist-info/uv_cache.json)
```

Then `git commit` in `wt` and `uv sync` again; compare version / cache JSON.

Loose-ref unit test at the failing revision:

```text
cargo test -p uv --test it invalidate_path_on_commit -- --exact
```

TREE (failing world fragment)

linked worktree `wt/`:
  .git                      # file: "gitdir: .../common.git/worktrees/wt"
  pyproject.toml
  src/cktest/__init__.py
  .venv/lib/.../cktest-*.dist-info/uv_cache.json   # commit: null

common.git/ (or main repo .git/):
  worktrees/wt/HEAD         # ref: refs/heads/main
  worktrees/wt/commondir
  packed-refs               # may hold the only copy of refs/heads/main
  refs/                     # may be empty after pack-refs

uv (failing_ref 6feeacc622b8d1a644397fe7d2b8af6d5c3dafcf)/
  crates/uv-cache-info/src/git_info.rs
  crates/uv/tests/it/pip_install.rs

RELEVANT MATERIAL

### git_info.rs


impl Commit {
    pub(crate) fn from_repository(path: &Path) -> Result<Self, GitInfoError> {
        let git_dir = path
            .ancestors()
            .map(|ancestor| ancestor.join(".git"))
            .find(|git_dir| git_dir.exists())
            .ok_or_else(|| GitInfoError::MissingGitDir(path.to_path_buf()))?;

        let git_head_path =
            git_head(&git_dir).ok_or_else(|| GitInfoError::MissingHead(git_dir.clone()))?;
        let git_head_contents = fs_err::read_to_string(git_head_path)?;

        let mut git_ref_parts = git_head_contents.split_whitespace();
        let commit_or_ref = git_ref_parts
            .next()
            .ok_or_else(|| GitInfoError::InvalidRef(git_dir.clone(), git_head_contents.clone()))?;
        let commit = if let Some(git_ref) = git_ref_parts.next() {
            let git_ref_path = git_dir.join(git_ref);
            let commit = fs_err::read_to_string(git_ref_path)?;
            commit.trim().to_string()
        } else {
            commit_or_ref.to_string()
        };
        // ... length/hex checks ...
        Ok(Self(commit))
    }
}

fn git_head(git_dir: &Path) -> Option<PathBuf> {
    let git_head_path = git_dir.join("HEAD");
    if git_head_path.exists() {
        return Some(git_head_path);
    }
    if !git_dir.is_file() {
        return None;
    }
    // worktree .git file: "gitdir: /path/to/.git/worktrees/pr2"
    let contents = fs_err::read_to_string(git_dir).ok()?;
    let (label, worktree_path) = contents.split_once(':')?;
    if label != "gitdir" {
        return None;
    }
    Some(PathBuf::from(worktree_path.trim()))
}

### invalidate_path_on_commit.rs


    // Create a Git repository (regular .git directory, loose ref).
    context
        .temp_dir
        .child(".git")
        .child("HEAD")
        .write_str("ref: refs/heads/main")?;
    context
        .temp_dir
        .child(".git")
        .child("refs")
        .child("heads")
        .child("main")
        .write_str("1b6638fdb424e993d8354e75c55a3e524050c857")?;

    // uv pip install -r requirements.txt  -> prepares example @ ./editable
    // second install -> "Checked 1 package"
    // change refs/heads/main to another 40-hex
    // third install -> re-prepares example

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
