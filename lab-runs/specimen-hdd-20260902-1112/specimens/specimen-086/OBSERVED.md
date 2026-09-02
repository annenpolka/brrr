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
