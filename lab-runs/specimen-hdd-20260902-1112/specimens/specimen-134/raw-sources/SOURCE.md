repository: moonrepo/moon
issue: https://github.com/moonrepo/moon/issues/481
pr: https://github.com/moonrepo/moon/pull/482
failing_ref (parent of squash on master): 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
fixed_ref (Fix an issue where .env is not considered an input): 2959d6f0bcc9dbe12fb3f35e54186d245b44586a
merged_at: 2022-11-30T23:58:31Z
pr_author: milesj
merged_by: milesj
changed_files: crates/core/task/src/task.rs, crates/core/vcs/src/git.rs, crates/core/runner/src/actions/run_target.rs, crates/cli/tests/run_test.rs
pr_title: fix: Fix an issue where `.env` is not considered an input.
scout_note: not 119 pixi leftover args. not 115 go-task leftover MATCH. Distinct leftover: env file omitted from task.inputs and skipped when gitignored so leftover cache after .env change is treated as current.
