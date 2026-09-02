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
