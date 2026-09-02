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
