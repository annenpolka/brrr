# TASK

A tiny crate cache reports freshness from a short hex identity. After the first build, only `Cargo.lock` (here, a one-line lockfile) changes: `serde = "1.0.0"` becomes `serde = "1.0.219"`. The second build prints FRESH. The artifact still says it was built with `1.0.0`.

The developer wants to know which bytes entered that identity, and whether the live lockfile is one of them.
