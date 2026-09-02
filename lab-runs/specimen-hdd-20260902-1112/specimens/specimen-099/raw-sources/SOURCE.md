repository: rust-lang/cargo
issue: https://github.com/rust-lang/cargo/issues/7987
pr: https://github.com/rust-lang/cargo/pull/16246
failing_ref (merge first parent): e91b2baa632c0c7e84216c91ecfe107c37d887c1
fixed_ref (squash merge): 0101bde5602af3625c2014fec9b0c497b3e7ef1f
pr_head: cf022a5752379e517d666ecc491298752b6190a0
second_parent: cf022a5752379e517d666ecc491298752b6190a0
merged_at: 2025-12-14T16:38:23Z
merged_by: weihanglo
pr_author: avnyu
changed_files: src/cargo/sources/git/source.rs, src/cargo/sources/git/utils.rs, tests/testsuite/git.rs
pr_title: Cache submodule into git db
milestone: 1.94.0
scout_note: not specimen-091 PathBuf ... not specimen-007 libgit2. Distinct leftover: nested submodule fetch skipped git/db so checkout-only identity.
