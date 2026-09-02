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
