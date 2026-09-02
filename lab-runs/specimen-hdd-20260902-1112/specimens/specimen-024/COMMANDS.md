# COMMANDS

Not executed in this packet. Source-backed only.

Requires nightly rustc/cargo with `-Zpublic-dependency`.

```text
cargo clean
cargo -Zpublic-dependency check --message-format=short
cargo check --message-format=short
cargo clean
cargo check --message-format=short
cargo -Zpublic-dependency check --message-format=short
```

Upstream test at the failing revision:

```text
cargo test --test testsuite pub_priv::z_public_dependency_invalidates_fingerprint -- --exact
```
