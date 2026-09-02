# FIX (sealed)

Issue: https://github.com/rust-lang/cargo/issues/16962
  title: `-Zpublic-dependency` does not invalidate build cache when it should
PR: https://github.com/rust-lang/cargo/pull/16965
  title: Rebuild when -Zpublic-dependency changes
failing_ref: ac87f85a9bfe1816fa5d4e805d8182a12d61d047
fixed_ref: 01a7bd605faf2f2f7e3a979a4f3d4c14e855aa88

Root cause: `-Zpublic-dependency` changes `--extern` for library units
(private deps get `priv`). That effective mode was not part of the
fingerprint config hash, so toggling the flag left the lib Fresh.

Fix: hash
`(unit.target.is_lib() && any(!dep.public) && is_public_dependency_enabled(...))`
into the fingerprint config, sharing `is_public_dependency_enabled`
with `extern_args`.

After the fix, the second and sixth checks include `[CHECKING] foo`
and the warning polarity matches the current flag.
