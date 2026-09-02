# OBSERVED

Public rust-lang/cargo#15981 (kaspar030, 2025-09-18) / PR 17204. Failing world: rust-lang/cargo `3d357a9dd6576d7108be731802282176e560d70f` (squash-merge first parent of `5bf4c0cf6aed9e3f3c7b020edca95d8ef541451b`). Local cargo execution was not performed on this lab host.

Issue reproduction:

```
cargo new tester; cd tester
cargo add serde --git "https://github.com/serde-rs/serde"
CARGO_HOME=${HOME}/tmp/subfolder/../cargo cargo build
```

Saw: `skipping duplicate package` for `serde` / `serde_core` / `serde_derive` at git+https PackageIds, with one manifest path keeping `subfolder/../cargo` and the other using the collapsed `tmp/cargo` spelling. Reporter note: the two paths point to the same directory.

On the failing revision, `GitSource::update` checks out to `$CARGO_HOME/git/checkouts/<ident>/<short-id>/` and wraps that PathBuf in `RecursivePathSource::new`. `RecursivePathSource::load` calls `read_packages` on that path.

`read_packages` walks the checkout. When a directory has a manifest it calls `read_nested_packages`. That function inserts `path.to_path_buf()` into a `HashSet<PathBuf>` named `visited` and pushes the package onto `HashMap<PackageId, Vec<Package>>`. Nested `path =` dependencies are then joined and passed through `paths::normalize_path` before the recursive call. The walk root itself is the checkout PathBuf as stored.

`first_package` warns when that `Vec` has length != 1 and `publish` is unset (`None`), printing ignored manifests then `in favor of` `pkgs[0]`'s manifest path.

`GitSource::download` forwards to the path source; a missing PackageId would be `failed to find {id} in path source`. Case B is a warning plus a finished build, not that error.

True two-directory same-name packages (case C) already warn on this revision with a clean `CARGO_HOME`.

Not executed on this lab host.
