#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet (cargo git+https vs path identity).

rust-lang/cargo#15981 / PR 17204. Git checkout walked at a CARGO_HOME path
that still contains `..`, while nested path= deps from the same git repo
are discovered at the collapsed spelling. Same git+https PackageId, two
manifest PathBufs, false 'skipping duplicate package'.

Not specimen-005 (SBOM extra output omitted from unit identity, cargo#15695).
Not specimen-024 (-Zpublic-dependency omitted from unit fingerprint).
Not specimen-086 (rustc_fingerprint path+mtime, cargo#14761).
Not cargo#17275 / #12233 (SourceId Hash ignores precise; unfixed, no
fixed_ref). Not cargo#17289 (checkout short-id length vs core.abbrev).
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, with_state
from update_index import main as update_index

JOB_ID = "job-0321"
WORKER = "scout-job-0321"
TRIAL = "hdd-gitpath"
START_N = 90


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 100):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id in 090-099")


def packet_for(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: rust-lang/cargo
failing_ref: 3d357a9dd6576d7108be731802282176e560d70f
fixed_ref: 5bf4c0cf6aed9e3f3c7b020edca95d8ef541451b
source_issue: https://github.com/rust-lang/cargo/issues/15981
source_pr: https://github.com/rust-lang/cargo/pull/17204
mechanism_tags:
  - git-https-path-identity
  - cargo-home-dotdot
  - duplicate-package-warning
  - recursive-path-source
ecosystem: rust
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7200
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

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
""",
        observed="""# OBSERVED

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
""",
        commands="""# COMMANDS

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
""",
        tree="""rust-lang/cargo
  src/cargo/sources/git/source.rs
  src/cargo/sources/path.rs
  tests/testsuite/git.rs
  $CARGO_HOME/git/checkouts/<ident>/<short-id>/
""",
        source="""repository: rust-lang/cargo
issue: https://github.com/rust-lang/cargo/issues/15981
pr: https://github.com/rust-lang/cargo/pull/17204
failing_ref (squash-merge first parent): 3d357a9dd6576d7108be731802282176e560d70f
fixed_ref (squash merge commit): 5bf4c0cf6aed9e3f3c7b020edca95d8ef541451b
pr_head: af5e90b67078c4ae589dc74a60d3e6fbb094ef31
second_parent: af5e90b67078c4ae589dc74a60d3e6fbb094ef31
merged_at: 2026-07-12T12:20:01Z
merged_by: weihanglo
pr_author: hirehamir
changed_files: src/cargo/sources/path.rs, tests/testsuite/git.rs
pr_title: fix(source): incorrect duplicate package warning
milestone: 1.99.0
scout_note: not specimen-005 (SBOM extra-output unit fingerprint, cargo#15695 / #17216). not specimen-024 (-Zpublic-dependency omitted from unit fingerprint, cargo#16962 / #16965). not specimen-086 (rustc_fingerprint path+mtime of rustc, cargo#14761). not cargo#17275 / #12233 (SourceId Hash ignores precise so two git+https revs collapse to one PathSource; PR closed unmerged, tests-only #17279). not cargo#17289 (checkout directory short-id followed core.abbrev). Distinct leftover: one git+https PackageId collected twice because the checkout walk PathBuf kept CARGO_HOME `..` while nested path= used the collapsed spelling.
""",
        answer_key="""KNOWN FIX (sealed): rust-lang/cargo PR 17204 squash merge 5bf4c0cf6aed9e3f3c7b020edca95d8ef541451b.

failing_ref is merge first parent 3d357a9dd6576d7108be731802282176e560d70f.

GitSource handed RecursivePathSource the raw checkout PathBuf under CARGO_HOME. A home path containing `..` stayed in that string for the filesystem walk. Nested path= edges from the same git manifests were joined and collapsed by cargo_util::paths::normalize_path, so visited (HashSet of PathBuf) and the per-PackageId Vec recorded two Packages for one git identity. first_package then emitted skipping-duplicate.

Repair in read_packages: bind the walk root through paths::normalize_path before walk/visited, so the walk and the nested path= recursion share one PathBuf. Added tests/testsuite/git.rs no_duplicate_package_warning_with_dotdot_cargo_home (git dep with a path member; CARGO_HOME = home/../cargo-home; stderr has no duplicate warning). Case C (two real directories, same name) is unchanged.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (clean CARGO_HOME one path vs `..` two spellings of one git checkout vs true two-directory same-name clash vs local path dep with no git checkout; git PackageId vs PathBuf identity; GitSource fingerprint is oid)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — git+https SourceId is one object; RecursivePathSource still keys discovery on unsmoothed PathBuf; nested path= already collapsed
ecosystem: rust / cargo
mechanism_family: git-https-path-identity, cargo-home-dotdot, duplicate-package-warning

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "git_source_checkout_failing.rs": """// Reduced excerpt of GitSource::update on failing_ref
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
""",
            "git_source_fingerprint_failing.rs": """// Reduced excerpt of GitSource::fingerprint on failing_ref
// src/cargo/sources/git/source.rs
// Identity for rebuild detection is the locked git oid, not a checkout PathBuf.

    fn fingerprint(&self, _pkg: &Package) -> CargoResult<String> {
        match &*self.locked_rev.borrow() {
            Revision::Locked(oid) => Ok(oid.to_string()),
            _ => unreachable!("locked_rev must be resolved when computing fingerprint"),
        }
    }
""",
            "read_packages_failing.rs": """// Reduced excerpt of read_packages on failing_ref
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
""",
            "read_nested_packages_failing.rs": """// Reduced excerpt of read_nested_packages on failing_ref
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
""",
            "first_package_failing.rs": """// Reduced excerpt of first_package on failing_ref
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
""",
            "leftover_identity_split.txt": """Registry / fixture:
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
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"launched": False, "reason": ""}

    def fn(state):
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == JOB_ID), None)
        if job is None:
            raise SystemExit(f"{JOB_ID} missing")
        if job.get("status") == "CLAIMED" and job.get("worker") == WORKER:
            complete(state, JOB_ID, result="ok", artifact=f"specimens/{spec_id}")
        elif job.get("status") == "DONE" and job.get("artifact") == f"specimens/{spec_id}":
            pass
        else:
            raise SystemExit(
                f"{JOB_ID} status={job.get('status')} worker={job.get('worker')} artifact={job.get('artifact')}"
            )
        ids = {s.get("id") for s in state.get("specimens") or []}
        if spec_id not in ids:
            state.setdefault("specimens", []).append({"id": spec_id})
        already = any(
            j.get("queue") == "READY_R1_DREAM"
            and j.get("specimen") == spec_id
            and j.get("status") in {"READY", "CLAIMED"}
            for j in state.get("ready_jobs") or []
        )
        if not already:
            enqueue(
                state,
                "READY_R1_DREAM",
                input_ref=f"seeds/{spec_id}.md trial={TRIAL}",
                expected_output="0001-dreamer.md",
                kill_condition="15m",
                estimated_cost="r1",
                priority_reason="cargo git+https vs path identity; CARGO_HOME .. duplicate; not 005/086",
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        ready_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "READY"
        ]
        if claimed_r1:
            note["reason"] = (
                "dream.sh not launched; R1 already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        elif any(j.get("lineage") != TRIAL for j in ready_r1):
            note["reason"] = (
                "dream.sh not launched; READY_R1_DREAM already queued: "
                + ",".join(
                    f"{j['id']}:{j.get('lineage')}"
                    for j in ready_r1
                    if j.get("lineage") != TRIAL
                )
            )
        else:
            note["reason"] = (
                "dream.sh not launched from scout; READY_R1_DREAM enqueued "
                f"trial={TRIAL} (coordinator owns dreamer slots)"
            )
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_for(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(f"enqueued READY_R1_DREAM trial={TRIAL} specimen={spec_id}")
        print(launch_note)
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
