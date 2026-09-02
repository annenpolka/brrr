repository: jdx/mise
discussion: https://github.com/jdx/mise/discussions/9978
pr: https://github.com/jdx/mise/pull/10114
failing_ref (squash parent): 2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c
fixed_ref (squash merge): f38bab024878162972660d16935ac5cc8340a582
merged_at: 2026-05-28T06:22:54Z
merged_by: jdx
pr_author: jdx
changed_files: e2e/cli/test_upgrade, src/cli/upgrade.rs, src/toolset/mod.rs
pr_title: fix(upgrade): preserve versions pinned by tracked locks
scout_note: not uv git-vs-directory. Distinct leftover: sibling tracked lock pin omitted from upgrade keep-set because use_locked_version=false was global.
