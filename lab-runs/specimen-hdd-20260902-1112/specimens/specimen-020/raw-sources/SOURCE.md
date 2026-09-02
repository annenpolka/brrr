TRANSFER_TARGET. Same mechanism as pnpm/pnpm#14343, different ecosystem (Rust/Node install → owned Python stdlib).
pr: https://github.com/pnpm/pnpm/pull/14343
merge_commit: 621f45c22ef8b284ef38bbad636162df8354cdea
merged_at: 2026-09-01T12:56:32Z
Mechanism: empty unified-diff old range treated like a nonempty 1-based range; insertion lands one line early; apply/install still exits 0.
Owned fixture; executed on lab host. pnpm was not installed.
