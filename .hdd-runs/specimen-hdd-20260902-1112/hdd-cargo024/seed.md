CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Source: https://github.com/rust-lang/cargo/issues/16962 and test
`z_public_dependency_invalidates_fingerprint` snapshot at
`ac87f85a9bfe1816fa5d4e805d8182a12d61d047`. Local execution was not
performed.

Issue steps (nightly cargo 1.97.0-nightly 4f9b52075):

```
1. cargo clean
2. cargo -Zpublic-dependency check   → warning, as expected
3. cargo check                       → warning, NOT as expected
4. cargo clean
5. cargo check                       → no warning, as expected
6. cargo -Zpublic-dependency check   → no warning, NOT as expected
```

Failing-revision test snapshot of steps 2→3 and 5→6 (short format):

After `check -Zpublic-dependency` (warning present), the next
`cargo check --message-format=short` still prints:

```
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s
```

Note: no `[CHECKING] foo` line on that second command.

After `cargo clean` then plain `cargo check` (no warning), the next
`cargo check -Zpublic-dependency --message-format=short` prints only:

```
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s
```

No `[CHECKING]`, no warning.

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

TREE (failing world fragment)

foo/
  Cargo.toml              # [dependencies] dep = "0.1.0"
  src/lib.rs              # pub fn use_dep(_: dep::FromDep)
  target/                 # reused across flag toggles

cargo (failing_ref ac87f85a9bfe1816fa5d4e805d8182a12d61d047)/
  src/cargo/core/compiler/fingerprint/mod.rs
  src/cargo/core/compiler/mod.rs
  tests/testsuite/pub_priv.rs

RELEVANT MATERIAL

### z_public_dependency_invalidates_fingerprint.rs


#[cargo_test(nightly, reason = "exported_private_dependencies lint is unstable")]
fn z_public_dependency_invalidates_fingerprint() {
    Package::new("dep", "0.1.0")
        .file("src/lib.rs", "pub struct FromDep;")
        .publish();
    let p = project()
        .file(
            "Cargo.toml",
            r#"
                [package]
                name = "foo"
                version = "0.0.1"
                edition = "2015"

                [dependencies]
                dep = "0.1.0"
            "#,
        )
        .file(
            "src/lib.rs",
            "
            extern crate dep;
            pub fn use_dep(_: dep::FromDep) {}
        ",
        )
        .build();

    p.cargo("check -Zpublic-dependency --message-format=short")
        .masquerade_as_nightly_cargo(&["public-dependency"])
        .with_stderr_data(str![[r#"
...
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
...
"#]])
        .run();

    p.cargo("check --message-format=short")
        .with_stderr_data(str![[r#"
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s

"#]])
        .run();

    p.cargo("clean").run();

    p.cargo("check --message-format=short")
        .with_stderr_data(str![[r#"
...
"#]])
        .run();

    p.cargo("check -Zpublic-dependency --message-format=short")
        .masquerade_as_nightly_cargo(&["public-dependency"])
        .with_stderr_data(str![[r#"
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s

"#]])
        .run();
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
