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
