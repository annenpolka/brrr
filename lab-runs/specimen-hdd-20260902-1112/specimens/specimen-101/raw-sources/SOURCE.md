repository: rust-lang/cargo
issue: https://github.com/rust-lang/cargo/issues/16740
pr: https://github.com/rust-lang/cargo/pull/16744
failing_ref (merge first parent): 843a683fef61e9b3f9607ab637b72b0774241513
fixed_ref (merge commit): cbb9bb8bd0fb272b1be0d63a010701ecb3d1d6d3
pr_head: f351947b87e997715796d3dc468e8e811f0e4dca
second_parent: f351947b87e997715796d3dc468e8e811f0e4dca
merged_at: 2026-03-13T15:12:23Z
merged_by: epage
pr_author: weihanglo
changed_files: src/cargo/sources/git/source.rs, src/cargo/sources/git/utils.rs, tests/testsuite/git.rs
pr_title: fix(git): preserve SCP-like submodule URLs for fetch
milestone: 1.96.0
related_pr: https://github.com/rust-lang/cargo/pull/16727
scout_note: not specimen-091 cargo PathBuf .. duplicate. Distinct leftover: GitRemote/fetch used converted ssh:// while .gitmodules still named the SCP-like URL.
