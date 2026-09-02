# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Cargo caches `rustc -vV` (and other rustc-info commands) in the workspace target directory as `.rustc_info.json`. The cache is keyed by a `u64` named `rustc_fingerprint`. `Cache::load` reuses the whole JSON when that field equals the fingerprint computed for the current compiler; otherwise it starts an empty cache.

`rustc_fingerprint` is computed in `src/cargo/util/rustc.rs` on rust-lang/cargo `40d6078bafd61645f13086f697104c360b25b7d3`. For each executable (the `rustc` path, optional `rustc_wrapper`, optional `rustc_workspace_wrapper`) a closure `hash_exe` hashes:

1. the resolved executable path
2. that path's mtime (`paths::mtime`)

It does not run `rustc -vV` as part of the fingerprint. Cached `-vV` stdout lives under a separate per-command map and is only consulted after the fingerprint matches.

Public report (Fedora distro rustc, shared `target/` including `.rustc_info.json`):

Two compilers, both invoked as `/usr/bin/rustc`, both `release: 1.82.0`, both `commit-hash` `f6e511eec` (2024-10-15), both mtimes clamped to `2024-10-17 00:00:00` by Fedora reproducible-builds policy.

Compiler X (`rustc -vV` if actually run):

```
rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc42)
```

Compiler Y:

```
rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc40)
```

A crate graph compiled under X leaves `target/debug/deps/libautocfg-589c41db1eea6297.rlib` plus `.rustc_info.json`. A later cargo on Y, same `target/`, surfaces:

```
error[E0514]: found crate `autocfg` compiled by an incompatible version of rustc
 --> build.rs:2:14
  |
2 |     let ac = autocfg::new();
  |              ^^^^^^^
  |
  = note: the following crate versions were found:
          crate `autocfg` compiled by rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc42): [...]/target/debug/deps/libautocfg-589c41db1eea6297.rlib
  = help: please recompile that crate using this compiler (rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc40)) (consider running `cargo clean` first)
```

Cases (distro rustc unless noted; `CARGO_CACHE_RUSTC_INFO` unset so caching is on):

Case A — X then Y, same path `/usr/bin/rustc`, same clamped mtime, shared `target/.rustc_info.json`. File lengths may differ. Creation times may differ. `rustc -vV` Fedora suffixes differ as above.

Case B — same as A, except the two binaries also have different `st_size`.

Case C — same as A, except the two binaries have the same length and the same mtime; only birth/creation time differs (and the Fedora suffix, if `-vV` were run).

Case D — rustup: `RUSTUP_HOME` and `RUSTUP_TOOLCHAIN` are set. `hash_exe` still runs on the `rustc` path (often the rustup shim). The rustup arm then also hashes the toolchain string, the home path, and `mtime` of `$RUSTUP_HOME/toolchains/$RUSTUP_TOOLCHAIN/bin/rustc`.

Case E — `CARGO_CACHE_RUSTC_INFO=0`. `load_global_rustc` passes `cache_location: None`.

Case F — `build.rustc-wrapper` set. That wrapper path is hashed with the same `hash_exe` as `rustc`.

The developer wants to know, for case A (and B/C), which identity `Cache::load` actually used for Y against X's `.rustc_info.json`: `rustc_fingerprint` equal (reuse cached `-vV` / "reusing existing rustc info cache"), unequal ("different compiler, creating new rustc info cache"), or cache disabled.

# OBSERVED

Public rust-lang/cargo#14761 (merged via bors). Failing world: `src/cargo/util/rustc.rs` at merge first parent `40d6078bafd61645f13086f697104c360b25b7d3`. Local cargo/rustc execution was not performed on this lab host.

`GlobalContext::load_global_rustc` (same revision, `src/cargo/util/context/mod.rs`) places the cache at `ws.target_dir().join(".rustc_info.json")` when a workspace is present and `CARGO_CACHE_RUSTC_INFO` is not `"0"`. The rustup-shim comparison path passed into `Rustc::new` is `$CARGO_HOME/bin/rustc`.

