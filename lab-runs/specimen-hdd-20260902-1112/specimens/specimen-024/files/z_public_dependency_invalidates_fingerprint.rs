
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
