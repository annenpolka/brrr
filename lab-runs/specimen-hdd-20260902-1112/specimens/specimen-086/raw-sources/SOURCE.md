repository: rust-lang/cargo
pr: https://github.com/rust-lang/cargo/pull/14761
issue: none (PR-only)
pr_title: Add more metadata to rustc_fingerprint
pr_head (bors-approved, verified): b5acf4ce4763ff90fd8bd92494490184a37fa24e
pr_head_parent: 497c22876324730f627e597f4c186b621f735bad
failing_ref (bors merge first parent): 40d6078bafd61645f13086f697104c360b25b7d3
fixed_ref (bors merge commit): 0310497822a7a673a330a5dd068b7aaa579a265e
second_parent: b5acf4ce4763ff90fd8bd92494490184a37fa24e
merged_at: 2024-11-01T20:06:37Z
merged_by: bors
changed_files: src/cargo/util/rustc.rs
author: Josh Stone (cuviper)
reviewer: epage
milestone: 1.84.0
scout_note: not specimen-005 (cargo SBOM extra-output unit fingerprint, cargo#15695 / #17216). not specimen-024 (-Zpublic-dependency omitted from unit fingerprint, cargo#16962 / #16965). not specimen-075 (rust-lang/rust#133828 incremental query-dep / next-solver false-green). Distinct leftover: rustc_fingerprint of the compiler executable is path+mtime only; Fedora-clamped mtimes make distinct rustc builds look identical so target/.rustc_info.json is reused.
