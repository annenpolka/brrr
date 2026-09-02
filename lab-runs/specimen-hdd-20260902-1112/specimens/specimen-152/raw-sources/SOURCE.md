repository: bazel-contrib/rules_distroless
issue: https://github.com/bazel-contrib/rules_distroless/pull/237
pr: https://github.com/bazel-contrib/rules_distroless/pull/237
failing_ref (parent of squash on main): 42dd9a20c5c761e4131325a2cf594a753ffffa2d
fixed_ref (snapshot URL in facts key): 52a250a1135cd35440a3ff6616fc4f6ebd4819a0
merged_at: 2026-07-28T18:35:23Z
pr_author: blorente
merged_by: thesayyn
changed_files: apt/extensions.bzl, apt/private/util.bzl, apt/tests/BUILD.bazel, apt/tests/facts_test.bzl
pr_title: fix: Add snapshot URL to facts keys
scout_note: not bazel#29298 env_inherit / not 064/070 nix / not 136 pants vcs. leftover apt facts after snapshot URL upgrade because URL omitted from fact key. unique vs 001-150.
