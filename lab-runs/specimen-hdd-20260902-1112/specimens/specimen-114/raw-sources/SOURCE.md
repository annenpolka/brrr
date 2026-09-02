repository: astral-sh/ruff
issue: https://github.com/astral-sh/ruff/issues/12264
pr: https://github.com/astral-sh/ruff/pull/12727
failing_ref (squash parent / PR base): 90e5bc2bd95e15086a3af81589cc2a1af298b6b2
fixed_ref (squash merge): a631d600acf3fa26c744ff00909f9891365e7ed4
merged_at: 2024-08-07T19:53:45Z
pr_author: MichaReiser
merged_by: MichaReiser
changed_files: crates/ruff_workspace/src/resolver.rs
pr_title: Fix cache invalidation for nested pyproject.toml files
scout_note: not specimen-001/002/003/107. Distinct leftover: nested pyproject identity vs leftover cache. job-0461. not ruff#1589 config-hash leftover.