On the failing revision, `hash_exe` is:

```
let path = paths::resolve_executable(path)?;
path.hash(hasher);
paths::mtime(&path)?.hash(hasher);
```

`Cache::load` then:

```
if data.rustc_fingerprint == rustc_fingerprint {
    debug!("reusing existing rustc info cache");
    dirty = false;
    data
} else {
    debug!("different compiler, creating new rustc info cache");
    empty
}
```

`Rustc::new` takes `verbose_version` from `cache.cached_output(&cmd, 0)` of `rustc -vV`. A fingerprint hit therefore does not re-run `-vV`, so the Fedora suffix in verbose version is not observed at fingerprint time.

PR report: Fedora clamps mtimes (https://fedoraproject.org/wiki/Changes/ReproducibleBuildsClampMtimes). Rust 1.82 across Fedora 39–42 presents as `/usr/bin/rustc` + `2024-10-17 00:00:00`. Shared `target/` (including `.rustc_info.json`) then hits E0514 as in TASK.

No in-tree regression test landed with the PR (single-file change to `rustc.rs`).

# COMMANDS

```
# not executed on this lab host
# failing_ref 40d6078bafd61645f13086f697104c360b25b7d3
# src/cargo/util/rustc.rs rustc_fingerprint / Cache::load
# src/cargo/util/context/mod.rs load_global_rustc -> target/.rustc_info.json

# public symptom (Fedora distro rustc, shared target/):
# cargo build
# error[E0514]: found crate `autocfg` compiled by an incompatible version of rustc
#   crate compiled by Fedora 1.82.0-1.fc42
#   current compiler Fedora 1.82.0-1.fc40
```

Source-backed only. Do not execute untrusted checkouts on the host.

rust-lang/cargo
  src/cargo/util/rustc.rs
  src/cargo/util/context/mod.rs
  <workspace>/target/.rustc_info.json

RELEVANT MATERIAL

### cache_load_compare.rs

# Reduced excerpt of Cache::load on failing_ref
# src/cargo/util/rustc.rs

#[derive(Serialize, Deserialize, Debug, Default)]
struct CacheData {
    rustc_fingerprint: u64,
    outputs: HashMap<u64, Output>,
    successes: HashMap<u64, bool>,
}

// Cache::load:
//   rustc_fingerprint = rustc_fingerprint(wrapper, workspace_wrapper, rustc, rustup_rustc, gctx)
//   read cache_location as CacheData
//   if data.rustc_fingerprint == rustc_fingerprint {
//       debug!("reusing existing rustc info cache");
//       dirty = false;
//       data
//   } else {
//       debug!("different compiler, creating new rustc info cache");
//       empty  // CacheData { rustc_fingerprint, outputs: {}, successes: {} }
//   }

// Rustc::new then:
//   cmd = rustc (wrapped) -vV
//   verbose_version = cache.cached_output(&cmd, 0)?.0

### fedora_rustc_identity_split.txt

Shared workspace target dir (all cases A–C):
  <ws>/target/.rustc_info.json
  <ws>/target/debug/deps/libautocfg-589c41db1eea6297.rlib

Compiler X (Fedora 1.82.0-1.fc42):
  path: /usr/bin/rustc
  mtime: 2024-10-17 00:00:00 (clamped)
  rustc -vV release: 1.82.0
  rustc -vV commit-hash: f6e511eec (2024-10-15)
  rustc -vV host: x86_64-unknown-linux-gnu
  rustc -vV extra suffix: (Fedora 1.82.0-1.fc42)

Compiler Y (Fedora 1.82.0-1.fc40):
  path: /usr/bin/rustc
  mtime: 2024-10-17 00:00:00 (clamped)
  rustc -vV release: 1.82.0
  rustc -vV commit-hash: f6e511eec (2024-10-15)
  rustc -vV host: x86_64-unknown-linux-gnu
  rustc -vV extra suffix: (Fedora 1.82.0-1.fc40)

hash_exe inputs on failing_ref (each of rustc, wrapper, workspace_wrapper):
  resolved path
  mtime

rustup extra inputs (only if RUSTUP_HOME and RUSTUP_TOOLCHAIN are both set):
  rustup_toolchain string
  rustup_home string
  mtime of $RUSTUP_HOME/toolchains/$RUSTUP_TOOLCHAIN/bin/rustc

Cache::load decision:
  equal rustc_fingerprint -> reuse entire CacheData (including cached -vV stdout)
  unequal -> empty CacheData with the new fingerprint

### load_global_rustc.rs

# Reduced excerpt of load_global_rustc on failing_ref
# src/cargo/util/context/mod.rs

pub fn load_global_rustc(&self, ws: Option<&Workspace<'_>>) -> CargoResult<Rustc> {
    let cache_location = ws.map(|ws| {
        ws.target_dir()
            .join(".rustc_info.json")
            .into_path_unlocked()
    });
    let wrapper = self.maybe_get_tool("rustc_wrapper", &self.build_config()?.rustc_wrapper);
    let rustc_workspace_wrapper = self.maybe_get_tool(
        "rustc_workspace_wrapper",
        &self.build_config()?.rustc_workspace_wrapper,
    );

    Rustc::new(
        self.get_tool(Tool::Rustc, &self.build_config()?.rustc),
        wrapper,
        rustc_workspace_wrapper,
        &self
            .home()
            .join("bin")
            .join("rustc")
            .into_path_unlocked()
            .with_extension(env::consts::EXE_EXTENSION),
        if self.cache_rustc_info {
            cache_location
        } else {
            None
        },
        self,
    )
}

// cache_rustc_info is false only when env CARGO_CACHE_RUSTC_INFO is "0"

### rustc_fingerprint_failing.rs

# Reduced excerpt of rustc_fingerprint on failing_ref
# src/cargo/util/rustc.rs
# 40d6078bafd61645f13086f697104c360b25b7d3

fn rustc_fingerprint(
    wrapper: Option<&Path>,
    workspace_wrapper: Option<&Path>,
    rustc: &Path,
    rustup_rustc: &Path,
    gctx: &GlobalContext,
) -> CargoResult<u64> {
    let mut hasher = StableHasher::new();

    let hash_exe = |hasher: &mut _, path| -> CargoResult<()> {
        let path = paths::resolve_executable(path)?;
        path.hash(hasher);

        paths::mtime(&path)?.hash(hasher);
        Ok(())
    };

    hash_exe(&mut hasher, rustc)?;
    if let Some(wrapper) = wrapper {
        hash_exe(&mut hasher, wrapper)?;
    }
    if let Some(workspace_wrapper) = workspace_wrapper {
        hash_exe(&mut hasher, workspace_wrapper)?;
    }

    let maybe_rustup = rustup_rustc == rustc;
    match (
        maybe_rustup,
        gctx.get_env("RUSTUP_HOME"),
        gctx.get_env("RUSTUP_TOOLCHAIN"),
    ) {
        (_, Ok(rustup_home), Ok(rustup_toolchain)) => {
            rustup_toolchain.hash(&mut hasher);
            rustup_home.hash(&mut hasher);
            let real_rustc = Path::new(&rustup_home)
                .join("toolchains")
                .join(rustup_toolchain)
                .join("bin")
                .join("rustc")
                .with_extension(env::consts::EXE_EXTENSION);
            paths::mtime(&real_rustc)?.hash(&mut hasher);
        }
        (true, _, _) => anyhow::bail!("probably rustup rustc, but without rustup's env vars"),
        _ => (),
    }

    Ok(hasher.finish())
}

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
