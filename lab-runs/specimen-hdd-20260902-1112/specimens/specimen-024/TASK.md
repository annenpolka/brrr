# TASK

A library crate depends on `dep` and exposes a type from that crate in
its public API:

```rust
extern crate dep;
pub fn use_dep(_: dep::FromDep) {}
```

Nightly rustc can emit `exported_private_dependencies` when Cargo
passes private `--extern` information. That extra rustc mode is
requested with `cargo check -Zpublic-dependency`.

The developer toggles that flag across successive checks on the same
`target/` directory (no source edits) and needs the warning presence to
match the *current* invocation, not a previous one.
