repository: rust-lang/cargo
issue: https://github.com/rust-lang/cargo/issues/15981
pr: https://github.com/rust-lang/cargo/pull/17204
failing_ref (squash-merge first parent): 3d357a9dd6576d7108be731802282176e560d70f
fixed_ref (squash merge commit): 5bf4c0cf6aed9e3f3c7b020edca95d8ef541451b
pr_head: af5e90b67078c4ae589dc74a60d3e6fbb094ef31
second_parent: af5e90b67078c4ae589dc74a60d3e6fbb094ef31
merged_at: 2026-07-12T12:20:01Z
merged_by: weihanglo
pr_author: hirehamir
changed_files: src/cargo/sources/path.rs, tests/testsuite/git.rs
pr_title: fix(source): incorrect duplicate package warning
milestone: 1.99.0
scout_note: not specimen-005 (SBOM extra-output unit fingerprint, cargo#15695 / #17216). not specimen-024 (-Zpublic-dependency omitted from unit fingerprint, cargo#16962 / #16965). not specimen-086 (rustc_fingerprint path+mtime of rustc, cargo#14761). not cargo#17275 / #12233 (SourceId Hash ignores precise so two git+https revs collapse to one PathSource; PR closed unmerged, tests-only #17279). not cargo#17289 (checkout directory short-id followed core.abbrev). Distinct leftover: one git+https PackageId collected twice because the checkout walk PathBuf kept CARGO_HOME `..` while nested path= used the collapsed spelling.
