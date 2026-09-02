# TASK

A crate depends on a git repository. Cargo checks that repo out under `$CARGO_HOME/git/checkouts/<ident>/<short-id>/` and then discovers packages with `RecursivePathSource` (a filesystem walk of the checkout, plus following `path =` dependencies written in those manifests). Package IDs for everything in that checkout are git+https (the git `SourceId`, including the locked revision). The on-disk identity of each discovered crate is the `PathBuf` of its `Cargo.toml`.

`CARGO_HOME` is allowed to contain a `..` segment that still resolves on disk (example from the public report: `/home/kaspar/tmp/subfolder/../cargo`).

Fixture used in-tree (one git repo, two crates, one `path =` edge):

```
dep/Cargo.toml          name = "dep"; member = { path = "member" }
dep/src/lib.rs
dep/member/Cargo.toml   name = "member"
dep/member/src/lib.rs
```

Consumer:

```
[dependencies]
dep = { git = "<dep-url>" }
```

Case A — `CARGO_HOME` has no `..` (harness default `$HOME/.cargo`). `cargo check` of the consumer. One checkout directory. No `skipping duplicate package` line for `member` or `dep`.

Case B — same tree, `CARGO_HOME=$HOME/../cargo-home` (the `..` resolves on disk). Public report used serde:

```
CARGO_HOME=/home/kaspar/tmp/subfolder/../cargo cargo build
```

On rust-lang/cargo `3d357a9dd6576d7108be731802282176e560d70f`, stderr contains `skipping duplicate package` for crates whose PackageId is the git URL + rev, listing two `Cargo.toml` paths that differ only by whether `subfolder/../` is still in the string. The two paths name the same directory after `..` is collapsed.

Public serde warning (kaspar030, cargo 1.89 / nightly 1.92):

```
warning: skipping duplicate package `serde v1.0.225 (https://github.com/serde-rs/serde#ee3c2372)`:
  /home/kaspar/tmp/cargo/git/checkouts/serde-1b10f8d7b61b7b51/ee3c237/serde/Cargo.toml
in favor of /home/kaspar/tmp/subfolder/../cargo/git/checkouts/serde-1b10f8d7b61b7b51/ee3c237/serde/Cargo.toml
```

Same shape for `serde_core` and `serde_derive`. Build still finishes.

Case C — true two-directory clash inside one git repo, clean `CARGO_HOME`. In-tree `duplicate1/` and `duplicate2/` both declare `name = "duplicate"`, `publish = true`. `cargo run` warns:

```
[WARNING] skipping duplicate package `duplicate v0.5.0 ([ROOTURL]/dep#[..])`:
  [ROOT]/home/.cargo/git/checkouts/dep-[HASH]/[..]/duplicate2/Cargo.toml
in favor of [ROOT]/home/.cargo/git/checkouts/dep-[HASH]/[..]/duplicate1/Cargo.toml
```

Those two `Cargo.toml` files are different files. No `..` in `CARGO_HOME`.

Case D — consumer depends on a local `path` crate only (no git+https). `CARGO_HOME` with `..` does not create a git checkout, so this walk is not the git `RecursivePathSource` under `$CARGO_HOME/git/checkouts`.

`GitSource::fingerprint` on this revision returns the locked git oid string, not a filesystem path.

The developer wants to know, for case B, which path identity `RecursivePathSource` actually stored for the git+https package: the leftover `..` spelling, the collapsed spelling, both (duplicate skip of one git PackageId), or omitted.
