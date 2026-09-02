# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# COMMANDS

```
# not executed on this lab host
# failing_ref 3d357a9dd6576d7108be731802282176e560d70f
# src/cargo/sources/git/source.rs GitSource::update -> RecursivePathSource
# src/cargo/sources/path.rs read_packages / read_nested_packages / first_package

# public symptom (CARGO_HOME retains ..):
# cargo new tester && cd tester
# cargo add serde --git "https://github.com/serde-rs/serde"
# CARGO_HOME=${HOME}/tmp/subfolder/../cargo cargo build
# warning: skipping duplicate package `serde v1.0.225 (https://github.com/serde-rs/serde#ee3c2372)`:
#   .../tmp/cargo/git/checkouts/serde-.../serde/Cargo.toml
# in favor of .../tmp/subfolder/../cargo/git/checkouts/serde-.../serde/Cargo.toml
```

Source-backed only. Do not execute untrusted checkouts on the host.

rust-lang/cargo
  src/cargo/sources/git/source.rs
  src/cargo/sources/path.rs
  tests/testsuite/git.rs
  $CARGO_HOME/git/checkouts/<ident>/<short-id>/

RELEVANT MATERIAL

### first_package_failing.rs

// Reduced excerpt of first_package on failing_ref
// src/cargo/sources/path.rs
// Warns when one PackageId mapped to more than one Package.

fn first_package<'p>(
    pkg_id: PackageId,
    pkgs: &'p Vec<Package>,
    warned_duplicate: &mut HashSet<PackageId>,
    gctx: &GlobalContext,
) -> &'p Package {
    if pkgs.len() != 1 && warned_duplicate.insert(pkg_id) {
        let ignored = pkgs[1..]
            .iter()
            .filter(|pkg| pkg.publish().is_none())
            .collect::<Vec<_>>();
        if !ignored.is_empty() {
            let _ = writeln!(&mut msg, "skipping duplicate package{plural} `{pkg_id}`:");
            for ignored in ignored {
                let _ = writeln!(&mut msg, "  {manifest_path}");
            }
            let _ = writeln!(&mut msg, "in favor of {manifest_path}");
            let _ = gctx.shell().warn(msg);
        }
    }
    &pkgs[0]
}

### git_source_checkout_failing.rs

// Reduced excerpt of GitSource::update on failing_ref
// src/cargo/sources/git/source.rs
// 3d357a9dd6576d7108be731802282176e560d70f
// Checkout lives under $CARGO_HOME/git/checkouts/<ident>/<short-id>/.
// RecursivePathSource is constructed with that PathBuf as-is.

        let checkout_path = self
            .gctx
            .git_checkouts_path()
            .join(&self.ident)
            .join(short_id.as_str());
        let checkout_path = checkout_path.into_path_unlocked();
        db.copy_to(actual_rev, &checkout_path, self.gctx, self.quiet)?;

        let source_id = self
            .source_id
            .borrow()
            .with_git_precise(Some(actual_rev.to_string()));
        let path_source = RecursivePathSource::new(&checkout_path, source_id, self.gctx);

        self.path_source.replace(Some(path_source));
        self.short_id.replace(Some(short_id.as_str().into()));
        self.locked_rev.replace(Revision::Locked(actual_rev));
        self.path_source.borrow().as_ref().unwrap().load()?;

### git_source_fingerprint_failing.rs

// Reduced excerpt of GitSource::fingerprint on failing_ref
// src/cargo/sources/git/source.rs
// Identity for rebuild detection is the locked git oid, not a checkout PathBuf.

    fn fingerprint(&self, _pkg: &Package) -> CargoResult<String> {
        match &*self.locked_rev.borrow() {
            Revision::Locked(oid) => Ok(oid.to_string()),
            _ => unreachable!("locked_rev must be resolved when computing fingerprint"),
        }
    }

### leftover_identity_split.txt

Registry / fixture:
  in-tree: git repo `dep` with path member `member` (PR 17204 regression shape)
  public #15981: serde git+https://github.com/serde-rs/serde (workspace members)

Git PackageId (both spellings, case B):
  serde v1.0.225 (https://github.com/serde-rs/serde#ee3c2372)
  member v0.1.0 (<dep-url>#<rev>)

Case A (CARGO_HOME without ..):
  cargo check
  one checkout PathBuf
  HashMap<PackageId, Vec<Package>> length 1 per id
  no skipping-duplicate for member/dep/serde

Case B (CARGO_HOME keeps ..):
  CARGO_HOME=/home/kaspar/tmp/subfolder/../cargo
  walk PathBuf retains subfolder/../cargo/git/checkouts/...
  nested path= PathBuf is the collapsed tmp/cargo/git/checkouts/...
  visited HashSet sees two keys
  Vec<Package> length 2 for one git PackageId
  warning lists both Cargo.toml spellings
  build finishes (not `failed to find ... in path source`)

Case C (true two-directory clash, clean CARGO_HOME):
  duplicate1/Cargo.toml and duplicate2/Cargo.toml, same name
  two different files
  warning still fires

Case D (local path dep, no git):
  no $CARGO_HOME/git/checkouts walk of this crate

GitSource::fingerprint on failing_ref:
  locked git oid string (not the checkout path)

Not this packet:
  SBOM extra output omitted from unit identity (specimen-005)
  rustc_fingerprint path+mtime of rustc (specimen-086)
  SourceId Hash ignoring precise rev (cargo#12233 / unmerged #17275)
  checkout short-id length vs core.abbrev (cargo#17289)

### read_nested_packages_failing.rs

// Reduced excerpt of read_nested_packages on failing_ref
// src/cargo/sources/path.rs
// visited is HashSet<PathBuf> (lexical). Nested path= edges are collapsed.

fn read_nested_packages(
    path: &Path,
    all_packages: &mut HashMap<PackageId, Vec<Package>>,
    source_id: SourceId,
    gctx: &GlobalContext,
    visited: &mut HashSet<PathBuf>,
    errors: &mut Vec<anyhow::Error>,
) -> CargoResult<()> {
    if !visited.insert(path.to_path_buf()) {
        return Ok(());
    }

    let manifest_path = find_project_manifest_exact(path, "Cargo.toml")?;
    // ...
    let pkg = Package::new(manifest, &manifest_path);
    let pkg_id = pkg.package_id();
    all_packages.entry(pkg_id).or_default().push(pkg);

    // We normalize the path here ensure that we don't infinitely walk around
    // looking for crates. By normalizing we ensure that we visit this crate at
    // most once.
    if !source_id.is_registry() {
        for p in nested.iter() {
            let path = paths::normalize_path(&path.join(p));
            let result =
                read_nested_packages(&path, all_packages, source_id, gctx, visited, errors);

### read_packages_failing.rs

// Reduced excerpt of read_packages on failing_ref
// src/cargo/sources/path.rs
// 3d357a9dd6576d7108be731802282176e560d70f
// Walks `path` as given (the git checkout PathBuf). No collapse of `..` here.

fn read_packages(
    path: &Path,
    source_id: SourceId,
    gctx: &GlobalContext,
) -> CargoResult<HashMap<PackageId, Vec<Package>>> {
    let mut all_packages = HashMap::default();
    let mut visited = HashSet::<PathBuf>::default();
    let mut errors = Vec::<anyhow::Error>::new();

    walk(path, &mut |dir| {
        if has_manifest(dir) {
            read_nested_packages(
                dir,
                &mut all_packages,
                source_id,
                gctx,
                &mut visited,
                &mut errors,
            )?;
        }
        Ok(true)
    })?;

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
