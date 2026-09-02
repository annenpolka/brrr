repository: astral-sh/uv
issue: https://github.com/astral-sh/uv/issues/19152
pr: https://github.com/astral-sh/uv/pull/19269
failing_ref (squash first parent): 77f271063993020770ee785469226e33324576be
fixed_ref (squash merge): a1c90c1fa12c95485f3d6a210daa4e6cc7466a90
pr_head: 0186fa6dd662fa11a600c29536f0fd482944eb5d
merged_at: 2026-05-05T00:47:10Z
merged_by: charliermarsh
pr_author: charliermarsh
changed_files: crates/uv-distribution/src/metadata/lowering.rs, crates/uv-distribution/src/metadata/requires_dist.rs, crates/uv/tests/it/sync.rs
pr_title: Fix transitive Git path dependencies in lockfiles
scout_note: leftover-identity in uv.lock (absolute directory vs git+subdirectory), not uv.lock vs pylock.toml. not specimen-006/022/023 cache fingerprints. Distinct leftover: Poetry path inside a git checkout serialized as a machine-specific directory.
